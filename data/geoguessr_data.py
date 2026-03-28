# PiicaBot — data/geoguessr_data.py
# All GeoGuessr meta data stored locally — zero API cost, instant responses.
# Sources: GeoGuessr community wiki, verified geography references,
#          Street View meta community (geohints.com, plonkit.net)

# ─────────────────────────────────────────────────────────────
# LICENSE PLATES
# Format: code → (description, notes)
# ─────────────────────────────────────────────────────────────
PLATES: dict[str, tuple[str, str]] = {
    "a":   ("Austria", "White plate · black text · EU band left"),
    "al":  ("Albania", "White plate · red/black text · eagle emblem"),
    "and": ("Andorra", "White plate · blue/yellow · AND code"),
    "arm": ("Armenia", "White plate · AMD code · blue stripe"),
    "az":  ("Azerbaijan", "White plate · AZ code · tricolor stripe"),
    "b":   ("Belgium", "Red text on white · B in red oval · EU band"),
    "bg":  ("Bulgaria", "White · BG code · EU band · Cyrillic possible"),
    "bh":  ("Bahrain", "White/red split · Arabic numerals · BRN"),
    "br":  ("Brazil", "Grey plate · Mercosur format · city name above"),
    "by":  ("Belarus", "White · red/green stripe left · BY code"),
    "ch":  ("Switzerland", "White · black text · CH oval · no EU band"),
    "cl":  ("Chile", "White · black text · flag colors left stripe"),
    "cn":  ("China", "Blue plate · white characters · province code first"),
    "co":  ("Colombia", "Yellow plate · black text · region code"),
    "cy":  ("Cyprus", "White · EU band · CY code"),
    "cz":  ("Czech Republic", "White · EU band · CZ code"),
    "d":   ("Germany", "White · black text · EU band · city code left"),
    "dk":  ("Denmark", "White · black text · EU band · DK"),
    "dz":  ("Algeria", "White · Arabic numerals · wilaya number"),
    "e":   ("Spain", "White · EU band · E code · province letters"),
    "eg":  ("Egypt", "White/yellow · Arabic text · blue stripe"),
    "est": ("Estonia", "White · EU band · EST code"),
    "et":  ("Ethiopia", "Yellow · Amharic script possible · ETH"),
    "f":   ("France", "White · EU band · F code · red/blue ends"),
    "fi":  ("Finland", "White · EU band · FIN code"),
    "fl":  ("Liechtenstein", "White · FL code · no EU band"),
    "gb":  ("United Kingdom", "White front / yellow rear · GB code"),
    "ge":  ("Georgia", "White · GE code · Georgian script possible"),
    "gr":  ("Greece", "White · EU band · GR code · Greek letters possible"),
    "hr":  ("Croatia", "White · EU band · HR code · checkerboard"),
    "hu":  ("Hungary", "White · EU band · H code"),
    "id":  ("Indonesia", "Black plate · white text · region code left"),
    "il":  ("Israel", "White · yellow Star of David · Hebrew characters"),
    "in":  ("India", "White front · yellow rear · state code · Hindi"),
    "ir":  ("Iran", "White · Arabic · IR code · green/red stripe"),
    "iq":  ("Iraq", "White · Arabic · IQ code"),
    "is":  ("Iceland", "White · IS code · no EU band"),
    "it":  ("Italy", "White · EU band · I code"),
    "j":   ("Japan", "White/yellow/green by vehicle type · hiragana + numbers"),
    "jo":  ("Jordan", "White · Arabic · JO code"),
    "kaz": ("Kazakhstan", "Yellow · KZ code · blue stripe top"),
    "ke":  ("Kenya", "White · black text · K code · county letters"),
    "kg":  ("Kyrgyzstan", "White · KG code · blue stripe"),
    "kh":  ("Cambodia", "White/blue · Khmer script · KH"),
    "kr":  ("South Korea", "White · Korean characters · green/blue stripe"),
    "kw":  ("Kuwait", "White · Arabic · KWT code"),
    "kz":  ("Kazakhstan", "Yellow · KZ · Kazakh text possible"),
    "lb":  ("Lebanon", "White · Arabic/Latin · cedar tree emblem"),
    "lt":  ("Lithuania", "White · EU band · LT code"),
    "lu":  ("Luxembourg", "White · EU band · L code"),
    "lv":  ("Latvia", "White · EU band · LV code"),
    "ma":  ("Morocco", "White · Arabic/Latin · MA code"),
    "mc":  ("Monaco", "White · MC code · tiny plate"),
    "md":  ("Moldova", "White · EU-style band · MD code"),
    "me":  ("Montenegro", "White · EU band · MNE code"),
    "mk":  ("North Macedonia", "White · EU band · MK code"),
    "mn":  ("Mongolia", "Yellow · MN code · Cyrillic possible"),
    "mx":  ("Mexico", "White · state name bottom · MX"),
    "my":  ("Malaysia", "White · black text · state letters · MAL"),
    "n":   ("Norway", "White · black text · N code · no EU band"),
    "ng":  ("Nigeria", "White/green · WN code format · state"),
    "nl":  ("Netherlands", "Yellow plate · black text · EU band · NL"),
    "no":  ("Norway", "White · black text · NO · no EU band"),
    "nz":  ("New Zealand", "White · black text · NZ · silver fern"),
    "p":   ("Portugal", "White · EU band · P code"),
    "ph":  ("Philippines", "White · blue text · PH · province name"),
    "pk":  ("Pakistan", "Black plate · white text · province initials"),
    "pl":  ("Poland", "White · EU band · PL code"),
    "pt":  ("Portugal", "White · EU band · P code"),
    "qa":  ("Qatar", "White · Arabic/Latin · QA code"),
    "ro":  ("Romania", "White · EU band · RO code"),
    "rs":  ("Serbia", "White · EU band · SRB code"),
    "ru":  ("Russia", "White · black text · RUS code · Cyrillic region"),
    "rw":  ("Rwanda", "Yellow · RWA code · black text"),
    "s":   ("Sweden", "White · black text · S code · no EU band"),
    "sa":  ("Saudi Arabia", "White · Arabic · SA code · green stripe"),
    "se":  ("Sweden", "White · EU band · S code"),
    "sg":  ("Singapore", "White · black text · S prefix · red/white"),
    "si":  ("Slovenia", "White · EU band · SLO code"),
    "sk":  ("Slovakia", "White · EU band · SK code"),
    "sm":  ("San Marino", "White · RSM code · no EU band"),
    "sn":  ("Senegal", "White · SN code · green/yellow stripe"),
    "th":  ("Thailand", "White · Thai script · province name · TH"),
    "tj":  ("Tajikistan", "White · TJ code · blue stripe"),
    "tm":  ("Turkmenistan", "White · TM code · green stripe"),
    "tn":  ("Tunisia", "White · Arabic · TN code · crescent moon"),
    "tr":  ("Turkey", "White · black text · TR code · plate city code"),
    "tw":  ("Taiwan", "White · Chinese characters · TW"),
    "tz":  ("Tanzania", "Yellow · TZ code · black text"),
    "ua":  ("Ukraine", "Yellow plate · black text · UA code · EU-style"),
    "ug":  ("Uganda", "White · UG code · black text"),
    "uk":  ("United Kingdom", "White front · yellow rear · GB code"),
    "us":  ("United States", "Varies by state · usually white · state name bottom"),
    "uz":  ("Uzbekistan", "White · UZ code · blue stripe"),
    "va":  ("Vatican City", "Yellow · SCV code · papal keys emblem"),
    "vn":  ("Vietnam", "Blue plate · white text · province number · VN"),
    "ye":  ("Yemen", "White · Arabic · YE code"),
    "za":  ("South Africa", "White · ZA code · green bar · province"),
    "zm":  ("Zambia", "White · ZM code · black text"),
    "zw":  ("Zimbabwe", "White · ZW code · black text"),
}


