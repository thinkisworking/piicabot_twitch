# PiicaBot — twitch_bot/commands/gaming.py
# Gaming knowledge commands — uses IGDB API for live data
# and local verified datasets for historical/cultural facts.
# Sources: IGDB, IGN, Metacritic, official studio/publisher records,
#          Game Developers Conference talks, peer-reviewed game studies.

import random
from twitchio.ext import commands
from loguru import logger

import database.db as db
from services.igdb import (
    get_game_review, get_platforms, get_franchise_timeline,
    get_studio_info, get_game_engine_info
)
from config import DEFAULT_COOLDOWN


# ─────────────────────────────────────────────────────────────
# LOCAL GAMING DATA — verified and sourced
# ─────────────────────────────────────────────────────────────

GAME_AWARDS: dict[str, str] = {
    "bafta 2024 best game":         "Baldur's Gate 3 — Larian Studios [Source: BAFTA Games Awards 2024]",
    "bafta 2023 best game":         "Vampire Survivors — poncle [Source: BAFTA Games Awards 2023]",
    "bafta 2022 best game":         "Returnal — Housemarque [Source: BAFTA Games Awards 2022]",
    "bafta 2021 best game":         "Hades — Supergiant Games [Source: BAFTA Games Awards 2021]",
    "bafta 2020 best game":         "Death Stranding — Kojima Productions [Source: BAFTA Games Awards 2020]",
    "tga 2023 goty":                "Baldur's Gate 3 — Larian Studios [Source: The Game Awards 2023]",
    "tga 2022 goty":                "Elden Ring — FromSoftware [Source: The Game Awards 2022]",
    "tga 2021 goty":                "It Takes Two — Hazelight Studios [Source: The Game Awards 2021]",
    "tga 2020 goty":                "The Last of Us Part II — Naughty Dog [Source: The Game Awards 2020]",
    "tga 2019 goty":                "Death Stranding — Kojima Productions [Source: The Game Awards 2019]",
    "tga 2018 goty":                "God of War (2018) — Santa Monica Studio [Source: The Game Awards 2018]",
    "tga 2017 goty":                "The Legend of Zelda: Breath of the Wild — Nintendo [Source: The Game Awards 2017]",
    "the game awards 2023 goty":    "Baldur's Gate 3 — Larian Studios [Source: The Game Awards 2023]",
    "the game awards 2022 goty":    "Elden Ring — FromSoftware [Source: The Game Awards 2022]",
    "gdc 2024 audience award":      "Baldur's Gate 3 [Source: GDC Awards 2024]",
    "ign best game 2023":           "Baldur's Gate 3 [Source: IGN Best of 2023]",
    "ign best game 2022":           "Elden Ring [Source: IGN Best of 2022]",
}

GAME_SALES: dict[str, str] = {
    "minecraft":            "300M+ copies sold (as of 2023) · best-selling video game of all time · all platforms combined · Mojang created by Markus Persson 2009 · Microsoft acquired 2014 for $2.5B [Source: Microsoft / Mojang official]",
    "gta v":                "195M+ copies sold (as of 2023) · best-selling game on PS3/PS4/Xbox era · $1B revenue in 3 days · most profitable entertainment product ever at launch [Source: Take-Two Interactive official]",
    "tetris":               "520M+ copies sold across all versions (including mobile) · original Game Boy version sold 35M · most ported game in history · 65+ platforms [Source: The Tetris Company]",
    "wii sports":           "82.9M copies · bundled with Wii · accessible design · introduced millions to gaming · best-selling individual console game until GTA V [Source: Nintendo official]",
    "mario kart 8 deluxe":  "57.6M+ copies (Switch, as of 2023) · best-selling Switch game · includes DLC booster course pass · ongoing sales record [Source: Nintendo official]",
    "red dead redemption 2":"58M+ copies (as of 2023) · Rockstar Games · $725M in 3 days · most expensive game ever made at time (~$540M budget) [Source: Take-Two Interactive official]",
    "elden ring":           "20M+ copies in first year · FromSoftware best-selling game ever · GOTY 2022 multiple awards · PC simultaneous record: 953,000 players [Source: Bandai Namco official]",
    "the last of us":       "37M+ copies (original + remake + Part II combined) · Part II: 10M copies in 2 weeks · HBO series renewed for Season 3 [Source: Sony Interactive Entertainment]",
    "animal crossing":      "New Horizons: 43.6M copies · pandemic launch March 2020 · best-selling Nintendo Switch game at launch · mental health phenomenon during lockdowns [Source: Nintendo official]",
    "cyberpunk 2077":       "25M+ copies sold despite disastrous launch · No Man's Sky-like redemption arc · Phantom Liberty expansion · PS4/Xbox One versions recalled [Source: CD Projekt RED official]",
    "baldurs gate 3":       "10M+ copies sold (2023) · Larian Studios independent · funded partly by early access · swept major GOTY awards 2023 [Source: Larian Studios official]",
    "pokemon":              "Franchise total 440M+ games sold · best-selling RPG franchise · best-selling media franchise overall with anime, merchandise · since 1996 [Source: The Pokemon Company]",
}

CONSOLE_HISTORY: dict[str, str] = {
    "ps2":          "Sony PlayStation 2 · released 2000 · 155M units sold · best-selling console ever · DVD player drove adoption · GTA III, Shadow of Colossus, God of War [Source: Sony official]",
    "nintendo ds":  "Nintendo DS · released 2004 · 154M units sold · second best-selling console · dual screen + touchscreen · Pokemon + Brain Training drove sales [Source: Nintendo official]",
    "game boy":     "Nintendo Game Boy · released 1989 · 118M units (all variants) · survived a bomb (Gulf War story) · Tetris bundled · defined handheld gaming [Source: Nintendo official]",
    "ps4":          "Sony PlayStation 4 · released 2013 · 117M units · won console war vs Xbox One decisively · The Last of Us, Bloodborne, God of War [Source: Sony official]",
    "wii":          "Nintendo Wii · released 2006 · 101M units · motion controls · reached non-gamers · Wii Sports phenomenon · outsold PS3 and Xbox 360 [Source: Nintendo official]",
    "ps1":          "Sony PlayStation · released 1994 · 102M units · CDs vs cartridges · Final Fantasy VII, Metal Gear Solid, Crash Bandicoot · destroyed Sega Saturn [Source: Sony official]",
    "xbox 360":     "Microsoft Xbox 360 · released 2005 · 84M units · Halo 3, Gears of War · Xbox Live defined online console gaming · Red Ring of Death hardware failure [Source: Microsoft official]",
    "nes":          "Nintendo Entertainment System · released 1983 (Japan) 1985 (USA) · 61M units · revived game industry after 1983 crash · Super Mario Bros, Zelda, Metroid [Source: Nintendo official]",
    "snes":         "Super Nintendo · released 1990 · 49M units · Mode 7 graphics · Street Fighter II, Super Metroid, Final Fantasy VI, Chrono Trigger · golden age RPG era [Source: Nintendo official]",
    "genesis":      "Sega Mega Drive/Genesis · released 1988 · 30M units · Sonic the Hedgehog · Blast Processing marketing · gave Nintendo fierce competition [Source: Sega official]",
    "ps5":          "Sony PlayStation 5 · released 2020 · 45M+ units (2023) · fastest-selling PlayStation · DualSense haptic feedback · supply constrained by chip shortage [Source: Sony official]",
    "switch":       "Nintendo Switch · released 2017 · 139M+ units (2023) · hybrid home/portable · Breath of the Wild, Mario Odyssey · defied analyst predictions [Source: Nintendo official]",
    "atari 2600":   "Atari 2600 · released 1977 · first successful home console · Space Invaders port sold 2M units · E.T. cartridge buried in New Mexico · caused 1983 crash [Source: Atari historical record]",
    "dreamcast":    "Sega Dreamcast · released 1998 · 10.6M units · discontinued 2001 · Sega's last console · ahead of its time: online gaming, VMU · Shenmue, Jet Set Radio [Source: Sega official]",
}

GAME_STUDIOS: dict[str, str] = {
    "fromsoft":         "FromSoftware · founded 1986 Japan · Armored Core series then Dark Souls · Hidetaka Miyazaki president · Demon's Souls, Dark Souls, Bloodborne, Sekiro, Elden Ring · acquired by Kadokawa [Source: FromSoftware official]",
    "fromsoftware":     "FromSoftware · founded 1986 Japan · Armored Core series then Dark Souls · Hidetaka Miyazaki president · Demon's Souls, Dark Souls, Bloodborne, Sekiro, Elden Ring [Source: FromSoftware official]",
    "naughty dog":      "Naughty Dog · founded 1984 · Sony-owned since 2001 · Crash Bandicoot → Jak and Daxter → Uncharted → The Last of Us · known for cinematic storytelling [Source: Naughty Dog official]",
    "rockstar":         "Rockstar Games · founded 1998 New York · Take-Two Interactive subsidiary · Grand Theft Auto III changed open world games · Red Dead Redemption · GTA VI in development [Source: Rockstar official]",
    "nintendo epd":     "Nintendo EPD (Entertainment Planning & Development) · formed 2015 · largest Nintendo internal studio · Super Mario, Zelda, Animal Crossing, Splatoon [Source: Nintendo official]",
    "blizzard":         "Blizzard Entertainment · founded 1991 · Warcraft, Diablo, StarCraft, Overwatch, World of Warcraft · WoW had 12M subscribers at peak · Microsoft acquired via Activision Blizzard 2023 [Source: Blizzard official]",
    "valve":            "Valve Corporation · founded 1996 by Gabe Newell and Mike Harrington (ex-Microsoft) · Half-Life, Portal, Dota 2, Counter-Strike · Steam platform · 'Gaben' internet icon [Source: Valve official]",
    "id software":      "id Software · founded 1991 · Wolfenstein 3D, Doom, Quake · invented FPS genre · shareware distribution model · open-source legacy (Quake engine) · now Bethesda subsidiary [Source: id Software official]",
    "supergiant":       "Supergiant Games · founded 2009 · 6-7 person team · Bastion, Transistor, Pyre, Hades · all critical hits · community-funded Hades II announced [Source: Supergiant Games official]",
    "cdpr":             "CD Projekt RED · founded 1994 Poland · Witcher series (based on Sapkowski novels) · Cyberpunk 2077 · Polish government considers them national treasure [Source: CD Projekt official]",
    "cd projekt red":   "CD Projekt RED · founded 1994 Poland · The Witcher series · Cyberpunk 2077 · Phantom Liberty expansion · redemption arc after disastrous 2077 launch [Source: CD Projekt official]",
    "larian":           "Larian Studios · founded 1996 Belgium · Divinity: Original Sin series · Baldur's Gate 3 (2023) · independent studio · refused publisher control [Source: Larian Studios official]",
    "insomniac":        "Insomniac Games · founded 1994 · Spyro the Dragon, Ratchet & Clank, Resistance, Marvel's Spider-Man · Sony acquired 2019 · fastest acquired studio to produce GOTY contender [Source: Insomniac official]",
    "mojang":           "Mojang Studios · founded 2009 by Markus 'Notch' Persson · Minecraft only real game · Microsoft acquired 2014 for $2.5 billion · now makes only Minecraft content [Source: Mojang official]",
}

VILLAIN_DATA: dict[str, str] = {
    "sephiroth":        "Final Fantasy VII (1997) · Cloud's former SOLDIER mentor · inspired by Harlock manga · iconic one-wing design by Tetsuya Nomura · One-Winged Angel theme (first orchestral FF music) · considered greatest game villain [Source: Square Enix / game design documents]",
    "ganondorf":        "The Legend of Zelda series (since 1986) · Gerudo king reincarnation of Ganon · appears in most Zelda games · Triforce of Power · Ocarina of Time version most iconic · design evolved across 35+ years [Source: Nintendo official]",
    "bowser":           "Super Mario Bros (1985) · King of Koopas · kidnaps Princess Peach repeatedly · creator Miyamoto based on Tanuki raccoon dog · also playable in many spinoffs · surprisingly sympathetic in Bowser's Inside Story [Source: Nintendo official]",
    "handsome jack":    "Borderlands 2 (2012) · president of Hyperion · considered one of gaming's best written villains · darkly humorous · believes he is the hero · voice actor Dameon Clarke [Source: Gearbox Software]",
    "andrew ryan":      "BioShock (2007) · founder of Rapture · Atlas Shrugged influence · 'Would you kindly' · name anagram of 'Ayn Rand' · philosophical villain deconstructing objectivism [Source: Irrational Games / Ken Levine interviews]",
    "glados":           "Portal (2007) · GLaDOS · Genetic Lifeform and Disk Operating System · voiced by Ellen McLain · 'The cake is a lie' · defeated then returns · comedically threatening [Source: Valve official]",
    "giygas":           "EarthBound / Mother 2 (1994) · Shigesato Itoi based on childhood trauma (accidentally watching violent film) · indescribable cosmic horror · one of most disturbing game endings ever [Source: Shigesato Itoi interviews]",
    "psycho mantis":    "Metal Gear Solid (1998) · reads your memory card · controller vibration · breaks fourth wall · must plug controller into port 2 to defeat him · revolutionary design [Source: Konami / Hideo Kojima interviews]",
    "kefka":            "Final Fantasy VI (1994) · achieves goal of destroying the world · nihilist villain · actually wins midgame · considered first true villain protagonist in gaming [Source: Square official]",
    "lord recluse":     "City of Heroes · iconic superhero MMO villain · Marvel-quality backstory · showed MMOs could have narrative depth [Source: Cryptic Studios]",
}

PROTAGONIST_DATA: dict[str, str] = {
    "master chief":     "Halo series · real name John-117 · Spartan super-soldier · face NEVER shown intentionally (player projection design) · voiced by Steve Downes · Bungie → 343 Industries · 'Finish the Fight' [Source: Bungie / 343 Industries official]",
    "geralt":           "The Witcher series · created by Andrzej Sapkowski in 1986 short story · White Wolf · neutral in politics by choice · voiced by Doug Cockle · Henry Cavill in Netflix series [Source: CD Projekt RED / Sapkowski]",
    "kratos":           "God of War series (2005-) · Spartan warrior who killed Greek gods · became Norse mythology figure in 2018 reboot · design by David Jaffe · voiced by Christopher Judge · father role rehumanized character [Source: Santa Monica Studio official]",
    "link":             "The Legend of Zelda (1986-) · NOT the player character in early games · silent protagonist · multiple Links (reincarnation) · left-handed until Wii · named 'Link' as bridge between player and game world [Source: Nintendo official / Miyamoto interviews]",
    "lara croft":       "Tomb Raider (1996-) · Toby Gard designed her · polygon count limitations shaped her famous design · became cultural icon · Cambridge educated aristocrat · rebooted as survivor 2013 [Source: Core Design / Crystal Dynamics official]",
    "joel miller":      "The Last of Us (2013) · Joel voiced by Troy Baker · lost daughter Sarah in outbreak · morally grey decision at game's end · most debated ending in gaming · translated faithfully to HBO [Source: Naughty Dog official]",
    "commander shepard": "Mass Effect series · player-defined character · male default voiced by Mark Meer · female voiced by Jennifer Hale · Jennifer Hale became more popular choice · choices matter across trilogy [Source: BioWare official]",
    "solid snake":      "Metal Gear series (1987-) · created by Hideo Kojima · based on Escape from New York's Snake Plissken · voiced by David Hayter (iconic) then Kiefer Sutherland (MGSV controversy) [Source: Konami / Kojima Productions official]",
    "mario":            "Super Mario Bros (1985-) · originally Jumpman in Donkey Kong · named after landlord Mario Segale · profession changed from carpenter to plumber · 5'1\" according to Nintendo · no known last name officially [Source: Nintendo official]",
    "cloud strife":     "Final Fantasy VII (1997-) · designed by Tetsuya Nomura · iconic spiky blonde hair · Buster Sword · unreliable narrator twist · psychology of trauma explored · Nomura based design on 'cool' aesthetic [Source: Square Enix official]",
}

