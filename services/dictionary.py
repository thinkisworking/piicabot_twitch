# PiicaBot — services/dictionary.py
# Wraps the Merriam-Webster Collegiate Dictionary API.
# Used by !define (definition) and !wordorigin (etymology).
# Free API key from: https://dictionaryapi.com
# Docs: https://dictionaryapi.com/products/json

import aiohttp
from loguru import logger
from config import MW_DICT_API_KEY

DICT_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"


def _clean(text: str) -> str:
    """
    Strip Merriam-Webster's proprietary markup tokens from response text.
    MW uses tokens like {bc}, {it}, {/it}, {dx}, {sx|word||} etc.
    """
    import re
    # Remove all {token} and {token|...} style markup
    text = re.sub(r'\{[^}]+\}', '', text)
    # Remove leftover pipes from token arguments
    text = re.sub(r'\|+', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def _truncate(text: str, max_len: int = 300) -> str:
    """Truncate text to fit in a Twitch chat message."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rsplit(' ', 1)[0] + '...'


async def _fetch(word: str) -> list | None:
    """Raw API fetch. Returns parsed JSON or None on error."""
    params = {"key": MW_DICT_API_KEY}
    url = f"{DICT_URL}/{word.lower().strip()}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 401:
                    logger.error("Merriam-Webster: invalid API key")
                    return None
                if resp.status != 200:
                    logger.error(f"Merriam-Webster: HTTP {resp.status}")
                    return None
                return await resp.json()

    except aiohttp.ClientError as e:
        logger.error(f"Dictionary request failed: {e}")
        return None


async def get_definition(word: str) -> str:
    """
    Return the definition of a word from Merriam-Webster.
    Includes part of speech and source citation.
    Usage: !define ephemeral
    """
    data = await _fetch(word)

    if data is None:
        return "Dictionary service is temporarily unavailable."

    # If the response is a list of strings, MW is suggesting corrections
    if not data or isinstance(data[0], str):
        suggestions = ", ".join(data[:4]) if data else "none"
        return (
            f"'{word}' not found in Merriam-Webster. "
            f"Did you mean: {suggestions}?"
        )

    entry = data[0]

    # Part of speech
    pos = entry.get("fl", "")

    # Get first definition from shortdef (clean summary) or dt (full)
    shortdefs = entry.get("shortdef", [])
    if shortdefs:
        definition = shortdefs[0]
    else:
        # Fall back to full definition text
        defs = entry.get("def", [])
        if not defs:
            return f"No definition found for '{word}'."
        sseqs = defs[0].get("sseq", [])
        if not sseqs:
            return f"No definition found for '{word}'."
        dt = sseqs[0][0][1].get("dt", [])
        text_parts = [t[1] for t in dt if t[0] == "text"]
        definition = _clean(text_parts[0]) if text_parts else "No definition text found."

    pos_display = f" ({pos})" if pos else ""
    definition  = _truncate(_clean(definition))

    return (
        f"'{word}'{pos_display}: {definition} "
        f"[Merriam-Webster Collegiate Dictionary]"
    )


async def get_etymology(word: str) -> str:
    """
    Return the etymology (word origin) of a word from Merriam-Webster.
    Usage: !wordorigin chaos
    """
    data = await _fetch(word)

    if data is None:
        return "Dictionary service is temporarily unavailable."

    if not data or isinstance(data[0], str):
        suggestions = ", ".join(data[:4]) if data else "none"
        return (
            f"'{word}' not found in Merriam-Webster. "
            f"Did you mean: {suggestions}?"
        )

    entry = data[0]
    et    = entry.get("et", [])

    if not et:
        return (
            f"No etymology found for '{word}' in Merriam-Webster. "
            f"Try a more specific or different spelling."
        )

    # Extract text parts from etymology structure
    et_text_parts = []
    for part in et:
        if part[0] == "text":
            et_text_parts.append(_clean(part[1]))
        elif part[0] == "et_snote" and part[1]:
            # Supplementary etymology note
            snote_parts = [_clean(p[1]) for p in part[1] if p[0] == "t"]
            et_text_parts.extend(snote_parts)

    if not et_text_parts:
        return f"No etymology text found for '{word}'."

    etymology = _truncate(" ".join(et_text_parts))
    date      = entry.get("date", "")
    date_note = f" | First known use: {_clean(date)}" if date else ""

    return (
        f"Origin of '{word}': {etymology}{date_note} "
        f"[Merriam-Webster Collegiate Dictionary]"
    )
