# PiicaBot — discord_bot/bot.py
# Main Discord bot class.
# Connects to Discord, loads all cogs, handles events.

import discord
from discord.ext import commands
from loguru import logger

import database.db as db
from discord_bot.ui import welcome_embed
from config import (
    DISCORD_TOKEN, DISCORD_GUILD_ID,
    DISCORD_LIVE_CHANNEL_ID, DISCORD_MIRROR_CHANNEL_ID,
    DISCORD_LOG_CHANNEL_ID,
)


class PiicaDiscord(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members          = True
        intents.guilds           = True

        super().__init__(
            command_prefix="?",          # Discord prefix (separate from Twitch !)
            intents=intents,
            help_command=None,           # we write our own
        )
        self.guild_id = DISCORD_GUILD_ID

    # ── Startup ──────────────────────────────────────────────

    async def setup_hook(self) -> None:
        """Called before the bot connects — load cogs here."""
        from discord_bot.cogs.alerts  import AlertsCog
        from discord_bot.cogs.mirror  import MirrorCog
        from discord_bot.cogs.roles   import RolesCog
        from discord_bot.cogs.fun     import FunCog

        await self.add_cog(AlertsCog(self))
        await self.add_cog(MirrorCog(self))
        await self.add_cog(RolesCog(self))
        await self.add_cog(FunCog(self))

        # Sync slash commands to the guild
        guild = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        logger.info("Discord cogs loaded and slash commands synced")

    async def on_ready(self) -> None:
        logger.info(f"Discord bot ready as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="majopiica's stream"
            )
        )

    # ── Error handling ───────────────────────────────────────

    async def on_command_error(self, ctx, error) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Discord command error: {error}")

    # ── Member events ────────────────────────────────────────

    async def on_member_join(self, member: discord.Member) -> None:
        """Welcome new members with polished embed."""
        if member.guild.id != self.guild_id:
            return

        channel = (
            member.guild.system_channel
            or self.get_channel(DISCORD_LOG_CHANNEL_ID)
        )
        if channel:
            try:
                await channel.send(embed=welcome_embed(member))
            except discord.Forbidden:
                logger.warning("Cannot send welcome message — missing permissions")

        logger.info(f"New member: {member.name} (#{member.guild.member_count})")


def create_bot() -> PiicaDiscord:
    """Factory function — creates and returns the Discord bot instance."""
    return PiicaDiscord()
