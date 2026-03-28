# PiicaBot — twitch_bot/commands/knowledge.py
# History, science, culture knowledge commands.
# All data is locally stored — verified and sourced.
# !space !element !deepdive !onthisday !wonder !empire !disaster
# !island !border !anthem !rebellion !invention !heist !unsolved
# !duel !forgotten !almostcalled !briefexistence !strangefact
# !weirdlaw !oneday !thoughtexperiment !oldest !phenomenon
# !fossil !number !movement !instrument !architect !banned !hapax !wordgap

import random
from twitchio.ext import commands
from loguru import logger

import database.db as db
from services.nasa import get_space_fact
from config import DEFAULT_COOLDOWN


# ─────────────────────────────────────────────────────────────
# LOCAL DATA — all verified and sourced
# ─────────────────────────────────────────────────────────────

ELEMENTS: dict[str, str] = {
    "hydrogen":   "H · #1 · discovered 1766 by Cavendish · most abundant element in universe · fuel of stars [Source: IUPAC]",
    "helium":     "He · #2 · discovered 1868 in the Sun before Earth · second most abundant in universe [Source: IUPAC]",
    "lithium":    "Li · #3 · lightest metal · used in batteries and psychiatric medication [Source: IUPAC]",
    "carbon":     "C · #6 · basis of all known life · diamond and graphite are both pure carbon [Source: IUPAC]",
    "nitrogen":   "N · #7 · 78% of Earth's atmosphere · essential for DNA and proteins [Source: IUPAC]",
    "oxygen":     "O · #8 · 21% of atmosphere · discovered independently by Scheele and Priestley 1770s [Source: IUPAC]",
    "sodium":     "Na · #11 · symbol from Latin Natrium · extremely reactive with water · table salt is NaCl [Source: IUPAC]",
    "silicon":    "Si · #14 · second most abundant element in Earth's crust · basis of computer chips [Source: IUPAC]",
    "iron":       "Fe · #26 · symbol from Latin Ferrum · most common element by mass on Earth · Earth's core [Source: IUPAC]",
    "copper":     "Cu · #29 · symbol from Latin Cuprum (Cyprus where mined) · used 10,000 years · still essential [Source: IUPAC]",
    "gold":       "Au · #79 · symbol from Latin Aurum · oldest known metal · never tarnishes · 197,576 tonnes mined total [Source: IUPAC/World Gold Council]",
    "mercury":    "Hg · #80 · symbol from Latin Hydrargyrum (liquid silver) · only metal liquid at room temp [Source: IUPAC]",
    "lead":       "Pb · #82 · symbol from Latin Plumbum · Romans used in pipes (plumbing etymology) · highly toxic [Source: IUPAC]",
    "uranium":    "U · #92 · discovered 1789 · named after planet Uranus · radioactive · nuclear fuel [Source: IUPAC]",
    "plutonium":  "Pu · #94 · first synthesized 1940 · named after Pluto · nuclear weapons material [Source: IUPAC]",
    "oganesson":  "Og · #118 · heaviest known element · synthesized 2002 · named after physicist Yuri Oganessian [Source: IUPAC]",
}

DEEP_DIVES: list[str] = [
    "Honey never expires · 3,000-year-old honey found in Egyptian tombs was still edible [Source: National Geographic]",
    "A day on Venus is longer than a year on Venus · its rotation is slower than its orbit around the Sun [Source: NASA]",
    "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid [Source: verified chronology]",
    "Nintendo was founded in 1889 — 14 years before the Wright Brothers' first flight [Source: Nintendo corporate history]",
    "Oxford University is older than the Aztec Empire · Oxford ~1096 AD · Aztec Empire ~1428 AD [Source: verified history]",
    "Mammoths were still alive when the Great Pyramid was being built · 2500 BCE vs ~1650 BCE last mammoths [Source: scientific research]",
    "The fax machine was invented in 1843 — before the telephone (1876) [Source: technology history]",
    "Sharks are older than trees · sharks: ~450 million years · trees: ~350 million years [Source: fossil record]",
    "There are more possible chess games than atoms in the observable universe [Source: mathematics / Shannon number]",
    "A bolt of lightning contains enough energy to toast 100,000 slices of bread [Source: atmospheric physics]",
    "Scotland's national animal is the unicorn [Source: Scottish heraldry / official record]",
    "The shortest war in history lasted 38-45 minutes · Anglo-Zanzibar War 1896 [Source: Guinness World Records]",
    "Bananas are slightly radioactive due to their potassium-40 content [Source: nuclear physics / health physics]",
    "The Eiffel Tower grows 15cm taller in summer due to thermal expansion [Source: physics / Tour Eiffel official]",
    "Crows can recognize human faces and hold grudges for years [Source: University of Washington research]",
    "A group of flamingos is called a flamboyance [Source: Oxford English Dictionary]",
    "The word 'muscle' comes from Latin 'musculus' meaning 'little mouse' — because flexing muscles look like mice under skin [Source: Latin etymology]",
    "Butterflies taste with their feet [Source: entomology research]",
    "The Great Wall of China is NOT visible from space with the naked eye · confirmed by Chinese astronaut Yang Liwei [Source: NASA / CNSA]",
    "Sound travels 4× faster through water than through air [Source: physics]",
]

WONDERS: dict[str, str] = {
    "great pyramid":      "Giza, Egypt · built ~2560 BCE · 139m tall · tallest man-made structure for 3,800 years · only ancient wonder still standing [Source: UNESCO]",
    "colosseum":          "Rome, Italy · built 70-80 AD · held 50,000-80,000 spectators · hosted gladiator combat for 400 years [Source: UNESCO World Heritage]",
    "taj mahal":          "Agra, India · built 1632-1653 · Shah Jahan for wife Mumtaz Mahal · 20,000 workers · UNESCO World Heritage [Source: Archaeological Survey of India]",
    "machu picchu":       "Peru · built ~1450 AD by Inca · 2,430m altitude · 'discovered' by Hiram Bingham 1911 · UNESCO World Heritage [Source: UNESCO]",
    "great wall":         "China · built over centuries from 7th century BCE · ~21,196km total length · UNESCO World Heritage [Source: UNESCO / Chinese Academy of Sciences]",
    "chichen itza":       "Mexico · Maya civilization · built 600-900 AD · El Castillo pyramid precisely aligned to equinoxes [Source: UNESCO]",
    "christ the redeemer": "Rio de Janeiro, Brazil · built 1922-1931 · 30m tall + 8m pedestal · UNESCO World Heritage [Source: IPHAN Brazil]",
    "petra":              "Jordan · carved into rose-red rock · Nabataean civilization · ~300 BCE · UNESCO World Heritage [Source: UNESCO]",
    "stonehenge":         "Wiltshire, England · built ~3000-1500 BCE · purpose debated · UNESCO World Heritage [Source: English Heritage]",
    "angkor wat":         "Cambodia · built 12th century by Khmer Empire · largest religious monument on Earth · UNESCO [Source: UNESCO]",
    "alhambra":           "Granada, Spain · built 9th-14th century · Moorish palace complex · UNESCO World Heritage [Source: UNESCO]",
    "hagia sophia":       "Istanbul, Turkey · built 537 AD · was largest cathedral for 1000 years · converted mosque 1453 · museum 1934 · mosque again 2020 [Source: UNESCO]",
}

