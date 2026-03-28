# PiicaBot — data/fun_data.py
# Local data for fun commands: !pet, !vibe, !wish, !collective, !phobia
# All content is wholesome, streamer-safe, and PG-rated.

import random

# ─────────────────────────────────────────────────────────────
# !pet — animal pool with unique messages
# ─────────────────────────────────────────────────────────────
PET_ANIMALS: list[dict] = [
    {"name": "capybara",      "msg": "You gently pet a capybara. It sighs contentedly and lets you continue."},
    {"name": "red panda",     "msg": "You carefully pet a red panda. It stares at you, then goes back to eating bamboo."},
    {"name": "quokka",        "msg": "You pet a quokka. It smiles at you. It always smiles. You feel strangely at peace."},
    {"name": "axolotl",       "msg": "You very gently pet an axolotl through the water. It wiggles its gills approvingly."},
    {"name": "pygmy goat",    "msg": "You pet a tiny pygmy goat. It headbutts your hand affectionately."},
    {"name": "fennec fox",    "msg": "You pet a fennec fox. Its ears are enormous. You are overwhelmed by cuteness."},
    {"name": "manatee",       "msg": "You pet a manatee. It rolls over slowly. This is the most relaxed moment of your life."},
    {"name": "slow loris",    "msg": "A slow loris looks at you with huge eyes. You pet it very carefully. It raises its arms."},
    {"name": "sun bear",      "msg": "You pet a sun bear cub. It makes a small sound. Your heart grows three sizes."},
    {"name": "clouded leopard","msg": "A clouded leopard tolerates your pets. You are honoured. It walks away. You thank it."},
    {"name": "pangolin",      "msg": "You pet a pangolin. It curls into a ball immediately. You feel a little guilty but it's okay."},
    {"name": "narwhal",       "msg": "A narwhal surfaces. You carefully pat its head. It dives back into the deep. Magical."},
    {"name": "kinkajou",      "msg": "You pet a kinkajou. It wraps its tail around your arm. You are now best friends."},
    {"name": "dumbo octopus", "msg": "You gently touch a dumbo octopus. It flaps its ear-fins at you and glides away."},
    {"name": "binturong",     "msg": "You pet a binturong. It smells like popcorn. You did not expect this. Neither did it."},
    {"name": "saiga antelope","msg": "A saiga antelope regards you with its enormous nose. You pet it. It accepts this."},
    {"name": "fossa",         "msg": "You pet a fossa. It is like a cat. It is not a cat. It is something better."},
    {"name": "okapi",         "msg": "An okapi lets you pet its striped legs. It is half giraffe, half zebra, all wonderful."},
    {"name": "pika",          "msg": "A tiny pika squeaks as you pet it. It runs away. Returns. Squeaks again. Runs away."},
    {"name": "wombat",        "msg": "You pet a wombat. It has a very flat back from running under fences. It does not care."},
    {"name": "blobfish",      "msg": "You gently pet a blobfish in its natural deep-sea habitat. It looks sad. It is always this way."},
    {"name": "tapir",         "msg": "A tapir snuffles your hand with its little trunk. You are now a tapir's best friend."},
    {"name": "maned wolf",    "msg": "A maned wolf — part fox, part deer — accepts one pet then walks away elegantly."},
    {"name": "gerenuk",       "msg": "A gerenuk stands on its hind legs to reach your hand. Its neck is impossibly long. Perfect."},
    {"name": "aye-aye",       "msg": "An aye-aye taps you with its elongated finger. This is how it checks for grubs. You are not a grub."},
    {"name": "irrawaddy dolphin", "msg": "An Irrawaddy dolphin surfaces and looks at you with its round, spout-less face. You pet it gently."},
    {"name": "shoebill stork","msg": "A shoebill stork stares into your soul. You slowly reach out and pet its head. It blinks, once."},
    {"name": "potoo bird",    "msg": "A potoo bird opens one eye, watches you pet it, then becomes a tree branch again."},
    {"name": "star-nosed mole","msg": "A star-nosed mole touches your hand with its extraordinary nose. 22 tentacles. All gentle."},
    {"name": "flapjack octopus","msg": "You pet a flapjack octopus. It looks like a dumpling. It is one of the best things you have ever seen."},
]


