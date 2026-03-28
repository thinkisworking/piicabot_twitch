# PiicaBot — twitch_bot/bot.py
# Main Twitch bot class. Connects to Twitch IRC, loads all command cogs,
# handles events (messages, subs, raids, follows, bits),
# runs the points scheduler, and processes custom commands.

import asyncio
from twitchio.ext import commands, routines
from loguru import logger

import database.db as db
from config import (
    TWITCH_ACCESS_TOKEN, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET,
    TWITCH_CHANNEL, BOT_NICK,
    POINTS_PER_MINUTE, POINTS_PER_MESSAGE,
    POINTS_ON_SUB, POINTS_ON_RAID,
)
from twitch_bot.commands.fun import add_to_vibe_buffer


class PiicaBot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_ACCESS_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            nick=BOT_NICK,
            prefix="!",
            initial_channels=[TWITCH_CHANNEL],
        )
        self._channel_name = TWITCH_CHANNEL
        self._viewers: set[str] = set()   # currently active viewers for points

    # ── Startup ──────────────────────────────────────────────

    async def event_ready(self) -> None:
        logger.info(f"PiicaBot connected as {self.nick}")
        logger.info(f"Watching channel: {self._channel_name}")

        # Load all command cogs
        self._load_cogs()

        # Start the points scheduler
        self._points_ticker.start()

        channel = self.get_channel(self._channel_name)
        if channel:
            await channel.send("PiicaBot is online! Type !commands to see what I can do.")

    def _load_cogs(self) -> None:
        """Load all command modules."""
        from twitch_bot.commands.general    import GeneralCog
        from twitch_bot.commands.points     import PointsCog
        from twitch_bot.commands.quotes     import QuotesCog
        from twitch_bot.commands.fun        import FunCog
        from twitch_bot.commands.moderation import ModerationCog

        self.add_cog(GeneralCog(self))
        self.add_cog(PointsCog(self))
        self.add_cog(QuotesCog(self))
        self.add_cog(FunCog(self))
        self.add_cog(ModerationCog(self))

        logger.info("All Twitch command cogs loaded")

    # ── Points ticker (every 60 seconds) ────────────────────

    @routines.routine(seconds=60)
    async def _points_ticker(self) -> None:
        """Award watch-time points to all active viewers every minute."""
        if not self._viewers:
            return
        for username in list(self._viewers):
            try:
                await db.add_points(username, POINTS_PER_MINUTE, "watch_time")
                await db.add_watch_minutes(username, 1)
            except Exception as e:
                logger.error(f"Points ticker error for {username}: {e}")

    # ── Message handler ──────────────────────────────────────

    async def event_message(self, message) -> None:
        """Handle every incoming chat message."""
        # Ignore messages from the bot itself
        if message.echo:
            return
        if not message.author:
            return

        username = message.author.name
        content  = message.content

        # Track viewer for points
        self._viewers.add(username.lower())

        # Update last seen and message count
        await db.get_or_create_user(username)
        await db.increment_message_count(username)

        # Feed vibe buffer
        add_to_vibe_buffer(content)

        # Run auto-mod check (skip commands)
        if not content.startswith("!"):
            from twitch_bot.commands.moderation import ModerationCog
            mod_cog = self.cogs.get("ModerationCog")
            if mod_cog:
                actioned = await mod_cog.check_message(message)
                if actioned:
                    return

            # Award message points
            await db.add_points(username, POINTS_PER_MESSAGE, "message")

        # Handle poll votes (A or B)
        if content.strip().upper() in ("A", "B") and not content.startswith("!"):
            await self._handle_poll_vote(username, content.strip().upper())

        # Check for custom commands
        if content.startswith("!"):
            cmd_name = content.split()[0][1:].lower()
            custom = await db.get_custom_command(cmd_name)
            if custom:
                await self._run_custom_command(message, custom)
                return

        # Process built-in commands
        await self.handle_commands(message)

    async def _run_custom_command(self, message, command) -> None:
        """Execute a custom command, replacing variables in the response."""
        response = command["response"]
        response = response.replace("{user}", message.author.name)
        response = response.replace("{channel}", self._channel_name)
        response = response.replace("{count}", str(command["use_count"] + 1))

        await db.increment_custom_command_count(command["name"])

        channel = self.get_channel(self._channel_name)
        if channel and len(response) <= 500:
            await channel.send(response)

    async def _handle_poll_vote(self, username: str, vote: str) -> None:
        """Record a poll vote from a viewer."""
        conn = db.get()
        async with conn.execute(
            "SELECT id FROM polls WHERE status = 'open' ORDER BY created_at DESC LIMIT 1"
        ) as cur:
            poll = await cur.fetchone()

        if not poll:
            return

        try:
            await conn.execute(
                "INSERT INTO poll_votes (poll_id, username, vote) VALUES (?, ?, ?)",
                (poll["id"], username, vote)
            )
            col = "votes_a" if vote == "A" else "votes_b"
            await conn.execute(
                f"UPDATE polls SET {col} = {col} + 1 WHERE id = ?",
                (poll["id"],)
            )
            await conn.commit()
        except Exception:
            # Duplicate vote — user already voted
            pass

    # ── Channel events ───────────────────────────────────────

    async def event_join(self, channel, user) -> None:
        """Track viewers as they join."""
        if user.name.lower() != self.nick.lower():
            self._viewers.add(user.name.lower())
            await db.get_or_create_user(user.name)

    async def event_part(self, user) -> None:
        """Remove viewers as they leave."""
        self._viewers.discard(user.name.lower())

    async def event_subscription(self, subscription) -> None:
        """Award points on subscription."""
        username = subscription.user.name
        await db.add_points(username, POINTS_ON_SUB, "subscription")
        logger.info(f"Sub event: {username} — +{POINTS_ON_SUB} PiicaPoints")

    async def event_raid(self, raid) -> None:
        """Award points to the raider."""
        raider   = raid.raider.name
        viewers  = raid.viewer_count
        await db.add_points(raider, POINTS_ON_RAID, "raid")
        logger.info(f"Raid: {raider} brought {viewers} viewers — +{POINTS_ON_RAID} PiicaPoints")

    async def event_bits(self, bits) -> None:
        """Award points for bits (50 points per 100 bits)."""
        username   = bits.user.name
        bits_count = bits.bits_used
        points     = (bits_count // 100) * 50
        if points > 0:
            await db.add_points(username, points, f"bits_{bits_count}")
            logger.info(f"Bits: {username} cheered {bits_count} bits — +{points} PiicaPoints")

    # ── Error handler ────────────────────────────────────────

    async def event_command_error(self, ctx, error) -> None:
        """Handle command errors gracefully."""
        if isinstance(error, commands.CommandNotFound):
            # Unknown command — check if it might be a typo of a custom command
            return
        logger.error(f"Command error in {ctx.command}: {error}")
