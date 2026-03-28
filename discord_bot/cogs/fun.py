# PiicaBot — discord_bot/cogs/fun.py
# All Discord slash commands with polished UX.
# Uses discord_bot/ui.py for consistent embed design.

import asyncio
import random
import discord
from discord.ext import commands
from loguru import logger

import database.db as db
from discord_bot.ui import (
    stream_quote_embed, wisdom_quote_embed,
    poll_embed, poll_results_embed,
    giveaway_embed, giveaway_winner_embed, giveaway_no_entries_embed,
    milestone_embed, no_milestones_embed,
    piicasays_embed, help_embed,
    success_embed, error_embed, info_embed,
)
from config import TWITCH_CHANNEL, DISCORD_GUILD_ID


# ─────────────────────────────────────────────────────────────
# POLL VIEW — interactive buttons for voting
# ─────────────────────────────────────────────────────────────

class PollView(discord.ui.View):
    """
    Interactive poll with A/B buttons.
    Tracks votes per user — one vote each.
    Shows live results as percentages update.
    """

    def __init__(self, question: str, option_a: str, option_b: str):
        super().__init__(timeout=None)   # persistent until manually closed
        self.question = question
        self.option_a = option_a
        self.option_b = option_b
        self.votes_a: set[int] = set()
        self.votes_b: set[int] = set()

    def _result_embed(self, closed: bool = False) -> discord.Embed:
        return poll_results_embed(
            question=self.question,
            votes_a=len(self.votes_a),
            votes_b=len(self.votes_b),
            option_a=self.option_a,
            option_b=self.option_b,
        ) if closed else poll_embed(
            self.question, self.option_a, self.option_b, "PiicaBot"
        )

    @discord.ui.button(label="A", style=discord.ButtonStyle.secondary, emoji="🅰️")
    async def vote_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if uid in self.votes_a:
            await interaction.response.send_message(
                "You've already voted **A**.", ephemeral=True
            )
            return
        self.votes_b.discard(uid)
        self.votes_a.add(uid)
        await interaction.response.send_message(
            f"Voted for **{self.option_a}**.", ephemeral=True
        )

    @discord.ui.button(label="B", style=discord.ButtonStyle.secondary, emoji="🅱️")
    async def vote_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        if uid in self.votes_b:
            await interaction.response.send_message(
                "You've already voted **B**.", ephemeral=True
            )
            return
        self.votes_a.discard(uid)
        self.votes_b.add(uid)
        await interaction.response.send_message(
            f"Voted for **{self.option_b}**.", ephemeral=True
        )

    @discord.ui.button(label="Results", style=discord.ButtonStyle.primary, emoji="📊")
    async def show_results(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = poll_results_embed(
            question=self.question,
            votes_a=len(self.votes_a),
            votes_b=len(self.votes_b),
            option_a=self.option_a,
            option_b=self.option_b,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ─────────────────────────────────────────────────────────────
# MAIN COG
# ─────────────────────────────────────────────────────────────

class FunCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ── /help ────────────────────────────────────────────────

    @discord.app_commands.command(
        name="help",
        description="Show all PiicaBot commands"
    )
    async def help_cmd(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=help_embed())

    # ── /quote ───────────────────────────────────────────────

    @discord.app_commands.command(
        name="quote",
        description="Get a random Majopiica stream quote"
    )
    async def quote(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        row = await db.get_random_stream_quote()
        if not row:
            await interaction.followup.send(
                embed=info_embed(
                    "No quotes yet",
                    "No stream quotes have been saved.\n"
                    "Majopiica can add one with `!addquote` in Twitch chat."
                )
            )
            return

        await interaction.followup.send(embed=stream_quote_embed(row))

    # ── /wisdom ──────────────────────────────────────────────

    @discord.app_commands.command(
        name="wisdom",
        description="Get a verified philosophy quote"
    )
    async def wisdom(
        self,
        interaction: discord.Interaction,
        author: str = "",
        topic: str = "",
        era: str = "",
    ) -> None:
        """
        Philosophy quote — optionally filtered.
        All parameters are optional.
        """
        await interaction.response.defer(thinking=True)

        row = await db.get_random_wisdom_quote(
            author=author.strip(),
            tag=topic.strip(),
            era=era.strip(),
        )

        if not row:
            filters = []
            if author:
                filters.append(f"author: *{author}*")
            if topic:
                filters.append(f"topic: *{topic}*")
            if era:
                filters.append(f"era: *{era}*")
            filter_str = "  ·  ".join(filters) if filters else "any"

            await interaction.followup.send(
                embed=error_embed(
                    "No quotes found.",
                    f"Filters applied: {filter_str}\n"
                    f"Try without filters, or try: author=`marcus aurelius`, era=`ancient`"
                ),
                ephemeral=True,
            )
            return

        # Add "another quote" button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Another",
            style=discord.ButtonStyle.secondary,
            emoji="✦",
            custom_id="wisdom_another",
        ))
        await interaction.followup.send(embed=wisdom_quote_embed(row))

    # ── /poll ────────────────────────────────────────────────

    @discord.app_commands.command(
        name="poll",
        description="Create an interactive poll (mod only)"
    )
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option_a: str = "Yes",
        option_b: str = "No",
    ) -> None:
        """Create a poll with interactive vote buttons."""
        view  = PollView(question, option_a, option_b)
        embed = poll_embed(question, option_a, option_b, interaction.user.display_name)

        # Add close button for the mod
        close_btn = discord.ui.Button(
            label="Close poll",
            style=discord.ButtonStyle.danger,
            emoji="🔒",
        )

        async def close_poll(btn_interaction: discord.Interaction):
            if not btn_interaction.user.guild_permissions.manage_messages:
                await btn_interaction.response.send_message(
                    "Only mods can close polls.", ephemeral=True
                )
                return
            # Show final results
            result_embed = poll_results_embed(
                question=question,
                votes_a=len(view.votes_a),
                votes_b=len(view.votes_b),
                option_a=option_a,
                option_b=option_b,
            )
            view.stop()
            for child in view.children:
                child.disabled = True
            await btn_interaction.response.edit_message(embed=result_embed, view=view)

        close_btn.callback = close_poll
        view.add_item(close_btn)

        await interaction.response.send_message(embed=embed, view=view)

        # Also save to DB for Twitch bot !pollresults
        conn = db.get()
        await conn.execute(
            "UPDATE polls SET status = 'closed', closed_at = datetime('now') WHERE status = 'open'"
        )
        await conn.execute(
            "INSERT INTO polls (question, option_a, option_b, created_by) VALUES (?, ?, ?, ?)",
            (question, option_a, option_b, interaction.user.name)
        )
        await conn.commit()

    # ── /giveaway ────────────────────────────────────────────

    @discord.app_commands.command(
        name="giveaway",
        description="Start a timed giveaway (mod only)"
    )
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def giveaway(
        self,
        interaction: discord.Interaction,
        prize: str,
        duration_minutes: int = 5,
    ) -> None:
        """Run a timed giveaway — members click to enter."""
        if duration_minutes < 1 or duration_minutes > 60:
            await interaction.response.send_message(
                embed=error_embed("Invalid duration.", "Must be between 1 and 60 minutes."),
                ephemeral=True,
            )
            return

        # Track entrants
        entrants: set[int] = set()

        view = discord.ui.View(timeout=duration_minutes * 60)

        enter_btn = discord.ui.Button(
            label="Enter giveaway",
            style=discord.ButtonStyle.primary,
            emoji="🎉",
        )

        async def enter(btn_interaction: discord.Interaction):
            uid = btn_interaction.user.id
            if uid in entrants:
                await btn_interaction.response.send_message(
                    "You're already entered — good luck!", ephemeral=True
                )
                return
            entrants.add(uid)
            count = len(entrants)
            await btn_interaction.response.send_message(
                f"You're entered! **{count}** {'person has' if count == 1 else 'people have'} entered.",
                ephemeral=True,
            )

        enter_btn.callback = enter
        view.add_item(enter_btn)

        embed = giveaway_embed(prize, duration_minutes, interaction.user.display_name)
        await interaction.response.send_message(embed=embed, view=view)

        logger.info(f"Giveaway started: {prize} ({duration_minutes}min)")

        # Wait for duration
        await asyncio.sleep(duration_minutes * 60)

        # Disable buttons
        for child in view.children:
            child.disabled = True

        # Pick winner
        try:
            msg = await interaction.original_response()
            if entrants:
                winner_id = random.choice(list(entrants))
                guild     = self.bot.get_guild(DISCORD_GUILD_ID)
                winner    = guild.get_member(winner_id) if guild else None

                if winner:
                    await msg.edit(view=view)
                    await interaction.channel.send(
                        content=winner.mention,
                        embed=giveaway_winner_embed(prize, winner),
                    )
                    logger.info(f"Giveaway winner: {winner.name} — {prize}")
                else:
                    await interaction.channel.send(
                        embed=giveaway_no_entries_embed(prize)
                    )
            else:
                await msg.edit(view=view)
                await interaction.channel.send(
                    embed=giveaway_no_entries_embed(prize)
                )
        except Exception as e:
            logger.error(f"Giveaway resolution error: {e}")

    # ── /milestone ───────────────────────────────────────────

    @discord.app_commands.command(
        name="milestone",
        description="Show current channel milestone goals"
    )
    async def milestone(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        conn = db.get()
        async with conn.execute(
            "SELECT * FROM milestones WHERE achieved = 0 ORDER BY target LIMIT 5"
        ) as cur:
            milestones = await cur.fetchall()

        if not milestones:
            await interaction.followup.send(embed=no_milestones_embed())
            return

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label=f"Follow on Twitch",
            url=f"https://twitch.tv/{TWITCH_CHANNEL}",
            style=discord.ButtonStyle.link,
            emoji="🔴",
        ))
        await interaction.followup.send(embed=milestone_embed(milestones), view=view)

    # ── /piicasays ───────────────────────────────────────────

    @discord.app_commands.command(
        name="piicasays",
        description="Get a random Majopiica catchphrase"
    )
    async def piicasays(self, interaction: discord.Interaction) -> None:
        conn = db.get()
        async with conn.execute(
            "SELECT * FROM piicasays ORDER BY RANDOM() LIMIT 1"
        ) as cur:
            row = await cur.fetchone()

        if not row:
            await interaction.response.send_message(
                embed=info_embed(
                    "Nothing saved yet",
                    "No catchphrases have been added. Mods can add them with `/addpiicasays`."
                ),
                ephemeral=True,
            )
            return

        await conn.execute(
            "UPDATE piicasays SET use_count = use_count + 1 WHERE id = ?",
            (row["id"],)
        )
        await conn.commit()

        await interaction.response.send_message(
            embed=piicasays_embed(row["text"], row["use_count"] + 1)
        )

    # ── /clip ────────────────────────────────────────────────

    @discord.app_commands.command(
        name="clip",
        description="Browse Majopiica's Twitch clips"
    )
    async def clip(self, interaction: discord.Interaction) -> None:
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Browse clips",
            url=f"https://www.twitch.tv/{TWITCH_CHANNEL}/clips",
            style=discord.ButtonStyle.link,
            emoji="🎬",
        ))
        embed = info_embed(
            "Clips",
            f"Browse all clips from **{TWITCH_CHANNEL}** on Twitch."
        )
        await interaction.response.send_message(embed=embed, view=view)

    # ── Mod management commands ──────────────────────────────

    @discord.app_commands.command(
        name="addpiicasays",
        description="Add a Majopiica catchphrase (mod only)"
    )
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def addpiicasays(
        self,
        interaction: discord.Interaction,
        text: str,
        context: str = "",
    ) -> None:
        conn = db.get()
        await conn.execute(
            "INSERT INTO piicasays (text, context) VALUES (?, ?)",
            (text[:500], context[:200])
        )
        await conn.commit()
        await interaction.response.send_message(
            embed=success_embed(
                "Catchphrase saved.",
                f'*"{text[:80]}{"..." if len(text) > 80 else ""}"*'
            ),
            ephemeral=True,
        )
        logger.info(f"Catchphrase added by {interaction.user.name}: {text[:50]}")

    @discord.app_commands.command(
        name="addmilestone",
        description="Add a channel milestone goal (mod only)"
    )
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def addmilestone(
        self,
        interaction: discord.Interaction,
        label: str,
        target: int,
        milestone_type: str = "followers",
    ) -> None:
        if milestone_type not in ("followers", "subs", "custom"):
            await interaction.response.send_message(
                embed=error_embed(
                    "Invalid type.",
                    "Must be one of: `followers`, `subs`, `custom`"
                ),
                ephemeral=True,
            )
            return

        conn = db.get()
        await conn.execute(
            "INSERT INTO milestones (type, target, label) VALUES (?, ?, ?)",
            (milestone_type, target, label[:200])
        )
        await conn.commit()
        await interaction.response.send_message(
            embed=success_embed(
                "Milestone added.",
                f"**{label}** — target: {target:,} {milestone_type}"
            ),
            ephemeral=True,
        )

    # ── Error handlers ───────────────────────────────────────

    @poll.error
    @giveaway.error
    @addpiicasays.error
    @addmilestone.error
    async def mod_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ) -> None:
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message(
                embed=error_embed(
                    "Permission denied.",
                    "This command requires the **Manage Messages** permission."
                ),
                ephemeral=True,
            )
        else:
            logger.error(f"Command error: {error}")
            await interaction.response.send_message(
                embed=error_embed("Something went wrong.", str(error)[:200]),
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(FunCog(bot))