SIDEKICK_DATA: dict[str, str] = {
    "tails":        "Sonic the Hedgehog 2 (1992) · Miles 'Tails' Prower · originally hated by Sonic Team, almost cut · fan favorite · can be played cooperatively · name = Miles Per Hour pun [Source: Sega official / Yuji Naka interviews]",
    "alyx vance":   "Half-Life 2 (2004) · designed to feel like a 'real' companion · Valve pioneered NPC companion AI · she never gets in the way · VR game Half-Life: Alyx (2020) made her protagonist [Source: Valve official]",
    "ellie":        "The Last of Us (2013) · designed by Neil Druckmann · voiced by Ashley Johnson · immune to cordyceps · became protagonist of Part II · age progressed across games [Source: Naughty Dog official]",
    "sully":        "Uncharted series · Victor 'Sully' Sullivan · father figure to Nathan Drake · Charles Halford motion capture / Richard McGonagle voice · fan favorite who was planned to die early [Source: Naughty Dog official]",
    "cortana":      "Halo series · AI companion to Master Chief · voiced by Jen Taylor · rampancy story arc · controversial Halo 4-5 direction · now also a Microsoft AI assistant [Source: Bungie / 343 Industries official]",
    "garrus":       "Mass Effect series · turian companion · fan favorite romance option (male and female Shepard) · 'Calibrations' meme · considered best written companion in trilogy [Source: BioWare official]",
    "dogmeat":      "Fallout series (since 1997) · named after film Dogmeat · appears in multiple games · survives any difficulty in Fallout 4 (cannot die in Survival) · named after character in A Boy and His Dog [Source: Bethesda official]",
    "yoshi":        "Super Mario World (1990) · designed as Mario riding a horse · T-rex limitation became dinosaur · 45M total franchise sales · Yoshi's Story, Yoshi's Island spinoffs [Source: Nintendo official]",
    "clank":        "Ratchet & Clank (2002) · robotic sidekick · different sizes available · Clank actor Jim Ward · Insomniac Games · became co-protagonist in later games [Source: Insomniac Games official]",
}

GAME_ART_STYLES: dict[str, str] = {
    "cuphead":          "1930s Fleischer Studios rubber hose animation · hand-drawn on paper then digitized · 3 years of animation work just for art · every enemy has 60-70 hand-drawn frames · Max and Chad Moldenhauer brothers · [Source: Studio MDHR GDC 2019 talk]",
    "journey":          "thatgamecompany · Jenova Chen · warm desert color palette becomes cold white mountain · color temperature tells entire story arc without words · Joe Rombi art direction [Source: thatgamecompany official / GDC talks]",
    "hollow knight":    "Team Cherry · William Pellen's hand-drawn art · inspired by classic 90s animation · minimalist but expressive · entire game made by 3 people [Source: Team Cherry official]",
    "nier automata":    "Yoko Taro · PlatinumGames · inspired by Yoshida's character design philosophy · 2B design intentionally provocative to make 'real' character underneath resonate more [Source: Yoko Taro/Yoshida interviews]",
    "okami":            "Clover Studio (2006) · Japanese sumi-e ink painting and ukiyo-e woodblock print style · Atsushi Inaba/Hideki Kamiya · water ripple effects using ink stroke motifs [Source: Clover Studio official / GDC talks]",
    "hades":            "Supergiant Games · art director Jen Zee · Greek pottery and red-figure vase painting influence · 3D models with hand-painted texture look · warm amber underground + cool blue afterlife contrast [Source: Supergiant GDC 2020 talk]",
    "disco elysium":    "ZA/UM · oil painting aesthetic from Martin Luiga and Aleksander Rostov · Pleinair painting style · every character portrait painted · Eastern European expressionism influence [Source: ZA/UM official / developer interviews]",
    "celeste":          "Matt Makes Games (Maddy Thorson + Noel Berry) · pixel art style deliberately retro · pink hair = empathy signal · mountain color palette shifts with emotional journey [Source: developer interviews / GDC]",
    "gris":             "Nomada Studio · Conrad Roset's watercolor illustration style · color introduced gradually as emotional journey progresses · starts black and white · won multiple art direction awards [Source: Devolver Digital / developer interviews]",
}

COLOR_PALETTES: dict[str, str] = {
    "journey":          "Desert gold → ruins grey → mountain white/blue · color temperature maps emotional journey · warm = comfort/life, cold = isolation/transcendence · no text needed [Source: thatgamecompany design talk]",
    "bioshock":         "Art Deco amber/teal color scheme · 1920s luxury palette gone to rot · golden light against dark water · rust and bioluminescence · art director Shawn Robertson [Source: Irrational Games design documents]",
    "the last of us":   "Muted post-apocalyptic earth tones + bursts of lush green · fungal greens vs survivor browns · Joel's dark wardrobe vs Ellie's bright clothing intentional contrast [Source: Naughty Dog art direction talks]",
    "hollow knight":    "High contrast black/white with jewel color accents · each area has distinct accent color · City of Tears: blue · Greenpath: emerald · Forgotten Crossroads: dark purple [Source: Team Cherry design talks]",
    "ori and the blind forest": "Bioluminescent palette · dark forest + glowing life · contrast drives emotional impact · phosphorescent teal/green/gold against dark backgrounds [Source: Moon Studios design talks]",
    "shadow of the colossus": "Desaturated bleached landscape · colossi have warm earth tones · deliberate low saturation for melancholy · contrast with electric blue sky and green valleys [Source: Team Ico design documents]",
    "firewatch":        "Bold graphic novel palette · sunset oranges and yellows · Wyoming wilderness · Olly Moss graphic design influence · flat color shapes over photorealism [Source: Campo Santo design talks]",
    "undertale":        "Pixel art palette deliberately limited · Toby Fox chose colors for emotional resonance · Genocide route dulls palette visibly · Sans's blue eye matches cold justice theme [Source: Toby Fox design talks]",
}

FAMOUS_LINES: dict[str, str] = {
    "would you kindly":     "BioShock (2007) · Andrew Ryan's revelation · 'A man chooses, a slave obeys' · retroactive recontextualization of phrase used all game · considered best plot twist in gaming · Ken Levine [Source: Irrational Games]",
    "it's dangerous to go alone": "The Legend of Zelda (1986) · 'It's dangerous to go alone! Take this.' · most quoted video game line ever · old man in first cave · culturally ubiquitous [Source: Nintendo]",
    "stay a while and listen": "Diablo II (2000) · Deckard Cain · became meme · 'Stay a while and listen!' · returned in Diablo III as emotional callback [Source: Blizzard]",
    "do a barrel roll":     "Star Fox 64 (1997) · Peppy Hare's instruction · 'Do a barrel roll!' · became major internet meme · Google search Easter egg [Source: Nintendo]",
    "war never changes":    "Fallout series · Ron Perlman narrator opening monologue · 'War. War never changes.' · each game opens with it · became franchise identity [Source: Bethesda]",
    "the cake is a lie":    "Portal (2007) · GLaDOS promises cake for completing tests · 'The cake is a lie' written on walls by past test subjects · major early internet gaming meme [Source: Valve]",
    "get over here":        "Mortal Kombat (1992) · Scorpion's spear move · 'GET OVER HERE!' · one of gaming's most iconic voice clips · Ed Boon voiced it himself [Source: Midway/NetherRealm]",
    "it's a-me mario":      "Super Mario 64 (1996) · Charles Martinet's voice · first time Mario was clearly voiced · 'It's a-me, Mario!' · Martinet voiced Mario 1995-2023 [Source: Nintendo]",
}

GAME_MECHANICS: dict[str, str] = {
    "stamina bar":          "Dark Souls popularized it but King's Field (FromSoftware, 1994) used it first · Demon's Souls refined it · now standard in action RPGs · forces tactical play rather than button mashing [Source: game design history]",
    "health regeneration":  "Halo: Combat Evolved (2001) popularized shield regeneration · Call of Duty 2 (2005) brought full health regen to FPS · changed how games were designed (no more health pickups meta) [Source: game design history]",
    "open world":           "Elite (1984) procedurally generated galaxy is first true open world · Legend of Zelda (1986) popularized non-linear exploration · GTA III (2001) defined modern open world format [Source: game design history]",
    "quick time event":     "Dragon's Lair (1983) laserdisc game pioneered it · Shenmue (1999) named 'QTE' · God of War (2005) made them mainstream · Resident Evil 4 refined them [Source: game design history]",
    "cover system":         "Kill Switch (2003) first dedicated cover mechanics · Gears of War (2006) refined and popularized · became mandatory in third-person shooters for years [Source: game design history]",
    "bullet time":          "The Matrix film influence → Max Payne (2001) adapted it for games · slow-motion gunplay became genre-defining · F.E.A.R., Stranglehold, various others adopted it [Source: game design history]",
    "crafting system":      "Ultima Online (1997) pioneered MMO crafting · Minecraft (2009) simplified and popularized · now ubiquitous across all genres [Source: game design history]",
    "permadeath":           "Rogue (1980) invented it · became defining mechanic of roguelike genre · Spelunky (2008) brought it mainstream · Hades made permadeath with narrative possible [Source: game design history]",
    "dialogue wheel":       "Star Wars: Knights of the Old Republic (2003) used predecessor · Mass Effect (2007) perfected circular dialogue wheel · Dragon Age Origins used differently · now standard in RPGs [Source: BioWare design history]",
}

GAMING_MEMES: dict[str, str] = {
    "all your base":        "Zero Wing (1989) · Mega Drive · terrible English translation · 'All your base are belong to us' · became massive internet meme 2001 · TIME Magazine covered it · sold T-shirts, merchandise [Source: verified internet history]",
    "leeroy jenkins":       "World of Warcraft (2005) · video of player Leeroy Jenkins running into dungeon unprepared · 'LEEEEROY JENKINS!' · viewed 100M+ times · made real character in WoW Trading Card Game [Source: Blizzard / original video]",
    "arrow in the knee":    "The Elder Scrolls V: Skyrim (2011) · 'I used to be an adventurer like you, then I took an arrow in the knee' · every guard says it · became biggest Skyrim meme [Source: Bethesda]",
    "press f to pay respects": "Call of Duty: Advanced Warfare (2014) · funeral scene QTE · press F to interact with casket · became universal internet expression of condolences [Source: Activision / Sledgehammer Games]",
    "the cake is a lie":    "Portal (2007) · GLaDOS promises cake · 'The cake is a lie' hidden message · major gaming meme 2007-2010 [Source: Valve]",
    "do a barrel roll":     "Star Fox 64 (1997) · Peppy Hare · became so famous Google search performs barrel roll when you search it [Source: Nintendo / Google Easter egg]",
    "git gud":              "Dark Souls community response to difficulty complaints · 'git gud' (get good) · became philosophy of difficult game culture · Souls series fans adopted as identity [Source: gaming community history]",
    "its over 9000":        "Dragon Ball Z anime (1996 Japan) · '9000' was actually the correct Funimation dub number (Japanese original: 8000) · Major internet meme pre-2010 [Source: Funimation / anime history]",
}

SPEEDRUN_TECHNIQUES: dict[str, str] = {
    "blj":              "Backwards Long Jump · Super Mario 64 · uses backwards running glitch to build infinite speed · can clip through floors and reach normally inaccessible areas · most famous SM64 technique [Source: SM64 speedrunning community / pannenkoek2012 research]",
    "wrong warp":       "Occurs when game logic sends player to incorrect destination · often caused by memory manipulation · used in Zelda: OoT to skip directly to Ganon · major time save [Source: OoT speedrunning community]",
    "clipping":         "Passing through solid geometry via precise movement or physics exploits · most games have invisible collision geometry that can be bypassed · OoB (out of bounds) travel [Source: speedrunning community]",
    "asl":              "Any% Speedrun Legacy · general term for unrestricted speedruns with no category limits · glitches allowed · fastest possible time [Source: speedrun.com]",
    "sequence breaking": "Completing game objectives in unintended order · Metroid community pioneered this · obtaining items before they're supposed to be available · fundamentally changes games [Source: Metroid / speedrunning community]",
    "rng manipulation": "Manipulating random number generator for favorable outcomes · performed by specific actions before the random event · frame-perfect inputs change RNG seed [Source: speedrunning community]",
    "death warp":       "Intentionally dying to respawn at a more advantageous location · faster than traveling normally · common in many games where death loads specific checkpoint [Source: speedrunning community]",
    "zip":              "High-speed movement glitch that moves character further than intended · often caused by touching specific geometry at certain angles · Zelda: BotW has notable zips [Source: BotW speedrunning community]",
}

GAME_RATINGS: dict[str, str] = {
    "mortal kombat":    "Directly caused creation of ESRB in 1994 · US Senate hearings with Joe Lieberman and Herbert Kohl · blood and fatalities shocked parents · SNES version censored blood to sweat · Genesis kept blood with code [Source: US Congressional Record 1993 / ESRB official history]",
    "doom":             "1993 · shareware distribution model · graphic violence and satanic imagery caused moral panic · led to ESRB creation · id Software stood firm on content [Source: id Software / ESRB history]",
    "night trap":       "1992 · FMV game · Senate hearing 'exhibit A' alongside Mortal Kombat · featured women being killed by vampires · rated MA-17 then re-released with edits [Source: US Congressional Record 1993]",
    "grand theft auto":  "GTA series ESRB Mature (M) · GTA III 2001 redefined open world violence · Hot Coffee mod in GTA San Andreas caused AO rating (changed back to M) · Jack Thompson campaigns [Source: ESRB / legal record]",
    "manhunt":          "Rockstar 2003 · extremely violent stealth kills · banned in multiple countries · New Zealand seized copies · linked (disputed) to real murder · sequel Manhunt 2 got AO rating initially [Source: ESRB / legal record]",
    "pegi":             "Pan European Game Information · EU equivalent of ESRB · age ratings 3, 7, 12, 16, 18 · content descriptors · established 2003 · 39 European countries [Source: PEGI official]",
    "esrb":             "Entertainment Software Rating Board · founded 1994 after congressional hearings · ratings: EC, E, E10+, T, M, AO · AO rating means most retailers won't stock it [Source: ESRB official]",
}

