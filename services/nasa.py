# PiicaBot — services/nasa.py
# Wraps NASA's free open APIs for the !space command.
# Uses the NASA Solar System OpenData API and Wikipedia fallback.
# API key optional (DEMO_KEY works with rate limits).
# Docs: https://api.nasa.gov

import aiohttp
from loguru import logger
from config import NASA_API_KEY

# Curated local facts for well-known celestial objects
# Source: NASA Solar System Exploration (solarsystem.nasa.gov)
SPACE_FACTS: dict[str, str] = {
    "mercury": (
        "Mercury — smallest planet · closest to Sun · "
        "surface temp: -180°C to 430°C · no atmosphere · "
        "1 day = 59 Earth days · NASA MESSENGER orbited 2011-2015 · "
        "[Source: NASA Solar System Exploration]"
    ),
    "venus": (
        "Venus — hottest planet (465°C average) · "
        "thick CO2 atmosphere · rotates backwards · "
        "1 day longer than 1 year · brightest object after Sun/Moon · "
        "[Source: NASA Solar System Exploration]"
    ),
    "earth": (
        "Earth — only known planet with life · "
        "71% surface covered by water · "
        "1 moon · magnetic field protects from solar radiation · "
        "age: ~4.5 billion years · "
        "[Source: NASA Solar System Exploration]"
    ),
    "mars": (
        "Mars — red from iron oxide · "
        "Olympus Mons: tallest volcano in solar system (21.9 km) · "
        "2 moons: Phobos and Deimos · "
        "day: 24h 37m · thin CO2 atmosphere · "
        "Perseverance rover active since 2021 · "
        "[Source: NASA Solar System Exploration]"
    ),
    "jupiter": (
        "Jupiter — largest planet · "
        "Great Red Spot: storm larger than Earth, ongoing 400+ years · "
        "95 known moons including Europa (subsurface ocean) · "
        "1 day = 10 hours · mass = 2.5× all other planets combined · "
        "[Source: NASA Solar System Exploration]"
    ),
    "saturn": (
        "Saturn — ring system spans 282,000 km but only ~10m thick · "
        "least dense planet (floats on water) · "
        "146 known moons · Titan has thick atmosphere and liquid methane lakes · "
        "Cassini mission explored 2004-2017 · "
        "[Source: NASA Solar System Exploration]"
    ),
    "uranus": (
        "Uranus — rotates on its side (98° axial tilt) · "
        "coldest atmosphere: -224°C · "
        "27 known moons named after Shakespeare characters · "
        "2 sets of rings discovered 1977 · ice giant composition · "
        "[Source: NASA Solar System Exploration]"
    ),
    "neptune": (
        "Neptune — winds fastest in solar system (2,100 km/h) · "
        "takes 165 Earth years to orbit Sun · "
        "Triton orbits backwards — likely captured Kuiper Belt object · "
        "Great Dark Spot observed by Voyager 2 in 1989 · "
        "[Source: NASA Solar System Exploration]"
    ),
    "moon": (
        "Moon — Earth's only natural satellite · "
        "formed ~4.5 billion years ago (giant impact theory) · "
        "same side always faces Earth (tidally locked) · "
        "12 humans walked on it 1969-1972 (Apollo program) · "
        "surface temp: -173°C to 127°C · "
        "[Source: NASA Solar System Exploration]"
    ),
    "sun": (
        "Sun — G-type main sequence star · "
        "contains 99.86% of solar system's mass · "
        "surface temp: 5,500°C · core: 15 million°C · "
        "age: ~4.6 billion years · "
        "light takes 8 min 20 sec to reach Earth · "
        "[Source: NASA Solar System Exploration]"
    ),
    "pluto": (
        "Pluto — dwarf planet since 2006 IAU decision · "
        "5 known moons, largest is Charon (half Pluto's size) · "
        "heart-shaped nitrogen ice plain (Tombaugh Regio) · "
        "New Horizons flyby July 2015 — first close images ever · "
        "[Source: NASA New Horizons / Solar System Exploration]"
    ),
    "europa": (
        "Europa — Jupiter's moon · "
        "subsurface ocean beneath 10-30 km ice shell · "
        "twice as much water as all Earth's oceans combined · "
        "top candidate for extraterrestrial life in solar system · "
        "NASA Europa Clipper launched October 2024 · "
        "[Source: NASA Solar System Exploration]"
    ),
    "titan": (
        "Titan — Saturn's largest moon · "
        "only moon with thick atmosphere · "
        "liquid methane lakes and rivers on surface · "
        "Huygens probe landed 2005 — only landing in outer solar system · "
        "NASA Dragonfly rotorcraft mission planned 2034 · "
        "[Source: NASA Solar System Exploration]"
    ),
    "io": (
        "Io — Jupiter's moon · "
        "most volcanically active body in solar system · "
        "400+ active volcanoes · "
        "surface constantly reshaped — no impact craters · "
        "volcanic plumes reach 500 km high · "
        "[Source: NASA Solar System Exploration]"
    ),
    "ganymede": (
        "Ganymede — Jupiter's moon · "
        "largest moon in solar system (bigger than Mercury) · "
        "only moon with its own magnetic field · "
        "subsurface saltwater ocean larger than all Earth's oceans · "
        "ESA JUICE mission en route, arrival 2034 · "
        "[Source: NASA / ESA Solar System Exploration]"
    ),
    "milky way": (
        "Milky Way — our galaxy · "
        "barred spiral galaxy · diameter ~100,000 light-years · "
        "200-400 billion stars · "
        "supermassive black hole Sagittarius A* at center (4M solar masses) · "
        "Solar System ~26,000 light-years from center · "
        "[Source: NASA, ESA Gaia mission]"
    ),
    "black hole": (
        "Black holes — regions where gravity is so strong light cannot escape · "
        "stellar: formed from collapsed massive stars · "
        "supermassive: millions to billions of solar masses at galaxy centers · "
        "first image: M87* captured by Event Horizon Telescope 2019 · "
        "Sagittarius A* imaged 2022 · "
        "[Source: NASA, Event Horizon Telescope Collaboration]"
    ),
    "international space station": (
        "ISS — continuously inhabited since November 2000 · "
        "orbits Earth every 90 minutes at 400 km altitude · "
        "speed: 27,600 km/h · "
        "15 nations involved in construction · "
        "length of a football field (109m) · "
        "planned deorbit: ~2030 · "
        "[Source: NASA ISS Program]"
    ),
    "iss": (
        "ISS — continuously inhabited since November 2000 · "
        "orbits at 400 km altitude every 90 minutes · "
        "speed: 27,600 km/h · 15 partner nations · "
        "109m long — size of a football field · "
        "[Source: NASA ISS Program]"
    ),
    "hubble": (
        "Hubble Space Telescope — launched 1990 · "
        "orbits at 547 km altitude · "
        "over 1.5 million observations since launch · "
        "serviced 5 times by Space Shuttle crews · "
        "helped calculate universe age: ~13.8 billion years · "
        "[Source: NASA Hubble Site]"
    ),
    "james webb": (
        "James Webb Space Telescope — launched December 25, 2021 · "
        "orbits Sun at L2 point (1.5M km from Earth) · "
        "infrared telescope — sees through dust clouds · "
        "first images released July 2022 · "
        "can detect galaxies from 100M years after Big Bang · "
        "[Source: NASA JWST]"
    ),
    "jwst": (
        "James Webb Space Telescope — launched December 25, 2021 · "
        "infrared vision sees through cosmic dust · "
        "first images July 2022: deepest infrared view of universe · "
        "observing exoplanet atmospheres, early galaxies, star formation · "
        "[Source: NASA JWST]"
    ),
}