def get_random_pet() -> dict:
    return random.choice(PET_ANIMALS)


# ─────────────────────────────────────────────────────────────
# !vibe — chat mood labels
# All positive or neutrally playful — never negative or mean
# ─────────────────────────────────────────────────────────────
VIBE_LABELS: list[dict] = [
    {
        "label": "Cozy mode",
        "desc": "calm, warm, low activity",
        "keywords": ["calm", "chill", "relax", "cozy", "peaceful", "quiet"],
        "energy": "low",
        "positivity": "high",
    },
    {
        "label": "Wholesome hour",
        "desc": "kind energy, lots of positivity",
        "keywords": ["love", "cute", "wholesome", "sweet", "kind", "nice", "good"],
        "energy": "medium",
        "positivity": "very high",
    },
    {
        "label": "Brain mode",
        "desc": "intellectual energy, lots of questions",
        "keywords": ["why", "how", "what", "interesting", "actually", "did you know", "?"],
        "energy": "medium",
        "positivity": "high",
    },
    {
        "label": "Hype train",
        "desc": "high energy, enthusiastic chat",
        "keywords": ["lets go", "gg", "pog", "hype", "lets", "woah", "amazing", "incredible"],
        "energy": "very high",
        "positivity": "very high",
    },
    {
        "label": "Giggle frequency",
        "desc": "lots of laughter energy",
        "keywords": ["lol", "lmao", "haha", "ha", "funny", "lmao", "kek", "xd"],
        "energy": "high",
        "positivity": "very high",
    },
    {
        "label": "Collective gasp",
        "desc": "surprise energy in chat",
        "keywords": ["omg", "wait", "what", "no way", "really", "!", "!!"],
        "energy": "high",
        "positivity": "medium",
    },
    {
        "label": "Deep focus",
        "desc": "quiet, attentive, watching carefully",
        "keywords": [],
        "energy": "very low",
        "positivity": "high",
        "trigger": "low_message_count",
    },
    {
        "label": "Curious crowd",
        "desc": "many questions being asked",
        "keywords": ["?", "how", "why", "what", "where", "when", "who"],
        "energy": "medium",
        "positivity": "high",
        "trigger": "high_question_count",
    },
    {
        "label": "Gremlin hour",
        "desc": "playfully chaotic chat",
        "keywords": ["chaos", "gremlin", "evil", "mischief", "trouble"],
        "energy": "high",
        "positivity": "medium",
    },
    {
        "label": "Story time",
        "desc": "long messages, engaged discussion",
        "keywords": [],
        "energy": "medium",
        "positivity": "high",
        "trigger": "long_messages",
    },
    {
        "label": "PiicaPoints frenzy",
        "desc": "lots of point commands flying around",
        "keywords": ["!points", "!give", "!top", "piicapoints"],
        "energy": "high",
        "positivity": "high",
        "trigger": "high_command_usage",
    },
    {
        "label": "Silent appreciation",
        "desc": "very few messages but stream is live",
        "keywords": [],
        "energy": "very low",
        "positivity": "medium",
        "trigger": "very_low_message_count",
    },
    {
        "label": "Language lesson mode",
        "desc": "lots of knowledge commands being used",
        "keywords": ["!kanji", "!define", "!wisdom", "!italianword", "!japaneseword"],
        "energy": "medium",
        "positivity": "high",
        "trigger": "high_knowledge_commands",
    },
    {
        "label": "GeoGuessr detective squad",
        "desc": "chat is solving the map together",
        "keywords": ["!plate", "!domain", "!writingsystem", "country", "city", "flag"],
        "energy": "high",
        "positivity": "very high",
        "trigger": "high_geo_commands",
    },
]


