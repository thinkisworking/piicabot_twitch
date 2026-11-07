# English: Stream monitoring cog. Warns the broadcaster if streams are left running indefinitely.
# Italiano: Cog di monitoraggio dello streaming. Avvisa lo streamer se gli stream rimangono aperti indefinitamente.

import asyncio
import aiohttp
from datetime import datetime, timezone
from twitchio.ext import commands, routines
from loguru import logger
from config import TWITCH_CHANNEL, _optional

# English: Alert threshold in hours. If stream is live longer than this, trigger warning.
# Italiano: Soglia di allarme in ore. Se lo stream è live per più tempo, attiva l'avviso.
MAX_STREAM_HOURS = 12.0 
YOUTUBE_API_KEY = _optional("YOUTUBE_API_KEY", None)
YOUTUBE_CHANNEL_ID = _optional("YOUTUBE_CHANNEL_ID", None)
TIKTOK_USERNAME = _optional("TIKTOK_USERNAME", None)

class MonitorCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._monitor_streams.start()

    def cog_unload(self):
        """
        English: Stops the routine when the cog is unloaded.
        Italiano: Interrompe la routine quando il cog viene scaricato.
        """
        self._monitor_streams.stop()

    @routines.routine(minutes=30)
    async def _monitor_streams(self) -> None:
        """
        English: Checks Twitch, YouTube, and TikTok stream status every 30 minutes.
        Italiano: Controlla lo stato dello stream su Twitch, YouTube e TikTok ogni 30 minuti.
        """
        await self._check_twitch()
        if YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID:
            await self._check_youtube()
        if TIKTOK_USERNAME:
            await self._check_tiktok()

    async def _check_twitch(self) -> None:
        """
        English: Checks Twitch uptime using TwitchIO's built-in methods.
        Italiano: Controlla l'uptime di Twitch utilizzando i metodi integrati di TwitchIO.
        """
        try:
            streams = await self.bot.fetch_streams(user_logins=[TWITCH_CHANNEL])
            if streams:
                stream = streams[0]
                started_at = stream.started_at
                now = datetime.now(timezone.utc)
                uptime = (now - started_at).total_seconds() / 3600.0

                if uptime > MAX_STREAM_HOURS:
                    await self._send_alert("Twitch", uptime)
        except Exception as e:
            logger.error(f"Twitch monitor error: {e}")

    async def _check_youtube(self) -> None:
        """
        English: Checks YouTube live status via YouTube Data API v3.
        Italiano: Controlla lo stato live di YouTube tramite l'API YouTube Data v3.
        """
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={YOUTUBE_CHANNEL_ID}&type=video&eventType=live&key={YOUTUBE_API_KEY}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("items"):
                            # English: Simplified check. For exact uptime, another API call to 'videos' endpoint is needed.
                            # Italiano: Controllo semplificato. Per l'uptime esatto, è necessaria un'altra chiamata API all'endpoint 'videos'.
                            logger.warning("YouTube stream is currently live.")
        except Exception as e:
            logger.error(f"YouTube monitor error: {e}")

    async def _check_tiktok(self) -> None:
        """
        English: Placeholder for TikTok live check. TikTok lacks a public API for this; requires scraping/unofficial endpoints.
        Italiano: Segnaposto per il controllo live di TikTok. TikTok non ha un'API pubblica per questo; richiede scraping/endpoint non ufficiali.
        """
        # Note: Implementation depends on specific unofficial TikTok wrappers (e.g., TikTokLive).
        logger.debug(f"TikTok monitor skipped for {TIKTOK_USERNAME} (Requires unofficial API).")

    async def _send_alert(self, platform: str, hours: float) -> None:
        """
        English: Sends a high-priority alert to the chat and logs it.
        Italiano: Invia un avviso ad alta priorità alla chat e lo registra.
        """
        channel = self.bot.get_channel(TWITCH_CHANNEL)
        alert_msg = f"@{TWITCH_CHANNEL} (⊙ _ ⊙ ) : Your {platform} stream has been running for over {hours:.1f} hours! Did you forget to turn it off? ( 0 x 0 )"
        
        logger.critical(alert_msg)
        if channel:
            await channel.send(alert_msg)


def prepare(bot):
    bot.add_cog(MonitorCog(bot))
