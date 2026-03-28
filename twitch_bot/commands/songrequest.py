# PiicaBot — twitch_bot/commands/songrequest.py
# Song request queue system.
# !songrequest (!sr), !currentsong, !queue, !skipsong (mod), !removesong (mod), !clearqueue (mod)
# Uses YouTube Data API to validate URLs and fetch titles.
# Falls back to URL-only mode if API key not configured.

import re
import aiohttp
from twitchio.ext import commands
from loguru import logger

import database.db as db
from config import DEFAULT_COOLDOWN

YOUTUBE_URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"


async def _get_video_info(url: str) -> tuple[str, int] | None:
    """
    Extract video ID from URL and fetch title + duration from YouTube.
    Returns (title, duration_seconds) or None if invalid/unavailable.
    Falls back to (url, 0) if no API key.
    """
    match = YOUTUBE_URL_PATTERN.search(url)
    if not match:
        return None

    video_id = match.group(4)

    # Try to get title from YouTube oEmbed (no API key needed)
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(oembed_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    title = data.get("title", f"YouTube video ({video_id})")
                    return title, 0
    except Exception as e:
        logger.debug(f"oEmbed fetch failed: {e}")

    return f"YouTube video ({video_id})", 0


class SongRequestCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def _respond(self, ctx: commands.Context, message: str) -> None:
        if len(message) > 490:
            message = message[:487] + "..."
        await ctx.send(message)

    def _is_mod_or_streamer(self, ctx: commands.Context) -> bool:
        return ctx.author.is_mod or ctx.author.name.lower() == ctx.channel.name.lower()

    async def _check_cooldown(
        self, ctx: commands.Context, command: str, cooldown: int = DEFAULT_COOLDOWN
    ) -> bool:
        if self._is_mod_or_streamer(ctx):
            await db.update_cooldown(ctx.author.name, command)
            return True
        on_cd, _ = await db.check_cooldown(ctx.author.name, command, cooldown)
        if on_cd:
            return False
        await db.update_cooldown(ctx.author.name, command)
        await db.increment_command_stat(command)
        return True

    # ── !songrequest ─────────────────────────────────────────

    @commands.command(
        name="songrequest",
        aliases=["sr", "requestsong", "addsong"]
    )
    async def songrequest(self, ctx: commands.Context, *, url: str = "") -> None:
        """
        Add a YouTube song to the request queue.
        Usage: !sr https://youtu.be/dQw4w9WgXcQ
        """
        if not url:
            await self._respond(ctx, "Usage: !sr [YouTube URL] — e.g. !sr https://youtu.be/...")
            return

        if not await self._check_cooldown(ctx, "songrequest", 30):
            return

        # Validate YouTube URL
        if not YOUTUBE_URL_PATTERN.search(url):
            await self._respond(ctx, "Please provide a valid YouTube URL. Usage: !sr https://youtu.be/...")
            return

        # Fetch video info
        info = await _get_video_info(url)
        if info is None:
            await self._respond(ctx, "Could not find that YouTube video. Please check the URL.")
            return

        title, duration = info

        # Check if this URL is already in queue
        conn = db.get()
        async with conn.execute(
            "SELECT id FROM song_queue WHERE url = ? AND status = 'queued'",
            (url,)
        ) as cur:
            existing = await cur.fetchone()

        if existing:
            await self._respond(ctx, f"'{title}' is already in the queue!")
            return

        position = await db.add_to_queue(ctx.author.name, title, url, duration)
        await self._respond(
            ctx,
            f"Added to queue at position #{position}: {title} "
            f"(requested by {ctx.author.name})"
        )

    # ── !currentsong ─────────────────────────────────────────

    @commands.command(
        name="currentsong",
        aliases=["nowplaying", "song"]
    )
    async def currentsong(self, ctx: commands.Context) -> None:
        """Show the currently playing song. Usage: !currentsong"""
        if not await self._check_cooldown(ctx, "currentsong", 10):
            return

        song = await db.get_current_song()
        if not song:
            await self._respond(ctx, "No song currently playing. Request one with !sr [YouTube URL]")
            return

        await self._respond(
            ctx,
            f"Now playing: {song['title']} "
            f"(requested by {song['requested_by']}) — {song['url']}"
        )

    # ── !queue ───────────────────────────────────────────────

    @commands.command(
        name="queue",
        aliases=["songqueue", "nextsongs", "upnext"]
    )
    async def queue(self, ctx: commands.Context) -> None:
        """Show the next 5 songs in the queue. Usage: !queue"""
        if not await self._check_cooldown(ctx, "queue", 15):
            return

        songs = await db.get_queue(5)
        if not songs:
            await self._respond(ctx, "Song queue is empty. Add one with !sr [YouTube URL]")
            return

        parts = [f"#{s['position']} {s['title']} ({s['requested_by']})" for s in songs]
        await self._respond(ctx, "Queue: " + " | ".join(parts))

    # ── !skipsong (mod) ──────────────────────────────────────

    @commands.command(
        name="skipsong",
        aliases=["skip", "nextsong"]
    )
    async def skipsong(self, ctx: commands.Context) -> None:
        """Skip the current song. Mod only. Usage: !skipsong"""
        if not self._is_mod_or_streamer(ctx):
            return

        conn = db.get()

        # Mark current as skipped
        await conn.execute(
            "UPDATE song_queue SET status = 'skipped' WHERE status = 'playing'"
        )

        # Get next queued song
        async with conn.execute(
            "SELECT * FROM song_queue WHERE status = 'queued' ORDER BY position LIMIT 1"
        ) as cur:
            next_song = await cur.fetchone()

        if next_song:
            await conn.execute(
                "UPDATE song_queue SET status = 'playing', played_at = datetime('now') WHERE id = ?",
                (next_song["id"],)
            )
            await conn.commit()
            await self._respond(
                ctx,
                f"Skipped. Now playing: {next_song['title']} (requested by {next_song['requested_by']})"
            )
        else:
            await conn.commit()
            await self._respond(ctx, "Song skipped. Queue is now empty.")

    # ── !removesong (mod) ────────────────────────────────────

    @commands.command(
        name="removesong",
        aliases=["removefromqueue", "delsong"]
    )
    async def removesong(self, ctx: commands.Context, *, position: str = "") -> None:
        """Remove a song from queue by position number. Mod only. Usage: !removesong 3"""
        if not self._is_mod_or_streamer(ctx):
            return

        if not position:
            await self._respond(ctx, "Usage: !removesong [position] — e.g. !removesong 3")
            return

        try:
            pos = int(position.strip())
        except ValueError:
            await self._respond(ctx, f"'{position}' is not a valid position number.")
            return

        conn = db.get()
        async with conn.execute(
            "SELECT * FROM song_queue WHERE position = ? AND status = 'queued'",
            (pos,)
        ) as cur:
            song = await cur.fetchone()

        if not song:
            await self._respond(ctx, f"No queued song at position #{pos}.")
            return

        await conn.execute(
            "UPDATE song_queue SET status = 'removed' WHERE id = ?",
            (song["id"],)
        )
        await conn.commit()
        await self._respond(ctx, f"Removed from queue: {song['title']}")

    # ── !clearqueue (mod) ────────────────────────────────────

    @commands.command(
        name="clearqueue",
        aliases=["emptyqueue", "clearsr"]
    )
    async def clearqueue(self, ctx: commands.Context) -> None:
        """Clear the entire song queue. Mod only. Usage: !clearqueue"""
        if not self._is_mod_or_streamer(ctx):
            return

        conn = db.get()
        async with conn.execute(
            "SELECT COUNT(*) as count FROM song_queue WHERE status = 'queued'"
        ) as cur:
            row = await cur.fetchone()
        count = row["count"] if row else 0

        await conn.execute(
            "UPDATE song_queue SET status = 'removed' WHERE status = 'queued'"
        )
        await conn.commit()
        await self._respond(ctx, f"Queue cleared. {count} song(s) removed.")


def prepare(bot):
    bot.add_cog(SongRequestCog(bot))