# ─────────────────────────────────────────────────────────────
# DRIVING SIDE
# Source: Wikipedia "Left- and right-hand traffic" (verified)
# ─────────────────────────────────────────────────────────────
DRIVE_SIDE: dict[str, tuple[str, str]] = {
    "australia":        ("Left",  "British colonial influence · since 1820s"),
    "bangladesh":       ("Left",  "British colonial influence"),
    "bhutan":           ("Left",  "British influence"),
    "botswana":         ("Left",  "British colonial"),
    "brunei":           ("Left",  "British colonial"),
    "cyprus":           ("Left",  "British colonial · joined EU but kept left"),
    "eswatini":         ("Left",  "British colonial"),
    "fiji":             ("Left",  "British colonial"),
    "guyana":           ("Left",  "British colonial"),
    "hong kong":        ("Left",  "British colonial · maintained after 1997 handover"),
    "india":            ("Left",  "British colonial · ~1.4 billion people drive left"),
    "indonesia":        ("Left",  "Dutch colonial"),
    "ireland":          ("Left",  "British influence · kept after independence"),
    "jamaica":          ("Left",  "British colonial"),
    "japan":            ("Left",  "Adopted from Britain 1872 · never colonized"),
    "kenya":            ("Left",  "British colonial"),
    "lesotho":          ("Left",  "British colonial"),
    "macau":            ("Left",  "Portuguese colonial · maintained after 1999"),
    "malawi":           ("Left",  "British colonial"),
    "malaysia":         ("Left",  "British colonial"),
    "malta":            ("Left",  "British colonial"),
    "mauritius":        ("Left",  "British colonial"),
    "mozambique":       ("Left",  "Portuguese colonial"),
    "namibia":          ("Left",  "British then South African colonial"),
    "nepal":            ("Left",  "British influence"),
    "new zealand":      ("Left",  "British colonial"),
    "pakistan":         ("Left",  "British colonial"),
    "papua new guinea": ("Left",  "Australian mandate"),
    "singapore":        ("Left",  "British colonial"),
    "south africa":     ("Left",  "British colonial"),
    "sri lanka":        ("Left",  "British colonial"),
    "suriname":         ("Left",  "Dutch colonial · unusual for South America"),
    "swaziland":        ("Left",  "British colonial"),
    "tanzania":         ("Left",  "British colonial"),
    "thailand":         ("Left",  "Adopted from Britain · never colonized"),
    "timor-leste":      ("Left",  "Portuguese colonial · retained after independence"),
    "trinidad and tobago": ("Left", "British colonial"),
    "uganda":           ("Left",  "British colonial"),
    "united kingdom":   ("Left",  "Historical · origin of global left-hand traffic"),
    "zambia":           ("Left",  "British colonial"),
    "zimbabwe":         ("Left",  "British colonial"),
}
# Everything not listed drives on the RIGHT


