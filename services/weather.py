# PiicaBot — services/weather.py
# Wraps the OpenWeatherMap API for !weather command.
# Supports city names and country names (auto-resolves to capital).
# All functions return clean strings ready to post in Twitch chat.

import aiohttp
from loguru import logger
from config import OPENWEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
GEO_URL  = "https://api.openweathermap.org/geo/1.0/direct"

# Country name → capital city mapping
# Used when viewer types a country name instead of a city
COUNTRY_CAPITALS: dict[str, str] = {
    "afghanistan": "Kabul", "albania": "Tirana", "algeria": "Algiers",
    "andorra": "Andorra la Vella", "angola": "Luanda", "argentina": "Buenos Aires",
    "armenia": "Yerevan", "australia": "Canberra", "austria": "Vienna",
    "azerbaijan": "Baku", "bahrain": "Manama", "bangladesh": "Dhaka",
    "belarus": "Minsk", "belgium": "Brussels", "belize": "Belmopan",
    "benin": "Porto-Novo", "bhutan": "Thimphu", "bolivia": "Sucre",
    "bosnia": "Sarajevo", "botswana": "Gaborone", "brazil": "Brasília",
    "brunei": "Bandar Seri Begawan", "bulgaria": "Sofia",
    "burkina faso": "Ouagadougou", "burundi": "Gitega",
    "cambodia": "Phnom Penh", "cameroon": "Yaoundé", "canada": "Ottawa",
    "chad": "N'Djamena", "chile": "Santiago", "china": "Beijing",
    "colombia": "Bogotá", "congo": "Brazzaville", "costa rica": "San José",
    "croatia": "Zagreb", "cuba": "Havana", "cyprus": "Nicosia",
    "czech republic": "Prague", "czechia": "Prague", "denmark": "Copenhagen",
    "djibouti": "Djibouti", "ecuador": "Quito", "egypt": "Cairo",
    "el salvador": "San Salvador", "eritrea": "Asmara", "estonia": "Tallinn",
    "ethiopia": "Addis Ababa", "fiji": "Suva", "finland": "Helsinki",
    "france": "Paris", "gabon": "Libreville", "gambia": "Banjul",
    "georgia": "Tbilisi", "germany": "Berlin", "ghana": "Accra",
    "greece": "Athens", "guatemala": "Guatemala City", "guinea": "Conakry",
    "guyana": "Georgetown", "haiti": "Port-au-Prince", "honduras": "Tegucigalpa",
    "hungary": "Budapest", "iceland": "Reykjavik", "india": "New Delhi",
    "indonesia": "Jakarta", "iran": "Tehran", "iraq": "Baghdad",
    "ireland": "Dublin", "israel": "Jerusalem", "italy": "Rome",
    "jamaica": "Kingston", "japan": "Tokyo", "jordan": "Amman",
    "kazakhstan": "Astana", "kenya": "Nairobi", "kuwait": "Kuwait City",
    "kyrgyzstan": "Bishkek", "laos": "Vientiane", "latvia": "Riga",
    "lebanon": "Beirut", "lesotho": "Maseru", "liberia": "Monrovia",
    "libya": "Tripoli", "liechtenstein": "Vaduz", "lithuania": "Vilnius",
    "luxembourg": "Luxembourg City", "madagascar": "Antananarivo",
    "malawi": "Lilongwe", "malaysia": "Kuala Lumpur", "maldives": "Malé",
    "mali": "Bamako", "malta": "Valletta", "mauritania": "Nouakchott",
    "mauritius": "Port Louis", "mexico": "Mexico City", "moldova": "Chișinău",
    "monaco": "Monaco", "mongolia": "Ulaanbaatar", "montenegro": "Podgorica",
    "morocco": "Rabat", "mozambique": "Maputo", "myanmar": "Naypyidaw",
    "namibia": "Windhoek", "nepal": "Kathmandu", "netherlands": "Amsterdam",
    "new zealand": "Wellington", "nicaragua": "Managua", "niger": "Niamey",
    "nigeria": "Abuja", "north korea": "Pyongyang",
    "north macedonia": "Skopje", "norway": "Oslo", "oman": "Muscat",
    "pakistan": "Islamabad", "panama": "Panama City",
    "papua new guinea": "Port Moresby", "paraguay": "Asunción",
    "peru": "Lima", "philippines": "Manila", "poland": "Warsaw",
    "portugal": "Lisbon", "qatar": "Doha", "romania": "Bucharest",
    "russia": "Moscow", "rwanda": "Kigali", "saudi arabia": "Riyadh",
    "senegal": "Dakar", "serbia": "Belgrade", "sierra leone": "Freetown",
    "singapore": "Singapore", "slovakia": "Bratislava",
    "slovenia": "Ljubljana", "somalia": "Mogadishu",
    "south africa": "Pretoria", "south korea": "Seoul",
    "south sudan": "Juba", "spain": "Madrid", "sri lanka": "Sri Jayawardenepura Kotte",
    "sudan": "Khartoum", "suriname": "Paramaribo", "sweden": "Stockholm",
    "switzerland": "Bern", "syria": "Damascus", "taiwan": "Taipei",
    "tajikistan": "Dushanbe", "tanzania": "Dodoma", "thailand": "Bangkok",
    "timor-leste": "Dili", "togo": "Lomé", "trinidad and tobago": "Port of Spain",
    "tunisia": "Tunis", "turkey": "Ankara", "turkmenistan": "Ashgabat",
    "uganda": "Kampala", "ukraine": "Kyiv", "united arab emirates": "Abu Dhabi",
    "uae": "Abu Dhabi", "united kingdom": "London", "uk": "London",
    "united states": "Washington D.C.", "usa": "Washington D.C.",
    "uruguay": "Montevideo", "uzbekistan": "Tashkent", "venezuela": "Caracas",
    "vietnam": "Hanoi", "yemen": "Sana'a", "zambia": "Lusaka",
    "zimbabwe": "Harare",
}