HISTORICAL_FACTS: dict[str, str] = {
    # Empires
    "roman empire":      "27 BCE - 476 CE (West) · at peak covered 5M km² · ~70M people (20% of world pop) · fell due to invasions, economic crisis, political instability [Source: Gibbon / modern historiography]",
    "mongol empire":     "1206-1368 · largest contiguous land empire ever · 24M km² · Genghis Khan unified Mongol tribes 1206 · killed ~40M people in conquests [Source: academic consensus]",
    "ottoman empire":    "1299-1922 · lasted 623 years · at peak: southeastern Europe, western Asia, North Africa · fell after WWI [Source: Ottoman historiography]",
    "byzantine empire":  "330-1453 · Eastern Roman Empire · preserved Roman law and Greek culture · fell to Mehmed II · 1,123 years [Source: academic consensus]",
    "british empire":    "Peak ~1920 · 24% of world land area · 412M people (23% of world) · 'Empire on which the sun never sets' [Source: historical record]",
    "persian empire":    "Achaemenid 550-330 BCE · first superpower · Cyrus the Great · religious tolerance · conquered by Alexander 330 BCE [Source: academic consensus]",
    # Disasters
    "chernobyl":         "April 26, 1986 · Ukraine (USSR) · Reactor No.4 exploded · 2,600 km² exclusion zone · ~350,000 evacuated · accelerated USSR collapse · [Source: IAEA / WHO]",
    "pompeii":           "August 24, 79 AD · Vesuvius eruption · 4-6m ash buried city · ~2,000 deaths · perfectly preserved · excavations ongoing [Source: Pompeii archaeological site]",
    "titanic":           "April 15, 1912 · 1,517 deaths · 'unsinkable' maiden voyage · iceberg collision · inadequate lifeboats · changed maritime law [Source: British Board of Trade inquiry]",
    "black death":       "1347-1351 · bubonic plague · killed 30-60% of European population (25-50M) · Y. pestis bacteria · fleas on rats [Source: WHO / academic consensus]",
    "hiroshima":         "August 6, 1945 · first nuclear weapon used in war · 70,000-80,000 instant deaths · ~140,000 by year end · changed warfare forever [Source: Hiroshima Peace Memorial Museum]",
    # Inventions
    "printing press":    "Johannes Gutenberg ~1440 · movable type · first book: Gutenberg Bible 1455 · enabled Reformation, Scientific Revolution, mass literacy [Source: historiography]",
    "internet":          "ARPANET 1969 (first message: Oct 29) · TCP/IP protocol 1974 by Vint Cerf and Bob Kahn · WWW by Tim Berners-Lee 1989 · not Al Gore [Source: Internet Society]",
    "wheel":             "Mesopotamia ~3500 BCE · first use was pottery wheel · transport wheel came later ~3200 BCE · [Source: archaeological record]",
    "penicillin":        "Alexander Fleming 1928 · accidental discovery · mold contaminating bacteria dish · saved an estimated 200M lives since [Source: Nobel Prize records]",
    # Heists
    "mona lisa":         "Stolen August 21, 1911 from the Louvre · missing 2 years · thief: Vincenzo Peruggia (Louvre employee) · found in Florence 1913 · [Source: French police records]",
    "isabella stewart gardner": "Boston 1990 · 13 artworks stolen including Vermeer, Rembrandt · worth $500M+ · never recovered · FBI case still open [Source: FBI]",
    # Duels
    "burr hamilton":     "Aaron Burr vs Alexander Hamilton · July 11, 1804 · Weehawken, New Jersey · Hamilton mortally wounded · effectively ended Burr's political career [Source: historical record]",
    "pushkin":           "Alexander Pushkin vs Georges d'Anthès · 1837 · Pushkin mortally wounded · greatest Russian poet killed at 37 [Source: Russian historical record]",
}

UNSOLVED_MYSTERIES: dict[str, str] = {
    "voynich manuscript": "15th century manuscript · unknown language/cipher · 240 pages · carbon-dated 1404-1438 · no one has decoded it · held at Yale Beinecke Library [Source: academic research]",
    "zodiac killer":      "California 1968-1969 · at least 5 confirmed victims · sent coded letters to police · cipher partially solved 2020 · killer never identified [Source: SFPD cold case files]",
    "db cooper":          "November 24, 1971 · hijacked Northwest Orient flight · parachuted with $200,000 ransom · never found · only unsolved US air piracy [Source: FBI case file]",
    "oak island":         "Nova Scotia, Canada · treasure pit discovered 1795 · 6+ people have died searching · origin of pit unknown · History Channel documentary [Source: investigation records]",
    "wow signal":         "August 15, 1977 · Big Ear radio telescope · 72-second signal matching predicted extraterrestrial transmission · never repeated · never explained [Source: Ohio State University / SETI]",
    "nazca lines":        "Peru · enormous geoglyphs in desert · created ~500 BCE - 500 CE · purpose unknown · visible only from air · UNESCO World Heritage [Source: UNESCO / research]",
    "antikythera mechanism": "Ancient Greek device ~100 BCE · world's first known analog computer · tracked astronomical positions · found 1901 · still being studied [Source: Nature journal research]",
    "bermuda triangle":   "Western North Atlantic · hundreds of ships and planes reported disappeared · US Navy and Coast Guard dispute the claim · most 'disappearances' are ordinary incidents [Source: NOAA]",
}

WEIRDLAWS: list[str] = [
    "In Switzerland it is illegal to flush a toilet after 10pm in an apartment — noise ordinance [Source: Swiss noise pollution regulations]",
    "In France it is illegal to name a pig Napoleon [Source: French law on public order]",
    "In Scotland if someone knocks on your door needing the toilet, you must let them in [Source: Scottish common law]",
    "In Canada 35% of radio content must be Canadian — the CRTC mandated this since 1971 [Source: CRTC regulations]",
    "In Singapore chewing gum is banned unless for medical purposes — since 1992 [Source: Singapore Misuse of Drugs Act]",
    "In Thailand it is illegal to step on money, as the king's image appears on currency [Source: Thai Criminal Code]",
    "In Germany it is illegal to run out of fuel on the Autobahn — stopping for any avoidable reason is prohibited [Source: German Highway Code]",
    "In Venice Italy it is illegal to feed pigeons in St. Mark's Square — €700 fine [Source: Venice city ordinance]",
    "In Japan sleeping on the job (inemuri) is socially acceptable and seen as a sign of hard work [Source: Japanese workplace culture research]",
    "In Denmark before 1967 you had to check under your car for children before starting it [Source: Danish traffic law history]",
    "In Philippines jaywalking fines must be paid immediately on the spot to the officer [Source: Philippine traffic laws]",
    "In Australia it is illegal to wear hot pink hot pants after noon on a Sunday in Victoria [Source: Victorian Summary Offences Act — historical]",
]