async def get_space_fact(query: str) -> str:
    """
    Return facts about a celestial object or space topic.
    First checks local curated data, then queries NASA APIs.
    Usage: !space europa | !space mars | !space black hole
    """
    lower = query.strip().lower()

    # Check local curated facts first (fast, verified, offline)
    if lower in SPACE_FACTS:
        return SPACE_FACTS[lower]

    # Try partial match in local data
    for key, fact in SPACE_FACTS.items():
        if lower in key or key in lower:
            return fact

    # Fall back to NASA Solar System API for bodies not in local data
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.le-systeme-solaire.net/rest/bodies/"
            params = {"filter[]": f"englishName,eq,{query.strip().title()}"}
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    bodies = data.get("bodies", [])
                    if bodies:
                        body = bodies[0]
                        name     = body.get("englishName", query)
                        body_type = body.get("bodyType", "Unknown")
                        mass_val  = body.get("mass", {})
                        mass_str  = ""
                        if mass_val and mass_val.get("massValue"):
                            mass_str = f" · Mass: {mass_val['massValue']}×10^{mass_val['massExponent']} kg"
                        moons    = body.get("moons", []) or []
                        moon_str = f" · {len(moons)} known moon(s)" if moons else ""
                        return (
                            f"{name} — {body_type}{mass_str}{moon_str} "
                            f"[Source: Le Système Solaire API / NASA data]"
                        )

    except aiohttp.ClientError as e:
        logger.error(f"NASA/solar system API request failed: {e}")

    return (
        f"No data found for '{query}'. "
        f"Try: planet names, moon names (europa, titan), "
        f"or space objects (hubble, jwst, iss, milky way)"
    )
