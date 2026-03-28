# PiicaBot — services/clock.py
# World clock service for the !time command.
# Supports city names and country names (resolves to capital).
# Uses pytz for timezone lookups — completely offline, no API needed.

from datetime import datetime
import pytz
from loguru import logger

# City / country → IANA timezone string
# Covers capitals and major cities viewers are likely to ask about
CITY_TIMEZONES: dict[str, str] = {
    # Capitals and major cities
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "rome": "Europe/Rome",
    "madrid": "Europe/Madrid",
    "amsterdam": "Europe/Amsterdam",
    "brussels": "Europe/Brussels",
    "vienna": "Europe/Vienna",
    "bern": "Europe/Zurich",
    "zurich": "Europe/Zurich",
    "stockholm": "Europe/Stockholm",
    "oslo": "Europe/Oslo",
    "copenhagen": "Europe/Copenhagen",
    "helsinki": "Europe/Helsinki",
    "athens": "Europe/Athens",
    "warsaw": "Europe/Warsaw",
    "prague": "Europe/Prague",
    "budapest": "Europe/Budapest",
    "bucharest": "Europe/Bucharest",
    "sofia": "Europe/Sofia",
    "zagreb": "Europe/Zagreb",
    "belgrade": "Europe/Belgrade",
    "sarajevo": "Europe/Sarajevo",
    "podgorica": "Europe/Podgorica",
    "skopje": "Europe/Skopje",
    "tirana": "Europe/Tirane",
    "valletta": "Europe/Malta",
    "nicosia": "Asia/Nicosia",
    "vilnius": "Europe/Vilnius",
    "riga": "Europe/Riga",
    "tallinn": "Europe/Tallinn",
    "reykjavik": "Atlantic/Reykjavik",
    "dublin": "Europe/Dublin",
    "lisbon": "Europe/Lisbon",
    "kyiv": "Europe/Kyiv",
    "minsk": "Europe/Minsk",
    "chisinau": "Europe/Chisinau",
    "moscow": "Europe/Moscow",
    "istanbul": "Europe/Istanbul",
    "ankara": "Europe/Istanbul",
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "pretoria": "Africa/Johannesburg",
    "nairobi": "Africa/Nairobi",
    "lagos": "Africa/Lagos",
    "abuja": "Africa/Lagos",
    "accra": "Africa/Accra",
    "dakar": "Africa/Dakar",
    "addis ababa": "Africa/Addis_Ababa",
    "khartoum": "Africa/Khartoum",
    "tripoli": "Africa/Tripoli",
    "tunis": "Africa/Tunis",
    "algiers": "Africa/Algiers",
    "rabat": "Africa/Casablanca",
    "casablanca": "Africa/Casablanca",
    "baghdad": "Asia/Baghdad",
    "tehran": "Asia/Tehran",
    "riyadh": "Asia/Riyadh",
    "dubai": "Asia/Dubai",
    "abu dhabi": "Asia/Dubai",
    "doha": "Asia/Qatar",
    "kuwait city": "Asia/Kuwait",
    "manama": "Asia/Bahrain",
    "muscat": "Asia/Muscat",
    "sana'a": "Asia/Aden",
    "amman": "Asia/Amman",
    "beirut": "Asia/Beirut",
    "damascus": "Asia/Damascus",
    "jerusalem": "Asia/Jerusalem",
    "tel aviv": "Asia/Jerusalem",
    "baku": "Asia/Baku",
    "yerevan": "Asia/Yerevan",
    "tbilisi": "Asia/Tbilisi",
    "tashkent": "Asia/Tashkent",
    "astana": "Asia/Almaty",
    "almaty": "Asia/Almaty",
    "bishkek": "Asia/Bishkek",
    "dushanbe": "Asia/Dushanbe",
    "ashgabat": "Asia/Ashgabat",
    "kabul": "Asia/Kabul",
    "islamabad": "Asia/Karachi",
    "karachi": "Asia/Karachi",
    "new delhi": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "dhaka": "Asia/Dhaka",
    "kathmandu": "Asia/Kathmandu",
    "thimphu": "Asia/Thimphu",
    "colombo": "Asia/Colombo",
    "malé": "Indian/Maldives",
    "yangon": "Asia/Rangoon",
    "naypyidaw": "Asia/Rangoon",
    "bangkok": "Asia/Bangkok",
    "vientiane": "Asia/Vientiane",
    "phnom penh": "Asia/Phnom_Penh",
    "hanoi": "Asia/Ho_Chi_Minh",
    "ho chi minh city": "Asia/Ho_Chi_Minh",
    "kuala lumpur": "Asia/Kuala_Lumpur",
    "singapore": "Asia/Singapore",
    "jakarta": "Asia/Jakarta",
    "manila": "Asia/Manila",
    "dili": "Asia/Dili",
    "tokyo": "Asia/Tokyo",
    "seoul": "Asia/Seoul",
    "pyongyang": "Asia/Pyongyang",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "hong kong": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei",
    "ulaanbaatar": "Asia/Ulaanbaatar",
    "canberra": "Australia/Sydney",
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "brisbane": "Australia/Brisbane",
    "perth": "Australia/Perth",
    "auckland": "Pacific/Auckland",
    "wellington": "Pacific/Auckland",
    "suva": "Pacific/Fiji",
    "ottawa": "America/Toronto",
    "toronto": "America/Toronto",
    "montreal": "America/Toronto",
    "vancouver": "America/Vancouver",
    "washington d.c.": "America/New_York",
    "washington dc": "America/New_York",
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "mexico city": "America/Mexico_City",
    "havana": "America/Havana",
    "kingston": "America/Jamaica",
    "port-au-prince": "America/Port-au-Prince",
    "santo domingo": "America/Santo_Domingo",
    "san josé": "America/Costa_Rica",
    "panama city": "America/Panama",
    "bogotá": "America/Bogota",
    "bogota": "America/Bogota",
    "quito": "America/Guayaquil",
    "lima": "America/Lima",
    "caracas": "America/Caracas",
    "georgetown": "America/Guyana",
    "paramaribo": "America/Paramaribo",
    "brasília": "America/Sao_Paulo",
    "brasilia": "America/Sao_Paulo",
    "são paulo": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "montevideo": "America/Montevideo",
    "asunción": "America/Asuncion",
    "santiago": "America/Santiago",
    "la paz": "America/La_Paz",
    "sucre": "America/La_Paz",
}