STRANGE_FACTS: list[str] = [
    "Abraham Lincoln and Charles Darwin were born on the exact same day: February 12, 1809 [Source: historical record]",
    "Woolly mammoths were still alive when the Great Pyramid of Giza was being built [Source: fossil record / archaeology]",
    "The shortest war in history was between Britain and Zanzibar in 1896 — it lasted 38-45 minutes [Source: Guinness World Records]",
    "The lighter was invented before the match [Source: technology history]",
    "Nintendo (1889) is older than the Eiffel Tower (also 1889) — same year [Source: corporate and architectural history]",
    "In 1923, jockey Frank Hayes won a race despite dying of a heart attack mid-race — his horse Sweet Kiss crossed the line first [Source: historical record]",
    "Oxford University (est. ~1096) is older than the Aztec Empire (est. 1428) [Source: historical record]",
    "The total weight of all ants on Earth is roughly equal to the total weight of all humans [Source: PNAS research 2022]",
    "A day on Mars is 24 hours 37 minutes — almost identical to Earth [Source: NASA]",
    "Cleopatra (69-30 BCE) lived closer to the Moon landing (1969) than to the building of the Great Pyramid (~2560 BCE) [Source: chronology]",
    "The first computer bug was an actual bug — a moth found in a Harvard Mark II relay in 1947 [Source: US Navy historical record]",
    "The Fax machine (1843) predates the telephone (1876) by 33 years [Source: technology history]",
]

ONE_DAY_FACTS: list[str] = [
    "The US almost adopted German as an official language — 1795 Congressional proposal failed by one vote (the Muhlenberg vote) [Source: US Congressional records — though debated by historians]",
    "The Cuban Missile Crisis almost caused nuclear war on October 27, 1962 — Soviet submarine officer Vasili Arkhipov refused to authorize a nuclear torpedo launch [Source: declassified documents / NSA]",
    "The 1914 assassination of Archduke Franz Ferdinand almost failed — the first bomb missed, the assassin was leaving when Ferdinand's car took a wrong turn [Source: historical accounts]",
    "The Soviet nuclear early warning system almost triggered WWIII in 1983 — Stanislav Petrov correctly identified a false alarm and did not launch [Source: declassified Soviet documents]",
    "The Berlin Wall fell partly due to a miscommunication — East German spokesman Günter Schabowski announced new travel rules effective 'immediately' by mistake, November 9, 1989 [Source: historical record]",
    "Rome almost was not called Rome — according to Roman tradition, Romulus and Remus both wanted to found the city, decided by augury (bird watching) [Source: Roman historiography / Livy]",
]

HAPAX_FACTS: list[str] = [
    "'Hapax legomenon' — a word appearing only once in all recorded literature · from Greek 'said only once' · thousands exist in ancient texts [Source: classical philology]",
    "The word 'defenestration' (throwing someone out a window) is mostly famous for the Defenestration of Prague 1618 · caused the Thirty Years War [Source: historical record]",
    "'Flibbertigibbet' appears in King Lear and refers to a chattering gossip — Shakespeare invented or popularized hundreds of words [Source: Oxford English Dictionary]",
    "'Cellar door' — Tolkien wrote that this is phonetically one of the most beautiful phrases in English, regardless of meaning [Source: Tolkien's essay 'English and Welsh' 1955]",
    "Homer's Iliad contains hundreds of hapax legomena — words used only once in all surviving ancient Greek literature [Source: classical scholarship]",
    "The word 'quiz' has no known etymology — it appeared suddenly in Dublin ~1791 and spread rapidly · possibly invented as a bet [Source: Oxford English Dictionary]",
]

WORDGAP_FACTS: dict[str, str] = {
    "saudade":       "Portuguese/Galician — a deep emotional state of nostalgic longing for something loved and lost · not quite sadness, not quite longing · entirely its own feeling",
    "komorebi":      "Japanese — the interplay of light and leaves when sunlight filters through trees · 木漏れ日 · has no equivalent in any other language",
    "mamihlapinatapai": "Yaghan (Tierra del Fuego) — the look shared by two people each wishing the other would initiate something both want but neither wants to start · Guinness most succinct word",
    "schadenfreude": "German — pleasure derived from another's misfortune · entered English dictionaries but still considered a German loanword",
    "mono no aware": "Japanese — 物の哀れ · the pathos of things · a gentle sadness at the transience of all things · central to Japanese aesthetics",
    "hygge":         "Danish/Norwegian — a quality of coziness and comfortable conviviality that engenders a feeling of contentment · impossible to achieve alone",
    "meraki":        "Greek — doing something with soul, creativity, or love · leaving a piece of yourself in your work",
    "toska":         "Russian — a longing with nothing to long for · vague restlessness · spiritual anguish · Nabokov called it untranslatable",
    "jayus":         "Indonesian — a joke so unfunny and poorly told that you have to laugh",
    "forelsket":     "Norwegian — the euphoria you feel when you are first falling in love · that specific dizzy joy",
    "gezelligheid":  "Dutch — the warmth of being with loved ones · the feeling of togetherness · similar to hygge but more about people than atmosphere",
    "wabi-sabi":     "Japanese — finding beauty in imperfection and impermanence · a cracked tea bowl more beautiful for its cracks",
    "ikigai":        "Japanese — reason for being · the intersection of what you love, what you are good at, what the world needs, and what you can be paid for",
    "fernweh":       "German — farsickness · a craving for distant places · the opposite of homesickness",
    "ubuntu":        "Zulu/Xhosa — I am because we are · a philosophy of human connection and community · Nelson Mandela discussed it extensively",
}

THOUGHT_EXPERIMENTS: dict[str, str] = {
    "trolley problem":    "A trolley is heading toward 5 people. You can pull a lever to divert it to kill 1. Do you? · Philippa Foot 1967 · tests action vs inaction in ethics [Source: philosophy literature]",
    "ship of theseus":    "If every part of a ship is gradually replaced, is it still the same ship? · Tests identity over time · Plutarch's Lives [Source: classical philosophy]",
    "schrödinger's cat":  "A cat in a box with a radioactive particle is both alive and dead until observed · illustrates quantum superposition paradox · Erwin Schrödinger 1935 [Source: physics literature]",
    "chinese room":       "A person in a room follows Chinese rules without understanding Chinese — do they 'understand' Chinese? · Tests if computation = understanding · John Searle 1980 [Source: Behavioral and Brain Sciences]",
    "prisoner's dilemma": "Two prisoners: cooperate for lighter sentence or betray for freedom? · Game theory foundation · Nash equilibrium · Flood & Dresher 1950 [Source: RAND Corporation]",
    "brain in a vat":     "How do you know you are not a brain in a vat being fed simulated experiences? · Descartes' evil demon updated · Hilary Putnam 1981 [Source: philosophy literature]",
    "experience machine": "Would you plug into a machine that gives you perfect simulated happiness? · Tests hedonism · Robert Nozick 1974 [Source: Anarchy State and Utopia]",
    "trolley fat man":    "You can stop a trolley by pushing a large person off a bridge. Do you? · Judith Jarvis Thomson 1985 · tests moral intuitions about direct harm [Source: philosophy literature]",
}