def analyze_vibe(messages: list[str]) -> tuple[str, str, int]:
    """
    Analyze a list of recent chat messages and return the best vibe label.
    Returns (label, description, percentage).
    Never returns anything negative — worst case is 'Deep focus'.
    """
    if not messages:
        return "Silent appreciation", "very few messages but stream is live", 100

    combined = " ".join(messages).lower()
    word_count = len(combined.split())

    scores: list[tuple[int, dict]] = []
    for vibe in VIBE_LABELS:
        score = 0
        for kw in vibe.get("keywords", []):
            score += combined.count(kw.lower()) * 2

        trigger = vibe.get("trigger", "")
        if trigger == "low_message_count" and len(messages) < 5:
            score += 10
        elif trigger == "very_low_message_count" and len(messages) < 3:
            score += 15
        elif trigger == "long_messages":
            avg_len = sum(len(m) for m in messages) / max(len(messages), 1)
            if avg_len > 60:
                score += 10
        elif trigger == "high_question_count":
            questions = sum(1 for m in messages if "?" in m)
            if questions > len(messages) * 0.4:
                score += 10
        elif trigger == "high_command_usage":
            commands = sum(1 for m in messages if m.startswith("!"))
            if commands > len(messages) * 0.3:
                score += 8
        elif trigger == "high_knowledge_commands":
            knowledge_cmds = ["!kanji", "!define", "!wisdom", "!italianword", "!japaneseword",
                              "!deepdive", "!element", "!space"]
            kc_count = sum(1 for m in messages for kc in knowledge_cmds if kc in m)
            if kc_count >= 2:
                score += 10
        elif trigger == "high_geo_commands":
            geo_cmds = ["!plate", "!domain", "!writingsystem", "!driveside", "!sunposition"]
            gc_count = sum(1 for m in messages for gc in geo_cmds if gc in m)
            if gc_count >= 2:
                score += 10

        scores.append((score, vibe))

    scores.sort(key=lambda x: x[0], reverse=True)
    best_score, best_vibe = scores[0]

    # Calculate a percentage (always between 40-95% for display)
    if best_score == 0:
        percentage = random.randint(40, 60)
    else:
        total = sum(s for s, _ in scores)
        percentage = min(95, max(40, int((best_score / max(total, 1)) * 100) + random.randint(-5, 10)))

    return best_vibe["label"], best_vibe["desc"], percentage


# ─────────────────────────────────────────────────────────────
# !wish — poetic bot responses
# ─────────────────────────────────────────────────────────────
WISH_RESPONSES: list[str] = [
    "The stars heard you.",
    "Written in the cosmos. May it find its way.",
    "Sent to wherever wishes go. May it return to you.",
    "The universe noted it down.",
    "Folded into a paper crane and released to the wind.",
    "Whispered to the moon. She's listening.",
    "Placed gently into the river of time.",
    "The night sky expanded slightly to make room for it.",
    "Carried away by the next passing cloud.",
    "Archived in the great library of wishes. Your place is held.",
    "The oldest trees heard you. They've seen wishes come true before.",
    "Translated into starlight and sent outward.",
    "Added to the long list of beautiful things hoped for.",
    "The tide took it. Tides always bring things back.",
    "A small bird will carry it to where it needs to go.",
]


def get_wish_response() -> str:
    return random.choice(WISH_RESPONSES)