def get_drive_side(country: str) -> str:
    country_lower = country.strip().lower()
    if country_lower in DRIVE_SIDE:
        side, note = DRIVE_SIDE[country_lower]
        return f"{country.title()} drives on the {side} · {note}"
    return f"{country.title()} drives on the Right (default for most countries)"


# ─────────────────────────────────────────────────────────────
# TOP-LEVEL DOMAINS
# Source: IANA Root Zone Database (iana.org/domains/root/db)
# ─────────────────────────────────────────────────────────────
DOMAINS: dict[str, str] = {
    ".ac": "Ascension Island (UK)", ".ad": "Andorra", ".ae": "United Arab Emirates",
    ".af": "Afghanistan", ".ag": "Antigua and Barbuda", ".ai": "Anguilla (UK)",
    ".al": "Albania", ".am": "Armenia", ".ao": "Angola", ".aq": "Antarctica",
    ".ar": "Argentina", ".as": "American Samoa (US)", ".at": "Austria",
    ".au": "Australia", ".aw": "Aruba (Netherlands)", ".ax": "Åland Islands (Finland)",
    ".az": "Azerbaijan", ".ba": "Bosnia and Herzegovina", ".bb": "Barbados",
    ".bd": "Bangladesh", ".be": "Belgium", ".bf": "Burkina Faso",
    ".bg": "Bulgaria", ".bh": "Bahrain", ".bi": "Burundi",
    ".bj": "Benin", ".bm": "Bermuda (UK)", ".bn": "Brunei",
    ".bo": "Bolivia", ".br": "Brazil", ".bs": "Bahamas",
    ".bt": "Bhutan", ".bw": "Botswana", ".by": "Belarus",
    ".bz": "Belize", ".ca": "Canada", ".cc": "Cocos Islands (Australia)",
    ".cd": "DR Congo", ".cf": "Central African Republic", ".cg": "Republic of Congo",
    ".ch": "Switzerland", ".ci": "Ivory Coast", ".ck": "Cook Islands (NZ)",
    ".cl": "Chile", ".cm": "Cameroon", ".cn": "China",
    ".co": "Colombia", ".cr": "Costa Rica", ".cu": "Cuba",
    ".cv": "Cape Verde", ".cw": "Curaçao (Netherlands)", ".cy": "Cyprus",
    ".cz": "Czech Republic", ".de": "Germany", ".dj": "Djibouti",
    ".dk": "Denmark", ".dm": "Dominica", ".do": "Dominican Republic",
    ".dz": "Algeria", ".ec": "Ecuador", ".ee": "Estonia",
    ".eg": "Egypt", ".er": "Eritrea", ".es": "Spain",
    ".et": "Ethiopia", ".eu": "European Union", ".fi": "Finland",
    ".fj": "Fiji", ".fk": "Falkland Islands (UK)", ".fm": "Micronesia",
    ".fo": "Faroe Islands (Denmark)", ".fr": "France", ".ga": "Gabon",
    ".gb": "United Kingdom", ".gd": "Grenada", ".ge": "Georgia",
    ".gf": "French Guiana (France)", ".gg": "Guernsey (UK)", ".gh": "Ghana",
    ".gi": "Gibraltar (UK)", ".gl": "Greenland (Denmark)", ".gm": "Gambia",
    ".gn": "Guinea", ".gp": "Guadeloupe (France)", ".gq": "Equatorial Guinea",
    ".gr": "Greece", ".gt": "Guatemala", ".gu": "Guam (US)",
    ".gw": "Guinea-Bissau", ".gy": "Guyana", ".hk": "Hong Kong (China)",
    ".hm": "Heard/McDonald Islands (Australia)", ".hn": "Honduras", ".hr": "Croatia",
    ".ht": "Haiti", ".hu": "Hungary", ".id": "Indonesia",
    ".ie": "Ireland", ".il": "Israel", ".im": "Isle of Man (UK)",
    ".in": "India", ".io": "British Indian Ocean Territory", ".iq": "Iraq",
    ".ir": "Iran", ".is": "Iceland", ".it": "Italy",
    ".je": "Jersey (UK)", ".jm": "Jamaica", ".jo": "Jordan",
    ".jp": "Japan", ".ke": "Kenya", ".kg": "Kyrgyzstan",
    ".kh": "Cambodia", ".ki": "Kiribati", ".km": "Comoros",
    ".kn": "Saint Kitts and Nevis", ".kp": "North Korea", ".kr": "South Korea",
    ".kw": "Kuwait", ".ky": "Cayman Islands (UK)", ".kz": "Kazakhstan",
    ".la": "Laos", ".lb": "Lebanon", ".lc": "Saint Lucia",
    ".li": "Liechtenstein", ".lk": "Sri Lanka", ".lr": "Liberia",
    ".ls": "Lesotho", ".lt": "Lithuania", ".lu": "Luxembourg",
    ".lv": "Latvia", ".ly": "Libya", ".ma": "Morocco",
    ".mc": "Monaco", ".md": "Moldova", ".me": "Montenegro",
    ".mg": "Madagascar", ".mh": "Marshall Islands", ".mk": "North Macedonia",
    ".ml": "Mali", ".mm": "Myanmar", ".mn": "Mongolia",
    ".mo": "Macau (China)", ".mp": "Northern Mariana Islands (US)",
    ".mq": "Martinique (France)", ".mr": "Mauritania", ".ms": "Montserrat (UK)",
    ".mt": "Malta", ".mu": "Mauritius", ".mv": "Maldives",
    ".mw": "Malawi", ".mx": "Mexico", ".my": "Malaysia",
    ".mz": "Mozambique", ".na": "Namibia", ".nc": "New Caledonia (France)",
    ".ne": "Niger", ".nf": "Norfolk Island (Australia)", ".ng": "Nigeria",
    ".ni": "Nicaragua", ".nl": "Netherlands", ".no": "Norway",
    ".np": "Nepal", ".nr": "Nauru", ".nu": "Niue (NZ)",
    ".nz": "New Zealand", ".om": "Oman", ".pa": "Panama",
    ".pe": "Peru", ".pf": "French Polynesia (France)", ".pg": "Papua New Guinea",
    ".ph": "Philippines", ".pk": "Pakistan", ".pl": "Poland",
    ".pm": "Saint-Pierre and Miquelon (France)", ".pn": "Pitcairn Islands (UK)",
    ".pr": "Puerto Rico (US)", ".ps": "Palestinian territories", ".pt": "Portugal",
    ".pw": "Palau", ".py": "Paraguay", ".qa": "Qatar",
    ".re": "Réunion (France)", ".ro": "Romania", ".rs": "Serbia",
    ".ru": "Russia", ".rw": "Rwanda", ".sa": "Saudi Arabia",
    ".sb": "Solomon Islands", ".sc": "Seychelles", ".sd": "Sudan",
    ".se": "Sweden", ".sg": "Singapore", ".sh": "Saint Helena (UK)",
    ".si": "Slovenia", ".sk": "Slovakia", ".sl": "Sierra Leone",
    ".sm": "San Marino", ".sn": "Senegal", ".so": "Somalia",
    ".sr": "Suriname", ".ss": "South Sudan", ".st": "São Tomé and Príncipe",
    ".sv": "El Salvador", ".sx": "Sint Maarten (Netherlands)", ".sy": "Syria",
    ".sz": "Eswatini", ".tc": "Turks and Caicos Islands (UK)", ".td": "Chad",
    ".tf": "French Southern Territories", ".tg": "Togo", ".th": "Thailand",
    ".tj": "Tajikistan", ".tk": "Tokelau (NZ)", ".tl": "Timor-Leste",
    ".tm": "Turkmenistan", ".tn": "Tunisia", ".to": "Tonga",
    ".tr": "Turkey", ".tt": "Trinidad and Tobago", ".tv": "Tuvalu",
    ".tw": "Taiwan", ".tz": "Tanzania", ".ua": "Ukraine",
    ".ug": "Uganda", ".uk": "United Kingdom", ".us": "United States",
    ".uy": "Uruguay", ".uz": "Uzbekistan", ".va": "Vatican City",
    ".vc": "Saint Vincent and the Grenadines", ".ve": "Venezuela",
    ".vg": "British Virgin Islands (UK)", ".vi": "US Virgin Islands",
    ".vn": "Vietnam", ".vu": "Vanuatu", ".wf": "Wallis and Futuna (France)",
    ".ws": "Samoa", ".ye": "Yemen", ".yt": "Mayotte (France)",
    ".za": "South Africa", ".zm": "Zambia", ".zw": "Zimbabwe",
}