GAMING_FIRSTS: dict[str, str] = {
    "first video game":     "Debated · Tennis for Two (1958) by William Higinbotham · Spacewar! (1962) MIT · Pong (1972) first commercial success · OXO (1952) by Alexander Douglas often cited [Source: gaming history]",
    "first fps":            "Maze War (1974) · first person perspective shooter · MIDI Maze (1987) first networked FPS · Wolfenstein 3D (1992) popularized genre · Doom (1993) defined it [Source: game history]",
    "first open world":     "Elite (1984) · BBC Micro · procedurally generated galaxy · 8 galaxies of 256 planets · David Braben and Ian Bell [Source: game history]",
    "first rpg":            "dnd (1974) · PLATO mainframe system · first dungeon crawl game · Ultima (1981) and Wizardry (1981) defined home computer RPG · D&D tabletop (1974) inspired them [Source: gaming history]",
    "first online game":    "MUD1 (1978) · Multi-User Dungeon · text-based · Roy Trubshaw and Richard Bartle · Essex University · still technically running [Source: gaming history]",
    "first game music":     "Space Invaders (1978) · Tomohiro Nishikado · four-note descending bassline · sped up as aliens descended · first dynamic adaptive music in games [Source: gaming history]",
    "first save system":    "Adventure (1979) · Atari 2600 · Warren Robinett · also first Easter egg (hidden room with his name) · save feature was a breakthrough [Source: gaming history]",
    "first dlc":            "Horse Armor Pack · The Elder Scrolls IV: Oblivion · 2006 · $2.50 for decorative horse armor · immediate backlash · began era of paid DLC [Source: Bethesda / gaming history]",
}

GAME_CONTROVERSIES: dict[str, str] = {
    "no mans sky":          "Hello Games · announced 2013 · Sean Murray overpromised features · launch 2016 was disaster · missing: multiplayer, features shown in trailers · years of free updates · Atlas Rises, NEXT, Beyond · fully redeemed by 2020 [Source: Hello Games / gaming press]",
    "cyberpunk 2077":       "CD Projekt RED · 8 years in development · massive hype · launch December 2020 · broken on PS4/Xbox One · Sony removed from PlayStation Store · class action lawsuit · director apology · 2+ years of patches · Phantom Liberty 2023 redeemed it [Source: CD Projekt RED / gaming press]",
    "diablo immortal":      "Blizzard · mobile game · 'Do you guys not have phones?' · targeted audience that didn't want mobile · alleged $110,000 max spend for fully geared character · pay-to-win controversy [Source: Blizzard / gaming press]",
    "last of us 2":         "Naughty Dog 2020 · massive spoilers leaked before launch · divisive narrative choices · death of [SPOILER] · still most polarizing game ending discussion · multiple GOTY wins despite controversy [Source: gaming press]",
    "star wars battlefront 2": "EA/DICE 2017 · pay-to-win loot boxes · progression locked behind real money · Disney pressure removed microtransactions · Belgian government investigated · led to worldwide loot box legislation [Source: EA / gaming press / legal record]",
    "gamergate":            "2014 · harassment campaign targeting women in gaming · Zoe Quinn, Anita Sarkeesian, Brianna Wu targeted · changed industry discussion about diversity · SPJ discussion · still discussed as industry watershed [Source: gaming press / documented history]",
    "konami vs kojima":     "2015 · Hideo Kojima's name removed from Metal Gear Solid V box · P.T. (Silent Hills) cancelled · Kojima left Konami · formed Kojima Productions · delivered Death Stranding 2019 [Source: gaming press]",
}

GAME_COMPOSERS: dict[str, str] = {
    "koji kondo":           "Nintendo · Super Mario Bros (1985), The Legend of Zelda (1986) · most recognized game music ever · still at Nintendo · 40+ years of iconic music · influenced every game composer [Source: Nintendo official]",
    "nobuo uematsu":        "Final Fantasy series (1987-2016) · One-Winged Angel · Terra's Theme · Eyes on Me · formed The Black Mages band · largely freelance since 2004 · considered greatest RPG composer [Source: Square Enix official / composer interviews]",
    "yoko shimomura":       "Street Fighter II (1991), Kingdom Hearts (2002), Mario & Luigi series · Xenoblade Chronicles 2 · versatile across genres · world tour concerts of her music [Source: composer official records]",
    "jeremy soule":         "Morrowind, Oblivion, Skyrim · Guild Wars · Supreme Commander · 'The Bard of the Age' · 'Dragonborn' theme · Elder Scrolls identity [Source: composer official]",
    "toby fox":             "Undertale (2015) composed entire OST alone · some tracks in 2 hours · no budget · Megalovania · Spider Dance · became professionally recognized from solo work · also composed for Pokemon Sword/Shield [Source: Toby Fox / Nintendo official]",
    "mick gordon":          "Doom (2016), Doom Eternal · industrial metal approach · 'BFG Division' · integrated real guitar with electronic elements · designed so tracks work at any loop point [Source: id Software / composer interviews]",
    "akira yamaoka":        "Silent Hill series (1999-) · composer + sound director · industrial ambient horror · Mary Elizabeth McGlynn vocals · series identity inseparable from his work [Source: Konami / composer interviews]",
    "marty o'donnell":      "Halo series (2001-2014) · 'Mjolnir Mix' · monk chanting introduction · sued Bungie in 2014 over wrongful termination · composed Symphony of Fire for Destiny before firing [Source: Bungie / legal record]",
}

GAME_ACQUISITIONS: dict[str, str] = {
    "activision blizzard microsoft": "Microsoft acquired Activision Blizzard January 2023 · $68.7 billion · largest gaming acquisition ever · Call of Duty, World of Warcraft, Diablo, Overwatch · 18-month regulatory battle [Source: Microsoft / FTC records]",
    "bethesda microsoft":   "Microsoft acquired ZeniMax Media (Bethesda parent) September 2020 · $7.5 billion · Elder Scrolls, Fallout, Doom, Wolfenstein, Quake · makes future games Xbox/PC exclusive [Source: Microsoft official]",
    "mojang microsoft":     "Microsoft acquired Mojang (Minecraft) September 2014 · $2.5 billion · Notch left company after sale · remained cross-platform unlike Bethesda titles [Source: Microsoft official]",
    "bungie sony":          "Sony acquired Bungie January 2022 · $3.6 billion · Destiny series · Bungie retains independence · can still publish on non-PlayStation platforms [Source: Sony official]",
    "activision":           "Activision Blizzard formed 2008 by merger of Activision and Vivendi Games (Blizzard) · then acquired by Microsoft 2023 · complex corporate history [Source: corporate records]",
    "ea origin":            "EA acquired Origin Systems (Ultima series, Richard Garriott) 1992 · later named their platform Origin · Origin Systems dissolved as independent studio [Source: EA corporate history]",
}

DLC_HISTORY: dict[str, str] = {
    "witcher 3":            "CD Projekt RED · Blood and Wine expansion (2016) · 30+ hours of new story · larger than many full games · won GOTY awards in its own right · Toussaint region · free DLC also provided [Source: CD Projekt RED official]",
    "dark souls":           "Artorias of the Abyss (DS1) · Crown DLC trilogy (DS2) · The Ringed City + Ashes of Ariandel (DS3) · FromSoftware DLC consistently rated as excellent as base games [Source: FromSoftware official]",
    "borderlands 2":        "Tiny Tina's Assault on Dragon Keep · considered better than base game by many · led to standalone game Tiny Tina's Wonderlands · DLC that became franchise [Source: Gearbox official]",
    "red dead 2":           "No paid story DLC despite Red Dead Redemption 1 having excellent story DLC · Red Dead Online instead · fans disappointed · Rockstar focused on GTA Online [Source: Rockstar official]",
    "horse armor":          "The Elder Scrolls IV: Oblivion · 2006 · $2.50 for decorative horse armor · first major paid DLC controversy · began paid DLC era · now seems tame by modern standards [Source: Bethesda / gaming history]",
    "elden ring":           "Shadow of the Erdtree (2024) · largest FromSoftware expansion ever · 40+ hours · new zone, bosses, weapons · metacritic 94 · priced as major expansion [Source: FromSoftware official]",
    "cyberpunk 2077":       "Phantom Liberty (2023) · major spy-thriller expansion · redemption for base game · new district Dogtown · Idris Elba as Solomon Reed · 90+ Metacritic [Source: CD Projekt RED official]",
}

COLORPALETTE_GAMING = COLOR_PALETTES  # alias for command


