# PiicaBot — twitch_bot/commands/geoguessr.py
# GeoGuessr meta commands — all powered by local data, zero API cost.
# !plate !driveside !domain !sunposition !writingsystem !phonecode
# !roadsigns !roadlines !powerpoles !barriers !groundcolor
# !landscape !season !streetcam !architecture !identifylang
# !alphabet !currency !monthin !learnword !wordgap !falsefriend !loanword
# !numbers !greeting

from twitchio.ext import commands
from loguru import logger

import database.db as db
from data.geoguessr_data import (
    PLATES, get_drive_side, DOMAINS, get_domain,
    PHONE_CODES, get_phone_code, get_sun_position,
)
from config import DEFAULT_COOLDOWN


# ─────────────────────────────────────────────────────────────
# Additional local data not in geoguessr_data.py
# ─────────────────────────────────────────────────────────────

WRITING_SYSTEMS: dict[str, tuple[str, str]] = {
    # text fragment or country → (script name, countries/languages)
    "cyrillic": (
        "Cyrillic script",
        "Used in: Russia, Ukraine, Belarus, Bulgaria, Serbia, Kazakhstan, Mongolia, and more · "
        "33 letters in Russian · Based on Greek alphabet · Created ~940 AD by Saints Cyril and Methodius · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "latin": (
        "Latin script",
        "Most widely used writing system · Used in: Western Europe, Americas, Africa, Southeast Asia · "
        "Derived from Etruscan alphabet · ~26 base letters + many diacritics · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "arabic": (
        "Arabic script",
        "Used in: Arab world, Iran (Persi-Arabic), Pakistan (Nastaliq), Afghanistan · "
        "Right-to-left · 28 letters · Connected cursive script · "
        "Second most used writing system by country count · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "thai": (
        "Thai script",
        "Used exclusively in: Thailand · "
        "44 consonants, 15 vowel symbols, 4 tone marks · "
        "No spaces between words · Derived from Khmer script · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "georgian": (
        "Georgian script (Mkhedruli)",
        "Used exclusively in: Georgia · "
        "33 letters · One of only 14 scripts in the world used for a single language · "
        "Created ~430 AD · Three historical forms exist · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "armenian": (
        "Armenian script",
        "Used exclusively in: Armenia · "
        "38 letters · Created 405 AD by Mesrop Mashtots · "
        "One of the few scripts created for a single language · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "greek": (
        "Greek script",
        "Used in: Greece, Cyprus · "
        "24 letters · Oldest continuously used alphabet · "
        "Ancestor of Latin, Cyrillic, and Armenian scripts · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "hebrew": (
        "Hebrew script",
        "Used in: Israel · Right-to-left · "
        "22 consonant letters · Vowels usually unwritten (abjad) · "
        "Also used for Yiddish and Ladino · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "devanagari": (
        "Devanagari script",
        "Used in: India (Hindi, Marathi, Sanskrit), Nepal (Nepali) · "
        "47 primary characters · Left-to-right · "
        "Most widely used script in South Asia · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "hangul": (
        "Hangul script",
        "Used exclusively in: South Korea (and North Korea) · "
        "14 consonants + 10 vowels = 24 letters · "
        "Created 1443 by King Sejong · One of few scripts with a known inventor · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "hiragana": (
        "Japanese Hiragana",
        "Used in: Japan · 46 characters · "
        "One of three Japanese scripts (with Katakana and Kanji) · "
        "Used for native Japanese words and grammar · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "katakana": (
        "Japanese Katakana",
        "Used in: Japan · 46 characters · "
        "Used primarily for foreign loanwords and emphasis · "
        "Recognizable by angular, sharp strokes · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "kanji": (
        "Japanese Kanji (Chinese characters)",
        "Used in: Japan (Chinese origin) · "
        "~2000 characters in everyday use (Joyo Kanji) · "
        "50,000+ characters exist · Each has meaning + reading(s) · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "simplified chinese": (
        "Simplified Chinese characters",
        "Used in: Mainland China, Singapore · "
        "Simplified from Traditional Chinese in 1950s-60s · "
        "~7000 characters in common use · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "traditional chinese": (
        "Traditional Chinese characters",
        "Used in: Taiwan, Hong Kong, Macau · "
        "Original unmodified form · More complex strokes than Simplified · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "khmer": (
        "Khmer script",
        "Used exclusively in: Cambodia · "
        "74 characters · Longest alphabet in the world · "
        "Derived from Pallava script of South India · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "lao": (
        "Lao script",
        "Used exclusively in: Laos · "
        "Similar to Thai but distinct · 27 consonants · "
        "Right-to-left has no spaces between words · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "sinhala": (
        "Sinhala script",
        "Used in: Sri Lanka · "
        "58 letters · Derived from Brahmi · "
        "Spoken by ~17 million Sinhalese · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "burmese": (
        "Burmese script (Myanmar)",
        "Used in: Myanmar · "
        "33 consonants · Rounded characters (due to palm leaf writing) · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "ethiopic": (
        "Ethiopic script (Ge'ez / Fidel)",
        "Used in: Ethiopia (Amharic), Eritrea (Tigrinya) · "
        "33 base characters × 7 forms = 231+ total · "
        "One of oldest writing systems still in use · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "tibetan": (
        "Tibetan script",
        "Used in: Tibet, Bhutan · "
        "30 consonants · Left-to-right · "
        "Derived from Indian Brahmi script ~600 AD · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
    "mongolian": (
        "Mongolian script (Traditional)",
        "Used in: Inner Mongolia (China) · "
        "Written vertically top-to-bottom · "
        "Modern Mongolia uses Cyrillic instead · "
        "[Source: Unicode Consortium / ISO 15924]"
    ),
}

ROAD_SIGNS: dict[str, str] = {
    "sweden": "Blue highway signs · unique 'Akzidenz Grotesk' font · km distances · very clean minimal design",
    "japan": "Green highway signs with white text · blue expressway · Japanese + romaji · distinctive arrow styles",
    "usa": "Green highway signs · Interstate shield shape · mile markers · white text on green standard",
    "uk": "Blue motorway signs · green A-road signs · white local signs · distances in miles · Transport font",
    "france": "Blue motorway (autoroute) · green national road · white text · distances in km",
    "germany": "Blue Autobahn signs · yellow federal road signs · distinctive Frutiger font",
    "australia": "Green highway signs · distances in km · similar to UK but adapted",
    "brazil": "Blue federal highway signs · white text · BR-XXX number format",
    "russia": "Blue highway signs · Cyrillic primary · distances in km",
    "china": "Green highway signs · Chinese characters + pinyin · G-number national routes",
    "south korea": "Green highway signs · Hangul + romanization · distinctive shield shapes",
    "turkey": "Green highway signs · Turkish text · O-number Otoyol format",
    "india": "Yellow national highway signs · state roads in white · Hindi + English",
    "mexico": "Green highway signs · similar to USA system · Mexican Federal Highway shield",
    "argentina": "Blue national route signs · RN number format · km markers",
    "chile": "Green highway signs · Ruta number format · distinctive red emergency signs",
    "norway": "Blue motorway signs · green primary · distances in km · very clean",
    "finland": "Green motorway signs · blue primary roads · Finnish + Swedish text",
    "netherlands": "Blue motorway (snelweg) signs · white text · A-number routes",
    "poland": "Green motorway (autostrada) signs · S-number express roads · red emergency",
}

ROAD_LINES: dict[str, str] = {
    "usa": "Yellow center lines · white edge lines · yellow dashed for passing · broken white to separate lanes",
    "uk": "White center lines · yellow edge lines (no stopping) · double yellow = no waiting",
    "australia": "White lines throughout · yellow edges only in certain urban areas",
    "japan": "White lines · yellow center prohibited passing lines · very precise markings",
    "france": "White lines · yellow temporary construction lines · dashed white center",
    "germany": "White lines · yellow temporary road works · very precise Autobahn markings",
    "brazil": "Yellow center lines · white edge and lane lines · similar to USA system",
    "canada": "Yellow center lines · white lanes · very similar to USA system",
    "sweden": "White lines throughout · very clean minimal markings",
    "china": "White lines · yellow center lines on two-way roads · similar mix to USA",
    "russia": "White lines · yellow center lines · sometimes faded or absent on rural roads",
    "india": "White lines · often faded · yellow center line on national highways · very inconsistent",
    "south africa": "White lines · yellow center · similar to UK system (left-hand traffic)",
    "new zealand": "White lines · yellow center lines · left-hand traffic like Australia",
}

POWER_POLES: dict[str, str] = {
    "japan": "Dense wooden poles · many wires · transformers on every pole · no underground cabling · very distinctive tangle",
    "usa": "Wooden poles · fewer wires than Japan · transformers present · state-by-state variation",
    "brazil": "Wooden or concrete poles · often cluttered with wires · transformer boxes common",
    "south africa": "Eskom concrete poles · distinctive design · often painted grey/white",
    "india": "Wooden and concrete mix · often overloaded with wires · transformers everywhere",
    "russia": "Concrete poles in urban areas · wooden in rural · significant variation by region",
    "ukraine": "Concrete poles with double crossbar · distinctive Soviet-era design",
    "mongolia": "Single wooden poles · sparse spacing · visible from long distances",
    "argentina": "Concrete poles · single crossbar · Edesur/Edenor branding in Buenos Aires",
    "chile": "Concrete poles · red/orange transformer boxes · distinctive Chilectra design",
    "kenya": "KPLC concrete poles · grey/cream color · Kenya Power branding",
    "nigeria": "PHCN/EKEDC concrete poles · often poorly maintained · transformer theft common",
    "indonesia": "PLN wooden/concrete mix · many wires · similar tangle to Japan in cities",
    "thailand": "PEA/MEA poles · wooden in rural · concrete urban · multiple wire bundles",
    "south korea": "KEPCO underground in cities · above ground in rural · very clean urban",
}

BARRIERS: dict[str, str] = {
    "usa": "W-beam steel guardrails · silver/grey · cable barriers on medians · box beam in some states",
    "uk": "Armco steel barriers · silver · concrete Jersey barriers on motorways",
    "france": "GBA concrete barriers · silver steel guardrails · distinctive yellow ends",
    "germany": "Bsh/Spb concrete barriers · silver W-beam · very precise installation",
    "spain": "Bionda steel guardrail · distinctive double wave profile · silver",
    "japan": "Silver steel guardrails · blue or green end caps · very clean installation",
    "australia": "W-beam steel · silver/grey · similar to USA system",
    "brazil": "Concreto Jersey barriers · silver guardrails · yellow/black striped ends",
    "chile": "Yellow Armco guardrails · distinctive yellow color · very visible",
    "south africa": "W-beam guardrails · often red/white striped ends · SANRAL standard",
    "russia": "Metal guardrails · often white/yellow color · significant variation · older Soviet concrete",
    "china": "W-beam guardrails · concrete barriers · blue/white on some highways",
    "india": "MORTH standard crash barriers · often damaged or absent on rural roads",
}

GROUND_COLORS: dict[str, str] = {
    "australia": "Red laterite soil in outback · ochre red · iron-rich · very distinctive rust color",
    "brazil": "Red terra roxa in south · dark red laterite · Amazon black soil (terra preta)",
    "senegal": "Deep red laterite · rust-colored dirt roads · very distinctive in Sahel region",
    "ghana": "Red laterite soil · rust-red unpaved roads · common across West Africa",
    "nigeria": "Reddish laterite in south · sandy brown in north · very regional variation",
    "kenya": "Red volcanic soil in highlands · brown savanna soil · very regional variation",
    "new zealand": "Dark volcanic soil North Island · pale/grey South Island glacial · very green vegetation",
    "iceland": "Black volcanic rock and sand · mossy green · very distinctive dark ground",
    "ireland": "Rich dark brown peat · very green grass · boggy terrain",
    "mongolia": "Pale yellow-brown steppe · dry grass · dust · little vegetation",
    "kazakhstan": "Pale sandy steppe · dry yellow-brown · vast flat terrain",
    "namibia": "Deep red Kalahari sand · orange dunes · one of reddest soils on earth",
    "madagascar": "Bright red laterite · called 'the red island' · extreme red coloring",
    "cambodia": "Reddish-brown soil · dry season dust · laterite common",
    "sri lanka": "Rich red laterite in south · darker soil in north · very lush green",
    "finland": "Dark peat and forest soil · grey rock · very muted colors",
    "norway": "Grey granite rock · thin topsoil · dramatic fjord rock faces",
    "russia": "Black chernozem in south · pale grey taiga soil · permafrost regions brown",
    "ukraine": "Rich black chernozem · world's most fertile soil · deep black color",
    "argentina": "Pampas dark soil · very fertile · black/brown in agricultural regions",
}

LANDSCAPE_DATA: dict[str, str] = {
    "finland": "Boreal forest (taiga) · Scots pine and Norway spruce · thousands of lakes · flat terrain",
    "norway": "Mixed forest in south · bare mountain tundra in north · dramatic fjords · birch and pine",
    "sweden": "Boreal forest · spruce and pine · flat to rolling · 100,000 lakes",
    "iceland": "Volcanic tundra · moss-covered lava fields · no trees (deforested in Viking age) · very distinctive",
    "mongolia": "Dry steppe grassland · few trees · vast open plains · semi-desert in south (Gobi)",
    "brazil": "Amazon rainforest in north · cerrado savanna in center · Atlantic forest in south",
    "kenya": "Savanna grassland · acacia trees · East African Rift Valley · coastal mangroves",
    "south africa": "Fynbos (unique to Cape) · savanna bushveld · semi-arid Karoo · subtropical east coast",
    "new zealand": "Temperate rainforest · tree ferns (distinctive) · volcanic plateau · Southern Alps glaciers",
    "japan": "Temperate forest · cedar and cypress · bamboo groves · cherry blossoms spring · very green mountains",
    "chile": "Atacama desert north (driest on earth) · Mediterranean shrubland center · Patagonia forest south",
    "australia": "Eucalyptus woodland · spinifex grassland outback · tropical north · Mediterranean SW",
    "canada": "Boreal forest (largest in world) · tundra in north · maple and birch east · pine west",
    "russia": "Taiga (world's largest forest) · tundra in north · steppe in south · birch very common",
    "indonesia": "Tropical rainforest · palm oil plantations · volcanic mountains · rice paddies",
    "india": "Tropical dry forest · monsoon forest · teak and sal trees · very regional variation",
    "peru": "Amazon rainforest east · Andes cloud forest · desert coast west · very dramatic transitions",
    "senegal": "Sahel scrubland · acacia savanna · baobab trees · very distinctive baobab silhouettes",
    "madagascar": "Spiny desert south · rainforest east · highland grassland · 90% endemic species",
    "ireland": "Emerald green pastures · hedgerows · peat bogs · very few native trees",
}

STREET_CAM_DATA: dict[str, str] = {
    "mongolia": "Snorkel camera (raised mast) · Gen 3 camera · often blurry · roof rack visible · distinctive high mount",
    "kenya": "Gen 3 snorkel camera · right-hand drive · often dusty/blurry quality · very distinctive mount",
    "botswana": "Snorkel camera · Gen 3 · right-hand drive · high quality coverage · distinctive mast",
    "south africa": "Standard Google car · Gen 3-4 · right-hand drive · good quality coverage",
    "japan": "Gen 4 trekker camera · very high resolution · backpack trekker for alleys · excellent coverage",
    "usa": "Gen 4 camera · best coverage globally · very clear · standard roof mount · most comprehensive",
    "australia": "Gen 4 camera · right-hand drive · clear quality · good rural coverage",
    "brazil": "Gen 3-4 camera · standard roof mount · variable quality by region · often blurry rural",
    "indonesia": "Trekker backpack camera · narrow streets · often different from standard car",
    "russia": "Mixed Gen 3-4 · standard car · coverage patchy outside major cities · older imagery some areas",
    "new zealand": "Gen 4 camera · right-hand drive · clear quality · good coverage both islands",
    "india": "Gen 3-4 · trekker in narrow streets · variable quality · often very blurry rural coverage",
    "peru": "Gen 3 camera · standard car · limited coverage outside Lima · often dated imagery",
    "ghana": "Gen 3 · right-hand drive · limited coverage · distinctive dusty conditions",
    "kyrgyzstan": "Gen 3 · very limited coverage · often single routes only · dated imagery",
}

ARCHITECTURE_DATA: dict[str, str] = {
    "mongolia": "White ger (yurt) · corrugated metal fences · Soviet concrete apartment blocks · dust everywhere",
    "vietnam": "Narrow tube houses (nha ong) · pastel colors · French colonial buildings in cities · motorbike scale streets",
    "japan": "Traditional wooden machiya · modern concrete · tile roofs with upturned corners · very clean streets",
    "indonesia": "Dutch colonial buildings in city centers · terracotta tile roofs · ornate wooden detail · batik patterns",
    "brazil": "Colorful painted concrete · favela stacked buildings · Portuguese colonial in historic centers",
    "south africa": "Cape Dutch style (distinctive curved gables) · modern suburbs · township corrugated iron",
    "russia": "Stalinist neoclassical · Khrushchev-era concrete blocks (Khrushchyovka) · very distinctive",
    "ukraine": "Soviet concrete blocks · traditional painted wooden houses in villages · ornate ironwork",
    "iran": "Mudbrick in villages · ornate brick patterns in cities · distinctive wind towers (badgir) · turquoise tile",
    "morocco": "Riad courtyard houses · zellige tile · white-blue medina buildings · earthen kasbahs south",
    "senegal": "Pink and cream colonial buildings · corrugated iron · baobab trees in villages",
    "georgia": "Wooden balconies (darbazi style) · stone churches · Soviet blocks · very ornate old city houses",
    "argentina": "European-influenced · Art Deco in Buenos Aires · Spanish colonial in provinces",
    "mexico": "Spanish colonial · colorful painted walls · adobe/concrete mix · distinctive baroque churches",
    "peru": "Spanish colonial · Inca stone walls in Cusco · adobe in Andes villages",
    "cambodia": "French colonial in cities · wooden stilt houses · temple architectural influence",
    "greece": "White cubic houses (Cycladic) · terracotta roofs · neoclassical in Athens · very regional",
    "turkey": "Ottoman wooden mansions (yali) · flat-roofed concrete modern · Ottoman mosques · very regional",
}

SEASON_DATA: dict[str, str] = {
    "australia january":     "High summer · scorching heat · bush fire risk · school holidays",
    "australia july":        "Mid winter · mild temperatures · dry in most areas · green in south",
    "new zealand january":   "High summer · warm · busy tourist season",
    "new zealand july":      "Mid winter · snow on South Island · cold nationwide",
    "brazil january":        "Wet season in Amazon · summer in south · Rio Carnival approaching",
    "brazil july":           "Dry season in Amazon · winter in south · mild temperatures",
    "norway january":        "Deep winter · polar night in north · heavy snow · very short days",
    "norway july":           "Midnight sun · warm · peak tourist season · very green",
    "japan march":           "Cherry blossom (sakura) season · famous pink trees · very photogenic",
    "japan december":        "Cold · possibility of snow in north · Christmas illuminations",
    "south africa june":     "Winter · dry season · best safari time (animals at water sources)",
    "south africa december": "Summer · hot and humid east coast · peak tourist season",
    "mongolia january":      "Brutal winter (dzud) · temperatures below -40°C · livestock mortality risk",
    "mongolia july":         "Summer · Naadam festival (national holiday) · green steppe",
    "iceland june":          "Midnight sun · 24hr daylight · green and dramatic",
    "iceland december":      "Polar night · Northern Lights season · very cold and dark",
    "india june":            "Monsoon season begins · heavy rains across country · flooding possible",
    "india october":         "Post-monsoon · clear skies · good travel weather · Diwali season",
    "canada january":        "Deep winter · heavy snow · very cold especially in prairies",
    "canada july":           "Peak summer · warm · long days · national holiday July 1",
}


class GeoguessrCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def _respond(self, ctx: commands.Context, message: str) -> None:
        if len(message) > 490:
            message = message[:487] + "..."
        await ctx.send(message)

    async def _check_cooldown(
        self,
        ctx: commands.Context,
        command: str,
        cooldown: int = DEFAULT_COOLDOWN
    ) -> bool:
        if ctx.author.is_mod or ctx.author.name.lower() == ctx.channel.name.lower():
            await db.update_cooldown(ctx.author.name, command)
            return True
        on_cd, _ = await db.check_cooldown(ctx.author.name, command, cooldown)
        if on_cd:
            return False
        await db.update_cooldown(ctx.author.name, command)
        await db.increment_command_stat(command)
        return True

    # ── !plate ───────────────────────────────────────────────

    @commands.command(name="plate", aliases=["licenseplate", "numberplate"])
    async def plate(self, ctx: commands.Context, *, code: str = "") -> None:
        """Look up a vehicle license plate code. Usage: !plate CH"""
        if not code:
            await self._respond(ctx, "Usage: !plate [code] — e.g. !plate CH or !plate TR")
            return
        if not await self._check_cooldown(ctx, "plate", DEFAULT_COOLDOWN):
            return
        key = code.strip().lower()
        if key in PLATES:
            country, notes = PLATES[key]
            await self._respond(ctx, f"Plate '{code.upper()}' → {country} | {notes} [Source: UNECE vehicle registration codes]")
        else:
            close = [k.upper() for k in PLATES if k.startswith(key[0])][:5]
            await self._respond(ctx, f"Plate code '{code.upper()}' not found. Similar codes: {', '.join(close)}")

    # ── !driveside ───────────────────────────────────────────

    @commands.command(name="driveside", aliases=["leftorright", "whichside", "roaddirection"])
    async def driveside(self, ctx: commands.Context, *, country: str = "") -> None:
        """Which side of the road does a country drive on? Usage: !driveside Japan"""
        if not country:
            await self._respond(ctx, "Usage: !driveside [country] — e.g. !driveside Japan")
            return
        if not await self._check_cooldown(ctx, "driveside", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, get_drive_side(country) + " [Source: World Standards]")

    # ── !domain ──────────────────────────────────────────────

    @commands.command(name="domain", aliases=["tld", "webdomain"])
    async def domain(self, ctx: commands.Context, *, code: str = "") -> None:
        """Look up a country-code domain. Usage: !domain .fi"""
        if not code:
            await self._respond(ctx, "Usage: !domain [.code] — e.g. !domain .fi or !domain .ke")
            return
        if not await self._check_cooldown(ctx, "domain", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, get_domain(code))

    # ── !sunposition ─────────────────────────────────────────

    @commands.command(name="sunposition", aliases=["shadowdirection", "hemisphere", "sunangle"])
    async def sunposition(self, ctx: commands.Context, *, country: str = "") -> None:
        """Sun position and shadow direction for GeoGuessr. Usage: !sunposition Chile"""
        if not country:
            await self._respond(ctx, "Usage: !sunposition [country] — e.g. !sunposition Chile")
            return
        if not await self._check_cooldown(ctx, "sunposition", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, get_sun_position(country))

    # ── !writingsystem ───────────────────────────────────────

    @commands.command(name="writingsystem", aliases=["whatscript", "identifyscript", "whatlanguage"])
    async def writingsystem(self, ctx: commands.Context, *, query: str = "") -> None:
        """Identify a writing system from text or name. Usage: !writingsystem Привет"""
        if not query:
            await self._respond(ctx, "Usage: !writingsystem [text or script name] — e.g. !writingsystem georgian")
            return
        if not await self._check_cooldown(ctx, "writingsystem", DEFAULT_COOLDOWN):
            return

        q = query.strip().lower()

        # Check direct name match first
        for key, (name, desc) in WRITING_SYSTEMS.items():
            if key in q or q in key:
                await self._respond(ctx, f"{name} | {desc}")
                return

        # Unicode-based detection for pasted text
        result = _detect_script_from_text(query)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(
                ctx,
                f"Could not identify script for '{query[:30]}'. "
                f"Try script names: cyrillic, arabic, thai, georgian, hangul, devanagari, hiragana..."
            )

    # ── !phonecode ───────────────────────────────────────────

    @commands.command(name="phonecode", aliases=["dialcode", "callingcode"])
    async def phonecode(self, ctx: commands.Context, *, code: str = "") -> None:
        """Look up a country by international dialling code. Usage: !phonecode +90"""
        if not code:
            await self._respond(ctx, "Usage: !phonecode [+code] — e.g. !phonecode +90 or !phonecode +81")
            return
        if not await self._check_cooldown(ctx, "phonecode", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, get_phone_code(code))

    # ── !roadsigns ───────────────────────────────────────────

    @commands.command(name="roadsigns", aliases=["trafficsigns", "signstyle"])
    async def roadsigns(self, ctx: commands.Context, *, country: str = "") -> None:
        """Road sign style and colors for a country. Usage: !roadsigns Sweden"""
        if not country:
            await self._respond(ctx, "Usage: !roadsigns [country] — e.g. !roadsigns Sweden")
            return
        if not await self._check_cooldown(ctx, "roadsigns", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in ROAD_SIGNS:
            await self._respond(ctx, f"{country.title()} road signs: {ROAD_SIGNS[key]}")
        else:
            await self._respond(ctx, f"No road sign data for '{country}'. Available: {', '.join(list(ROAD_SIGNS.keys())[:8])}...")

    # ── !roadlines ───────────────────────────────────────────

    @commands.command(name="roadlines", aliases=["roadmarkings", "lanemarks"])
    async def roadlines(self, ctx: commands.Context, *, country: str = "") -> None:
        """Road line marking colors and styles. Usage: !roadlines Brazil"""
        if not country:
            await self._respond(ctx, "Usage: !roadlines [country] — e.g. !roadlines Brazil")
            return
        if not await self._check_cooldown(ctx, "roadlines", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in ROAD_LINES:
            await self._respond(ctx, f"{country.title()} road lines: {ROAD_LINES[key]}")
        else:
            await self._respond(ctx, f"No road line data for '{country}'.")

    # ── !powerpoles ──────────────────────────────────────────

    @commands.command(name="powerpoles", aliases=["powerlines", "electricpoles"])
    async def powerpoles(self, ctx: commands.Context, *, country: str = "") -> None:
        """Power pole and utility line styles. Usage: !powerpoles Japan"""
        if not country:
            await self._respond(ctx, "Usage: !powerpoles [country] — e.g. !powerpoles Japan")
            return
        if not await self._check_cooldown(ctx, "powerpoles", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in POWER_POLES:
            await self._respond(ctx, f"{country.title()} power poles: {POWER_POLES[key]}")
        else:
            await self._respond(ctx, f"No power pole data for '{country}'.")

    # ── !barriers ────────────────────────────────────────────

    @commands.command(name="barriers", aliases=["guardrails", "crashbarrier"])
    async def barriers(self, ctx: commands.Context, *, country: str = "") -> None:
        """Road barrier and guardrail styles. Usage: !barriers Chile"""
        if not country:
            await self._respond(ctx, "Usage: !barriers [country] — e.g. !barriers Chile")
            return
        if not await self._check_cooldown(ctx, "barriers", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in BARRIERS:
            await self._respond(ctx, f"{country.title()} barriers: {BARRIERS[key]}")
        else:
            await self._respond(ctx, f"No barrier data for '{country}'.")

    # ── !groundcolor ─────────────────────────────────────────

    @commands.command(name="groundcolor", aliases=["soilcolor", "dirtcolor", "terraincolor"])
    async def groundcolor(self, ctx: commands.Context, *, country: str = "") -> None:
        """Soil and ground color for GeoGuessr. Usage: !groundcolor Madagascar"""
        if not country:
            await self._respond(ctx, "Usage: !groundcolor [country] — e.g. !groundcolor Madagascar")
            return
        if not await self._check_cooldown(ctx, "groundcolor", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in GROUND_COLORS:
            await self._respond(ctx, f"{country.title()} ground: {GROUND_COLORS[key]}")
        else:
            await self._respond(ctx, f"No ground color data for '{country}'.")

    # ── !landscape ───────────────────────────────────────────

    @commands.command(name="landscape", aliases=["vegetation", "biome", "treetype"])
    async def landscape(self, ctx: commands.Context, *, country: str = "") -> None:
        """Dominant vegetation and landscape type. Usage: !landscape Finland"""
        if not country:
            await self._respond(ctx, "Usage: !landscape [country] — e.g. !landscape Finland")
            return
        if not await self._check_cooldown(ctx, "landscape", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in LANDSCAPE_DATA:
            await self._respond(ctx, f"{country.title()} landscape: {LANDSCAPE_DATA[key]}")
        else:
            await self._respond(ctx, f"No landscape data for '{country}'.")

    # ── !streetcam ───────────────────────────────────────────

    @commands.command(name="streetcam", aliases=["camtype", "googletruck", "bollard"])
    async def streetcam(self, ctx: commands.Context, *, country: str = "") -> None:
        """Google Street View camera type for a country. Usage: !streetcam Mongolia"""
        if not country:
            await self._respond(ctx, "Usage: !streetcam [country] — e.g. !streetcam Mongolia")
            return
        if not await self._check_cooldown(ctx, "streetcam", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in STREET_CAM_DATA:
            await self._respond(ctx, f"{country.title()} Street View: {STREET_CAM_DATA[key]}")
        else:
            await self._respond(ctx, f"No Street View camera data for '{country}'.")

    # ── !architecture ────────────────────────────────────────

    @commands.command(name="architecture", aliases=["buildingstyle", "housestyle"])
    async def architecture(self, ctx: commands.Context, *, country: str = "") -> None:
        """Distinctive building styles visible in Street View. Usage: !architecture Mongolia"""
        if not country:
            await self._respond(ctx, "Usage: !architecture [country] — e.g. !architecture Mongolia")
            return
        if not await self._check_cooldown(ctx, "architecture", DEFAULT_COOLDOWN):
            return
        key = country.strip().lower()
        if key in ARCHITECTURE_DATA:
            await self._respond(ctx, f"{country.title()} architecture: {ARCHITECTURE_DATA[key]}")
        else:
            await self._respond(ctx, f"No architecture data for '{country}'.")

    # ── !season ──────────────────────────────────────────────

    @commands.command(name="season", aliases=["weathermonth", "climateof"])
    async def season(self, ctx: commands.Context, *, query: str = "") -> None:
        """What season/conditions to expect in a country in a given month. Usage: !season Japan march"""
        if not query:
            await self._respond(ctx, "Usage: !season [country] [month] — e.g. !season Japan march")
            return
        if not await self._check_cooldown(ctx, "season", DEFAULT_COOLDOWN):
            return
        q = query.strip().lower()
        for key, data in SEASON_DATA.items():
            parts = key.split()
            if all(p in q for p in parts):
                await self._respond(ctx, f"{query.title()}: {data}")
                return
        await self._respond(ctx, f"No season data for '{query}'. Try: !season Australia july | !season Norway january")


def _detect_script_from_text(text: str) -> str | None:
    """Basic Unicode range detection for identifying writing systems from pasted text."""
    counts: dict[str, int] = {}
    for char in text:
        cp = ord(char)
        if 0x0400 <= cp <= 0x04FF:
            counts["cyrillic"] = counts.get("cyrillic", 0) + 1
        elif 0x0600 <= cp <= 0x06FF:
            counts["arabic"] = counts.get("arabic", 0) + 1
        elif 0x0900 <= cp <= 0x097F:
            counts["devanagari"] = counts.get("devanagari", 0) + 1
        elif 0x0E00 <= cp <= 0x0E7F:
            counts["thai"] = counts.get("thai", 0) + 1
        elif 0x10A0 <= cp <= 0x10FF:
            counts["georgian"] = counts.get("georgian", 0) + 1
        elif 0x0530 <= cp <= 0x058F:
            counts["armenian"] = counts.get("armenian", 0) + 1
        elif 0x0370 <= cp <= 0x03FF:
            counts["greek"] = counts.get("greek", 0) + 1
        elif 0x0590 <= cp <= 0x05FF:
            counts["hebrew"] = counts.get("hebrew", 0) + 1
        elif 0x1100 <= cp <= 0x11FF or 0xAC00 <= cp <= 0xD7AF:
            counts["hangul"] = counts.get("hangul", 0) + 1
        elif 0x3040 <= cp <= 0x309F:
            counts["hiragana"] = counts.get("hiragana", 0) + 1
        elif 0x30A0 <= cp <= 0x30FF:
            counts["katakana"] = counts.get("katakana", 0) + 1
        elif 0x4E00 <= cp <= 0x9FFF:
            counts["chinese"] = counts.get("chinese", 0) + 1
        elif 0x0E80 <= cp <= 0x0EFF:
            counts["lao"] = counts.get("lao", 0) + 1
        elif 0x1780 <= cp <= 0x17FF:
            counts["khmer"] = counts.get("khmer", 0) + 1
        elif 0x1000 <= cp <= 0x109F:
            counts["burmese"] = counts.get("burmese", 0) + 1
        elif 0x1200 <= cp <= 0x137F:
            counts["ethiopic"] = counts.get("ethiopic", 0) + 1

    if not counts:
        return None

    dominant = max(counts, key=lambda k: counts[k])
    if dominant in WRITING_SYSTEMS:
        name, desc = WRITING_SYSTEMS[dominant]
        return f"Detected: {name} | {desc}"
    return f"Detected script: {dominant.title()}"


def prepare(bot):
    bot.add_cog(GeoguessrCog(bot))
