# PiicaBot — config.py
# Loads all environment variables in one place.
# Every other file imports from here — never from dotenv directly.

import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def _require(key: str) -> str:
    """Load a required env variable. Crash early with a clear message if missing."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {key}\n"
            f"Check your .env file against .env.example"
        )
    return value


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# ── Twitch ────────────────────────────────────────────────────
TWITCH_CLIENT_ID     = _require("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = _require("TWITCH_CLIENT_SECRET")
TWITCH_ACCESS_TOKEN  = _require("TWITCH_ACCESS_TOKEN")
TWITCH_CHANNEL       = _require("TWITCH_CHANNEL")
BOT_NICK             = _require("BOT_NICK")

# ── Discord ───────────────────────────────────────────────────
DISCORD_TOKEN              = _require("DISCORD_TOKEN")
DISCORD_GUILD_ID           = int(_require("DISCORD_GUILD_ID"))
DISCORD_LIVE_CHANNEL_ID    = int(_optional("DISCORD_LIVE_CHANNEL_ID", "0"))
DISCORD_MIRROR_CHANNEL_ID  = int(_optional("DISCORD_MIRROR_CHANNEL_ID", "0"))
DISCORD_LOG_CHANNEL_ID     = int(_optional("DISCORD_LOG_CHANNEL_ID", "0"))

# ── External APIs ─────────────────────────────────────────────
OPENWEATHER_API_KEY = _require("OPENWEATHER_API_KEY")
MW_DICT_API_KEY     = _require("MW_DICT_API_KEY")
NASA_API_KEY        = _optional("NASA_API_KEY", "DEMO_KEY")

# ── Bot behaviour ─────────────────────────────────────────────
DEFAULT_COOLDOWN     = int(_optional("DEFAULT_COOLDOWN", "30"))
POINTS_PER_MINUTE    = int(_optional("POINTS_PER_MINUTE", "1"))
POINTS_PER_MESSAGE   = int(_optional("POINTS_PER_MESSAGE", "2"))
POINTS_ON_SUB        = int(_optional("POINTS_ON_SUB", "500"))
POINTS_ON_RAID       = int(_optional("POINTS_ON_RAID", "200"))

# ── Database ──────────────────────────────────────────────────
DB_PATH = _optional("DB_PATH", "database/piicabot.db")

# ── Logging ───────────────────────────────────────────────────
LOG_LEVEL = _optional("LOG_LEVEL", "INFO")

logger.remove()
logger.add(
    "logs/piicabot.log",
    level=LOG_LEVEL,
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    sink=lambda msg: print(msg, end=""),
    level=LOG_LEVEL,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
)

logger.info("Config loaded successfully")