def get_domain(code: str) -> str:
    """Look up a country-code TLD."""
    key = code.strip().lower()
    if not key.startswith("."):
        key = "." + key
    if key in DOMAINS:
        return f"{key} → {DOMAINS[key]} [Source: IANA Root Zone Database]"
    return f"'{key}' not found in IANA domain list. Try with a dot: !domain .fi"


# ─────────────────────────────────────────────────────────────
# PHONE CODES
# Source: ITU-T E.164 (itu.int)
# ─────────────────────────────────────────────────────────────
PHONE_CODES: dict[str, str] = {
    "1":    "USA / Canada",
    "7":    "Russia / Kazakhstan",
    "20":   "Egypt", "27": "South Africa",
    "30":   "Greece", "31": "Netherlands",
    "32":   "Belgium", "33": "France",
    "34":   "Spain", "36": "Hungary",
    "39":   "Italy", "40": "Romania",
    "41":   "Switzerland", "43": "Austria",
    "44":   "United Kingdom", "45": "Denmark",
    "46":   "Sweden", "47": "Norway",
    "48":   "Poland", "49": "Germany",
    "51":   "Peru", "52": "Mexico",
    "53":   "Cuba", "54": "Argentina",
    "55":   "Brazil", "56": "Chile",
    "57":   "Colombia", "58": "Venezuela",
    "60":   "Malaysia", "61": "Australia",
    "62":   "Indonesia", "63": "Philippines",
    "64":   "New Zealand", "65": "Singapore",
    "66":   "Thailand", "81": "Japan",
    "82":   "South Korea", "84": "Vietnam",
    "86":   "China", "90": "Turkey",
    "91":   "India", "92": "Pakistan",
    "93":   "Afghanistan", "94": "Sri Lanka",
    "95":   "Myanmar", "98": "Iran",
    "212":  "Morocco", "213": "Algeria",
    "216":  "Tunisia", "218": "Libya",
    "220":  "Gambia", "221": "Senegal",
    "222":  "Mauritania", "223": "Mali",
    "224":  "Guinea", "225": "Ivory Coast",
    "226":  "Burkina Faso", "227": "Niger",
    "228":  "Togo", "229": "Benin",
    "230":  "Mauritius", "231": "Liberia",
    "232":  "Sierra Leone", "233": "Ghana",
    "234":  "Nigeria", "235": "Chad",
    "236":  "Central African Republic", "237": "Cameroon",
    "238":  "Cape Verde", "239": "São Tomé and Príncipe",
    "240":  "Equatorial Guinea", "241": "Gabon",
    "242":  "Republic of Congo", "243": "DR Congo",
    "244":  "Angola", "245": "Guinea-Bissau",
    "246":  "British Indian Ocean Territory", "247": "Ascension Island",
    "248":  "Seychelles", "249": "Sudan",
    "250":  "Rwanda", "251": "Ethiopia",
    "252":  "Somalia", "253": "Djibouti",
    "254":  "Kenya", "255": "Tanzania",
    "256":  "Uganda", "257": "Burundi",
    "258":  "Mozambique", "260": "Zambia",
    "261":  "Madagascar", "262": "Réunion / Mayotte",
    "263":  "Zimbabwe", "264": "Namibia",
    "265":  "Malawi", "266": "Lesotho",
    "267":  "Botswana", "268": "Eswatini",
    "269":  "Comoros", "290": "Saint Helena",
    "291":  "Eritrea", "297": "Aruba",
    "298":  "Faroe Islands", "299": "Greenland",
    "350":  "Gibraltar", "351": "Portugal",
    "352":  "Luxembourg", "353": "Ireland",
    "354":  "Iceland", "355": "Albania",
    "356":  "Malta", "357": "Cyprus",
    "358":  "Finland", "359": "Bulgaria",
    "370":  "Lithuania", "371": "Latvia",
    "372":  "Estonia", "373": "Moldova",
    "374":  "Armenia", "375": "Belarus",
    "376":  "Andorra", "377": "Monaco",
    "378":  "San Marino", "380": "Ukraine",
    "381":  "Serbia", "382": "Montenegro",
    "385":  "Croatia", "386": "Slovenia",
    "387":  "Bosnia and Herzegovina", "389": "North Macedonia",
    "420":  "Czech Republic", "421": "Slovakia",
    "423":  "Liechtenstein", "500": "Falkland Islands",
    "501":  "Belize", "502": "Guatemala",
    "503":  "El Salvador", "504": "Honduras",
    "505":  "Nicaragua", "506": "Costa Rica",
    "507":  "Panama", "509": "Haiti",
    "590":  "Guadeloupe", "591": "Bolivia",
    "592":  "Guyana", "593": "Ecuador",
    "594":  "French Guiana", "595": "Paraguay",
    "596":  "Martinique", "597": "Suriname",
    "598":  "Uruguay", "599": "Netherlands Antilles",
    "670":  "Timor-Leste", "672": "Norfolk Island",
    "673":  "Brunei", "674": "Nauru",
    "675":  "Papua New Guinea", "676": "Tonga",
    "677":  "Solomon Islands", "678": "Vanuatu",
    "679":  "Fiji", "680": "Palau",
    "682":  "Cook Islands", "685": "Samoa",
    "686":  "Kiribati", "687": "New Caledonia",
    "688":  "Tuvalu", "689": "French Polynesia",
    "690":  "Tokelau", "691": "Micronesia",
    "692":  "Marshall Islands", "850": "North Korea",
    "852":  "Hong Kong", "853": "Macau",
    "855":  "Cambodia", "856": "Laos",
    "880":  "Bangladesh", "886": "Taiwan",
    "960":  "Maldives", "961": "Lebanon",
    "962":  "Jordan", "963": "Syria",
    "964":  "Iraq", "965": "Kuwait",
    "966":  "Saudi Arabia", "967": "Yemen",
    "968":  "Oman", "970": "Palestinian territories",
    "971":  "United Arab Emirates", "972": "Israel",
    "973":  "Bahrain", "974": "Qatar",
    "975":  "Bhutan", "976": "Mongolia",
    "977":  "Nepal", "992": "Tajikistan",
    "993":  "Turkmenistan", "994": "Azerbaijan",
    "995":  "Georgia", "996": "Kyrgyzstan",
    "998":  "Uzbekistan",
}