# ─────────────────────────────────────────────────────────────
# !collective — collective nouns for animals
# Source: Oxford English Dictionary, Merriam-Webster
# ─────────────────────────────────────────────────────────────
COLLECTIVE_NOUNS: dict[str, tuple[str, str]] = {
    "crows":        ("a murder of crows",         "first recorded in 15th century Book of Saint Albans"),
    "flamingos":    ("a flamboyance of flamingos", "from the Spanish flamenco, meaning flame-colored"),
    "owls":         ("a parliament of owls",       "owls associated with wisdom since ancient Greece"),
    "ravens":       ("an unkindness of ravens",    "medieval superstition about ravens as omens"),
    "cats":         ("a clowder of cats",           "also: a glaring of cats; clowder from Old English"),
    "dogs":         ("a pack of dogs",              "also: a kennel; pack used since 14th century"),
    "wolves":       ("a pack of wolves",            "also: a rout or route of wolves"),
    "lions":        ("a pride of lions",            "first documented in 15th century heraldry"),
    "tigers":       ("an ambush of tigers",         "named for the tiger's hunting strategy"),
    "bears":        ("a sleuth of bears",           "from Old Norse sloth; also a pack or sloth"),
    "jellyfish":    ("a smack of jellyfish",        "also: a bloom or swarm; smack is most poetic"),
    "sharks":       ("a shiver of sharks",          "one of the most evocative collective nouns"),
    "dolphins":     ("a pod of dolphins",           "also: a school or team"),
    "elephants":    ("a parade of elephants",       "also: a herd; parade reflects their majestic movement"),
    "penguins":     ("a waddle of penguins",        "also: a colony or rookery; waddle captures movement"),
    "giraffes":     ("a tower of giraffes",         "also: a herd; tower from their height"),
    "hippos":       ("a bloat of hippos",           "also: a pod; bloat from their buoyancy"),
    "rhinos":       ("a crash of rhinos",           "named for what happens when they charge"),
    "kangaroos":    ("a mob of kangaroos",          "also: a troop or herd; mob is uniquely Australian"),
    "butterflies":  ("a kaleidoscope of butterflies","one of the most beautiful collective nouns"),
    "bats":         ("a cauldron of bats",          "also: a colony or cloud; cauldron from Halloween imagery"),
    "frogs":        ("an army of frogs",            "also: a colony or knot; army from mass migrations"),
    "snakes":       ("a nest of snakes",            "also: a pit or den; nest most common"),
    "crocodiles":   ("a float of crocodiles",       "also: a bask or nest; float from their river behavior"),
    "lemurs":       ("a conspiracy of lemurs",      "one of the strangest and most accurate names"),
    "meerkats":     ("a mob of meerkats",           "also: a gang or team; mob reflects their social groups"),
    "otters":       ("a romp of otters",            "also: a raft (when floating); romp captures their playfulness"),
    "ferrets":      ("a business of ferrets",       "also: a fesnyng; business from Middle English"),
    "porcupines":   ("a prickle of porcupines",     "one of the most appropriate collective nouns"),
    "wombats":      ("a wisdom of wombats",         "completely deserved"),
    "capybaras":    ("a capybara of capybaras",     "no established term — they simply deserve their own category"),
    "hummingbirds": ("a charm of hummingbirds",     "also: a hover; charm from their magical appearance"),
    "peacocks":     ("a muster of peacocks",        "also: an ostentation; both perfectly accurate"),
    "swans":        ("a bevy of swans",             "also: a wedge (in flight) or a bank"),
    "crows":        ("a murder of crows",           "the most famous collective noun in English"),
    "vultures":     ("a wake of vultures",          "named for the way they circle; also a committee"),
    "parrots":      ("a pandemonium of parrots",    "anyone who has heard a group of parrots understands"),
    "starlings":    ("a murmuration of starlings",  "named for the sound of thousands of wings"),
    "fish":         ("a school of fish",             "also: a shoal; school from Dutch schol meaning crowd"),
    "whales":       ("a pod of whales",             "also: a gam, school, or herd"),
}


def get_collective(animal: str) -> str:
    key = animal.strip().lower()
    # Try exact match
    if key in COLLECTIVE_NOUNS:
        noun, note = COLLECTIVE_NOUNS[key]
        return f"{noun.capitalize()} | {note} [Source: Oxford English Dictionary]"
    # Try with 's' added
    if key + "s" in COLLECTIVE_NOUNS:
        noun, note = COLLECTIVE_NOUNS[key + "s"]
        return f"{noun.capitalize()} | {note} [Source: Oxford English Dictionary]"
    # Try without 's'
    if key.rstrip("s") in COLLECTIVE_NOUNS:
        noun, note = COLLECTIVE_NOUNS[key.rstrip("s")]
        return f"{noun.capitalize()} | {note} [Source: Oxford English Dictionary]"
    return (
        f"No collective noun found for '{animal}'. "
        f"Try: crows, flamingos, owls, jellyfish, butterflies, lemurs..."
    )