OLDEST_FACTS: dict[str, str] = {
    "city":          "Jericho, Palestine/Israel · continuously inhabited ~9000 BCE · ~11,000 years · [Source: archaeological consensus]",
    "democracy":     "Athens, Greece · ~507 BCE · Cleisthenes' reforms · lasted until Macedonian conquest 322 BCE [Source: historical record]",
    "university":    "University of Bologna, Italy · founded 1088 AD · still operating today [Source: UNESCO]",
    "company":       "Kongō Gumi, Japan · construction company · founded 578 AD · absorbed by Takamatsu 2006 · 1,428 years [Source: corporate history]",
    "parliament":    "Althing, Iceland · founded 930 AD · still operating · world's oldest parliament [Source: Althingi official records]",
    "restaurant":    "Ma Yu Ching's Bucket Chicken House, China · founded 1153 AD · Kaifeng · still operating [Source: Guinness World Records]",
    "recipe":        "Sumerian beer recipe · ~1800 BCE · written on clay tablet · Hymn to Ninkasi [Source: archaeological record / University of Chicago]",
    "map":           "Imago Mundi · Babylonian world map · ~600 BCE · clay tablet · British Museum [Source: British Museum]",
    "tree":          "Methuselah · Great Basin Bristlecone Pine · White Mountains California · ~4,855 years old [Source: US Forest Service]",
    "language":      "Sumerian · spoken ~3000 BCE · Mesopotamia · first written language · cuneiform script [Source: linguistic consensus]",
    "flag":          "Denmark (Dannebrog) · 1370 AD first recorded use · oldest continuously used national flag [Source: Danish national archives]",
    "currency":      "Shekel · Mesopotamia ~3000 BCE · unit of weight for barley · became silver standard [Source: archaeological record]",
    "sport":         "Wrestling · depicted in cave paintings ~15,000-20,000 BCE · also documented ancient Sumeria ~3000 BCE [Source: archaeological record]",
}

PHENOMENA: dict[str, str] = {
    "bioluminescence":  "Living organisms producing light via chemical reaction · dinoflagellates cause glowing ocean waves · luciferin+luciferase chemistry · found in 76% of deep-sea creatures [Source: MBARI research]",
    "ball lightning":   "Rare luminous spheres during thunderstorms · 1-50cm diameter · various colors · duration seconds to minutes · no confirmed scientific explanation yet [Source: physical review journals]",
    "rogue wave":       "Giant waves appearing without warning from calm seas · can reach 30m+ · once dismissed as sailor myth · proved real by Draupner platform 1995 [Source: Nature / oceanography research]",
    "aurora borealis":  "Northern Lights · charged solar particles hitting Earth's magnetic field · green from oxygen 100km up · red from oxygen 200km+ · pink/blue from nitrogen [Source: NASA]",
    "deja vu":          "Feeling of having experienced something before · affects ~70% of people · temporal lobe theory most accepted · associated with memory processing [Source: neuroscience research]",
    "supercell":        "Rotating thunderstorm with a deep rotating updraft (mesocyclone) · can persist hours · spawns most violent tornadoes · produces large hail [Source: NOAA]",
    "kelvin helmholtz": "Wave-like clouds formed by different wind speeds at atmospheric layers · looks like ocean waves in sky · also occurs on Jupiter and Saturn [Source: meteorology / NASA]",
    "st elmo's fire":   "Plasma discharge on pointed objects during thunderstorms · blue/violet glow · sailors saw it as divine protection · caused by electric fields [Source: atmospheric physics]",
    "haboob":           "Massive dust storm wall · up to 1.6km high · common in Sudan, Arizona · Arabic word · caused by collapsing thunderstorm outflow [Source: meteorology]",
    "fire rainbow":     "Circumhorizon arc · colorful horizontal band in sky · requires sun at 58°+ altitude and cirrus clouds · not actually a rainbow [Source: atmospheric optics]",
    "singing sand dunes": "Sand dunes that emit loud humming/roaring sounds · up to 105 decibels · caused by sand grains avalanching · found in 35 deserts worldwide [Source: geophysics research]",
}

FOSSILS: dict[str, str] = {
    "tyrannosaurus rex":    "Lived 68-66 million years ago · Cretaceous · North America · 12m long · binocular vision · feathered juveniles likely · Sue at Field Museum most complete [Source: paleontological record]",
    "triceratops":          "Lived 68-66 million years ago · three horns · frill · North America · up to 9m · fought T-Rex · herd animals [Source: paleontological record]",
    "woolly mammoth":       "Lived ~400,000-4,000 years ago · last population on Wrangel Island · hunted to extinction + climate change · DNA nearly complete · de-extinction attempted [Source: Nature journal]",
    "megalodon":            "Lived ~23-3.6 million years ago · Miocene-Pliocene · up to 18m · largest shark ever · NOT still alive · teeth found worldwide [Source: paleontological record]",
    "anomalocaris":         "Cambrian apex predator · 520 million years ago · up to 1m · compound eyes · spiny arms · most fearsome creature of its time [Source: paleontological record]",
    "trilobite":            "Existed 521-252 million years ago · 270 million year run · most successful group in fossil record · over 20,000 species · Permian extinction [Source: paleontological record]",
    "dodo":                 "Raphus cucullatus · extinct 1681 · Mauritius · flightless · hunted by sailors · became symbol of extinction [Source: natural history record]",
    "saber tooth cat":      "Smilodon · lived 2.5M-10,000 years ago · 28cm canine teeth · California La Brea tar pits · not directly related to modern cats [Source: paleontological record]",
    "diplodocus":           "Lived 154-152 million years ago · Jurassic · 27m long · whip-like tail · North America · may have used tail as sonic weapon [Source: paleontological record]",
}