def get_phone_code(code: str) -> str:
    """Look up a country by international dialling code."""
    key = code.strip().lstrip("+").lstrip("00")
    if key in PHONE_CODES:
        return f"+{key} → {PHONE_CODES[key]} [Source: ITU-T E.164]"
    return f"Phone code +{key} not found. Make sure to include only digits after the +."


# ─────────────────────────────────────────────────────────────
# SUN POSITION / HEMISPHERE CLUES
# Source: Geography / astronomy fundamentals
# ─────────────────────────────────────────────────────────────
SUN_DATA: dict[str, tuple[str, str, str]] = {
    # country → (hemisphere, shadow direction at noon, notes)
    "australia":     ("Southern", "North",  "Sun in north at noon · shadows point north"),
    "new zealand":   ("Southern", "North",  "Sun in north · strong UV · shadows short at summer noon"),
    "argentina":     ("Southern", "North",  "Southern hemisphere · same sun arc as Australia"),
    "brazil":        ("Both",     "Varies", "Equator passes through · north part has sun overhead"),
    "chile":         ("Southern", "North",  "Long thin country · south part very cold shadows"),
    "south africa":  ("Southern", "North",  "Shadows point north at noon"),
    "kenya":         ("Both",     "Varies", "On the equator · sun nearly overhead · short shadows"),
    "indonesia":     ("Both",     "Varies", "Equatorial · sun very high · shadows near vertical"),
    "mongolia":      ("Northern", "South",  "Far north · long shadows · sun low in sky"),
    "iceland":       ("Northern", "South",  "Very north · sun barely rises in winter"),
    "norway":        ("Northern", "South",  "Far north · midnight sun in summer"),
    "finland":       ("Northern", "South",  "Far north · polar night in winter"),
    "canada":        ("Northern", "South",  "Sun always in south · long shadows in winter"),
    "russia":        ("Northern", "South",  "Vast · Siberia has extreme low sun angles"),
    "japan":         ("Northern", "South",  "Mid-latitude · sun clearly in south at noon"),
    "usa":           ("Northern", "South",  "Sun in south · Hawaii closer to equator"),
    "india":         ("Northern", "South",  "Mostly northern hemisphere · south near equator"),
}