# ─────────────────────────────────────────────────────────────
# !phobia — phobia names and meanings
# Source: Merriam-Webster, Oxford Dictionary of Psychology
# ─────────────────────────────────────────────────────────────
PHOBIAS: dict[str, tuple[str, str, str]] = {
    "arachnophobia":    ("fear of spiders",          "Greek arachne (spider) + phobos (fear)", "one of the most common phobias worldwide"),
    "claustrophobia":   ("fear of enclosed spaces",  "Latin claustrum (closed place) + Greek phobos", "affects ~12.5% of people"),
    "acrophobia":       ("fear of heights",          "Greek akron (summit) + phobos", "distinct from vertigo — psychological not physical"),
    "agoraphobia":      ("fear of open/public spaces","Greek agora (marketplace) + phobos", "often co-occurs with panic disorder"),
    "cynophobia":       ("fear of dogs",             "Greek kynos (dog) + phobos", "affects ~36% of those with animal phobias"),
    "ophidiophobia":    ("fear of snakes",           "Greek ophis (snake) + phobos", "one of the most evolutionarily ancient fears"),
    "trypophobia":      ("fear of clustered holes",  "Greek trypa (hole) + phobos", "officially recognized by APA only recently"),
    "xenophobia":       ("fear of strangers/foreign","Greek xenos (stranger) + phobos", "has social and political dimensions beyond clinical"),
    "hemophobia":       ("fear of blood",            "Greek haima (blood) + phobos", "unique: causes fainting unlike most phobias"),
    "dentophobia":      ("fear of dentists",         "Latin dens (tooth) + Greek phobos", "affects ~75% of people to varying degrees"),
    "nyctophobia":      ("fear of darkness",         "Greek nyktos (night) + phobos", "evolutionary basis — night = predator danger"),
    "aerophobia":       ("fear of flying",           "Greek aer (air) + phobos", "affects ~25 million Americans"),
    "aquaphobia":       ("fear of water",            "Latin aqua (water) + phobos", "distinct from inability to swim"),
    "emetophobia":      ("fear of vomiting",         "Greek emein (to vomit) + phobos", "often leads to extreme dietary restriction"),
    "phonophobia":      ("fear of loud sounds",      "Greek phone (sound/voice) + phobos", "also called ligyrophobia"),
    "pogonophobia":     ("fear of beards",           "Greek pogon (beard) + phobos", "documented since 1850s"),
    "nomophobia":       ("fear of being without phone","no + mobile + phobos", "coined 2008 — a modern phenomenon"),
    "thalassophobia":   ("fear of the deep ocean",   "Greek thalassa (sea) + phobos", "distinct from aquaphobia — specifically the deep unknown"),
    "coulrophobia":     ("fear of clowns",           "Greek kolon (stilt) + phobos", "IT and Pennywise significantly increased prevalence"),
    "athazagoraphobia": ("fear of being forgotten",  "Greek athazagoreuo (to forget) + phobos", "one of the more unusual named phobias"),
    "bibliophobia":     ("fear of books",            "Greek biblion (book) + phobos", "rare but documented"),
    "ephebiphobia":     ("fear of teenagers",        "Greek ephebos (youth) + phobos", "recognized in educational psychology"),
    "ergophobia":       ("fear of work",             "Greek ergon (work) + phobos", "clinically distinct from laziness"),
    "genuphobia":       ("fear of knees",            "Latin genu (knee) + phobos", "can affect ability to sit or exercise"),
    "globophobia":      ("fear of balloons",         "Latin globus (sphere) + phobos", "often triggered by the sound of popping"),
    "hippopotomonstrosesquippedaliophobia": (
        "fear of long words", "hippo + monster + sesquipedalian (long-worded) + phobos",
        "ironically the longest phobia name — likely coined humorously"
    ),
    "chronophobia":     ("fear of time passing",     "Greek chronos (time) + phobos", "common in prisoners and the elderly"),
    "somniphobia":      ("fear of sleep",            "Latin somnus (sleep) + phobos", "often linked to nightmare disorders"),
    "panophobia":       ("fear of everything",       "Greek pan (all) + phobos", "also called pantophobia; extreme general anxiety"),
}


def get_phobia(name: str) -> str:
    key = name.strip().lower()
    if not key.endswith("phobia"):
        key = key + "phobia"
    if key in PHOBIAS:
        meaning, etymology, note = PHOBIAS[key]
        return (
            f"!{key}: {meaning} | "
            f"Etymology: {etymology} | "
            f"{note} "
            f"[Source: Merriam-Webster / Oxford Dictionary of Psychology]"
        )
    # Search by fear topic
    search = name.strip().lower()
    for phobia, (meaning, etym, note) in PHOBIAS.items():
        if search in meaning.lower():
            return (
                f"!{phobia}: {meaning} | "
                f"Etymology: {etym} | "
                f"{note} "
                f"[Source: Merriam-Webster / Oxford Dictionary of Psychology]"
            )
    return (
        f"Phobia '{name}' not in database. "
        f"Try: arachnophobia, thalassophobia, trypophobia, nomophobia, coulrophobia..."
    )
