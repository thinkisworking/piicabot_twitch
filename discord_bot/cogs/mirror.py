# PiicaBot — discord_bot/cogs/mirror.py
# Mirrors Twitch chat to Discord with polished UX.

import discord
from discord.ext import commands
from loguru import logger

import database.db as db
from discord_bot.ui import success_embed, info_embed, error_embed
from config import DISCORD_MIRROR_CHANNEL_ID, TWITCH_CHANNEL

_mirror_cog_instance = None


def get_mirror_cog():
    return _mirror_cog_instance


class MirrorCog(commands.Cog):

    def __init__(self, bot):
        self.bot              = bot
        self._mirror_enabled  = True
        self._webhook         = None
        global _mirror_cog_instance
        _mirror_cog_instance = self

    async def post_to_discord(self, username: str, message: str) -> None:
        """Forward a Twitch chat message to the Discord mirror channel."""
        if not self._mirror_enabled:
            return

        channel = self.bot.get_channel(DISCORD_MIRROR_CHANNEL_ID)
        if not channel:
            return

        if message.startswith("!"):
            return

        if len(message) > 400:
            message = message[:397] + "..."

        try:
            if self._webhook:
                await self._webhook.send(
                    content=message,
                    username=f"{username}",
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            else:
                await channel.send(
                    f"**{username}**: {message}",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

            conn = db.get()
            await conn.execute(
                "INSERT INTO mirror_log (source, username, message) VALUES ('twitch', ?, ?)",
                (username, message)
            )
            await conn.commit()

        except discord.Forbidden:
            logger.warning("Missing permission for mirror channel")
        except Exception as e:
            logger.error(f"Mirror error: {e}")

    async def _setup_webhook(self) -> None:
        channel = self.bot.get_channel(DISCORD_MIRROR_CHANNEL_ID)
        if not channel or not isinstance(channel, discord.TextChannel):
            return
        try:
            webhooks = await channel.webhooks()
            for wh in webhooks:
                if wh.name == "PiicaBot Mirror":
                    self._webhook = wh
                    logger.info("Mirror webhook found")
                    return
            self._webhook = await channel.create_webhook(name="PiicaBot Mirror")
            logger.info("Mirror webhook created")
        except discord.Forbidden:
            logger.info("No webhook permission — using regular messages for mirror")
        except Exception as e:
            logger.error(f"Webhook setup error: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        await self._setup_webhook()

    @discord.app_commands.command(
        name="mirrortoggle",
        description="Enable or disable Twitch chat mirroring (mod only)"
    )
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def mirrortoggle(self, interaction: discord.Interaction) -> None:
        self._mirror_enabled = not self._mirror_enabled
        state = "enabled" if self._mirror_enabled else "disabled"
        embed = success_embed(
            f"Twitch chat mirror is now **{state}**.",
            f"Messages from twitch.tv/{TWITCH_CHANNEL} will {'appear' if self._mirror_enabled else 'no longer appear'} in this server."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Mirror {state} by {interaction.user.name}")

    @discord.app_commands.command(
        name="mirrorstatus",
        description="Check if Twitch chat mirroring is active"
    )
    async def mirrorstatus(self, interaction: discord.Interaction) -> None:
        state = "active" if self._mirror_enabled else "paused"
        embed = info_embed(
            "Mirror status",
            f"Twitch chat mirroring is currently **{state}**."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MirrorCog(bot))
