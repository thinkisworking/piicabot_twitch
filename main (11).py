# PiicaBot — main.py
# Starts both the Twitch bot and Discord bot concurrently.
# This is the only file you need to run: python main.py
# Both bots share the same SQLite database via asyncio.

import asyncio
import os
from loguru import logger

import database.db as db
from twitch_bot.bot  import PiicaBot
from discord_bot.bot import create_bot


async def main() -> None:
    """
    Initialize database, then start both bots concurrently.
    Both bots run in the same event loop sharing one DB connection.
    """

    # ── 1. Initialize database ───────────────────────────────
    logger.info("Initializing database...")
    await db.init()

    # ── 2. Create bot instances ──────────────────────────────
    twitch_bot  = PiicaBot()
    discord_bot = create_bot()

    # ── 3. Bridge: connect Twitch messages to Discord mirror ─
    # When a Twitch message arrives, forward it to Discord
    original_event_message = twitch_bot.event_message

    async def bridged_event_message(message) -> None:
        await original_event_message(message)
        # Mirror to Discord (non-blocking)
        if message.author and not message.echo:
            try:
                from discord_bot.cogs.mirror import get_mirror_cog
                mirror = get_mirror_cog()
                if mirror:
                    asyncio.create_task(
                        mirror.post_to_discord(
                            message.author.name,
                            message.content
                        )
                    )
            except Exception:
                pass  # Mirror failure should never crash Twitch bot

    twitch_bot.event_message = bridged_event_message

    # ── 4. Start both bots concurrently ─────────────────────
    logger.info("Starting PiicaBot — Twitch + Discord")

    from config import DISCORD_TOKEN

    try:
        await asyncio.gather(
            twitch_bot.start(),
            discord_bot.start(DISCORD_TOKEN),
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        await db.close()
        logger.info("PiicaBot stopped cleanly")


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("database", exist_ok=True)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("PiicaBot stopped by user")
