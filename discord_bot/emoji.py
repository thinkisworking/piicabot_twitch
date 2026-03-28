# PiicaBot — discord_bot/emoji.py
# Single source of truth for every emoji used across the bot.
# Import from here in ui.py and all command cogs.
# To change any emoji: edit here, change propagates everywhere.

# ─────────────────────────────────────────────────────────────
# DISCORD EMBED TITLES
# ─────────────────────────────────────────────────────────────
WELCOME         = "🪄"
LIVE            = "🔴"
OFFLINE         = "🌇"
POLL            = "📊"
POLL_BOT        = "🤖"
GIVEAWAY        = "ଘ(∩^o^)⊃━☆゜"
GIVEAWAY_WINNER = "🎈"
POINTS          = "🪙"
LEADERBOARD     = "🪙"
QUOTE           = "🧙‍♂️"
WISDOM          = "💎"
WISDOM_FOOTER   = "🕵️‍♀️"
PIICASAYS       = "🪄"
LINKTWITCH      = "🪄"
MILESTONE       = ""          # no emoji — clean title only
ERROR           = ""          # no emoji — red color speaks
SUCCESS         = ""          # no emoji — yellow speaks

# ─────────────────────────────────────────────────────────────
# KNOWLEDGE COMMANDS
# ─────────────────────────────────────────────────────────────
DEFINE          = "👨‍🏫"        # !define !wordorigin
ANCIENT         = "🪨"        # !wonder !empire !forgotten !almostcalled !briefexistence
OLDEST          = "🏛️"        # !oldest — shares 🏛️ with ARCHIVE (both are about old things)
HEIST           = "🗡️"        # !heist !duel !oneday
THOUGHT         = "⚛️"        # !thoughtexperiment !strangefact !number !weirdlaw
UNSOLVED        = "👩🏻‍🔬"      # !unsolved !phenomenon !deepdive — all three share scientist
ELEMENT         = "🧪"        # !element
SPACE           = "🪐"        # !space !planet
FOSSIL          = "🦕"        # !fossil
DISASTER        = "🌋"        # !disaster
ARCHIVE         = "🏛️"        # !hapax !oldestrecipe !oldest

# ─────────────────────────────────────────────────────────────
# GAMING COMMANDS
# ─────────────────────────────────────────────────────────────
AWARD           = "🎗️"        # !award
SALES           = "🛒"        # !sales
CONSOLE         = "🕹️"        # !console + !franchise !platforms !canceledgame !secret !lostgame !speedruntech
DEV             = "🧑‍💻"        # !studio !gameengine !indie !writtenby
FILM            = "🎥"        # !gameinfilm !gametoanime
COMPOSER        = "📀"        # !composer !iconictrack
VILLAIN         = "🦹🏼‍♀️"      # !villain !famousline !iconicscene
PROTAGONIST     = "🦸"        # !protagonist !sidekick
GAMEPAD         = "🕹️"        # alias of CONSOLE — same emoji group
WORLDRECORD     = "🏆"        # !worldrecord
PUZZLE          = "💥"        # !branchingstory !howhard !gamingmeme

# ─────────────────────────────────────────────────────────────
# GEOGUESSR COMMANDS
# ─────────────────────────────────────────────────────────────
GEO_MAP         = "🗺️"        # !driveside !domain !phonecode
GEO_ROAD        = "🚲"        # !streetcam !plate !roadsigns !roadlines !barriers !powerpoles
GEO_NATURE      = "🌿"        # !landscape !groundcolor
GEO_SUN         = "☀️"        # !sunposition !season
GEO_SCRIPT      = "🔤"        # !writingsystem

# ─────────────────────────────────────────────────────────────
# LANGUAGE COMMANDS
# ─────────────────────────────────────────────────────────────
JAPANESE        = "🇯🇵"        # all Japanese commands
ITALIAN         = "🇮🇹"        # all Italian commands
CROSSLANG       = "💬"        # !falsefriend !loanword !greeting !numbers
WORDGAP         = "🌀"        # !wordgap !untranslatable

# ─────────────────────────────────────────────────────────────
# COOKING COMMANDS
# ─────────────────────────────────────────────────────────────
DISH            = "🍱"        # !dish
FOOD_ORIGIN     = "🍲"        # !foodorigin
STREETFOOD      = "🍹"        # !streetfood !ingredient
ITALIAN_FOOD    = "🍷"        # !italianfood !pairing
FERMENTED       = "🍸"        # !fermented !technique
UMAMI           = "🤔"        # !umami
OLD_RECIPE      = "🏛️"        # !oldestrecipe — same as ARCHIVE

# ─────────────────────────────────────────────────────────────
# FUN COMMANDS
# ─────────────────────────────────────────────────────────────
PET             = "🐿️"        # !pet
WISH            = "🪄"        # !wish
WEIRD           = "🦆"        # !roll
SECRET          = "🐞"        # !secret !gamingmeme
VIBE            = "🌊"        # !vibe (calm wave energy)
COLLECTIVE      = "🐾"        # !collective
PHOBIA          = "😱"        # !phobia

# ─────────────────────────────────────────────────────────────
# ROTATING FOOTERS — never used as command prefixes
# ─────────────────────────────────────────────────────────────
FOOTERS = [
    "🐿️  PiicaBot · twitch.tv/majopiica",
    "🪄  PiicaBot · majopiica's companion",
    "🦭  PiicaBot · knowledge lives here",
    "🐬  PiicaBot · always watching",
    "🪙  PiicaBot · at your service",
    "🐝  PiicaBot · gathering knowledge",
    "🐧  PiicaBot · deep in the archive",
    "🦆  PiicaBot · something unexpected",
    "🐞  PiicaBot · finding the secrets",
]
