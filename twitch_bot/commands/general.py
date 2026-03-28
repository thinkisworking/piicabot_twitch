# PiicaBot — twitch_bot/commands/general.py
# Core info commands: !clip, !define, !wordorigin, !weather, !time
# Each command checks cooldown, calls the appropriate service, responds in chat.

from twitchio.ext import commands
from loguru import logger

import database.db as db
from services.weather import get_weather
from services.clock import get_time
from services.dictionary import get_definition, get_etymology
from config import DEFAULT_COOLDOWN


class GeneralCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ── Helpers ──────────────────────────────────────────────

    async def _check_and_update_cooldown(
        self,
        ctx: commands.Context,
        command: str,
        cooldown: int = DEFAULT_COOLDOWN
    ) -> bool:
        """
        Check if user is on cooldown. If yes, optionally whisper remaining time.
        Returns True if the command should proceed, False if on cooldown.
        Mods and the streamer bypass all cooldowns.
        """
        # Mods and broadcaster bypass cooldowns
        if ctx.author.is_mod or ctx.author.name.lower() == ctx.channel.name.lower():
            await db.update_cooldown(ctx.author.name, command)
            return True

        on_cd, remaining = await db.check_cooldown(ctx.author.name, command, cooldown)
        if on_cd:
            # Silent fail — don't spam chat with cooldown messages
            logger.debug(f"Cooldown: {ctx.author.name} tried !{command} — {remaining}s remaining")
            return False

        await db.update_cooldown(ctx.author.name, command)
        await db.increment_command_stat(command)
        return True

    async def _respond(self, ctx: commands.Context, message: str) -> None:
        """Send a response, truncating to Twitch's 500 char limit."""
        if len(message) > 490:
            message = message[:487] + "..."
        await ctx.send(message)

    # ── !clip ────────────────────────────────────────────────

    @commands.command(name="clip")
    async def clip(self, ctx: commands.Context) -> None:
        """
        Creates a Twitch clip of the last 30 seconds and posts the URL.
        Uses the Twitch API via the bot's token.
        """
        if not await self._check_and_update_cooldown(ctx, "clip", 30):
            return

        try:
            # TwitchIO's API wrapper for clip creation
            clips = await self.bot.create_clip(ctx.channel.name)
            if clips:
                clip_url = f"https://clips.twitch.tv/{clips[0].id}"
                await self._respond(ctx, f"Clip created by {ctx.author.name}! {clip_url}")
            else:
                await self._respond(ctx, "Could not create clip. Is the stream live?")
        except Exception as e:
            logger.error(f"Clip creation failed: {e}")
            await self._respond(ctx, "Clip creation failed. Try again in a moment.")

    # ── !define ──────────────────────────────────────────────

    @commands.command(
        name="define",
        aliases=["meaning", "dictionary", "dict", "whatis"]
    )
    async def define(self, ctx: commands.Context, *, word: str = "") -> None:
        """
        Look up the definition of a word from Merriam-Webster.
        Usage: !define ephemeral
        """
        if not word:
            await self._respond(ctx, "Usage: !define [word] — e.g. !define ephemeral")
            return

        if not await self._check_and_update_cooldown(ctx, "define", DEFAULT_COOLDOWN):
            return

        result = await get_definition(word.strip())
        await self._respond(ctx, result)

    # ── !wordorigin ──────────────────────────────────────────

    @commands.command(
        name="wordorigin",
        aliases=["etymology", "wordhistory", "wordroots"]
    )
    async def wordorigin(self, ctx: commands.Context, *, word: str = "") -> None:
        """
        Look up the etymology (word origin) of a word from Merriam-Webster.
        Usage: !wordorigin chaos
        """
        if not word:
            await self._respond(ctx, "Usage: !wordorigin [word] — e.g. !wordorigin chaos")
            return

        if not await self._check_and_update_cooldown(ctx, "wordorigin", DEFAULT_COOLDOWN):
            return

        result = await get_etymology(word.strip())
        await self._respond(ctx, result)

    # ── !weather ─────────────────────────────────────────────

    @commands.command(
        name="weather",
        aliases=["forecast", "currentweather"]
    )
    async def weather(self, ctx: commands.Context, *, location: str = "") -> None:
        """
        Get current weather for any city or country.
        Country names are auto-resolved to their capital city.
        Usage: !weather Tokyo | !weather Japan | !weather New Zealand
        """
        if not location:
            await self._respond(ctx, "Usage: !weather [city or country] — e.g. !weather Tokyo or !weather Japan")
            return

        if not await self._check_and_update_cooldown(ctx, "weather", DEFAULT_COOLDOWN):
            return

        result = await get_weather(location.strip())
        await self._respond(ctx, result)

    # ── !time ────────────────────────────────────────────────

    @commands.command(
        name="time",
        aliases=["localtime", "clockin"]
    )
    async def time_cmd(self, ctx: commands.Context, *, location: str = "") -> None:
        """
        Get the current local time in any city or country.
        Completely offline — instant response.
        Usage: !time Tokyo | !time Japan | !time New Zealand
        """
        if not location:
            await self._respond(ctx, "Usage: !time [city or country] — e.g. !time Tokyo or !time Japan")
            return

        if not await self._check_and_update_cooldown(ctx, "time", DEFAULT_COOLDOWN):
            return

        result = get_time(location.strip())
        await self._respond(ctx, result)


def prepare(bot):
    bot.add_cog(GeneralCog(bot))
