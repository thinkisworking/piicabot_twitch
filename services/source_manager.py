# English: Utility module for managing and formatting academic sources and references.
# Italiano: Modulo di utilità per la gestione e la formattazione delle fonti accademiche e dei riferimenti.

import re
from loguru import logger

def format_citation(text: str, source_name: str, language: str = "en") -> str:
    """
    English: Appends a properly formatted citation to the text.
    Italiano: Aggiunge una citazione formattata correttamente al testo.
    """
    if language == "it":
        return f"{text.strip()} [Fonte: {source_name}]"
    return f"{text.strip()}"

def extract_source(text: str) -> tuple[str, str | None]:
    """
    English: Extracts the source from a string if it exists (e.g., extracting from "").
    Italiano: Estrae la fonte da una stringa se esiste (ad es., estraendo da "[Source: X]").
    """
    match = re.search(r"\", text, re.IGNORECASE)
    if match:
        clean_text = re.sub(r"\", "", text, flags=re.IGNORECASE).strip()
        return clean_text, match.group(1)
    return text, None