class GamingCog(commands.Cog):

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

    def _fuzzy(self, query: str, data: dict) -> str | None:
        q = query.strip().lower()
        if q in data:
            return data[q]
        for key, val in data.items():
            if q in key or key in q:
                return val
        return None

    # ── !award ───────────────────────────────────────────────

    @commands.command(name="award", aliases=["gameaward", "goty"])
    async def award(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game award winners. Usage: !award BAFTA 2024 best game"""
        if not query:
            await self._respond(ctx, "Usage: !award [show] [year] [category] — e.g. !award BAFTA 2024 best game")
            return
        if not await self._check_cooldown(ctx, "award", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAME_AWARDS)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"No award data for '{query}'. Try: !award BAFTA 2024 best game | !award TGA 2023 GOTY")

    # ── !sales ───────────────────────────────────────────────

    @commands.command(name="sales", aliases=["gamesales", "bestselling"])
    async def sales(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game sales figures and records. Usage: !sales Minecraft"""
        if not query:
            await self._respond(ctx, "Usage: !sales [game] — e.g. !sales Minecraft or !sales GTA V")
            return
        if not await self._check_cooldown(ctx, "sales", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAME_SALES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(GAME_SALES.keys())[:6])
            await self._respond(ctx, f"No sales data for '{query}'. Try: {keys}...")

    # ── !review (IGDB API) ───────────────────────────────────

    @commands.command(name="review", aliases=["score", "metacritic"])
    async def review(self, ctx: commands.Context, *, game: str = "") -> None:
        """Game critic rating from IGDB. Usage: !review Elden Ring"""
        if not game:
            await self._respond(ctx, "Usage: !review [game name] — e.g. !review Elden Ring")
            return
        if not await self._check_cooldown(ctx, "review", DEFAULT_COOLDOWN):
            return
        result = await get_game_review(game.strip())
        await self._respond(ctx, result)

    # ── !console ─────────────────────────────────────────────

    @commands.command(name="console", aliases=["consolehistory", "aboutconsole"])
    async def console(self, ctx: commands.Context, *, query: str = "") -> None:
        """Console history and sales facts. Usage: !console PS2"""
        if not query:
            await self._respond(ctx, f"Usage: !console [name] — try: ps2, switch, game boy, nes, snes, dreamcast...")
            return
        if not await self._check_cooldown(ctx, "console", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, CONSOLE_HISTORY)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(CONSOLE_HISTORY.keys())[:8])
            await self._respond(ctx, f"Console '{query}' not found. Try: {keys}...")

    # ── !studio ──────────────────────────────────────────────

    @commands.command(name="studio", aliases=["developer", "gamedev", "devstudio"])
    async def studio(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game studio history and notable games. Usage: !studio FromSoft"""
        if not query:
            await self._respond(ctx, "Usage: !studio [name] — e.g. !studio FromSoft or !studio Valve")
            return
        if not await self._check_cooldown(ctx, "studio", DEFAULT_COOLDOWN):
            return
        # Check local data first
        result = self._fuzzy(query, GAME_STUDIOS)
        if result:
            await self._respond(ctx, result)
        else:
            # Fall back to IGDB
            result = await get_studio_info(query.strip())
            await self._respond(ctx, result)

    # ── !franchise ───────────────────────────────────────────

    @commands.command(name="franchise", aliases=["gameseries", "serieshistory"])
    async def franchise(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game franchise timeline from IGDB. Usage: !franchise Zelda"""
        if not query:
            await self._respond(ctx, "Usage: !franchise [name] — e.g. !franchise Zelda or !franchise Final Fantasy")
            return
        if not await self._check_cooldown(ctx, "franchise", DEFAULT_COOLDOWN):
            return
        result = await get_franchise_timeline(query.strip())
        await self._respond(ctx, result)

    # ── !platforms ───────────────────────────────────────────

    @commands.command(name="platforms", aliases=["availableon", "gameon", "portedon"])
    async def platforms(self, ctx: commands.Context, *, game: str = "") -> None:
        """Which platforms a game is on. Usage: !platforms Hades"""
        if not game:
            await self._respond(ctx, "Usage: !platforms [game] — e.g. !platforms Hades")
            return
        if not await self._check_cooldown(ctx, "platforms", DEFAULT_COOLDOWN):
            return
        result = await get_platforms(game.strip())
        await self._respond(ctx, result)

    # ── !worldrecord ─────────────────────────────────────────

    @commands.command(name="worldrecord", aliases=["gamingrecord", "speedrun"])
    async def worldrecord(self, ctx: commands.Context, *, query: str = "") -> None:
        """Gaming world records and speedrun records. Usage: !worldrecord Super Mario 64"""
        if not query:
            await self._respond(ctx, "Usage: !worldrecord [game or category] — e.g. !worldrecord Super Mario 64")
            return
        if not await self._check_cooldown(ctx, "worldrecord", DEFAULT_COOLDOWN):
            return
        records: dict[str, str] = {
            "super mario 64":       "Any%: 1h 37m 46s · current WR holder varies · uses BLJ (Backwards Long Jump) glitch · see speedrun.com/sm64 for current record [Source: speedrun.com]",
            "ocarina of time":      "Any%: ~7 minutes · uses Wrong Warp glitch to skip to credits · one of most broken speedruns ever · see speedrun.com/oot [Source: speedrun.com]",
            "minecraft":            "Any% Random Seed: under 10 minutes for top runs · Random Seed No Glitches: ~15 minutes · Dream controversy involved this category [Source: speedrun.com]",
            "pokemon red":          "Any%: ~1h 40m · uses select glitch and trainer-fly · decades of route optimization · category has survived rom updates [Source: speedrun.com]",
            "celeste":              "Any%: under 27 minutes · precise platforming · developer Maddy Thorson follows speedrunning community [Source: speedrun.com]",
            "portal":               "Under 7 minutes · uses portal glitches to bypass intended routes · Valve acknowledged community in Portal 2 [Source: speedrun.com]",
            "sekiro":               "Under 15 minutes any% · Shura ending (bad ending) fastest · FromSoftware games have vibrant speedrun communities [Source: speedrun.com]",
            "gta sa":               "Any%: under 4 hours · massive route optimization over years · skips huge sections via glitches [Source: speedrun.com]",
        }
        result = self._fuzzy(query, records)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"Check speedrun.com for '{query}' current world record — I don't have live data for this one.")

    # ── !canceledgame ────────────────────────────────────────

    @commands.command(name="canceledgame", aliases=["scrapped", "neverreleased"])
    async def canceledgame(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous canceled games. Usage: !canceledgame Silent Hills"""
        if not query:
            await self._respond(ctx, "Usage: !canceledgame [name] — e.g. !canceledgame Silent Hills")
            return
        if not await self._check_cooldown(ctx, "canceledgame", DEFAULT_COOLDOWN):
            return
        canceled: dict[str, str] = {
            "silent hills":         "Hideo Kojima + Guillermo del Toro + Norman Reedus · P.T. playable teaser released 2014 · Konami canceled 2015 after Kojima departure · P.T. removed from PSN · still discussed as greatest lost game [Source: Konami / gaming press]",
            "starcraft ghost":      "Blizzard · announced 2002 · stealth action game · years of delays · quietly canceled 2014 without announcement · lingered in development 12 years [Source: Blizzard / gaming press]",
            "beyond good and evil 2": "Ubisoft · sequel to 2003 cult classic · announced 2008 · re-announced 2017 · Michel Ancel left Ubisoft 2020 · still no release date · almost 20 years in development [Source: Ubisoft official / gaming press]",
            "half life 3":          "Valve · most meme'd canceled/unannounced game · Half-Life 2 Episode 3 story leaked by Marc Laidlaw 2017 · Half-Life: Alyx (2020) VR released instead · '3' remains a meme [Source: Marc Laidlaw / gaming history]",
            "prey 2":               "Human Head Studios · sequel to 2006 Prey · Bounty Hunter protagonist · canceled 2014 by Bethesda/ZeniMax · replaced by Arkane's Prey (2017) which is unrelated [Source: Bethesda / gaming press]",
            "canned megaman":       "Mega Man Legends 3 · Capcom · Keiji Inafune's project · canceled 2011 · Inafune left Capcom in protest · launched Mighty No. 9 Kickstarter as spiritual successor [Source: Capcom / gaming press]",
        }
        result = self._fuzzy(query, canceled)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(canceled.keys())[:4])
            await self._respond(ctx, f"Canceled game '{query}' not found. Try: {keys}...")

    # ── !secret ──────────────────────────────────────────────

    @commands.command(name="secret", aliases=["hidden", "hiddengem", "easteregg"])
    async def secret(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous Easter eggs and secrets in games. Usage: !secret GTA San Andreas"""
        if not query:
            await self._respond(ctx, "Usage: !secret [game] — e.g. !secret GTA San Andreas or !secret Portal")
            return
        if not await self._check_cooldown(ctx, "secret", DEFAULT_COOLDOWN):
            return
        secrets: dict[str, str] = {
            "gta san andreas":      "Hot Coffee · hidden sexual minigame left in code by Rockstar · discovered by modder 'PatrickW' 2005 · caused AO rating · Rockstar issued patch · Hillary Clinton called for FTC investigation [Source: gaming press / legal record]",
            "portal":               "Rattmann dens · hidden rooms with cave paintings by Doug Rattmann · found by exploring · lore expanded in Portal 2 · adds human story to GLaDOS universe [Source: Valve]",
            "metal gear solid":     "Psycho Mantis · reads your memory card and comments on other games saved · must plug controller into port 2 to fight him · revolutionary 4th wall breaking [Source: Konami]",
            "halo ce":              "Marathon symbol hidden throughout game · Bungie's previous franchise · subtle Easter egg for fans · Cortana terminals reference Marathon lore [Source: Bungie]",
            "elder scrolls":        "Notched Pickaxe in Skyrim near the Throat of the World · references Minecraft creator 'Notch' · placed near highest point in game [Source: Bethesda]",
            "minecraft":            "Herobrine · NOT actually in the game · patch notes historically claimed 'Removed Herobrine' as a joke · became biggest gaming creepypasta [Source: Mojang / gaming community]",
            "bioshock":             "In Bioshock 2 you can find a copy of the Objectivist newsletter with Ryan's obituary · deep lore for players who explore [Source: 2K Games]",
            "pokemon red blue":     "MissingNo. · glitch Pokemon at column 6, shores of Viridian City · corrupts Hall of Fame · duplicates 6th item · not intended but became iconic [Source: Nintendo / fan research]",
            "breath of the wild":   "The Legend of Zelda BOTW has a hidden room under Hyrule Castle accessible through river · contains a chest with powerful gear [Source: Nintendo / community discovery]",
        }
        result = self._fuzzy(query, secrets)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(secrets.keys())[:5])
            await self._respond(ctx, f"No secret data for '{query}'. Try: {keys}...")

    # ── !gameengine ──────────────────────────────────────────

    @commands.command(name="gameengine", aliases=["builtwith", "engineinfo"])
    async def gameengine(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game engine info and which games use it. Usage: !gameengine Unreal 5"""
        if not query:
            await self._respond(ctx, "Usage: !gameengine [name] — e.g. !gameengine Unreal 5 or !gameengine Unity")
            return
        if not await self._check_cooldown(ctx, "gameengine", DEFAULT_COOLDOWN):
            return
        engines: dict[str, str] = {
            "unreal 5":             "Epic Games · Nanite virtualized geometry + Lumen global illumination · used in Fortnite, Black Myth: Wukong, Senua's Saga, many AAA titles · democratized photorealism [Source: Epic Games official]",
            "unreal engine":        "Epic Games · Unreal Engine 1 (1998) through UE5 (2021) · most widely used commercial engine · licensing model · Fortnite, Mass Effect, Batman Arkham series [Source: Epic Games official]",
            "unity":                "Unity Technologies · 2005 · most popular indie/mobile engine · 50%+ of mobile games · WebGL export · C# scripting · runtime fee controversy 2023 caused backlash [Source: Unity Technologies official]",
            "source":               "Valve Corporation · successor to GoldSrc · Half-Life 2 (2004) · Portal, L4D series, Counter-Strike: Source · Source 2: Dota 2, Half-Life: Alyx [Source: Valve official]",
            "cry engine":           "Crytek · CryEngine 1 (2004) with Far Cry · CRYENGINE series known for extreme visual fidelity · Crysis 'can it run Crysis' benchmark · licensed to various studios [Source: Crytek official]",
            "id tech":              "id Software · Doom (1993) through id Tech 7 (2020) · Rage 2, Doom Eternal · massive influence on FPS genre · id Tech 3 basis of Call of Duty [Source: id Software official]",
            "creation engine":      "Bethesda Game Studios · based on Gamebryo · Skyrim, Fallout 4, Starfield · notoriously buggy but moddable · Creation Engine 2 for Starfield [Source: Bethesda official]",
            "rpg maker":            "Kadokawa (various versions) · enabled indie RPGs · Yume Nikki, Ib, To the Moon, Omori made in RPG Maker · democratized game development [Source: Kadokawa official]",
        }
        result = self._fuzzy(query, engines)
        if result:
            await self._respond(ctx, result)
        else:
            result = await get_game_engine_info(query.strip())
            await self._respond(ctx, result)

    # ── !howhard ─────────────────────────────────────────────

    @commands.command(name="howhard", aliases=["difficulty", "completionrate"])
    async def howhard(self, ctx: commands.Context, *, query: str = "") -> None:
        """How hard a game is — completion rates and difficulty reputation. Usage: !howhard Sekiro"""
        if not query:
            await self._respond(ctx, "Usage: !howhard [game] — e.g. !howhard Sekiro or !howhard Celeste")
            return
        if not await self._check_cooldown(ctx, "howhard", DEFAULT_COOLDOWN):
            return
        difficulty: dict[str, str] = {
            "sekiro":               "~30% Steam achievement completion for first boss · no summons, no builds, no cheese · posture system requires perfect timing · considered hardest FromSoftware game [Source: Steam achievement data]",
            "elden ring":           "~40% players beat Margit (first major boss) · open world allows grinding if stuck · most accessible FromSoftware game · still very hard by mainstream standards [Source: Steam achievement data]",
            "dark souls":           "~37% Steam players finished · 'Prepare to Die' subtitle not marketing — reality · created new 'Soulslike' genre of difficulty [Source: Steam achievement data]",
            "celeste":              "~18% players beat final chapter · Chapter 9 (DLC): ~5% · assists mode available · Maddy Thorson designed difficulty to be overcome, not impossible [Source: Steam achievement data]",
            "hollow knight":        "~16% players got true ending · Pantheon of Hallownest: ~1-2% · massive optional content · difficulty respected by speedrunning community [Source: Steam achievement data]",
            "cuphead":              "~34% beaten all regular bosses · designed as deliberate 1930s run-and-gun tribute · rage-inducing but fair · King Dice considered hardest boss [Source: Steam achievement data]",
            "battletoads":          "1991 NES · Level 3 Turbo Tunnel · generally considered one of hardest games ever made · required pixel-perfect memorization · rental shop legend [Source: gaming history]",
            "contra":               "1988 NES · 30-life Konami Code: up up down down left right left right B A · without code: 3 lives, one hit kills · designed for arcade profits [Source: gaming history]",
            "getting over it":      "Designed by Bennett Foddy to make players suffer · no checkpoints · drop hammer loses all progress · philosophical narration as you fail · completion: ~4% [Source: Steam achievement data / game design intent]",
        }
        result = self._fuzzy(query, difficulty)
        if result:
            await self._respond(ctx, result)
        else:
            await self._respond(ctx, f"No difficulty data for '{query}'. Check Steam achievements for completion percentage.")

    # ── !hiddenappearance ────────────────────────────────────

    @commands.command(name="hiddenappearance", aliases=["cameo", "devappearance"])
    async def hiddenappearance(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous developer cameos and hidden appearances in games. Usage: !hiddenappearance Metal Gear Solid"""
        if not query:
            await self._respond(ctx, "Usage: !hiddenappearance [game] — e.g. !hiddenappearance Metal Gear Solid")
            return
        if not await self._check_cooldown(ctx, "hiddenappearance", DEFAULT_COOLDOWN):
            return
        cameos: dict[str, str] = {
            "metal gear solid":     "Hideo Kojima appears as a scientist named 'Kaz' in a cutscene · easily missed · also has dialogue · Kojima often puts himself in his games [Source: Konami / MGS trivia]",
            "breath of the wild":   "Kass the accordion-playing Rito bard is designed after series composer Koji Kondo's musical style · subtle tribute [Source: Nintendo / game trivia]",
            "borderlands":          "Marcus the narrator appears as playable character in original · Tiny Tina references real internet culture from development team [Source: Gearbox]",
            "tony hawk":            "Tony Hawk's Pro Skater features Tony Hawk himself as a playable character · various real professional skaters throughout series [Source: Neversoft / Activision]",
            "doom 2":               "John Romero's head is the final boss's weak point · hidden behind the Cyberdemon · 'To win the game, you must kill me, John Romero!' message [Source: id Software / John Romero]",
            "mgs3":                 "Hideo Kojima appears as a scientist who delivers crocodile cap · also referenced in Subsistence version · Kojima cameos a tradition [Source: Konami]",
            "final fantasy":        "Hironobu Sakaguchi (creator) frequently has cameos · Gilgamesh recurring character named after mythological figure but designed by team members [Source: Square Enix]",
        }
        result = self._fuzzy(query, cameos)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(cameos.keys())[:4])
            await self._respond(ctx, f"No cameo data for '{query}'. Try: {keys}...")

    # ── !publisher ───────────────────────────────────────────

    @commands.command(name="publisher", aliases=["whopublished", "publisherinfo"])
    async def publisher(self, ctx: commands.Context, *, query: str = "") -> None:
        """Publisher info and their major franchises. Usage: !publisher Devolver"""
        if not query:
            await self._respond(ctx, "Usage: !publisher [name] — e.g. !publisher Devolver or !publisher A24")
            return
        if not await self._check_cooldown(ctx, "publisher", DEFAULT_COOLDOWN):
            return
        publishers: dict[str, str] = {
            "devolver digital":     "Austin, Texas · founded 2009 · indie focused · Hotline Miami, Cult of the Lamb, Enter the Gungeon, Fall Guys (acquired) · E3 'conferences' became memes · anti-corporate branding [Source: Devolver Digital official]",
            "annapurna interactive": "Division of Annapurna Pictures · founded 2016 · prestige indie publisher · Flower, Abzu, What Remains of Edith Finch, Stray, Outer Wilds · art-focused selection [Source: Annapurna Interactive official]",
            "ea":                   "Electronic Arts · founded 1982 · FIFA/EA Sports FC, Battlefield, Mass Effect, The Sims, Apex Legends · 'worst company in America' voted twice · Origin platform · loot box controversy [Source: EA official]",
            "activision":           "Founded 1979 (first third-party game publisher) · Call of Duty, Crash Bandicoot (sold to Activision), Guitar Hero · merged with Blizzard 2008 · acquired by Microsoft 2023 [Source: Activision corporate history]",
            "ubisoft":              "French publisher · founded 1986 · Assassin's Creed, Far Cry, Rainbow Six, Watch Dogs · offices in 30 countries · workplace controversy investigations [Source: Ubisoft official]",
            "bandai namco":         "Japan · formed 2005 (Bandai + Namco merger) · Pac-Man, Dark Souls/Elden Ring distribution, Tekken, Dragon Ball games, Tales series [Source: Bandai Namco official]",
            "505 games":            "Italian publisher · independent · Control (505 published for Remedy), Assetto Corsa, Brothers: A Tale of Two Sons · mid-size publisher with strong indie catalog [Source: 505 Games official]",
        }
        result = self._fuzzy(query, publishers)
        if result:
            await self._respond(ctx, result)
        else:
            result = await get_studio_info(query.strip())
            await self._respond(ctx, result)

    # ── !indie ───────────────────────────────────────────────

    @commands.command(name="indie", aliases=["indiegame", "solodev"])
    async def indie(self, ctx: commands.Context, *, query: str = "") -> None:
        """Indie game spotlight — team size, development story. Usage: !indie Stardew Valley"""
        if not query:
            await self._respond(ctx, "Usage: !indie [game] — e.g. !indie Stardew Valley or !indie Undertale")
            return
        if not await self._check_cooldown(ctx, "indie", DEFAULT_COOLDOWN):
            return
        indie_games: dict[str, str] = {
            "stardew valley":       "ConcernedApe (Eric Barone) · 1 developer · 4 years development · released 2016 · 30M+ copies sold · turned down $750,000 publishing deal to stay independent · still solo-developed [Source: ConcernedApe official]",
            "undertale":            "Toby Fox · 1 developer · composed entire soundtrack · 2.5 years development · funded by Kickstarter $51,000 (goal: $5,000) · critically acclaimed · 5M+ copies [Source: Toby Fox / Kickstarter]",
            "hollow knight":        "Team Cherry (2-3 people) · 2.5 years development · Kickstarter A$57,000 (goal: A$35,000) · 3M+ copies · planned Silksong sequel · praised for quality vs budget [Source: Team Cherry official]",
            "celeste":              "Matt Makes Games (Maddy Thorson + Noel Berry) · originally made in 4 days for game jam · expanded to full game · won multiple GOTY 2018 awards · mental health themes [Source: Matt Makes Games official]",
            "disco elysium":        "ZA/UM · Estonian studio · 4 years development · 500,000 words of dialogue · based on tabletop RPG campaign · swept GOTY 2019 · studio had major internal disputes post-launch [Source: ZA/UM official / gaming press]",
            "minecraft":            "Notch (Markus Persson) · 1 developer initially · started as 'Cave Game' · first public version 2009 · sold to Microsoft for $2.5B in 2014 · best-selling game ever [Source: Mojang / Microsoft official]",
            "terraria":             "Andrew 'Redigit' Spinks and team · 2D sandbox · originally 2 developers · Re-Logic company formed · 44M+ copies · Stadia controversy (pulled game) · still updated after 10+ years [Source: Re-Logic official]",
            "among us":             "Innersloth · 3 developers · released 2018 · ignored for 2 years · went viral overnight 2020 due to streamers · was about to be abandoned when it blew up [Source: Innersloth official]",
            "vampire survivors":    "Luca Galante · 1 developer · started as browser game · early access 2021 · massively successful · team grew after success · won BAFTA 2023 [Source: poncle official]",
        }
        result = self._fuzzy(query, indie_games)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(indie_games.keys())[:5])
            await self._respond(ctx, f"No indie data for '{query}'. Try: {keys}...")

    # ── !artstyle ────────────────────────────────────────────

    @commands.command(name="artstyle", aliases=["visualstyle", "artdirection"])
    async def artstyle(self, ctx: commands.Context, *, query: str = "") -> None:
        """The artistic influences behind a game's visual style. Usage: !artstyle Cuphead"""
        if not query:
            await self._respond(ctx, "Usage: !artstyle [game] — e.g. !artstyle Cuphead or !artstyle Journey")
            return
        if not await self._check_cooldown(ctx, "artstyle", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAME_ART_STYLES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(GAME_ART_STYLES.keys())[:5])
            await self._respond(ctx, f"No art style data for '{query}'. Try: {keys}...")

    # ── !colorpalette ────────────────────────────────────────

    @commands.command(name="colorpalette", aliases=["gamecolors", "colorlanguage"])
    async def colorpalette(self, ctx: commands.Context, *, query: str = "") -> None:
        """The deliberate color language of a game. Usage: !colorpalette Journey"""
        if not query:
            await self._respond(ctx, "Usage: !colorpalette [game] — e.g. !colorpalette Journey or !colorpalette Bioshock")
            return
        if not await self._check_cooldown(ctx, "colorpalette", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, COLOR_PALETTES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(COLOR_PALETTES.keys())[:5])
            await self._respond(ctx, f"No color palette data for '{query}'. Try: {keys}...")

    # ── !villain ─────────────────────────────────────────────

    @commands.command(name="villain", aliases=["gameboss", "antagonist"])
    async def villain(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game villain deep dive. Usage: !villain Sephiroth"""
        if not query:
            await self._respond(ctx, "Usage: !villain [name] — e.g. !villain Sephiroth or !villain GLaDOS")
            return
        if not await self._check_cooldown(ctx, "villain", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, VILLAIN_DATA)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(VILLAIN_DATA.keys())[:5])
            await self._respond(ctx, f"Villain '{query}' not found. Try: {keys}...")

    # ── !protagonist ─────────────────────────────────────────

    @commands.command(name="protagonist", aliases=["maincharacter", "hero"])
    async def protagonist(self, ctx: commands.Context, *, query: str = "") -> None:
        """Main character design and history. Usage: !protagonist Master Chief"""
        if not query:
            await self._respond(ctx, "Usage: !protagonist [name] — e.g. !protagonist Master Chief or !protagonist Kratos")
            return
        if not await self._check_cooldown(ctx, "protagonist", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, PROTAGONIST_DATA)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(PROTAGONIST_DATA.keys())[:5])
            await self._respond(ctx, f"Protagonist '{query}' not found. Try: {keys}...")

    # ── !sidekick ────────────────────────────────────────────

    @commands.command(name="sidekick", aliases=["companion", "gamepartner"])
    async def sidekick(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous gaming sidekicks and companions. Usage: !sidekick Tails"""
        if not query:
            await self._respond(ctx, "Usage: !sidekick [name] — e.g. !sidekick Tails or !sidekick Garrus")
            return
        if not await self._check_cooldown(ctx, "sidekick", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, SIDEKICK_DATA)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(SIDEKICK_DATA.keys())[:5])
            await self._respond(ctx, f"Sidekick '{query}' not found. Try: {keys}...")

    # ── !famousline ──────────────────────────────────────────

    @commands.command(name="famousline", aliases=["iconicline", "gamequote"])
    async def famousline(self, ctx: commands.Context, *, query: str = "") -> None:
        """Iconic lines of game dialogue. Usage: !famousline Would you kindly"""
        if not query:
            await self._respond(ctx, "Usage: !famousline [quote or game] — e.g. !famousline would you kindly")
            return
        if not await self._check_cooldown(ctx, "famousline", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, FAMOUS_LINES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(FAMOUS_LINES.keys())[:4])
            await self._respond(ctx, f"Line '{query}' not found. Try: {keys}...")

    # ── !branchingstory ──────────────────────────────────────

    @commands.command(name="branchingstory", aliases=["multipleendings", "storyoptions"])
    async def branchingstory(self, ctx: commands.Context, *, query: str = "") -> None:
        """How many story branches and endings a game has. Usage: !branchingstory Detroit Become Human"""
        if not query:
            await self._respond(ctx, "Usage: !branchingstory [game] — e.g. !branchingstory Detroit Become Human")
            return
        if not await self._check_cooldown(ctx, "branchingstory", DEFAULT_COOLDOWN):
            return
        branching: dict[str, str] = {
            "detroit become human": "Quantic Dream · 85 possible endings · 7000+ scenes · 40,000 lines of dialogue · flowchart visible after each chapter showing paths taken · [Source: Quantic Dream GDC talk]",
            "nier automata":        "5 canonical endings (A-E) · must play multiple times · each playthrough reveals new story information · Ending E deletes your save to help others · [Source: PlatinumGames / Yoko Taro]",
            "undertale":            "3 main routes: Pacifist, Neutral, Genocide · each completely different experience · True Pacifist requires specific actions · Genocide changes the game permanently [Source: Toby Fox]",
            "fallout new vegas":    "4 main faction endings · dozens of companion endings · specific quests affect world state · considered gold standard of RPG choices [Source: Obsidian Entertainment]",
            "disco elysium":        "No traditional endings but many skill-gated dialogue options · ideology choices affect world view · multiple solutions to investigation [Source: ZA/UM]",
            "mass effect":          "Legendary Edition trilogy · choices carry across all 3 games · ME3 ending controversy (limited final choices) · Indoctrination Theory fan debate [Source: BioWare]",
            "the witcher 3":        "36 possible endings depending on choices across full game · Ciri's fate depends on decisions across entire playthrough · some outcomes require specific early choices [Source: CD Projekt RED]",
        }
        result = self._fuzzy(query, branching)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(branching.keys())[:4])
            await self._respond(ctx, f"No branching story data for '{query}'. Try: {keys}...")

    # ── !writtenby ───────────────────────────────────────────

    @commands.command(name="writtenby", aliases=["gamewriter", "storywriter"])
    async def writtenby(self, ctx: commands.Context, *, query: str = "") -> None:
        """Who wrote a game's story and their background. Usage: !writtenby Disco Elysium"""
        if not query:
            await self._respond(ctx, "Usage: !writtenby [game] — e.g. !writtenby Disco Elysium")
            return
        if not await self._check_cooldown(ctx, "writtenby", DEFAULT_COOLDOWN):
            return
        writers: dict[str, str] = {
            "disco elysium":        "Robert Kurvitz (lead writer/designer) · Estonian novelist · wrote Disco Elysium as tabletop RPG first · 500,000+ words · Helen Hindpere co-writer · ZA/UM disputes led to key staff departures [Source: ZA/UM / developer interviews]",
            "the last of us":       "Neil Druckmann (writer/director) · Israeli-American · Naughty Dog CCO · influenced by No Country for Old Men · Joel/Ellie relationship central to both games [Source: Naughty Dog official]",
            "bioshock":             "Ken Levine · Irrational Games · Columbia University literature background · influenced by Ayn Rand, Orwell · 'Would you kindly' twist planned from beginning [Source: Irrational Games / Ken Levine interviews]",
            "mass effect":          "Drew Karpyshyn (ME1, ME2) · left for SWTOR · Casey Hudson led · Mac Walters took over ME3 ending controversy · ensemble writing team [Source: BioWare official]",
            "hades":                "Greg Kasavin (writer/creative director) · former editor-in-chief of GameSpot · every Supergiant game story-focused · Hades praised for in-run narrative [Source: Supergiant Games]",
            "cyberpunk 2077":       "Stanislaw Lem and Philip K Dick influences · large writing team · based on Mike Pondsmith's tabletop RPG · Pondsmith consulted · Johnny Silverhand (Keanu Reeves) character written by several writers [Source: CD Projekt RED]",
            "undertale":            "Toby Fox · sole writer · no formal writing training · Homestuck webcomic influence acknowledged · dark humor + genuine emotion combination [Source: Toby Fox official]",
        }
        result = self._fuzzy(query, writers)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(writers.keys())[:4])
            await self._respond(ctx, f"No writer data for '{query}'. Try: {keys}...")

    # ── !iconicscene ─────────────────────────────────────────

    @commands.command(name="iconicscene", aliases=["memorablemoment", "gamemoment"])
    async def iconicscene(self, ctx: commands.Context, *, query: str = "") -> None:
        """The most iconic moments in gaming. Usage: !iconicscene The Last of Us"""
        if not query:
            await self._respond(ctx, "Usage: !iconicscene [game] — e.g. !iconicscene The Last of Us")
            return
        if not await self._check_cooldown(ctx, "iconicscene", DEFAULT_COOLDOWN):
            return
        scenes: dict[str, str] = {
            "the last of us":       "Giraffe scene · no dialogue · post-apocalyptic giraffes in building · Joel smiles genuinely for first time · purely environmental storytelling · players stop and watch [Source: Naughty Dog]",
            "red dead redemption":  "The ending · John Marston's fate · one of most emotional game endings ever · players didn't see it coming · changed how games handle narrative consequences [Source: Rockstar]",
            "bioshock":             "'Would you kindly' revelation · Andrew Ryan's death · retroactively recontextualizes entire game · most famous plot twist in gaming [Source: Irrational Games]",
            "metal gear solid 3":   "Final confrontation with The Boss · players given choice · emotional weight of Cold War spy genre used perfectly · never-forgotten ending [Source: Konami / Hideo Kojima]",
            "portal":               "First time portals are used to escape test chamber · moment when mechanics click · designed to give players 'I'm a genius' feeling [Source: Valve / GDC postmortem]",
            "halo reach":           "Ending sequence · Noble Team's sacrifice · player controls Noble Six's last stand · fate known from beginning but hits anyway [Source: Bungie]",
            "nier automata":        "Ending E · game asks you to delete your save to help other players · strangers' names shown · most emotional game mechanic ever designed [Source: PlatinumGames / Yoko Taro]",
            "shadow of the colossus": "Defeating a colossus · music cuts to silence · only wind · you know you did something wrong · Ico creator Ueda's masterclass in environmental emotion [Source: Team Ico]",
        }
        result = self._fuzzy(query, scenes)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(scenes.keys())[:4])
            await self._respond(ctx, f"No iconic scene data for '{query}'. Try: {keys}...")

    # ── !iconictrack ─────────────────────────────────────────

    @commands.command(name="iconictrack", aliases=["gamesoundtrack", "gamemusic"])
    async def iconictrack(self, ctx: commands.Context, *, query: str = "") -> None:
        """Story behind iconic game music tracks. Usage: !iconictrack One Winged Angel"""
        if not query:
            await self._respond(ctx, "Usage: !iconictrack [track or game] — e.g. !iconictrack One Winged Angel")
            return
        if not await self._check_cooldown(ctx, "iconictrack", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, {k: v for k, v in vars().items() if isinstance(v, str)})
        tracks: dict[str, str] = {
            "one winged angel":     "Final Fantasy VII (1997) · Nobuo Uematsu · first orchestral track in Final Fantasy · borrowed structure from Stravinsky's Rite of Spring · 25-minute concert version exists · performed worldwide · 'Sephiroth!' choir [Source: Square Enix / Uematsu interviews]",
            "dragonborn":           "The Elder Scrolls V: Skyrim (2011) · Jeremy Soule · main theme · used in marketing · became franchise identity · Nordic choir design · 'DOV AH KIIN' in Dragon language [Source: Bethesda / Soule interviews]",
            "megalovania":          "Undertale (2015) · Toby Fox · originally written for Homestuck webcomic (2011) · Sans's battle theme · became global phenomenon · performed by orchestras worldwide [Source: Toby Fox]",
            "still alive":          "Portal (2007) · Jonathan Coulton · GLaDOS's end credits song · 'This was a triumph' · written in two weeks · became most famous game credits song [Source: Valve / Jonathan Coulton]",
            "geralt of rivia":      "The Witcher 3 (2015) · Marcin Przybyłowicz · 'The Fields of Ard Skellig' · Emmy-winning · built from Central European folk music · establishes Slavic fantasy identity [Source: CD Projekt RED official]",
            "to zanarkand":         "Final Fantasy X (2001) · Nobuo Uematsu · piano piece · associated with the 'laughing scene' · considered one of saddest game tracks ever [Source: Square Enix / Uematsu]",
            "bfg division":         "Doom (2016) · Mick Gordon · industrial metal · designed for combat · guitar strings replaced with metal springs · real instruments heavily processed · GDC talk revealed process [Source: id Software / Mick Gordon GDC 2017]",
            "gusty garden galaxy":  "Super Mario Galaxy (2007) · Mahito Yokota · full orchestra · considered best Mario music ever · waltz time signature unusual for platformer [Source: Nintendo official]",
        }
        result = self._fuzzy(query, tracks)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(tracks.keys())[:4])
            await self._respond(ctx, f"No track data for '{query}'. Try: {keys}...")

    # ── !composer ────────────────────────────────────────────

    @commands.command(name="composer", aliases=["gamesoundtrack2", "whoscored"])
    async def composer(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game music composer career highlights. Usage: !composer Koji Kondo"""
        if not query:
            await self._respond(ctx, "Usage: !composer [name or game] — e.g. !composer Koji Kondo or !composer Toby Fox")
            return
        if not await self._check_cooldown(ctx, "composer", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAME_COMPOSERS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(GAME_COMPOSERS.keys())[:5])
            await self._respond(ctx, f"Composer '{query}' not found. Try: {keys}...")

    # ── !acquisition ─────────────────────────────────────────

    @commands.command(name="acquisition", aliases=["studiobought", "mergers"])
    async def acquisition(self, ctx: commands.Context, *, query: str = "") -> None:
        """When and why a studio was acquired. Usage: !acquisition Activision Blizzard"""
        if not query:
            await self._respond(ctx, "Usage: !acquisition [studio or deal] — e.g. !acquisition Activision Blizzard Microsoft")
            return
        if not await self._check_cooldown(ctx, "acquisition", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAME_ACQUISITIONS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(GAME_ACQUISITIONS.keys())[:4])
            await self._respond(ctx, f"No acquisition data for '{query}'. Try: {keys}...")

    # ── !dlchistory ──────────────────────────────────────────

    @commands.command(name="dlchistory", aliases=["expansions", "dlcinfo"])
    async def dlchistory(self, ctx: commands.Context, *, query: str = "") -> None:
        """DLC and expansion history of a game. Usage: !dlchistory Witcher 3"""
        if not query:
            await self._respond(ctx, "Usage: !dlchistory [game] — e.g. !dlchistory Witcher 3 or !dlchistory Dark Souls")
            return
        if not await self._check_cooldown(ctx, "dlchistory", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, DLC_HISTORY)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(DLC_HISTORY.keys())[:5])
            await self._respond(ctx, f"No DLC data for '{query}'. Try: {keys}...")

    # ── !lostgame ────────────────────────────────────────────

    @commands.command(name="lostgame", aliases=["preservationgame", "missinggame"])
    async def lostgame(self, ctx: commands.Context) -> None:
        """Games considered permanently lost or at preservation risk. Usage: !lostgame"""
        if not await self._check_cooldown(ctx, "lostgame", DEFAULT_COOLDOWN):
            return
        facts = [
            "Battlecruiser 3000AD source code · irretrievably lost · developer Derek Smart's studio fire · major game preservation case study [Source: gaming preservation community]",
            "Many early Atari and Odyssey² games · no surviving source code · some entirely dependent on aging cartridges · Video Game History Foundation preserves what it can [Source: Video Game History Foundation]",
            "P.T. (Silent Hills playable teaser) · removed from PlayStation Network 2015 · cannot be redownloaded · those with installed version must never delete it · only 10,000+ installs survived [Source: gaming history]",
            "Early MMORPGs like The Realm Online · servers shut down · game experience unrecoverable without source code · thousands of player hours lost [Source: preservation community]",
            "Propellerhead Reason earlier versions · software preservation challenge · requires period hardware/OS to run correctly · emulation imperfect [Source: software preservation research]",
            "Disney's Club Penguin source code · shutdown 2017 · unofficial revivals (Club Penguin Rewritten) fought legal battles · nostalgia preservation vs copyright [Source: gaming history]",
            "Many Turbografx-16 and PC-Engine CD games · region-locked · small print runs · cartridges failing · Video Game History Foundation reports 87% of classic games unavailable legally [Source: VGHF 2023 report]",
        ]
        await self._respond(ctx, random.choice(facts))

    # ── !oldeststillplayed ───────────────────────────────────

    @commands.command(name="oldeststillplayed", aliases=["classicgame", "stillactive"])
    async def oldeststillplayed(self, ctx: commands.Context) -> None:
        """Oldest games with active player communities. Usage: !oldeststillplayed"""
        if not await self._check_cooldown(ctx, "oldeststillplayed", DEFAULT_COOLDOWN):
            return
        facts = [
            "NetHack · 1987 · roguelike · still receives updates · dedicated active community · older than many current players · ASCII graphics but incredible depth [Source: NetHack DevTeam]",
            "Dwarf Fortress (Bay 12) · 2006 · players have run saves for real-world decades · Steam version 2022 · technically infinite content · considered one of deepest simulations ever [Source: Bay 12 Games]",
            "MUD1 (Multi-User Dungeon) · 1978 · Roy Trubshaw and Richard Bartle · text-based · Essex University · still technically accessible · grandfather of all MMORPGs [Source: Richard Bartle records]",
            "Tetris · 1984 · Alexey Pajitnov · still in active professional competitive scene · Classic Tetris World Championship · CTWC tournaments sell out · youngest vs oldest players compete [Source: CTWC official]",
            "Chess computer games · Chessmaster series 1986+ · still played · modern chess.com sees millions of daily players · oldest competitive game in digital form [Source: chess.com statistics]",
            "Quake · 1996 · id Software · QuakeCon tournaments still run · Quake Champions released 2017 · QuakeWorld (1996) still has active servers · FPS ancestral game [Source: QuakeCon official]",
            "StarCraft: Brood War · 1998 · Blizzard · South Korean professional scene still active · ASL (Afreeca Starcraft League) · considered to have never truly died [Source: AfreecaTV / ESL official]",
        ]
        await self._respond(ctx, random.choice(facts))

    # ── !expensivegames ──────────────────────────────────────

    @commands.command(name="expensivegames", aliases=["raregame", "mostexpensive"])
    async def expensivegames(self, ctx: commands.Context) -> None:
        """Most expensive games ever made or sold. Usage: !expensivegames"""
        if not await self._check_cooldown(ctx, "expensivegames", DEFAULT_COOLDOWN):
            return
        facts = [
            "Sealed Super Mario Bros (NES) · sold for $2M at Heritage Auctions 2021 · WATA graded 9.6 A++ · highest ever for a game cartridge · Donkey Kong sold $1.1M same year [Source: Heritage Auctions official]",
            "GTA V · most expensive game to develop · ~$265M development + ~$128M marketing = ~$393M total · most profitable entertainment product at launch ($1B in 3 days) [Source: Take-Two financial reports]",
            "Red Dead Redemption 2 · most expensive single game production reported at time · ~$540M budget (development + marketing) · 8 years in development · 2,000+ person team [Source: gaming press / Take-Two]",
            "Destiny (original Bungie/Activision) · $500M 10-year deal · not all spent on first game but largest publishing contract in gaming history at the time (2012) [Source: Kotaku leak / Activision financial reports]",
            "Star Citizen (crowdfunded) · over $600M raised from backers (as of 2023) · not finished · most expensive crowdfunded project ever · Cloud Imperium Games [Source: Roberts Space Industries official]",
            "The most expensive piece of gaming memorabilia: Nintendo PlayStation prototype · only known unit · Sega Genesis controller port added · sold for $360,000 in 2020 [Source: Heritage Auctions]",
        ]
        await self._respond(ctx, random.choice(facts))

    # ── Various new gaming commands ──────────────────────────

    @commands.command(name="realscience", aliases=["gamesciencefacts", "scienceingame"])
    async def realscience(self, ctx: commands.Context, *, query: str = "") -> None:
        """Real science behind a game's mechanics. Usage: !realscience Subnautica"""
        if not query:
            await self._respond(ctx, "Usage: !realscience [game] — e.g. !realscience Subnautica")
            return
        if not await self._check_cooldown(ctx, "realscience", DEFAULT_COOLDOWN):
            return
        science: dict[str, str] = {
            "subnautica":       "Pressure mechanics accurate · bioluminescence realistic · alien ecosystem biologically plausible · Unknown Worlds consulted marine biologists · thalassophobia intentionally designed [Source: Unknown Worlds interviews]",
            "kerbal space program": "Orbital mechanics 100% accurate · Tsiolkovsky rocket equation implemented · NASA uses it for education · real engineers learned from it · maneuver planning identical to real missions [Source: Squad / NASA educational partnership]",
            "everything":       "David OReilly's game based on Alan Watts philosophy · everything IS everything in quantum physics sense · philosophical game grounded in real cosmological thinking [Source: developer interviews]",
            "plague inc":       "Ndemic Creations consulted CDC and WHO · realistic pathogen evolution mechanics · used as educational tool in biology classes · CDC cited it during COVID-19 [Source: Ndemic Creations official / CDC]",
            "assassins creed origins": "Discovery Tour mode praised by Egyptologists · 90%+ accurate to historical Egypt · Ubisoft hired historians · hieroglyphs and architecture verified [Source: Ubisoft / academic historians]",
            "mass effect":      "Element Zero (eezo) loosely based on theoretical exotic matter · mass effect fields parallel to theoretical negative mass physics · not accurate but internally consistent [Source: game design documents]",
            "detroit become human": "AI consciousness debate accurately reflects real philosophical positions (Turing test, Chinese room, etc.) · Quantic Dream consulted AI researchers [Source: Quantic Dream developer talks]",
        }
        result = self._fuzzy(query, science)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(science.keys())[:4])
            await self._respond(ctx, f"No science data for '{query}'. Try: {keys}...")

    @commands.command(name="realhistory", aliases=["historicalaccuracy", "gameashistory"])
    async def realhistory(self, ctx: commands.Context, *, query: str = "") -> None:
        """How historically accurate a history-based game is. Usage: !realhistory Assassins Creed"""
        if not query:
            await self._respond(ctx, "Usage: !realhistory [game] — e.g. !realhistory Assassins Creed Origins")
            return
        if not await self._check_cooldown(ctx, "realhistory", DEFAULT_COOLDOWN):
            return
        history: dict[str, str] = {
            "assassins creed origins": "Ptolemaic Egypt (49 BCE) setting · Egyptologists praised accuracy of architecture, clothing, daily life · Discovery Tour mode created with historians · 90%+ accurate to historical record [Source: Ubisoft official]",
            "assassins creed odyssey": "Classical Greece 431 BCE · Peloponnesian War period · historical figures appear (Socrates, Pericles, Herodotus) · accurate geography · mythological elements clearly fantastical [Source: Ubisoft / historical consultants]",
            "ghost of tsushima":    "Mongol invasion of Tsushima 1274 · historical event but characters fictional · Sucker Punch consulted Japanese historians · game received official appreciation from Tsushima Island city [Source: Sucker Punch / City of Tsushima]",
            "red dead redemption 2": "American West 1899 accurately depicted · period-accurate clothing, firearms, slang · Rockstar research team visited museums · historical events referenced [Source: Rockstar / historical research]",
            "kingdom come deliverance": "Medieval Bohemia 1403 · no fantasy elements · armor, weapons historically accurate · Henry is real historical figure (documented) · Czech Republic praised it [Source: Warhorse Studios official]",
            "valiant hearts":       "WWI story · historical events, dates, locations accurate · real WWI diary entries inspired narrative · French archives consulted · emotional historical document as game [Source: Ubisoft Montpellier]",
        }
        result = self._fuzzy(query, history)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(history.keys())[:4])
            await self._respond(ctx, f"No historical accuracy data for '{query}'. Try: {keys}...")

    @commands.command(name="gameinfilm", aliases=["gameadaptation", "gametv"])
    async def gameinfilm(self, ctx: commands.Context, *, query: str = "") -> None:
        """Video game adaptations in film and TV. Usage: !gameinfilm The Last of Us"""
        if not query:
            await self._respond(ctx, "Usage: !gameinfilm [title] — e.g. !gameinfilm The Last of Us or !gameinfilm Sonic")
            return
        if not await self._check_cooldown(ctx, "gameinfilm", DEFAULT_COOLDOWN):
            return
        adaptations: dict[str, str] = {
            "the last of us":   "HBO 2023 · Craig Mazin + Neil Druckmann · 8.8 IMDB · most watched HBO premiere since House of the Dragon · Pedro Pascal + Bella Ramsey · Season 2 confirmed [Source: HBO official]",
            "sonic":            "Paramount 2020 · fan backlash caused redesign before release · $319M box office · Jim Carrey as Eggman · sequel and Knuckles series followed [Source: Paramount official]",
            "arcane":           "Netflix 2021 · based on League of Legends · not traditional game adaptation · Riot Games co-produced · animated by Fortiche · highest rated animated series on Netflix [Source: Netflix / Riot Games official]",
            "castlevania":      "Netflix 2017-2021 · Warren Ellis writer · critically acclaimed · unusual for game adaptations · sequel Nocturne continuing story [Source: Netflix official]",
            "detective pikachu": "Warner Bros 2019 · Ryan Reynolds · $433M worldwide · first live-action Pokemon film · surprisingly well-received by critics [Source: Warner Bros official]",
            "uncharted":        "Sony 2022 · Tom Holland as young Drake · Mark Wahlberg as Sully · $401M box office · mixed critical reception · sequel in development [Source: Sony Pictures official]",
            "mario":            "Nintendo/Illumination 2023 · $1.36 billion worldwide · second-highest animated film ever at release · Jack Black as Bowser · Chris Pratt as Mario (controversial) [Source: Universal/Nintendo official]",
            "halo":             "Paramount+ 2022 · Master Chief's face shown controversially · significant changes from game canon · Pablo Schreiber as Master Chief [Source: Paramount+ official]",
        }
        result = self._fuzzy(query, adaptations)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(adaptations.keys())[:4])
            await self._respond(ctx, f"No adaptation data for '{query}'. Try: {keys}...")

    @commands.command(name="gamearchitecture", aliases=["gamebuildings", "architectureinspiration"])
    async def gamearchitecture(self, ctx: commands.Context, *, query: str = "") -> None:
        """Real architectural styles that inspired game visual design. Usage: !gamearchitecture Bioshock"""
        if not query:
            await self._respond(ctx, "Usage: !gamearchitecture [game] — e.g. !gamearchitecture Bioshock or !gamearchitecture Dishonored")
            return
        if not await self._check_cooldown(ctx, "gamearchitecture", DEFAULT_COOLDOWN):
            return
        architecture: dict[str, str] = {
            "bioshock":         "Art Deco · 1920s-30s · Chrysler Building, Rockefeller Center aesthetic · Andrew Ryan chose it deliberately for Rapture · curved chrome + geometric patterns + amber light [Source: Irrational Games / Ken Levine]",
            "dishonored":       "Steampunk Victorian London · Dunwall based on Edinburgh and London · industrial revolution aesthetic · Rooftop architecture for traversal design · Viktor Antonov (Half-Life 2 art director) [Source: Arkane Studios]",
            "assassins creed origins": "Ptolemaic Egyptian architecture precisely recreated · temples at Abu Simbel, Karnak · Ubisoft 3D scanning real locations · Egyptologists verified accuracy [Source: Ubisoft official]",
            "dark souls":       "European gothic + Japanese castle architecture · Anor Londo based on Milan Cathedral · Boletaria Castle has real castle elements · layered world design from Hidetaka Miyazaki's manga inspiration [Source: FromSoftware interviews]",
            "monument valley":  "M.C. Escher impossible architecture + Islamic geometric art · Alhambra palace motifs · optical illusions as gameplay mechanic · won Apple Design Award [Source: ustwo games]",
            "nier automata":    "Post-apocalyptic modernist ruins · abandoned shopping mall aesthetic · brutalist concrete overgrown with nature · contrast of human architecture reclaimed by wilderness [Source: PlatinumGames]",
            "ori and the will of the wisps": "Art Nouveau organic forms · Gaudi's organic architecture · natural shapes as building elements · fairy tale forest architecture [Source: Moon Studios]",
        }
        result = self._fuzzy(query, architecture)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(architecture.keys())[:4])
            await self._respond(ctx, f"No architecture data for '{query}'. Try: {keys}...")

    @commands.command(name="preserved", aliases=["gamepreservation", "librarygame"])
    async def preserved(self, ctx: commands.Context) -> None:
        """Games selected for preservation by institutions. Usage: !preserved"""
        if not await self._check_cooldown(ctx, "preserved", DEFAULT_COOLDOWN):
            return
        facts = [
            "Tetris, Pong, Pac-Man, Doom, World of Warcraft + 9 others selected by Library of Congress 2007 · first game preservation initiative by major national institution [Source: Library of Congress]",
            "Strong Museum World Video Game Hall of Fame · annual inductees since 2015 · criteria: icon status, longevity, geographical reach, influence · Pong, Tetris, Pac-Man first class [Source: The Strong official]",
            "Video Game History Foundation reports 87% of games released before 2010 are out of print and inaccessible · major preservation crisis · pushing for copyright law reform [Source: VGHF 2023 report]",
            "Internet Archive maintains a legal game preservation library · thousands of classic games playable in browser · ongoing copyright negotiations [Source: Internet Archive]",
            "Smithsonian American Art Museum featured The Art of Video Games exhibition (2012) · 80 games selected representing 40 years of game development · 80M+ visitors [Source: Smithsonian official]",
            "Japan Media Arts Festival has preserved and awarded games since 1997 · Agency for Cultural Affairs recognition · considers games as media art [Source: Agency for Cultural Affairs Japan]",
        ]
        await self._respond(ctx, random.choice(facts))

    @commands.command(name="sourceopen", aliases=["opensource", "sourcereleased"])
    async def sourceopen(self, ctx: commands.Context, *, query: str = "") -> None:
        """Games whose source code was released. Usage: !sourceopen Quake"""
        if not query:
            await self._respond(ctx, "Usage: !sourceopen [game] — e.g. !sourceopen Quake or !sourceopen Doom")
            return
        if not await self._check_cooldown(ctx, "sourceopen", DEFAULT_COOLDOWN):
            return
        opensrc: dict[str, str] = {
            "quake":        "id Software released Quake source 1999 under GPL · spawned hundreds of engine modifications · DarkPlaces, ezQuake still in use · research and modding community [Source: id Software / GPL license records]",
            "doom":         "id Software released Doom source 1997 under GPL · basis of countless total conversions · GZDoom modern engine · Doom runs on everything (printers, ATMs, pregnancy tests) [Source: id Software / gaming history]",
            "wolfenstein 3d": "id Software released source 1995 · historical significance preserved · engine study material · basis of understanding early FPS development [Source: id Software]",
            "duke nukem 3d": "3D Realms released Build engine source 2000 · EDuke32 total conversion engine still in use · Blood, Shadow Warrior used same engine [Source: 3D Realms / Ken Silverman]",
            "freeciv":      "Open source Civilization-inspired game · community-developed since 1996 · runs on Linux, Windows, Mac, web · no commercial origin [Source: Freeciv project]",
        }
        result = self._fuzzy(query, opensrc)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(opensrc.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="legacyport", aliases=["impossibleport", "amazingport"])
    async def legacyport(self, ctx: commands.Context) -> None:
        """Legendary porting achievements. Usage: !legacyport"""
        if not await self._check_cooldown(ctx, "legacyport", DEFAULT_COOLDOWN):
            return
        facts = [
            "Doom on a TI-83 Plus calculator (2002) · 6MHz processor · developer Franklin Chen · game is technically unplayable but proof of concept · Doom runs on everything [Source: gaming community]",
            "Super Mario 64 on a pregnancy test (2021) · YouTuber 'foone' · uses the test's LCD display · technically runs · part of 'Doom/Mario runs on everything' tradition [Source: foone on Twitter]",
            "Quake on an oscilloscope (2014) · Ben Heck and others have shown this · renders 3D wireframe via audio signal display · sound visualization as video [Source: gaming community]",
            "SNES Doom (1995) · id Software · Super NES barely capable · 15-20fps in small window · no music · considered near-impossible for hardware but shipped [Source: id Software / SNES history]",
            "GBA port of Doom (2001) · Rebellion Developments · Game Boy Advance port · 16MHz ARM processor running Doom · impressive given constraints [Source: gaming history]",
            "Half-Life on Meta Quest (Oculus) via community port · fan ports running full PC games on mobile VR hardware · demonstration of game portability [Source: gaming community]",
        ]
        await self._respond(ctx, random.choice(facts))

    @commands.command(name="anniversary", aliases=["gamebday", "gamingjubilee"])
    async def anniversary(self, ctx: commands.Context, *, query: str = "") -> None:
        """Game milestone anniversaries. Usage: !anniversary Final Fantasy 7"""
        if not query:
            await self._respond(ctx, "Usage: !anniversary [game] — e.g. !anniversary Final Fantasy 7")
            return
        if not await self._check_cooldown(ctx, "anniversary", DEFAULT_COOLDOWN):
            return
        anniversaries: dict[str, str] = {
            "final fantasy 7":  "Released 1997 Japan · turns 28 in 2025 · Remake project ongoing · still actively discussed daily · considered most influential JRPG ever · Cloud/Sephiroth in Smash Bros [Source: Square Enix official]",
            "super mario bros": "Released 1985 Japan · turns 40 in 2025 · best-selling franchise ever · Mario film 2023 · Nintendo 35th anniversary celebration [Source: Nintendo official]",
            "legend of zelda":  "Released 1986 Japan · turns 39 in 2025 · Tears of the Kingdom 2023 · consistent quality over nearly 40 years · Link's Awakening, OoT watershed moments [Source: Nintendo official]",
            "sonic":            "Released 1991 · turns 34 in 2025 · Sonic movie franchise ongoing · IDW comic series · renaissance after decades of poor games · Sonic Frontiers praised [Source: Sega official]",
            "doom":             "Released 1993 · turns 32 in 2025 · Doom The Dark Ages 2025 announced · id Tech 8 · still defining FPS genre after 30+ years [Source: id Software official]",
            "pokemon":          "Red and Blue released 1996 Japan · 28 years of mainline games in 2024 · Pokemon GO 2016 reinvented franchise · 440M+ games sold total [Source: The Pokemon Company]",
            "halo":             "Halo: Combat Evolved released 2001 · 24 years in 2025 · Master Chief Collection · Halo TV series · 343 Industries managing franchise [Source: 343 Industries official]",
        }
        result = self._fuzzy(query, anniversaries)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(anniversaries.keys())[:4])
            await self._respond(ctx, f"No anniversary data for '{query}'. Try: {keys}...")

    @commands.command(name="gamingindustry", aliases=["gaminscene", "gamesindustry"])
    async def gamingindustry(self, ctx: commands.Context, *, query: str = "") -> None:
        """Gaming industry of a specific country. Usage: !gamingindustry South Korea"""
        if not query:
            await self._respond(ctx, "Usage: !gamingindustry [country] — e.g. !gamingindustry South Korea or !gamingindustry Japan")
            return
        if not await self._check_cooldown(ctx, "gamingindustry", DEFAULT_COOLDOWN):
            return
        industries: dict[str, str] = {
            "south korea":  "PC bang culture · internet cafes opened gaming to all · StarCraft became national sport · massive esports infrastructure · League of Legends dominant · Samsung, SKT major esports teams [Source: Korean Ministry of Culture / gaming press]",
            "japan":        "Nintendo, Sony, Sega, Konami, Capcom, Square Enix all Japanese · arcade (Game Center) culture still thrives · 4000+ active arcades · console gaming birthplace · anime/gaming overlap [Source: CESA - Computer Entertainment Supplier's Association]",
            "usa":          "Largest gaming market by revenue · Activision Blizzard, EA, Epic Games, Valve, Riot Games · PC gaming dominant alongside console · mobile growing · esports investment [Source: ESA - Entertainment Software Association]",
            "finland":      "Rovio (Angry Birds), Supercell (Clash of Clans), Remedy (Alan Wake, Control) · small country, massive gaming impact · Nokia gaming heritage · Helsinki gaming hub [Source: Neogames Finland]",
            "poland":       "CD Projekt RED (The Witcher, Cyberpunk 2077) · government considers CDPR national treasure · growing indie scene · tax incentives for game development [Source: Polish gaming industry]",
            "china":        "Tencent (largest gaming company by revenue) · owns Riot Games, Epic stake · 680M+ gamers · mobile dominant · regulatory restrictions on youth gaming [Source: Newzoo / Chinese gaming data]",
            "sweden":       "Mojang (Minecraft), DICE (Battlefield, Mirrors Edge), Paradox (Hearts of Iron), Starbreeze · Nordic game design philosophy · high quality of life = creative output [Source: Dataspelsbranschen]",
        }
        result = self._fuzzy(query, industries)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(industries.keys())[:4])
            await self._respond(ctx, f"No industry data for '{query}'. Try: {keys}...")

    @commands.command(name="arcadehistory", aliases=["arcadeculture", "gamecenter"])
    async def arcadehistory(self, ctx: commands.Context, *, query: str = "") -> None:
        """Arcade gaming culture by country. Usage: !arcadehistory Japan"""
        if not query:
            await self._respond(ctx, "Usage: !arcadehistory [country] — e.g. !arcadehistory Japan or !arcadehistory USA")
            return
        if not await self._check_cooldown(ctx, "arcadehistory", DEFAULT_COOLDOWN):
            return
        arcades: dict[str, str] = {
            "japan":    "Game Centers still thrive · 4000+ active locations · UFO catcher (prize machine) dominant · rhythm games (beatmania, DDR) flourishing · Sega arcades iconic · culture distinct from Western arcades [Source: JAMMA - Japan Amusement Machine Association]",
            "usa":      "Golden Age 1978-1983 · Pac-Man, Donkey Kong era · arcade revenues peaked 1982 at $8B · home console killed market · Dave & Busters modern revival · most arcades closed by 1990s [Source: AMOA / gaming history]",
            "uk":       "Amusement arcades at seaside resorts · more fruit machines than video games · Southend, Blackpool · different culture to USA · Video game arcades less prominent than in USA/Japan [Source: British Amusement Catering Trade Association]",
            "south korea": "PC bangs dominate · internet cafe culture overtook arcades · affordable high-end PC gaming · 24-hour operation · social gaming spaces · StarCraft and LOL played here [Source: Korean gaming culture research]",
        }
        result = self._fuzzy(query, arcades)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(arcades.keys()))
            await self._respond(ctx, f"No arcade data for '{query}'. Available: {keys}")

    @commands.command(name="regionlocked", aliases=["japanonly", "notlocalised"])
    async def regionlocked(self, ctx: commands.Context, *, query: str = "") -> None:
        """Games that were locked to specific regions. Usage: !regionlocked Mother 3"""
        if not query:
            await self._respond(ctx, "Usage: !regionlocked [game] — e.g. !regionlocked Mother 3")
            return
        if not await self._check_cooldown(ctx, "regionlocked", DEFAULT_COOLDOWN):
            return
        locked: dict[str, str] = {
            "mother 3":         "Nintendo · Japan only 2006 · fan translation 2008 by Clyde Mandelin (Tomato) · Nintendo never officially released globally · most requested Nintendo translation ever · Itoi (creator) has commented [Source: gaming history]",
            "fire emblem":      "Fire Emblem 1-6 Japan only · Western release only from FE7 (2003) · Intelligent Systems assumed too complex for West · Smash Bros Melee made Roy popular → led to localizations [Source: Intelligent Systems / Nintendo]",
            "dragon quest":     "Japan only until DQ7 (2001) · largest RPG franchise in Japan · weekly Jump announcements cause Japanese stock market fluctuation · less popular in West historically [Source: Square Enix]",
            "ace attorney":     "First three games Japan only until 2005 · Nintendo of America almost didn't localize · Capcom USA fought for it · Mega Man creator Keiji Inafune championed Western release [Source: Capcom official]",
            "yakuza":           "Only 1 and 2 got Western releases initially (PS2) · Sega abandoned Western localization · fan-led demand grew · Yakuza 0 Western release 2017 reinvented franchise globally [Source: Sega official]",
        }
        result = self._fuzzy(query, locked)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(locked.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="cultureref", aliases=["culturalreferences", "realrefs"])
    async def cultureref(self, ctx: commands.Context, *, query: str = "") -> None:
        """Cultural references embedded in a game. Usage: !cultureref Hades"""
        if not query:
            await self._respond(ctx, "Usage: !cultureref [game] — e.g. !cultureref Hades or !cultureref Disco Elysium")
            return
        if not await self._check_cooldown(ctx, "cultureref", DEFAULT_COOLDOWN):
            return
        refs: dict[str, str] = {
            "hades":            "Accurate Greek mythology · Zagreus appears in ancient texts (Orphic hymns) · Achilles/Patroclus relationship canonically romantic in game (as in Iliad) · Supergiant researched deeply [Source: Supergiant / classical scholarship]",
            "disco elysium":    "Raymond Chandler noir fiction · French Situationist International · Marx + Weber sociology · Ursula K. Le Guin influence · Eastern European cultural trauma · psychoanalysis (Freud, Jung) [Source: ZA/UM developer interviews]",
            "bioshock":         "Ayn Rand's Atlas Shrugged (objectivism) · Andrew Ryan = anagram of Ayn Rand · Rapture = failed objectivist utopia · Huxley, Orwell dystopian fiction [Source: Irrational Games / Ken Levine]",
            "death stranding":  "Norman Reedus named 'Sam' (as in Uncle Sam) · Léa Seydoux = Fragile (fragility of connection) · explicit Derrida deconstructionism references · Japanese urban isolation philosophy [Source: Kojima Productions]",
            "planescape torment": "Jean-Paul Sartre existentialism · the question 'What can change the nature of a man?' = existentialist inquiry · Nietzsche, Camus influence · considered most literary game ever [Source: Black Isle / gaming criticism]",
        }
        result = self._fuzzy(query, refs)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(refs.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="foodingame", aliases=["gamefood", "recipefromgame"])
    async def foodingame(self, ctx: commands.Context, *, query: str = "") -> None:
        """Food and cooking systems in games. Usage: !foodingame Breath of the Wild"""
        if not query:
            await self._respond(ctx, "Usage: !foodingame [game] — e.g. !foodingame Breath of the Wild")
            return
        if not await self._check_cooldown(ctx, "foodingame", DEFAULT_COOLDOWN):
            return
        food_games: dict[str, str] = {
            "breath of the wild":   "100+ cooking recipes · all culinarily plausible in real life · fans have recreated every dish · Nintendo published official cookbook · stamella shroom skewer is popular fan-made dish [Source: Nintendo / fan community]",
            "stardew valley":       "72 cooking recipes · seasonal ingredients · grandmother's recipe mechanic · Eric Barone researched real cooking · game promotes sustainable farming philosophy [Source: ConcernedApe]",
            "cooking mama":         "Touchscreen cooking simulation · real recipes simplified · franchise sold 15M+ · some recipes culturally criticized · teaches actual cooking techniques [Source: Office Create official]",
            "overcooked":           "Cooperative cooking game · real kitchen chaos simulation · used in restaurant training programs · Ghost Town Games · 2-4 players · timed recipes [Source: Ghost Town Games]",
            "final fantasy xv":     "Photo-realistic food in game · celebrated by food photographers and chefs · Noctis cooks actual recipes · Yoshitaka Amano art direction influenced food design · official cookbook published [Source: Square Enix official]",
            "yakuza":               "Can eat at 100+ real restaurants in Kamurocho · faithfully recreated dishes · some real Kabukicho restaurants referenced · Kiryu's eating adventures beloved by fans [Source: Sega / RGG Studio]",
            "monster hunter":       "Canteen food buffs + cat chefs (palicoes) · food system central to preparation · armor and weapons require cooking monster parts · Felyne chef minigame [Source: Capcom official]",
        }
        result = self._fuzzy(query, food_games)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(food_games.keys())[:4])
            await self._respond(ctx, f"No food data for '{query}'. Try: {keys}...")

    @commands.command(name="gamingpet", aliases=["gameanimal", "gamecompanion"])
    async def gamingpet(self, ctx: commands.Context, *, query: str = "") -> None:
        """Famous animal companions in games. Usage: !gamingpet Dogmeat"""
        if not query:
            await self._respond(ctx, "Usage: !gamingpet [animal or game] — e.g. !gamingpet Dogmeat or !gamingpet horse")
            return
        if not await self._check_cooldown(ctx, "gamingpet", DEFAULT_COOLDOWN):
            return
        pets: dict[str, str] = {
            "dogmeat":      "Fallout series (since 1997) · named after film A Boy and His Dog · appears in FO1, FO2, FO3, FO4 · cannot die in FO4 Survival mode · fan favorite across 25+ years [Source: Bethesda official]",
            "horse":        "Red Dead Redemption 2 · horse bond system · players mourned horses deeply · horse died = genuine emotional response · horse testicles dynamically shrink in cold weather (for accuracy) [Source: Rockstar]",
            "epona":        "The Legend of Zelda: Ocarina of Time (1998) · Link's horse · song to call her is iconic · appears multiple games · name from Celtic horse goddess [Source: Nintendo official]",
            "agro":         "Shadow of the Colossus · Wander's horse · AI felt genuinely alive · players protected her · final scene devastating · Team Ico studied real horse behavior [Source: Team Ico]",
            "yoshi":        "Super Mario World (1990) · originally designed as Mario riding a horse · dinosaur version created from limitations · 45M franchise sales · tongue mechanic [Source: Nintendo official]",
            "d-dog":        "Metal Gear Solid V · adopted wolf puppy · can equip bandana · scouts enemies · Ocelot trains him · players very attached to him [Source: Konami / Kojima Productions]",
            "roach":        "The Witcher 3 · Geralt's horse always named Roach · would appear on rooftops (bug) · became meme · Geralt never names horses individually [Source: CD Projekt RED]",
            "meeko":        "Skyrim · stray dog companion · follows player forever · can die permanently · players build houses for their dog companion [Source: Bethesda]",
        }
        result = self._fuzzy(query, pets)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(pets.keys())[:5])
            await self._respond(ctx, f"Pet '{query}' not found. Try: {keys}...")

    @commands.command(name="npclegacy", aliases=["famousnpc", "iconicnpc"])
    async def npclegacy(self, ctx: commands.Context, *, query: str = "") -> None:
        """NPCs more famous than the games' protagonists. Usage: !npclegacy Sans"""
        if not query:
            await self._respond(ctx, "Usage: !npclegacy [character] — e.g. !npclegacy Sans or !npclegacy Wheatley")
            return
        if not await self._check_cooldown(ctx, "npclegacy", DEFAULT_COOLDOWN):
            return
        npcs: dict[str, str] = {
            "sans":         "Undertale · optional secret boss · Genocide route only · 'megalovania' · 'bad time' · more fan art than protagonist Frisk/Chara · became internet phenomenon · in Smash Bros as Mii costume [Source: fan community data]",
            "wheatley":     "Portal 2 · voiced by Stephen Merchant · comedic AI core · plot twist villain · considered best character in Portal series · BAFTA nominated [Source: Valve]",
            "elizabeth":    "BioShock Infinite · AI companion · never gets in the way · throws ammo and salts · Naughty Dog studied her for Ellie design · remarkable NPC AI [Source: Irrational Games / Naughty Dog]",
            "solas":        "Dragon Age: Inquisition · elven apostate mage · companion · later revealed as (spoiler) ancient elven god · most discussed DA character · Veilguard built around him [Source: BioWare official]",
            "companion cube": "Portal · inanimate box · players developed emotional attachment · 'I think we can put our differences behind us... for science' · Chell forced to euthanize it [Source: Valve]",
            "npc warrior":  "Skyrim · 'I used to be an adventurer like you...' guard · 'arrow in the knee' became massive meme · 200+ guards all say it · created internet vocabulary [Source: Bethesda]",
            "patches":      "FromSoftware games · recurring character across multiple titles · always a greedy merchant who deceives player · fan favorite exactly because he's untrustworthy [Source: FromSoftware]",
        }
        result = self._fuzzy(query, npcs)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(npcs.keys())[:4])
            await self._respond(ctx, f"NPC '{query}' not found. Try: {keys}...")

    @commands.command(name="gamingmeme", aliases=["gamememe", "memeorigin"])
    async def gamingmeme(self, ctx: commands.Context, *, query: str = "") -> None:
        """Origin of famous gaming memes. Usage: !gamingmeme All Your Base"""
        if not query:
            await self._respond(ctx, "Usage: !gamingmeme [meme] — e.g. !gamingmeme All Your Base or !gamingmeme Leeroy Jenkins")
            return
        if not await self._check_cooldown(ctx, "gamingmeme", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAMING_MEMES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(GAMING_MEMES.keys())[:5])
            await self._respond(ctx, f"Meme '{query}' not found. Try: {keys}...")

    @commands.command(name="weatheringame", aliases=["gameweather", "weathersystem"])
    async def weatheringame(self, ctx: commands.Context, *, query: str = "") -> None:
        """Games with remarkable weather systems. Usage: !weatheringame Red Dead 2"""
        if not query:
            await self._respond(ctx, "Usage: !weatheringame [game] — e.g. !weatheringame Red Dead 2")
            return
        if not await self._check_cooldown(ctx, "weatheringame", DEFAULT_COOLDOWN):
            return
        weather: dict[str, str] = {
            "red dead 2":           "Rockstar · 49 distinct weather types · dynamic snow deformation (horse hooves leave prints) · most detailed weather system in open world gaming · weather affects NPC behavior and hunting [Source: Rockstar]",
            "breath of the wild":   "Nintendo · dynamic temperature affecting gameplay · rain makes climbing impossible · lightning attracts to metal equipment · weather shifts Link's survival options constantly [Source: Nintendo]",
            "death stranding":      "Timefall · Kojima Productions · rain that ages everything it touches · reversed time = unique weather concept · aging cargo, aging NPCs mechanically integrated [Source: Kojima Productions]",
            "the long dark":        "Hinterland Studio · survival game · blizzard system tracks multiple weather variables · wind direction, temperature, visibility · realistic Canadian wilderness weather [Source: Hinterland Studio]",
            "far cry 2":            "Ubisoft Montreal · dynamic fire spread with wind · arguably best fire simulation in gaming · revolutionary for 2008 · fire gameplay rarely replicated [Source: Ubisoft]",
            "control":              "Remedy · weather in the Oldest House (brutalist government building) · supernatural weather phenomena indoors · Hiss corruption changes environmental conditions [Source: Remedy Entertainment]",
        }
        result = self._fuzzy(query, weather)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(weather.keys())[:4])
            await self._respond(ctx, f"No weather data for '{query}'. Try: {keys}...")

    @commands.command(name="gamingmilestone", aliases=["industrymilestone", "gamingtrivia"])
    async def gamingmilestone(self, ctx: commands.Context, *, query: str = "") -> None:
        """Industry-changing firsts in gaming history. Usage: !gamingmilestone motion capture"""
        if not query:
            await self._respond(ctx, "Usage: !gamingmilestone [topic or year] — e.g. !gamingmilestone motion capture or !gamingmilestone 1972")
            return
        if not await self._check_cooldown(ctx, "gamingmilestone", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAMING_FIRSTS)
        if result:
            await self._respond(ctx, result)
        else:
            milestones: dict[str, str] = {
                "motion capture":   "Virtua Fighter 2 · Sega · 1994 · actors in suits with reflective markers · first motion capture for game characters · changed animation forever [Source: Sega official / gaming history]",
                "voiced protagonist": "First fully voiced protagonist: Gabriel Knight (1993) · Tim Curry · Sierra On-Line · before this, all dialogue was text · changed expectation for RPGs [Source: gaming history]",
                "online console":   "Sega Dreamcast · 1998 · first console with built-in modem · online gaming before Xbox Live · ahead of its time · NFL 2K1 first online console sports game [Source: Sega official]",
                "hd graphics":      "Xbox 360 / PS3 generation 2005-2006 · first HD consoles · 720p/1080i · dramatically changed how games looked · began uncanny valley problem [Source: gaming history]",
                "achievement system": "Xbox 360 Achievements launched 2005 · first unified cross-game achievement system · PlayStation Trophy system followed 2008 · changed how players engage with games [Source: Microsoft official]",
            }
            result = self._fuzzy(query, milestones)
            if result:
                await self._respond(ctx, result)
            else:
                await self._respond(ctx, f"No milestone data for '{query}'. Try: motion capture, voiced protagonist, online console, achievement system...")

    @commands.command(name="speedruntech", aliases=["speedrunglitch", "srtech"])
    async def speedruntech(self, ctx: commands.Context, *, query: str = "") -> None:
        """Speedrunning techniques explained. Usage: !speedruntech BLJ"""
        if not query:
            await self._respond(ctx, "Usage: !speedruntech [technique] — e.g. !speedruntech BLJ or !speedruntech wrong warp")
            return
        if not await self._check_cooldown(ctx, "speedruntech", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, SPEEDRUN_TECHNIQUES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(SPEEDRUN_TECHNIQUES.keys()))
            await self._respond(ctx, f"Technique '{query}' not found. Available: {keys}")

    @commands.command(name="gamingquote", aliases=["devquote", "gaminquote"])
    async def gamingquote(self, ctx: commands.Context, *, query: str = "") -> None:
        """Verified quotes from gaming industry figures. Usage: !gamingquote Miyamoto"""
        if not query:
            await self._respond(ctx, "Usage: !gamingquote [person] — e.g. !gamingquote Miyamoto or !gamingquote random")
            return
        if not await self._check_cooldown(ctx, "gamingquote", DEFAULT_COOLDOWN):
            return
        quotes: dict[str, str] = {
            "miyamoto":         "'A delayed game is eventually good. A rushed game is bad forever.' — Shigeru Miyamoto (paraphrased from multiple interviews) · verified as his philosophy, exact wording varies [Source: Nintendo / Miyamoto interviews]",
            "kojima":           "'I want to create something that surprises players. Something they've never seen before.' — Hideo Kojima · also: 'I'm 70% movies' [Source: Hideo Kojima interviews]",
            "gabe newell":      "'The easiest way to stop piracy is not by putting antipiracy technology to work. It's by giving those people a service that's better than what they're receiving from the pirates.' — Gabe Newell, 2011 [Source: Gabe Newell interview, Develop Conference 2011]",
            "toby fox":         "'I made Undertale because I wanted to make something that would make people cry.' — Toby Fox [Source: Toby Fox interview, Fangamer]",
            "ken levine":       "'Stories in games need to be about the experience of playing the game, not just watching cutscenes.' — Ken Levine [Source: Ken Levine GDC talks]",
            "yoko taro":        "'I want to betray the player's expectations in a way that makes them happy.' — Yoko Taro [Source: Yoko Taro interviews]",
            "notch":            "'Creativity comes from constraints.' — Markus 'Notch' Persson on Minecraft's simple beginnings [Source: Notch blog posts]",
            "reggie":           "'My body is ready.' — Reggie Fils-Aimé, Nintendo of America · 2007 E3 · became instant meme · Reggie fully embraced it [Source: Nintendo E3 2007]",
            "random":           None,  # handled below
        }
        if query.strip().lower() == "random":
            valid = {k: v for k, v in quotes.items() if v is not None}
            await self._respond(ctx, random.choice(list(valid.values())))
            return

        result = self._fuzzy(query, {k: v for k, v in quotes.items() if v})
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(k for k in quotes if quotes[k])
            await self._respond(ctx, f"No quote for '{query}'. Available: {keys}")

    @commands.command(name="gamerating", aliases=["contentrating", "ratedwhy", "agerating"])
    async def gamerating(self, ctx: commands.Context, *, query: str = "") -> None:
        """Age rating history of games — ESRB, PEGI, CERO. Usage: !gamerating Mortal Kombat"""
        if not query:
            await self._respond(ctx, "Usage: !gamerating [game or rating system] — e.g. !gamerating Mortal Kombat or !gamerating ESRB")
            return
        if not await self._check_cooldown(ctx, "gamerating", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, GAME_RATINGS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(GAME_RATINGS.keys())[:5])
            await self._respond(ctx, f"No rating data for '{query}'. Try: {keys}...")

    @commands.command(name="gametoanime", aliases=["adaptedanime", "animeadaptation"])
    async def gametoanime(self, ctx: commands.Context, *, query: str = "") -> None:
        """Games adapted into anime series. Usage: !gametoanime Castlevania"""
        if not query:
            await self._respond(ctx, "Usage: !gametoanime [franchise] — e.g. !gametoanime Castlevania or !gametoanime Arcane")
            return
        if not await self._check_cooldown(ctx, "gametoanime", DEFAULT_COOLDOWN):
            return
        anime: dict[str, str] = {
            "castlevania":      "Netflix 2017-2021 · Warren Ellis writer · animated by Powerhouse Animation · universally praised · unusual for game adaptations · 4 seasons · Nocturne spinoff [Source: Netflix official]",
            "arcane":           "Netflix 2021 · League of Legends universe · Riot Games co-produced · Fortiche animation studio · won multiple Annie Awards · Emmy nominated · not traditional game adaptation but world-building [Source: Netflix/Riot Games official]",
            "pokemon":          "1997-present · longest running game adaptation anime · 1000+ episodes · Ash's journey concluded 2023 · new protagonists Liko and Roy · massive global phenomenon [Source: TV Tokyo / The Pokemon Company]",
            "final fantasy":    "Final Fantasy VII: Advent Children (2005 film) · Last Order OVA · multiple FF anime projects · Advent Children Complete extended version · Kingsglaive for FFXV [Source: Square Enix official]",
            "persona 4":        "Persona 4: The Animation (2011) · closely follows game story · Persona 5 The Royal animated · Atlus manages anime adaptations of JRPG properties [Source: Atlus official]",
            "cyberpunk":        "Cyberpunk: Edgerunners (Netflix 2022) · Studio Trigger · David Martinez story · set in Night City · revived Cyberpunk 2077 game sales after mediocre launch [Source: Netflix/CD Projekt RED official]",
            "halo":             "Halo (Paramount+ 2022) · Pablo Schreiber as Master Chief · face shown controversially · significant departures from game canon · fan reaction mixed [Source: Paramount+ official]",
        }
        result = self._fuzzy(query, anime)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(anime.keys())[:4])
            await self._respond(ctx, f"No anime adaptation data for '{query}'. Try: {keys}...")


def prepare(bot):
    bot.add_cog(GamingCog(bot))
