# PiicaBot — services/igdb.py
# Wraps the IGDB API (owned by Twitch) for all gaming knowledge commands.
# Uses your existing Twitch Client ID + Secret — no extra signup needed.
# Docs: https://api-docs.igdb.com
#
# Commands served: !review, !platforms, !franchise, !console,
#                  !studio, !publisher, !gameengine, !gametoanime

import aiohttp
import time
from loguru import logger
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_URL  = "https://api.igdb.com/v4"

# Simple in-memory token cache — tokens last ~60 days
_token_cache: dict = {"access_token": None, "expires_at": 0}


async def _get_token() -> str | None:
    """
    Get a valid IGDB access token.
    Caches the token and only refreshes when expired.
    """
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    params = {
        "client_id":     TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type":    "client_credentials",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    logger.error(f"IGDB token fetch failed: HTTP {resp.status}")
                    return None
                data = await resp.json()
                _token_cache["access_token"] = data["access_token"]
                _token_cache["expires_at"]   = now + data["expires_in"]
                logger.debug("IGDB access token refreshed")
                return _token_cache["access_token"]

    except aiohttp.ClientError as e:
        logger.error(f"IGDB token request failed: {e}")
        return None


async def _query(endpoint: str, body: str) -> list | None:
    """Send a raw IGDB API query. Returns parsed JSON list or None."""
    token = await _get_token()
    if not token:
        return None

    headers = {
        "Client-ID":     TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Content-Type":  "text/plain",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{IGDB_URL}/{endpoint}",
                headers=headers,
                data=body,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    logger.error(f"IGDB query failed: HTTP {resp.status} — {body}")
                    return None
                return await resp.json()

    except aiohttp.ClientError as e:
        logger.error(f"IGDB request failed: {e}")
        return None


def _truncate(text: str, max_len: int = 280) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rsplit(' ', 1)[0] + '...'


def _rating_label(score: float) -> str:
    """Convert IGDB 0-100 score to a human-readable label."""
    if score >= 90: return "Masterpiece"
    if score >= 80: return "Great"
    if score >= 70: return "Good"
    if score >= 60: return "Decent"
    if score >= 50: return "Mixed"
    return "Poor"


async def get_game_review(game_name: str) -> str:
    """
    Fetch critic rating and summary for a game from IGDB.
    Usage: !review Elden Ring
    """
    body = (
        f'search "{game_name}"; '
        f'fields name, rating, rating_count, summary, url; '
        f'where rating != null & version_parent = null; '
        f'limit 1;'
    )
    data = await _query("games", body)

    if not data:
        return f"Could not find '{game_name}' on IGDB. Try the full game title."

    game   = data[0]
    name   = game.get("name", game_name)
    rating = round(game.get("rating", 0), 1)
    count  = game.get("rating_count", 0)
    label  = _rating_label(rating)
    summary = _truncate(game.get("summary", "No summary available."), 200)

    return (
        f"{name} — IGDB: {rating}/100 ({label}, {count} ratings) | "
        f"{summary} [igdb.com]"
    )


async def get_platforms(game_name: str) -> str:
    """
    Return which platforms a game is available on.
    Usage: !platforms Hades
    """
    body = (
        f'search "{game_name}"; '
        f'fields name, platforms.name; '
        f'where version_parent = null; '
        f'limit 1;'
    )
    data = await _query("games", body)

    if not data:
        return f"Could not find '{game_name}' on IGDB."

    game      = data[0]
    name      = game.get("name", game_name)
    platforms = game.get("platforms", [])

    if not platforms:
        return f"No platform data found for '{name}' on IGDB."

    platform_names = ", ".join(sorted(p["name"] for p in platforms))
    return f"{name} is available on: {platform_names} [igdb.com]"


async def get_franchise_timeline(franchise_name: str) -> str:
    """
    Return the mainline games in a franchise in chronological order.
    Usage: !franchise zelda
    """
    body = (
        f'search "{franchise_name}"; '
        f'fields name, games.name, games.first_release_date; '
        f'limit 1;'
    )
    data = await _query("franchises", body)

    if not data:
        # Try searching by game name instead
        body2 = (
            f'search "{franchise_name}"; '
            f'fields name, franchise.name, first_release_date; '
            f'where version_parent = null; '
            f'limit 10;'
        )
        data = await _query("games", body2)
        if not data:
            return f"Could not find franchise '{franchise_name}' on IGDB."

        games = sorted(data, key=lambda g: g.get("first_release_date", 0))
        entries = []
        for g in games[:8]:
            year = ""
            if g.get("first_release_date"):
                import datetime
                year = str(datetime.datetime.utcfromtimestamp(g["first_release_date"]).year)
            entries.append(f"{g['name']} ({year})" if year else g["name"])

        return f"{franchise_name.title()} franchise: " + " → ".join(entries) + " [igdb.com]"

    franchise = data[0]
    fname     = franchise.get("name", franchise_name)
    games     = franchise.get("games", [])

    if not games:
        return f"No games found for franchise '{fname}' on IGDB."

    games_sorted = sorted(games, key=lambda g: g.get("first_release_date", 0))
    entries = []
    for g in games_sorted[:8]:
        year = ""
        if g.get("first_release_date"):
            import datetime
            year = str(datetime.datetime.utcfromtimestamp(g["first_release_date"]).year)
        entries.append(f"{g['name']} ({year})" if year else g["name"])

    return f"{fname} franchise: " + " → ".join(entries) + " [igdb.com]"


async def get_studio_info(studio_name: str) -> str:
    """
    Return info about a game studio.
    Usage: !studio fromsoft
    """
    body = (
        f'search "{studio_name}"; '
        f'fields name, description, country, start_date, developed.name; '
        f'limit 1;'
    )
    data = await _query("companies", body)

    if not data:
        return f"Could not find studio '{studio_name}' on IGDB."

    studio      = data[0]
    name        = studio.get("name", studio_name)
    description = _truncate(studio.get("description", ""), 200)
    developed   = studio.get("developed", [])

    notable = ", ".join(g["name"] for g in developed[-5:]) if developed else "Unknown"

    return (
        f"{name} | "
        f"{description + ' | ' if description else ''}"
        f"Notable games: {notable} [igdb.com]"
    )


async def get_game_engine_info(engine_name: str) -> str:
    """
    Return info about a game engine.
    Usage: !gameengine unreal5
    """
    body = (
        f'search "{engine_name}"; '
        f'fields name, description, companies.name, platforms.name; '
        f'limit 1;'
    )
    data = await _query("game_engines", body)

    if not data:
        return f"Could not find engine '{engine_name}' on IGDB."

    engine      = data[0]
    name        = engine.get("name", engine_name)
    description = _truncate(engine.get("description", ""), 200)
    companies   = engine.get("companies", [])
    platforms   = engine.get("platforms", [])

    company_str  = ", ".join(c["name"] for c in companies) if companies else "Unknown"
    platform_str = ", ".join(p["name"] for p in platforms[:5]) if platforms else "Multiple platforms"

    return (
        f"{name} | Developer: {company_str} | "
        f"Platforms: {platform_str}"
        f"{' | ' + description if description else ''} [igdb.com]"
    )
