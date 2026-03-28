# PiicaBot — twitch_bot/commands/moderation.py
# Moderation commands: !permit, !poll, !addcmd, !editcmd, !delcmd (streamer only)
# Also handles auto-mod (spam filter, link filter, banned words)

import re
from datetime import datetime, timedelta
from twitchio.ext import commands
from loguru import logger

import database.db as db


# ── Auto-mod patterns ────────────────────────────────────────

LINK_PATTERN  = re.compile(r"(https?://|www\.|\S+\.\S{2,4}\b)", re.IGNORECASE)
CAPS_THRESHOLD = 0.7   # 70% caps triggers warning


class ModerationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def _respond(self, ctx: commands.Context, message: str) -> None:
        if len(message) > 490:
            message = message[:487] + "..."
        await ctx.send(message)

    def _is_streamer(self, ctx: commands.Context) -> bool:
        return ctx.author.name.lower() == ctx.channel.name.lower()

    def _is_mod_or_streamer(self, ctx: commands.Context) -> bool:
        return ctx.author.is_mod or self._is_streamer(ctx)

    # ── Auto-mod (called from bot.py event_message) ──────────

    async def check_message(self, message) -> bool:
        """
        Run auto-mod checks on a message.
        Returns True if message should be removed/actioned.
        Called from bot.py before processing commands.
        Mods and broadcaster are exempt.
        """
        if message.author.is_mod:
            return False
        if message.channel and message.author.name.lower() == message.channel.name.lower():
            return False

        content  = message.content
        username = message.author.name
        conn     = db.get()

        # ── Link filter ──────────────────────────────────────
        if LINK_PATTERN.search(content):
            # Check if user has a link permit
            async with conn.execute(
                "SELECT expires_at FROM permitted_links WHERE username = ? COLLATE NOCASE",
                (username,)
            ) as cur:
                permit = await cur.fetchone()

            if not permit or datetime.fromisoformat(permit["expires_at"]) < datetime.now():
                # Remove expired permit if exists
                await conn.execute(
                    "DELETE FROM permitted_links WHERE username = ? COLLATE NOCASE",
                    (username,)
                )
                await conn.commit()

                await conn.execute(
                    "INSERT INTO moderation_log (username, action, reason) VALUES (?, ?, ?)",
                    (username, "delete", "link posted without permit")
                )
                await conn.commit()
                logger.info(f"Auto-mod: link blocked from {username}")
                return True

        # ── Banned word filter ───────────────────────────────
        async with conn.execute("SELECT word, action FROM banned_words") as cur:
            banned = await cur.fetchall()

        for row in banned:
            if row["word"].lower() in content.lower():
                await conn.execute(
                    "INSERT INTO moderation_log (username, action, reason) VALUES (?, ?, ?)",
                    (username, row["action"], f"banned word: {row['word']}")
                )
                await conn.commit()
                logger.info(f"Auto-mod: banned word '{row['word']}' from {username}")
                return True

        return False

    # ── !permit (mod only) ───────────────────────────────────

    @commands.command(
        name="permit",
        aliases=["allowlink"]
    )
    async def permit(self, ctx: commands.Context, target: str = "") -> None:
        """
        Allow a user to post one link in the next 30 seconds.
        Usage: !permit username
        """
        if not self._is_mod_or_streamer(ctx):
            return

        if not target:
            await self._respond(ctx, "Usage: !permit [username]")
            return

        target   = target.lstrip("@").lower()
        expires  = (datetime.now() + timedelta(seconds=30)).isoformat()
        conn     = db.get()

        await conn.execute(
            """INSERT INTO permitted_links (username, permitted_by, expires_at)
               VALUES (?, ?, ?)
               ON CONFLICT(username) DO UPDATE SET
               permitted_by = ?, expires_at = ?""",
            (target, ctx.author.name, expires, ctx.author.name, expires)
        )
        await conn.commit()
        await self._respond(ctx, f"{target} can post a link for the next 30 seconds.")

    # ── !poll (mod only) ─────────────────────────────────────

    @commands.command(
        name="poll",
        aliases=["vote", "chatvote"]
    )
    async def poll(self, ctx: commands.Context, *, question: str = "") -> None:
        """
        Start a simple A/B chat vote. Viewers type A or B to vote.
        Usage: !poll Is pineapple on pizza good?
        """
        if not self._is_mod_or_streamer(ctx):
            return

        if not question:
            await self._respond(ctx, "Usage: !poll [question] — viewers vote with A or B")
            return

        conn = db.get()

        # Close any existing open polls
        await conn.execute(
            "UPDATE polls SET status = 'closed', closed_at = datetime('now') WHERE status = 'open'"
        )

        # Create new poll
        await conn.execute(
            "INSERT INTO polls (question, created_by) VALUES (?, ?)",
            (question[:200], ctx.author.name)
        )
        await conn.commit()

        await self._respond(
            ctx,
            f"Poll started: {question} | Type A or B to vote! "
            f"Use !pollresults to see results."
        )

    @commands.command(name="pollresults", aliases=["voteresults"])
    async def pollresults(self, ctx: commands.Context) -> None:
        """Show current poll results."""
        conn = db.get()
        async with conn.execute(
            "SELECT * FROM polls WHERE status = 'open' ORDER BY created_at DESC LIMIT 1"
        ) as cur:
            poll = await cur.fetchone()

        if not poll:
            await self._respond(ctx, "No active poll. Start one with !poll [question]")
            return

        total = poll["votes_a"] + poll["votes_b"]
        pct_a = round((poll["votes_a"] / total * 100)) if total > 0 else 0
        pct_b = round((poll["votes_b"] / total * 100)) if total > 0 else 0

        await self._respond(
            ctx,
            f"Poll: {poll['question']} | "
            f"A: {poll['votes_a']} ({pct_a}%) | "
            f"B: {poll['votes_b']} ({pct_b}%) | "
            f"Total votes: {total}"
        )

    @commands.command(name="endpoll", aliases=["closepoll"])
    async def endpoll(self, ctx: commands.Context) -> None:
        """Close the current poll and show final results."""
        if not self._is_mod_or_streamer(ctx):
            return

        conn = db.get()
        async with conn.execute(
            "SELECT * FROM polls WHERE status = 'open' ORDER BY created_at DESC LIMIT 1"
        ) as cur:
            poll = await cur.fetchone()

        if not poll:
            await self._respond(ctx, "No active poll to close.")
            return

        await conn.execute(
            "UPDATE polls SET status = 'closed', closed_at = datetime('now') WHERE id = ?",
            (poll["id"],)
        )
        await conn.commit()

        total = poll["votes_a"] + poll["votes_b"]
        winner = "A" if poll["votes_a"] > poll["votes_b"] else "B" if poll["votes_b"] > poll["votes_a"] else "Tie"
        pct_a  = round((poll["votes_a"] / total * 100)) if total > 0 else 0
        pct_b  = round((poll["votes_b"] / total * 100)) if total > 0 else 0

        await self._respond(
            ctx,
            f"Poll closed! {poll['question']} | "
            f"A: {poll['votes_a']} ({pct_a}%) | "
            f"B: {poll['votes_b']} ({pct_b}%) | "
            f"Winner: {winner} | Total: {total} votes"
        )

    # ── Custom commands (!addcmd, !editcmd, !delcmd) ─────────
    # Streamer only

    @commands.command(name="addcmd")
    async def addcmd(self, ctx: commands.Context, name: str = "", *, response: str = "") -> None:
        """
        Add a custom text command. Streamer only.
        Supports {user} and {count} variables in the response.
        Usage: !addcmd hype {user} just made the chat go wild!
        """
        if not self._is_streamer(ctx):
            return

        if not name or not response:
            await self._respond(ctx, "Usage: !addcmd [name] [response] — e.g. !addcmd hype Chat goes wild!")
            return

        name = name.lstrip("!").lower()

        success = await db.add_custom_command(name, response)
        if success:
            await self._respond(ctx, f"Command !{name} added successfully!")
            logger.info(f"Custom command !{name} added by {ctx.author.name}")
        else:
            await self._respond(
                ctx,
                f"Command !{name} already exists. Use !editcmd to change it."
            )

    @commands.command(name="editcmd")
    async def editcmd(self, ctx: commands.Context, name: str = "", *, response: str = "") -> None:
        """
        Edit an existing custom command. Streamer only.
        Usage: !editcmd hype New response text here!
        """
        if not self._is_streamer(ctx):
            return

        if not name or not response:
            await self._respond(ctx, "Usage: !editcmd [name] [new response]")
            return

        name = name.lstrip("!").lower()
        success = await db.edit_custom_command(name, response)

        if success:
            await self._respond(ctx, f"Command !{name} updated!")
            logger.info(f"Custom command !{name} edited by {ctx.author.name}")
        else:
            await self._respond(ctx, f"Command !{name} not found. Use !addcmd to create it.")

    @commands.command(name="delcmd", aliases=["deletecmd", "removecmd"])
    async def delcmd(self, ctx: commands.Context, name: str = "") -> None:
        """
        Delete a custom command. Streamer only.
        Usage: !delcmd hype
        """
        if not self._is_streamer(ctx):
            return

        if not name:
            await self._respond(ctx, "Usage: !delcmd [name]")
            return

        name    = name.lstrip("!").lower()
        success = await db.delete_custom_command(name)

        if success:
            await self._respond(ctx, f"Command !{name} deleted.")
            logger.info(f"Custom command !{name} deleted by {ctx.author.name}")
        else:
            await self._respond(ctx, f"Command !{name} not found.")

    @commands.command(name="commands", aliases=["cmdlist", "help"])
    async def cmd_list(self, ctx: commands.Context) -> None:
        """List all available commands."""
        await self._respond(
            ctx,
            "PiicaBot commands: "
            "!clip !weather !time !define !wordorigin !space !element "
            "!plate !domain !driveside !writingsystem "
            "!wisdom !quote !points !give !top "
            "!pet !wish !vibe !collective !phobia !randomcolor "
            "!songrequest !currentsong !queue "
            "and many more! Ask in chat what you want to know!"
        )


def prepare(bot):
    bot.add_cog(ModerationCog(bot))
