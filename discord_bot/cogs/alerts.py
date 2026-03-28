# PiicaBot — discord_bot/cogs/alerts.py
# Live stream alerts with polished UX.

import aiohttp
import time
import discord
from discord.ext import commands, tasks
from loguru import logger

import database.db as db
from discord_bot.ui import (
    live_alert_embed, offline_embed,
    live_status_embed, offline_status_embed,
    error_embed,
)
from config import (
    TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET,
    TWITCH_CHANNEL, DISCORD_LIVE_CHANNEL_ID,
)

TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"
TWITCH_TOKEN_URL   = "https://id.twitch.tv/oauth2/token"

_token_cache: dict = {"token": None, "expires_at": 0}


async def _get_app_token() -> str | None:
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TWITCH_TOKEN_URL, params=params,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                _token_cache["token"]      = data["access_token"]
                _token_cache["expires_at"] = now + data["expires_in"]
                return _token_cache["token"]
    except Exception as e:
        logger.error(f"Token fetch failed: {e}")
        return None


class AlertsCog(commands.Cog):

    def __init__(self, bot):
        self.bot        = bot
        self._was_live  = False
        self._alert_msg = None
        self._check_stream.start()

    def cog_unload(self):
        self._check_stream.cancel()

    @tasks.loop(minutes=2)
    async def _check_stream(self) -> None:
        token = await _get_app_token()
        if not token:
            return
        headers = {
            "Client-ID":     TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    TWITCH_STREAMS_URL,
                    headers=headers,
                    params={"user_login": TWITCH_CHANNEL},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        return
                    data = await resp.json()

            streams = data.get("data", [])
            is_live = bool(streams)

            if is_live and not self._was_live:
                stream = streams[0]
                thumb  = stream.get("thumbnail_url", "").replace("{width}", "1280").replace("{height}", "720")
                await self._post_live(stream, thumb)
                self._was_live = True
                logger.info(f"Stream live: {stream.get('title', '')}")

            elif not is_live and self._was_live:
                await self._post_offline()
                self._was_live = False
                logger.info("Stream offline")

        except Exception as e:
            logger.error(f"Stream check error: {e}")

    @_check_stream.before_loop
    async def _before_check(self):
        await self.bot.wait_until_ready()

    async def _post_live(self, stream: dict, thumb: str) -> None:
        channel = self.bot.get_channel(DISCORD_LIVE_CHANNEL_ID)
        if not channel:
            return

        embed = live_alert_embed(
            title=stream.get("title", ""),
            game=stream.get("game_name", ""),
            viewer_count=stream.get("viewer_count", 0),
            thumbnail_url=thumb,
            stream_url=f"https://twitch.tv/{TWITCH_CHANNEL}",
        )

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Watch live",
            url=f"https://twitch.tv/{TWITCH_CHANNEL}",
            style=discord.ButtonStyle.link,
            emoji="🔴",
        ))

        try:
            self._alert_msg = await channel.send(
                content=f"@here  **{TWITCH_CHANNEL}** is live.",
                embed=embed,
                view=view,
            )
        except discord.Forbidden:
            logger.error("Missing permission to post live alert")

    async def _post_offline(self) -> None:
        if not self._alert_msg:
            return
        try:
            await self._alert_msg.edit(
                content="The stream has ended.",
                embed=offline_embed(),
                view=None,
            )
        except Exception as e:
            logger.debug(f"Could not edit offline message: {e}")
        finally:
            self._alert_msg = None

    @discord.app_commands.command(
        name="livestatus",
        description="Check if Majopiica is currently live"
    )
    async def livestatus(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        token = await _get_app_token()
        if not token:
            await interaction.followup.send(
                embed=error_embed("Could not reach Twitch API.", "Try again in a moment."),
                ephemeral=True,
            )
            return

        try:
            headers = {
                "Client-ID":     TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {token}",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    TWITCH_STREAMS_URL,
                    headers=headers,
                    params={"user_login": TWITCH_CHANNEL},
                ) as resp:
                    data = await resp.json()

            streams = data.get("data", [])
            if streams:
                s     = streams[0]
                thumb = s.get("thumbnail_url", "").replace("{width}", "1280").replace("{height}", "720")
                s["thumbnail_url"] = thumb
                view = discord.ui.View()
                view.add_item(discord.ui.Button(
                    label="Watch now",
                    url=f"https://twitch.tv/{TWITCH_CHANNEL}",
                    style=discord.ButtonStyle.link,
                    emoji="🔴",
                ))
                await interaction.followup.send(embed=live_status_embed(s), view=view)
            else:
                await interaction.followup.send(embed=offline_status_embed())

        except Exception as e:
            logger.error(f"livestatus error: {e}")
            await interaction.followup.send(
                embed=error_embed("Could not fetch stream status."),
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(AlertsCog(bot))