# Weather condition code → simple emoji description
CONDITION_MAP: dict[int, str] = {
    200: "thunderstorm with light rain",  201: "thunderstorm with rain",
    202: "thunderstorm with heavy rain",  210: "light thunderstorm",
    211: "thunderstorm",                  212: "heavy thunderstorm",
    221: "ragged thunderstorm",           230: "thunderstorm with drizzle",
    300: "light drizzle",                 301: "drizzle",
    302: "heavy drizzle",                 310: "light drizzle rain",
    311: "drizzle rain",                  312: "heavy drizzle rain",
    321: "shower drizzle",               500: "light rain",
    501: "moderate rain",                 502: "heavy rain",
    503: "very heavy rain",              504: "extreme rain",
    511: "freezing rain",                 520: "light shower rain",
    521: "shower rain",                   522: "heavy shower rain",
    600: "light snow",                    601: "snow",
    602: "heavy snow",                    611: "sleet",
    615: "light rain and snow",           616: "rain and snow",
    620: "light shower snow",             621: "shower snow",
    622: "heavy shower snow",             701: "mist",
    711: "smoke",                         721: "haze",
    731: "dust/sand whirls",             741: "fog",
    751: "sand",                          761: "dust",
    762: "volcanic ash",                  771: "squalls",
    781: "tornado",                       800: "clear sky",
    801: "few clouds",                    802: "scattered clouds",
    803: "broken clouds",                 804: "overcast clouds",
}


def _celsius_to_fahrenheit(c: float) -> float:
    return round(c * 9 / 5 + 32, 1)


def _resolve_city(query: str) -> str:
    """If query is a country name, return its capital. Otherwise return as-is."""
    lower = query.strip().lower()
    return COUNTRY_CAPITALS.get(lower, query.strip())


async def get_weather(query: str) -> str:
    """
    Fetch weather for a city or country name.
    Returns a single chat-ready string.
    Usage: !weather Tokyo | !weather Japan | !weather New Zealand
    """
    city = _resolve_city(query)
    resolved_note = f" (capital of {query.strip().title()})" if city.lower() != query.strip().lower() else ""

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 404:
                    return f"Could not find weather for '{query}'. Try a more specific city name."
                if resp.status == 401:
                    logger.error("OpenWeatherMap: invalid API key")
                    return "Weather service is temporarily unavailable."
                if resp.status != 200:
                    logger.error(f"OpenWeatherMap: HTTP {resp.status}")
                    return "Weather service is temporarily unavailable."

                data = await resp.json()

        temp_c    = round(data["main"]["temp"], 1)
        feels_c   = round(data["main"]["feels_like"], 1)
        humidity  = data["main"]["humidity"]
        wind_ms   = round(data["wind"]["speed"], 1)
        wind_kmh  = round(wind_ms * 3.6, 1)
        cond_code = data["weather"][0]["id"]
        condition = CONDITION_MAP.get(cond_code, data["weather"][0]["description"])
        city_name = data["name"]
        country   = data["sys"]["country"]

        return (
            f"{city_name}{resolved_note} ({country}): "
            f"{condition} | {temp_c}°C (feels like {feels_c}°C) | "
            f"Humidity: {humidity}% | Wind: {wind_kmh} km/h"
        )

    except aiohttp.ClientError as e:
        logger.error(f"Weather request failed: {e}")
        return "Could not reach the weather service. Try again in a moment."