HEMISPHERE_NOTE = (
    "Northern hemisphere: sun is in the SOUTH at noon → shadows point NORTH. "
    "Southern hemisphere: sun is in the NORTH at noon → shadows point SOUTH. "
    "Near equator: sun nearly overhead → very short shadows."
)


def get_sun_position(country: str) -> str:
    """Return sun position and shadow direction for a country."""
    key = country.strip().lower()
    if key in SUN_DATA:
        hemi, shadow, note = SUN_DATA[key]
        return (
            f"{country.title()} — Hemisphere: {hemi} | "
            f"Noon shadow direction: {shadow} | {note} "
            f"[Source: Geography fundamentals]"
        )
    # Generic northern/southern check based on known geography
    southern = {
        "uruguay", "paraguay", "bolivia", "peru", "ecuador",
        "lesotho", "botswana", "namibia", "zimbabwe", "zambia",
        "mozambique", "madagascar", "malawi", "eswatini",
        "fiji", "samoa", "tonga", "vanuatu", "solomon islands",
        "papua new guinea", "timor-leste",
    }
    if key in southern:
        return (
            f"{country.title()} — Southern hemisphere | "
            f"Sun in north at noon · shadows point north "
            f"[Source: Geography fundamentals]"
        )
    return (
        f"{country.title()} — Likely Northern hemisphere | "
        f"Sun in south at noon · shadows point north. "
        f"Tip: {HEMISPHERE_NOTE}"
    )