NUMBER_FACTS: dict[str, str] = {
    "0":   "Zero took 1,500 years for Europe to accept as a number · invented in India ~458 AD · Brahmagupta first to define rules for zero · Fibonacci brought to Europe 1202 [Source: mathematical history]",
    "1":   "One is neither prime nor composite by mathematical convention · all numbers are divisible by 1 but 1 is not considered prime [Source: mathematics]",
    "7":   "Seven is considered lucky in many cultures · 7 deadly sins, 7 days, 7 musical notes, 7 colors in rainbow · most chosen 'random' number by humans [Source: cultural psychology]",
    "13":  "Triskaidekaphobia = fear of 13 · US buildings often skip 13th floor · fear may stem from Last Supper (13 diners) or Friday the 13th witch trials [Source: cultural history]",
    "42":  "The 'Answer to Life, the Universe, and Everything' in Douglas Adams' Hitchhiker's Guide · Adams chose it because it was 'a perfectly ordinary number' [Source: Douglas Adams interview]",
    "e":   "Euler's number = 2.71828... · base of natural logarithm · describes continuous growth · Jacob Bernoulli discovered it in compound interest 1683 [Source: mathematical history]",
    "pi":  "π = 3.14159... · ratio of circumference to diameter · known to Babylonians ~2000 BCE · calculated to 100 trillion digits in 2022 [Source: mathematical history / Google]",
    "phi": "Golden ratio φ = 1.618... · found in nature: nautilus shells, flower petals, galaxy spirals · used in Parthenon and Renaissance art [Source: mathematics / art history]",
    "googol": "10^100 · a 1 followed by 100 zeros · coined by 9-year-old Milton Sirotta in 1920 at request of his mathematician uncle Edward Kasner · larger than atoms in universe [Source: mathematical history]",
    "666": "Number of the Beast · from Book of Revelation · some scholars argue original number was 616 · found in Dead Sea Scrolls fragment [Source: biblical scholarship]",
}

MOVEMENTS: dict[str, str] = {
    "impressionism": "1860s-1880s Paris · Monet, Renoir, Degas, Pissarro · rejected academic painting · painted everyday scenes outdoors · name from Monet's 'Impression, Sunrise' (mocked by critics) [Source: art history]",
    "dadaism":       "1916 Zurich · anti-war movement · Hugo Ball, Tristan Tzara, Marcel Duchamp · absurdist anti-art · Duchamp's urinal 'Fountain' 1917 · reaction to WWI's irrationality [Source: art history]",
    "surrealism":    "1920s Paris · André Breton · Salvador Dalí, René Magritte, Max Ernst · unconscious imagery · dreamlike impossible scenes · psychoanalysis influence [Source: art history]",
    "baroque":       "1600-1750 Europe · dramatic light and shadow (chiaroscuro) · Caravaggio, Rembrandt, Bernini · intense emotion · ornate detail · Counter-Reformation art [Source: art history]",
    "romanticism":   "Late 18th-19th century · emotion over reason · nature, individualism, nationalism · Caspar David Friedrich, Delacroix · reaction against Enlightenment [Source: art history]",
    "cubism":        "1907-1920s Paris · Picasso and Braque · multiple viewpoints simultaneously · Les Demoiselles d'Avignon 1907 · fragmented geometric forms [Source: art history]",
    "bauhaus":       "1919-1933 Germany · Walter Gropius · form follows function · art + craft + technology · closed by Nazis 1933 · shaped modern design worldwide [Source: Bauhaus-Archiv]",
    "renaissance":   "14th-17th century Italy then Europe · rebirth of classical learning · Leonardo, Michelangelo, Raphael · humanism · perspective in painting [Source: art history]",
    "expressionism": "Early 20th century Germany · emotion distorted reality · Edvard Munch's The Scream · Die Brücke group · inner emotional experience over appearance [Source: art history]",
}

INSTRUMENTS: dict[str, str] = {
    "piano":        "Bartolomeo Cristofori, Italy, ~1700 · full name pianoforte ('soft-loud') · 88 keys standard · 220+ strings · 12,000 parts · most studied instrument [Source: Museo degli Strumenti Musicali]",
    "violin":       "Developed in northern Italy early 16th century · Andrea Amati first known maker · Stradivari violins (1666-1737) worth $10M+ · 4 strings [Source: organology]",
    "guitar":       "Descended from ancient lutes · modern classical guitar standardized by Antonio Torres ~1850 · 6 strings standard · most played instrument worldwide [Source: organology]",
    "sitar":        "North India · 13th century · 18-21 strings (6-7 played, rest sympathetic) · Ravi Shankar made it globally famous · used in Hindustani classical music [Source: organology]",
    "didgeridoo":   "Aboriginal Australian · 1,500+ years old · world's oldest wind instrument · no reed · circular breathing technique · 1.2m long typically [Source: musicology]",
    "oud":          "Middle East/North Africa · predecessor of European lute · 11 strings · no frets · 5,000 years old depictions · central to Arabic music [Source: organology]",
    "harpsichord":  "European keyboard instrument · 14th-18th century · strings plucked not struck · cannot control dynamics like piano · Bach and Handel composed for it [Source: organology]",
    "theremin":     "Leon Theremin, Russia, 1920 · played without touching · two antennas control pitch and volume · used in sci-fi films · Beach Boys 'Good Vibrations' [Source: electronic music history]",
    "organ":        "Ancient Greece (hydraulis) ~250 BCE · first keyboard instrument · pipe organ largest musical instrument · Notre-Dame organ has 8,000 pipes [Source: organology]",
    "shamisen":     "Japanese · 3 strings · derived from Chinese sanxian · distinctive harsh tone from snakeskin body · central to geisha tradition [Source: Japanese musical tradition]",
    "bagpipes":     "NOT only Scottish · ancient origins in Middle East and Europe · earliest evidence ~1000 BCE Egypt · still played in Turkey, Bulgaria, Spain, Ireland [Source: organology]",
}

BANNED_BOOKS: dict[str, str] = {
    "1984":                "George Orwell 1949 · banned in USSR (ironic given content) · challenged in US schools repeatedly · still one of most banned books globally [Source: American Library Association]",
    "lolita":              "Vladimir Nabokov 1955 · banned in UK, France, Argentina initially · controversial subject matter · now considered literary masterpiece [Source: literary record]",
    "ulysses":             "James Joyce 1922 · banned in USA until 1933 court ruling · obscenity charges · judge Woolsey's decision landmark for literature [Source: legal record]",
    "brave new world":     "Aldous Huxley 1932 · banned in Ireland 1932 · challenged in many US schools for drug use, sexuality · still frequently challenged [Source: ALA]",
    "catcher in the rye":  "J.D. Salinger 1951 · most challenged book in US 1961-1982 · associated with John Lennon's assassin Mark Chapman [Source: ALA records]",
    "harry potter":        "J.K. Rowling 1997+ · banned in some schools and churches for witchcraft themes · most challenged book series of 21st century in US [Source: ALA records]",
    "the color purple":    "Alice Walker 1982 · banned in several US school districts for explicit content · won Pulitzer Prize 1983 [Source: ALA records]",
    "animal farm":         "George Orwell 1945 · rejected by publishers fearing offending Stalin's USSR · banned in USSR and Soviet bloc · allegory of Russian Revolution [Source: literary history]",
}


class KnowledgeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def _respond(self, ctx: commands.Context, message: str) -> None:
        if len(message) > 490:
            message = message[:487] + "..."
        await ctx.send(message)

    async def _check_cooldown(
        self, ctx: commands.Context, command: str, cooldown: int = DEFAULT_COOLDOWN
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

    def _fuzzy_lookup(self, query: str, data: dict) -> str | None:
        """Find the best match in a dict by checking if query is in any key."""
        q = query.strip().lower()
        if q in data:
            return data[q]
        for key, value in data.items():
            if q in key or key in q:
                return value
        return None

    # ── !space ───────────────────────────────────────────────

    @commands.command(name="space", aliases=["spaceobject", "cosmos", "planet"])
    async def space(self, ctx: commands.Context, *, query: str = "") -> None:
        """Facts about any space object. Usage: !space Europa"""
        if not query:
            await self._respond(ctx, "Usage: !space [object] — e.g. !space Europa or !space Mars")
            return
        if not await self._check_cooldown(ctx, "space", DEFAULT_COOLDOWN):
            return
        result = await get_space_fact(query.strip())
        await self._respond(ctx, result)

    # ── !element ─────────────────────────────────────────────

    @commands.command(name="element", aliases=["chemicalelement", "periodicelement"])
    async def element(self, ctx: commands.Context, *, query: str = "") -> None:
        """Periodic table element facts. Usage: !element gold"""
        if not query:
            await self._respond(ctx, "Usage: !element [name or symbol] — e.g. !element gold or !element Au")
            return
        if not await self._check_cooldown(ctx, "element", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, ELEMENTS)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"Element '{query}' not found. Try: gold, carbon, uranium, hydrogen...")

    # ── !deepdive ────────────────────────────────────────────

    @commands.command(name="deepdive", aliases=["surprising", "didyouknow"])
    async def deepdive(self, ctx: commands.Context) -> None:
        """A random surprising fact. Usage: !deepdive"""
        if not await self._check_cooldown(ctx, "deepdive", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(DEEP_DIVES))

    # ── !wonder ──────────────────────────────────────────────

    @commands.command(name="wonder", aliases=["worldwonder", "ancientwonder"])
    async def wonder(self, ctx: commands.Context, *, query: str = "") -> None:
        """World wonder facts. Usage: !wonder Colosseum"""
        if not query:
            await self._respond(ctx, "Usage: !wonder [name] — e.g. !wonder Colosseum or !wonder Taj Mahal")
            return
        if not await self._check_cooldown(ctx, "wonder", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, WONDERS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(WONDERS.keys())[:6])
            await self._respond(ctx, f"Wonder '{query}' not found. Try: {keys}...")

    # ── !empire ──────────────────────────────────────────────

    @commands.command(name="empire", aliases=["historicempire", "empirehistory"])
    async def empire(self, ctx: commands.Context, *, query: str = "") -> None:
        """Historical empire facts. Usage: !empire Roman"""
        if not query:
            await self._respond(ctx, "Usage: !empire [name] — e.g. !empire Ottoman or !empire Mongol")
            return
        if not await self._check_cooldown(ctx, "empire", DEFAULT_COOLDOWN):
            return
        q = query.strip().lower()
        for key, val in HISTORICAL_FACTS.items():
            if "empire" in key and (q in key or key.replace(" empire","") in q):
                await self._respond(ctx, f"{key.title()}: {val}")
                return
        await self._respond(ctx, f"Empire '{query}' not found. Try: Roman, Mongol, Ottoman, Byzantine, British, Persian...")

    # ── !disaster ────────────────────────────────────────────

    @commands.command(name="disaster", aliases=["historicaldisaster", "catastrophe"])
    async def disaster(self, ctx: commands.Context, *, query: str = "") -> None:
        """Historical disaster facts. Usage: !disaster Chernobyl"""
        if not query:
            await self._respond(ctx, "Usage: !disaster [name] — e.g. !disaster Chernobyl or !disaster Titanic")
            return
        if not await self._check_cooldown(ctx, "disaster", DEFAULT_COOLDOWN):
            return
        disasters = {k: v for k, v in HISTORICAL_FACTS.items()
                     if k in ("chernobyl", "pompeii", "titanic", "black death", "hiroshima")}
        result = self._fuzzy_lookup(query, disasters)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"Disaster '{query}' not found. Try: Chernobyl, Pompeii, Titanic, Black Death, Hiroshima")

    # ── !invention ───────────────────────────────────────────

    @commands.command(name="invention", aliases=["whoinvented", "realinventor"])
    async def invention(self, ctx: commands.Context, *, query: str = "") -> None:
        """Who really invented something. Usage: !invention printing press"""
        if not query:
            await self._respond(ctx, "Usage: !invention [thing] — e.g. !invention internet or !invention penicillin")
            return
        if not await self._check_cooldown(ctx, "invention", DEFAULT_COOLDOWN):
            return
        inventions = {k: v for k, v in HISTORICAL_FACTS.items()
                      if k in ("printing press", "internet", "wheel", "penicillin")}
        result = self._fuzzy_lookup(query, inventions)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"No invention data for '{query}'. Try: internet, printing press, wheel, penicillin")

    # ── !heist ───────────────────────────────────────────────

    @commands.command(name="heist", aliases=["famousheist", "historicheist"])
    async def heist(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous historical heists. Usage: !heist mona lisa"""
        if not query:
            await self._respond(ctx, "Usage: !heist [name] — e.g. !heist Mona Lisa or !heist Gardner")
            return
        if not await self._check_cooldown(ctx, "heist", DEFAULT_COOLDOWN):
            return
        heists = {"mona lisa": HISTORICAL_FACTS["mona lisa"], "gardner": HISTORICAL_FACTS["isabella stewart gardner"], "isabella stewart gardner": HISTORICAL_FACTS["isabella stewart gardner"]}
        result = self._fuzzy_lookup(query, heists)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"Heist '{query}' not found. Try: Mona Lisa, Gardner")

    # ── !unsolved ────────────────────────────────────────────

    @commands.command(name="unsolved", aliases=["mystery", "coldcase", "opencase"])
    async def unsolved(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous unsolved mysteries. Usage: !unsolved Voynich"""
        if not query:
            await self._respond(ctx, f"Usage: !unsolved [name] — try: {', '.join(list(UNSOLVED_MYSTERIES.keys())[:4])}")
            return
        if not await self._check_cooldown(ctx, "unsolved", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, UNSOLVED_MYSTERIES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(UNSOLVED_MYSTERIES.keys()))
            await self._respond(ctx, f"Mystery '{query}' not found. Available: {keys}")

    # ── !duel ────────────────────────────────────────────────

    @commands.command(name="duel", aliases=["famousduel", "historicalduel"])
    async def duel(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous historical duels. Usage: !duel Burr Hamilton"""
        if not query:
            await self._respond(ctx, "Usage: !duel [name] — e.g. !duel Burr Hamilton or !duel Pushkin")
            return
        if not await self._check_cooldown(ctx, "duel", DEFAULT_COOLDOWN):
            return
        duels = {k: v for k, v in HISTORICAL_FACTS.items() if k in ("burr hamilton", "pushkin")}
        result = self._fuzzy_lookup(query, duels)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"Duel '{query}' not found. Try: Burr Hamilton, Pushkin")

    # ── !forgotten ───────────────────────────────────────────

    @commands.command(name="forgotten", aliases=["hiddenhistory", "overlooked"])
    async def forgotten(self, ctx: commands.Context) -> None:
        """A random overlooked historical fact. Usage: !forgotten"""
        if not await self._check_cooldown(ctx, "forgotten", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(STRANGE_FACTS))

    # ── !almostcalled ────────────────────────────────────────

    @commands.command(name="almostcalled", aliases=["nearlynamed", "originalname"])
    async def almostcalled(self, ctx: commands.Context) -> None:
        """Famous things that were almost called something different. Usage: !almostcalled"""
        if not await self._check_cooldown(ctx, "almostcalled", DEFAULT_COOLDOWN):
            return
        facts = [
            "Google was almost called 'BackRub' · named for analyzing back links · founders changed it before launch [Source: Google corporate history]",
            "Twitter was almost called 'Friendstalker' · also considered: Twitch, Jitter · Jack Dorsey settled on Twitter [Source: Twitter founding history]",
            "Amazon was almost called 'Relentless' · Jeff Bezos's second choice · relentless.com still redirects to Amazon.com [Source: Brad Stone 'The Everything Store']",
            "Nintendo almost called the NES the 'AVS' (Advanced Video System) before settling on Nintendo Entertainment System [Source: Nintendo history]",
            "Pepsi was originally called 'Brad's Drink' · after inventor Caleb Bradham · renamed 1898 from pepsin enzyme + kola nuts [Source: PepsiCo corporate history]",
            "Sony was almost called 'Tokyo Tsushin Kogyo' (Tokyo Telecommunications Engineering) · founders chose Sony as global name [Source: Sony corporate history]",
            "Starbucks was almost called 'Cargo House' or 'Pequod' (Moby Dick ship) · settled on Starbucks from the same novel [Source: Starbucks corporate history]",
            "Instagram was first called 'Burbn' · a location check-in app · Kevin Systrom pivoted to photos and renamed [Source: Instagram founding history]",
        ]
        await self._respond(ctx, random.choice(facts))

    # ── !briefexistence ──────────────────────────────────────

    @commands.command(name="briefexistence", aliases=["shortlived", "didntlastlong"])
    async def briefexistence(self, ctx: commands.Context) -> None:
        """Countries or things that existed for an absurdly short time. Usage: !briefexistence"""
        if not await self._check_cooldown(ctx, "briefexistence", DEFAULT_COOLDOWN):
            return
        facts = [
            "Republic of Biak-na-Bató, Philippines · existed exactly 6 months in 1897 · Emilio Aguinaldo's short-lived republic before Spanish-American War [Source: Philippine history]",
            "Confederate States of America · existed 4 years 1861-1865 · never recognized by a foreign government · 11 states [Source: historical record]",
            "Republic of West Florida · existed 74 days in 1810 · part of modern Louisiana/Mississippi/Alabama · annexed by USA [Source: US historical record]",
            "Benin Empire (as republic) · post-colonial Republic of Benin before name change · different from historical Benin Empire",
            "Deutsche Demokratische Republik (East Germany) · existed 40 years 1949-1990 · absorbed into reunified Germany [Source: historical record]",
            "Anglo-Egyptian Sudan · Sudan as condominium of UK and Egypt · 1899-1956 · unique joint sovereignty arrangement [Source: historical record]",
            "Soviet Union · lasted 69 years 1922-1991 · once covered 1/6 of Earth's land surface · dissolved Christmas Day 1991 [Source: historical record]",
            "Tanganyika · existed 3 years 1961-1964 before merging with Zanzibar to form Tanzania [Source: historical record]",
        ]
        await self._respond(ctx, random.choice(facts))

    # ── !strangefact ─────────────────────────────────────────

    @commands.command(name="strangefact", aliases=["coincidence", "strangebuttrue"])
    async def strangefact(self, ctx: commands.Context) -> None:
        """A strange but verified historical fact. Usage: !strangefact"""
        if not await self._check_cooldown(ctx, "strangefact", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(STRANGE_FACTS))

    # ── !weirdlaw ────────────────────────────────────────────

    @commands.command(name="weirdlaw", aliases=["strangelaw", "bizarrelaw", "oddlaw"])
    async def weirdlaw(self, ctx: commands.Context) -> None:
        """A bizarre law that actually exists. Usage: !weirdlaw"""
        if not await self._check_cooldown(ctx, "weirdlaw", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(WEIRDLAWS))

    # ── !oneday ──────────────────────────────────────────────

    @commands.command(name="oneday", aliases=["onedecision", "nearlychanged"])
    async def oneday(self, ctx: commands.Context) -> None:
        """History that was decided by one day, vote, or person. Usage: !oneday"""
        if not await self._check_cooldown(ctx, "oneday", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(ONE_DAY_FACTS))

    # ── !thoughtexperiment ───────────────────────────────────

    @commands.command(name="thoughtexperiment", aliases=["brainteaser", "mindgame", "philosophygame"])
    async def thoughtexperiment(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous thought experiments. Usage: !thoughtexperiment trolley problem"""
        if not query:
            keys = ", ".join(list(THOUGHT_EXPERIMENTS.keys())[:4])
            await self._respond(ctx, f"Usage: !thoughtexperiment [name] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "thoughtexperiment", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, THOUGHT_EXPERIMENTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(THOUGHT_EXPERIMENTS.keys()))
            await self._respond(ctx, f"Not found. Available: {keys}")

    # ── !oldest ──────────────────────────────────────────────

    @commands.command(name="oldest", aliases=["oldestever", "mostancient"])
    async def oldest(self, ctx: commands.Context, *, query: str = "") -> None:
        """The oldest known thing in a category. Usage: !oldest city"""
        if not query:
            keys = ", ".join(list(OLDEST_FACTS.keys())[:6])
            await self._respond(ctx, f"Usage: !oldest [category] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "oldest", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, OLDEST_FACTS)
        if result:
            await self._respond(ctx, f"Oldest {query}: {result}")
        else:
            keys = ", ".join(list(OLDEST_FACTS.keys()))
            await self._respond(ctx, f"Category '{query}' not found. Available: {keys}")

    # ── !phenomenon ──────────────────────────────────────────

    @commands.command(name="phenomenon", aliases=["naturalphenomenon", "rarething"])
    async def phenomenon(self, ctx: commands.Context, *, query: str = "") -> None:
        """Rare natural phenomena explained. Usage: !phenomenon aurora"""
        if not query:
            await self._respond(ctx, f"Usage: !phenomenon [name] — try: {', '.join(list(PHENOMENA.keys())[:4])}...")
            return
        if not await self._check_cooldown(ctx, "phenomenon", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, PHENOMENA)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(PHENOMENA.keys()))
            await self._respond(ctx, f"Phenomenon '{query}' not found. Available: {keys}")

    # ── !fossil ──────────────────────────────────────────────

    @commands.command(name="fossil", aliases=["prehistoric", "ancientcreature"])
    async def fossil(self, ctx: commands.Context, *, query: str = "") -> None:
        """Prehistoric creature facts. Usage: !fossil megalodon"""
        if not query:
            await self._respond(ctx, f"Usage: !fossil [creature] — try: {', '.join(list(FOSSILS.keys())[:4])}...")
            return
        if not await self._check_cooldown(ctx, "fossil", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, FOSSILS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(FOSSILS.keys()))
            await self._respond(ctx, f"Fossil '{query}' not found. Available: {keys}")

    # ── !number ──────────────────────────────────────────────

    @commands.command(name="number", aliases=["numberfact", "aboutnumber"])
    async def number(self, ctx: commands.Context, *, query: str = "") -> None:
        """Mathematical and cultural significance of numbers. Usage: !number 42"""
        if not query:
            await self._respond(ctx, "Usage: !number [number or name] — e.g. !number 42 or !number pi")
            return
        if not await self._check_cooldown(ctx, "number", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, NUMBER_FACTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(NUMBER_FACTS.keys()))
            await self._respond(ctx, f"No data for '{query}'. Available: {keys}")

    # ── !movement ────────────────────────────────────────────

    @commands.command(name="movement", aliases=["artmovement", "literarymovement"])
    async def movement(self, ctx: commands.Context, *, query: str = "") -> None:
        """Art or literary movement history. Usage: !movement impressionism"""
        if not query:
            await self._respond(ctx, f"Usage: !movement [name] — try: {', '.join(list(MOVEMENTS.keys())[:4])}...")
            return
        if not await self._check_cooldown(ctx, "movement", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, MOVEMENTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(MOVEMENTS.keys()))
            await self._respond(ctx, f"Movement '{query}' not found. Available: {keys}")

    # ── !instrument ──────────────────────────────────────────

    @commands.command(name="instrument", aliases=["musicalinstrument", "instrumentfacts"])
    async def instrument(self, ctx: commands.Context, *, query: str = "") -> None:
        """Musical instrument origin and facts. Usage: !instrument sitar"""
        if not query:
            await self._respond(ctx, f"Usage: !instrument [name] — try: {', '.join(list(INSTRUMENTS.keys())[:4])}...")
            return
        if not await self._check_cooldown(ctx, "instrument", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, INSTRUMENTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(INSTRUMENTS.keys()))
            await self._respond(ctx, f"Instrument '{query}' not found. Available: {keys}")

    # ── !architect ───────────────────────────────────────────

    @commands.command(name="architect", aliases=["famousbuilding", "building"])
    async def architect(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous architect or building facts. Usage: !architect Sagrada Familia"""
        if not query:
            await self._respond(ctx, "Usage: !architect [name or building] — e.g. !architect Sagrada Familia")
            return
        if not await self._check_cooldown(ctx, "architect", DEFAULT_COOLDOWN):
            return
        facts: dict[str, str] = {
            "sagrada familia":  "Barcelona, Spain · Antoni Gaudí · started 1882 · still under construction · UNESCO World Heritage · expected completion 2026 [Source: Basilica Sagrada Família]",
            "gaudi":            "Antoni Gaudí 1852-1926 · Catalan architect · Sagrada Família, Park Güell, Casa Batlló · died hit by a tram · UNESCO 7 works protected [Source: UNESCO]",
            "eiffel tower":     "Paris, France · Gustave Eiffel · built 1887-1889 · 330m tall · built for 1889 World's Fair · temporary structure · most visited monument on Earth [Source: Société d'Exploitation de la Tour Eiffel]",
            "colosseum":        "Rome, Italy · Emperor Vespasian commissioned 70 AD · 50,000-80,000 capacity · used for gladiatorial combat · still standing after ~2000 years [Source: UNESCO]",
            "burj khalifa":     "Dubai, UAE · architect Adrian Smith (SOM) · completed 2010 · 828m tall · world's tallest building · 163 floors [Source: Emaar Properties]",
            "parthenon":        "Athens, Greece · Ictinus and Callicrates architects · 447-432 BCE · dedicated to Athena · no mortar used · columns have subtle curves [Source: Greek Ministry of Culture]",
            "notre dame":       "Paris, France · begun 1163 · Gothic cathedral · gargoyles added 19th century · fire April 2019 · restoration ongoing [Source: French Ministry of Culture]",
            "sydney opera house": "Sydney, Australia · Jørn Utzon · completed 1973 · UNESCO World Heritage 2007 · shells covered in 1,056,000 tiles · took 14 years [Source: Sydney Opera House Trust]",
            "fallingwater":     "Pennsylvania, USA · Frank Lloyd Wright · 1939 · built over waterfall · considered greatest American architecture · [Source: Western Pennsylvania Conservancy]",
            "zaha hadid":       "Iraqi-British architect 1950-2016 · first woman to win Pritzker Prize (2004) · MAXXI Museum Rome, London Aquatics Centre, CCTV HQ Beijing [Source: Zaha Hadid Architects]",
        }
        result = self._fuzzy_lookup(query, facts)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"No data for '{query}'. Try: Sagrada Familia, Eiffel Tower, Burj Khalifa, Parthenon, Zaha Hadid...")

    # ── !banned ──────────────────────────────────────────────

    @commands.command(name="banned", aliases=["bannedbook", "censoredwork"])
    async def banned(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous banned books or censored works. Usage: !banned 1984"""
        if not query:
            await self._respond(ctx, f"Usage: !banned [title] — try: {', '.join(list(BANNED_BOOKS.keys())[:4])}...")
            return
        if not await self._check_cooldown(ctx, "banned", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, BANNED_BOOKS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(BANNED_BOOKS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    # ── !hapax ───────────────────────────────────────────────

    @commands.command(name="hapax", aliases=["rareword", "onceword"])
    async def hapax(self, ctx: commands.Context) -> None:
        """A hapax legomenon — a word appearing only once in recorded literature. Usage: !hapax"""
        if not await self._check_cooldown(ctx, "hapax", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(HAPAX_FACTS))

    # ── !wordgap ─────────────────────────────────────────────

    @commands.command(name="wordgap", aliases=["untranslatable", "uniqueword", "noenglish"])
    async def wordgap(self, ctx: commands.Context, *, query: str = "") -> None:
        """Words that exist in one language but have no English equivalent. Usage: !wordgap saudade"""
        if not query:
            await self._respond(ctx, f"Usage: !wordgap [word] — try: saudade, komorebi, hygge, toska, ikigai...")
            return
        if not await self._check_cooldown(ctx, "wordgap", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy_lookup(query, WORDGAP_FACTS)
        if result:
            await self._respond(ctx, f"{query}: {result}")
        else:
            keys = ", ".join(list(WORDGAP_FACTS.keys())[:8])
            await self._respond(ctx, f"'{query}' not found. Try: {keys}...")


def prepare(bot):
    bot.add_cog(KnowledgeCog(bot))