# Country name → city key (for country lookups)
COUNTRY_TO_CITY: dict[str, str] = {
    "uk": "london", "united kingdom": "london",
    "england": "london", "scotland": "london",
    "france": "paris", "germany": "berlin",
    "italy": "rome", "spain": "madrid",
    "netherlands": "amsterdam", "belgium": "brussels",
    "austria": "vienna", "switzerland": "bern",
    "sweden": "stockholm", "norway": "oslo",
    "denmark": "copenhagen", "finland": "helsinki",
    "greece": "athens", "poland": "warsaw",
    "czechia": "prague", "czech republic": "prague",
    "hungary": "budapest", "romania": "bucharest",
    "bulgaria": "sofia", "croatia": "zagreb",
    "serbia": "belgrade", "albania": "tirana",
    "malta": "valletta", "lithuania": "vilnius",
    "latvia": "riga", "estonia": "tallinn",
    "iceland": "reykjavik", "ireland": "dublin",
    "portugal": "lisbon", "ukraine": "kyiv",
    "belarus": "minsk", "moldova": "chisinau",
    "russia": "moscow", "turkey": "ankara",
    "egypt": "cairo", "south africa": "johannesburg",
    "kenya": "nairobi", "nigeria": "abuja",
    "ghana": "accra", "senegal": "dakar",
    "ethiopia": "addis ababa", "sudan": "khartoum",
    "libya": "tripoli", "tunisia": "tunis",
    "algeria": "algiers", "morocco": "rabat",
    "iraq": "baghdad", "iran": "tehran",
    "saudi arabia": "riyadh", "uae": "dubai",
    "united arab emirates": "dubai", "qatar": "doha",
    "kuwait": "kuwait city", "bahrain": "manama",
    "oman": "muscat", "yemen": "sana'a",
    "jordan": "amman", "lebanon": "beirut",
    "syria": "damascus", "israel": "jerusalem",
    "azerbaijan": "baku", "armenia": "yerevan",
    "georgia": "tbilisi", "uzbekistan": "tashkent",
    "kazakhstan": "astana", "kyrgyzstan": "bishkek",
    "tajikistan": "dushanbe", "turkmenistan": "ashgabat",
    "afghanistan": "kabul", "pakistan": "islamabad",
    "india": "new delhi", "bangladesh": "dhaka",
    "nepal": "kathmandu", "bhutan": "thimphu",
    "sri lanka": "colombo", "maldives": "malé",
    "myanmar": "naypyidaw", "thailand": "bangkok",
    "laos": "vientiane", "cambodia": "phnom penh",
    "vietnam": "hanoi", "malaysia": "kuala lumpur",
    "singapore": "singapore", "indonesia": "jakarta",
    "philippines": "manila", "japan": "tokyo",
    "south korea": "seoul", "north korea": "pyongyang",
    "china": "beijing", "taiwan": "taipei",
    "mongolia": "ulaanbaatar", "australia": "canberra",
    "new zealand": "wellington", "fiji": "suva",
    "canada": "ottawa", "usa": "washington dc",
    "united states": "washington dc", "mexico": "mexico city",
    "cuba": "havana", "jamaica": "kingston",
    "colombia": "bogota", "ecuador": "quito",
    "peru": "lima", "venezuela": "caracas",
    "brazil": "brasilia", "argentina": "buenos aires",
    "uruguay": "montevideo", "paraguay": "asunción",
    "chile": "santiago", "bolivia": "sucre",
}


def get_time(query: str) -> str:
    """
    Return the current local time for a city or country.
    Completely offline — no API call needed.
    Usage: !time Tokyo | !time Japan | !time New Zealand
    """
    lower = query.strip().lower()

    # Resolve country → city if needed
    city_key = COUNTRY_TO_CITY.get(lower, lower)
    display_query = query.strip().title()

    tz_name = CITY_TIMEZONES.get(city_key)

    if not tz_name:
        # Try partial match
        for key, tz in CITY_TIMEZONES.items():
            if lower in key or key in lower:
                tz_name = tz
                city_key = key
                break

    if not tz_name:
        return (
            f"Could not find timezone for '{query}'. "
            f"Try a capital city name — e.g. !time Tokyo or !time Japan"
        )

    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        time_str  = now.strftime("%H:%M")
        date_str  = now.strftime("%A, %d %B %Y")
        offset    = now.strftime("%z")
        offset_hr = f"UTC{offset[:3]}:{offset[3:]}"

        city_display = city_key.title()
        return (
            f"{city_display} ({display_query}) — "
            f"{time_str} on {date_str} ({offset_hr})"
        )

    except pytz.exceptions.UnknownTimeZoneError:
        logger.error(f"Unknown timezone: {tz_name}")
        return f"Timezone error for '{query}'. Please report this to the streamer."
