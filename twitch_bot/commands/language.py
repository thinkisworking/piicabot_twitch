# PiicaBot — twitch_bot/commands/language.py
# Japanese, Italian, and cross-language commands.
# All data is local — verified against official sources.
# Japanese: !kanji !japaneseconcept !japaneseword !honorific !japanesecount !japaneseproverb !jlpt !japanesefood
# Italian: !italianword !italiangesture !italiandialect !italianconcept !italianfood !latinroot !italianidiom !italianmusicalterm
# Cross-language: !falsefriend !loanword !numbers !greeting

import random
from twitchio.ext import commands
from loguru import logger

import database.db as db
from config import DEFAULT_COOLDOWN


# ─────────────────────────────────────────────────────────────
# JAPANESE DATA
# Sources: NHK World Japanese, JLPT official lists, Kenkyusha dictionary
# ─────────────────────────────────────────────────────────────

KANJI_DATA: dict[str, str] = {
    "木": "ki/moku · tree/wood · 4 strokes · JLPT N5 · 木曜日 Thursday · 木村 Kimura · 木々 trees",
    "水": "mizu/sui · water · 4 strokes · JLPT N5 · 水曜日 Wednesday · 水道 waterworks · 水泳 swimming",
    "火": "hi/ka · fire · 4 strokes · JLPT N5 · 火曜日 Tuesday · 火山 volcano · 花火 fireworks",
    "山": "yama/san · mountain · 3 strokes · JLPT N5 · 山田 Yamada · 富士山 Mt. Fuji · 山道 mountain path",
    "川": "kawa/sen · river · 3 strokes · JLPT N5 · 川端 Kawabata · 小川 stream · 川崎 Kawasaki",
    "日": "hi/nichi/jitsu · sun/day · 4 strokes · JLPT N5 · 日本 Japan · 日曜日 Sunday · 毎日 every day",
    "月": "tsuki/getsu/gatsu · moon/month · 4 strokes · JLPT N5 · 月曜日 Monday · 毎月 every month",
    "人": "hito/jin/nin · person · 2 strokes · JLPT N5 · 日本人 Japanese person · 一人 one person",
    "大": "oo/dai/tai · big · 3 strokes · JLPT N5 · 大学 university · 大阪 Osaka · 大きい big",
    "小": "ko/sho · small · 3 strokes · JLPT N5 · 小学校 elementary school · 小さい small",
    "中": "naka/chuu · middle/inside · 4 strokes · JLPT N5 · 中国 China · 中学校 middle school",
    "国": "kuni/koku · country · 8 strokes · JLPT N5 · 中国 China · 外国 foreign country",
    "語": "kataru/go · language/word · 14 strokes · JLPT N5 · 日本語 Japanese · 英語 English",
    "食": "taberu/shoku · eat/food · 9 strokes · JLPT N5 · 食事 meal · 食べ物 food · 食堂 cafeteria",
    "見": "miru/ken · see/look · 7 strokes · JLPT N5 · 見る to see · 見物 sightseeing · 意見 opinion",
    "愛": "ai · love · 13 strokes · JLPT N3 · 愛情 affection · 愛知 Aichi prefecture · 愛する to love",
    "夢": "yume/mu · dream · 13 strokes · JLPT N3 · 夢を見る to dream · 悪夢 nightmare · 夢中 absorbed in",
    "空": "sora/kuu/ku · sky/empty · 8 strokes · JLPT N4 · 空港 airport · 空気 air · 青空 blue sky",
    "花": "hana/ka · flower · 7 strokes · JLPT N4 · 花見 hanami · 桜の花 cherry blossom · 花火 fireworks",
    "心": "kokoro/shin · heart/mind · 4 strokes · JLPT N3 · 心配 worry · 親心 parental love · 安心 relief",
}

JAPANESE_CONCEPTS: dict[str, str] = {
    "ikigai":        "生き甲斐 · reason for being · intersection of what you love, are good at, world needs, and can be paid for · Okinawa longevity attributed partly to having ikigai [Source: Japanese philosophy]",
    "wabi-sabi":     "侘び寂び · finding beauty in imperfection and impermanence · a cracked tea bowl is more beautiful for its cracks · central to Japanese aesthetics and tea ceremony [Source: Japanese aesthetics]",
    "mono no aware": "物の哀れ · pathos of things · gentle sadness at transience · bittersweet appreciation of impermanence · cherry blossoms (sakura) embody this [Source: Heian literature / Motoori Norinaga]",
    "komorebi":      "木漏れ日 · sunlight filtering through leaves · interplay of light and shadow through trees · no equivalent word exists in English [Source: Japanese linguistics]",
    "ma":            "間 · negative space · the pause between notes · the emptiness in a room · silence in conversation · as important as what is present · fundamental to Japanese art [Source: Japanese aesthetics]",
    "wabi":          "侘 · rustic simplicity · irregular beauty · understated elegance · finding worth in simple imperfect things · kintsugi (gold joinery) embodies this [Source: Japanese aesthetics]",
    "sabi":          "寂 · beauty of age and wear · the rust on iron · worn wood · the patina of time · opposite of 'new' but more beautiful [Source: Japanese aesthetics]",
    "shokunin":      "職人 · artisan spirit · single-minded pursuit of perfection in one's craft · a sushi shokunin trains 10+ years before making rice · total dedication [Source: Japanese craft tradition]",
    "gaman":         "我慢 · enduring the seemingly unbearable with patience and dignity · demonstrated by Japanese communities after 2011 earthquake · stoic composure [Source: Japanese cultural values]",
    "kaizen":        "改善 · continuous improvement · small incremental positive changes · Toyota Production System built on this · now used in business worldwide [Source: Japanese management philosophy]",
    "omotenashi":    "おもてなし · wholehearted hospitality · anticipating guests' needs before they ask · no expectation of reward · centerpiece of Japanese service culture [Source: Japanese hospitality tradition]",
    "amae":          "甘え · the pleasurable feeling of dependence on another's benevolence · unique concept in Japanese psychology · Takeo Doi's study [Source: Doi Takeo 'The Anatomy of Dependence']",
    "hara hachi bu": "腹八分目 · eat until 80% full · Okinawan practice · linked to longevity · Confucian concept adopted in Japan [Source: Blue Zones / Okinawa Centenarian Study]",
    "senpai":        "先輩 · senior/mentor · someone who has walked the path before you · respected guide · kohai is the junior · relationship fundamental to Japanese social structure [Source: Japanese social structure]",
}

JAPANESE_WORDS: dict[str, str] = {
    "sakura":       "桜 · cherry blossom · Japan's national flower · blooms ~2 weeks · hanami (flower viewing) tradition · symbol of transience and renewal [Source: Japan Tourism Agency]",
    "kawaii":       "可愛い · cute/adorable · now global term · originally meant pitiable in classical Japanese · evolved to mean charming/loveable [Source: Japanese linguistics]",
    "otaku":        "おたく · originally negative: reclusive obsessive · now globally used for anime/manga enthusiasts · reclaimed by community · major cultural export [Source: Japanese cultural studies]",
    "tsunami":      "津波 · harbor wave · tsu (harbor) + nami (wave) · Japanese term now universal · caused by seismic displacement of ocean floor [Source: Japanese/seismology]",
    "emoji":        "絵文字 · picture character · e (picture) + moji (character) · created by Shigetaka Kurita for DoCoMo 1999 · now Unicode standard worldwide [Source: MoMA collection / Unicode]",
    "futon":        "布団 · Japanese bedding · fu (cloth) + ton (round/fat) · originally very different from Western usage · floor bedding rolled up during day [Source: Japanese language]",
    "karaoke":      "カラオケ · empty orchestra · kara (empty) + okesutora (orchestra) · invented by Daisuke Inoue 1971 (Kobe) · he didn't patent it [Source: Time magazine]",
    "ramen":        "ラーメン · Chinese origin word (拉麺) · arrived Japan via Chinese immigrants · each region has distinct style · now UNESCO Intangible Heritage candidate [Source: Japanese culinary history]",
    "manga":        "漫画 · whimsical pictures · man (whimsical) + ga (picture) · distinct art style · reads right-to-left · Osamu Tezuka 'God of Manga' [Source: Japanese publishing history]",
    "bonsai":       "盆栽 · tray planting · bon (tray) + sai (planting) · originally Chinese (penjing) · taken to Japan by Buddhist monks · oldest known bonsai is 1000+ years [Source: Kokufu Bonsai Exhibition]",
}

HONORIFICS: dict[str, str] = {
    "san":   "さん · Mr./Mrs./Ms. equivalent · most common honorific · used for adults regardless of gender · safe neutral choice · do NOT use for yourself [Source: Japanese social customs]",
    "kun":   "くん · used for younger males or subordinates · also used by superiors addressing juniors · can be used by anyone addressing boys [Source: Japanese social customs]",
    "chan":  "ちゃん · cute/informal · children, close friends, young women · also for pets and cute things · intimate — don't use with strangers [Source: Japanese social customs]",
    "sama":  "様 · highest respect · royalty, deities, valued customers · 'o-kyaku-sama' for customers · very formal — overuse sounds sarcastic [Source: Japanese social customs]",
    "sensei":"先生 · teacher/master/doctor · anyone with expertise who teaches others · doctors, lawyers, politicians also addressed as sensei [Source: Japanese social customs]",
    "senpai":"先輩 · senior · someone who joined school/company before you · not always older but has seniority · important relationship in Japan [Source: Japanese social customs]",
    "kohai": "後輩 · junior · someone who joined after you · senpai has responsibility for kohai · reciprocal relationship [Source: Japanese social customs]",
    "dono":  "殿 · archaic very formal · used in formal documents and historical drama · above sama in formality · rarely used in daily life [Source: Japanese historical linguistics]",
}

JAPANESE_COUNTERS: dict[str, str] = {
    "animals (small)":  "匹 (hiki) · used for small animals: dogs, cats, fish, insects · ippiki, nihiki, sanbiki",
    "animals (large)":  "頭 (tou) · used for large animals: horses, cows, elephants · ittou, nitou, santou",
    "birds":            "羽 (wa) · used for birds and rabbits · ichiwa, niwa, sanwa",
    "long thin objects":"本 (hon) · pens, bottles, rivers, roads, films · ippon, nihon, sanbon",
    "flat objects":     "枚 (mai) · paper, stamps, plates, shirts · ichimai, nimai, sanmai",
    "small objects":    "個 (ko) · small round things: eggs, apples, rocks · ikko, niko, sanko",
    "books":            "冊 (satsu) · bound books and magazines · issatsu, nisatsu, sansatsu",
    "machines/vehicles":"台 (dai) · cars, computers, machines · ichidai, nidai, sandai",
    "people":           "人 (nin/hitori/futari) · people · hitori (1 person), futari (2), san-nin (3+)",
    "age":              "歳 (sai) · years of age · issai, nisai, sansai · also: 才 informal",
    "floors":           "階 (kai) · floors of a building · ikkai (1F), nikai (2F), sangai (3F)",
    "glasses/cups":     "杯 (hai) · glasses, cups, bowls of liquid · ippai, nihai, sanbai",
}

JAPANESE_PROVERBS: list[str] = [
    "七転び八起き (nana korobi ya oki) · fall seven times rise eight · perseverance despite failure · fundamental Japanese value [Source: Japanese proverb tradition]",
    "一期一会 (ichi-go ichi-e) · one time one meeting · treasure each encounter as it will never happen again · tea ceremony philosophy [Source: Sen no Rikyū / tea ceremony tradition]",
    "出る釘は打たれる (deru kugi wa utareru) · the nail that sticks out gets hammered down · conformity valued · don't draw unwanted attention [Source: Japanese proverb tradition]",
    "七つ道具 (nanatsu dougu) · seven tools · being fully prepared · always have what you need [Source: Japanese proverb tradition]",
    "花より団子 (hana yori dango) · dumplings over flowers · practical concerns over aesthetics · prefer substance to appearance [Source: Japanese proverb tradition]",
    "猿も木から落ちる (saru mo ki kara ochiru) · even monkeys fall from trees · even experts make mistakes · similar to 'nobody's perfect' [Source: Japanese proverb tradition]",
    "石の上にも三年 (ishi no ue ni mo sannen) · three years on a stone · persevere and even a cold stone will warm · patience brings reward [Source: Japanese proverb tradition]",
    "急がば回れ (isogaba maware) · more haste less speed · if in a hurry take the safer longer route · equivalent of 'slow and steady' [Source: Sogi's poetry collection 1480]",
    "虎穴に入らずんば虎子を得ず (koketsu ni irazunba koji wo ezu) · nothing ventured nothing gained · you must enter the tiger's cave to get the cub [Source: Later Han Shu / Japanese adoption]",
    "七光り (nana hikari) · seven glows · benefiting from a parent's fame · inherited privilege/reputation [Source: Japanese proverb tradition]",
]

JLPT_WORDS: dict[str, tuple[str, str]] = {
    "ありがとう": ("N5", "arigatou · thank you · most basic politeness · arigatou gozaimasu formal version"),
    "すみません": ("N5", "sumimasen · excuse me/I'm sorry · used to get attention or apologize · very versatile"),
    "大丈夫": ("N5", "daijoubu · it's okay/are you okay · extremely common · yes=大丈夫です"),
    "電車": ("N5", "densha · train (electric) · den=electric, sha=vehicle · most common transport in Japan"),
    "醸造": ("N1", "jouzo · brewing/fermentation · used in sake, soy sauce industry · advanced vocabulary"),
    "忖度": ("N1", "sontaku · reading the air · inferring superior's wishes without being told · major political term 2017"),
    "曖昧": ("N2", "aimai · vague/ambiguous · Japanese communication often described as aimai · important cultural concept"),
    "納豆": ("N4", "nattou · fermented soybeans · strong smell · breakfast staple · very polarizing food"),
    "木漏れ日": ("N1", "komorebi · sunlight through leaves · untranslatable · poetic vocabulary"),
}

JAPANESE_FOOD: dict[str, str] = {
    "ramen": "ラーメン · regional styles: Sapporo (miso, corn), Hakata (tonkotsu), Tokyo (shoyu), Kyoto (tori paitan) · Chinese origin · UNESCO heritage candidate [Source: Japan Ramen Association]",
    "sushi": "寿司 · originally preserved fish in fermented rice (narezushi) · vinegared rice developed Edo period · nigiri style ~1820s Tokyo · omakase = chef's choice [Source: Japanese culinary history]",
    "tempura": "天ぷら · introduced by Portuguese missionaries 16th century · from Latin 'tempora' (Ember Days fasting) · Japanese perfected the batter technique [Source: Japanese culinary history]",
    "osechi": "おせち · traditional New Year food · each dish has symbolic meaning · 煮しめ (nimono) = family harmony · 数の子 (herring roe) = fertility · prepared before New Year [Source: Japanese cultural tradition]",
    "takoyaki": "たこ焼き · octopus balls · Osaka street food · invented by Tomekichi Endo 1935 · tako=octopus, yaki=grilled · special round pan required [Source: Osaka culinary history]",
    "wagashi": "和菓子 · traditional Japanese sweets · made from plant ingredients · reflect seasons · paired with matcha · nerikiri most artistic form [Source: Japanese confectionery tradition]",
    "kaiseki": "懐石 · multi-course Japanese haute cuisine · seasonal ingredients · presentation as art · Kyoto tradition · evolved from tea ceremony meal [Source: Japanese culinary arts]",
    "yakitori": "焼き鳥 · grilled chicken skewers · yaki=grilled, tori=bird · every part of chicken used · tare (sauce) or shio (salt) · izakaya staple [Source: Japanese food culture]",
    "miso soup": "味噌汁 · fermented soybean paste + dashi broth · eaten at breakfast in Japan · miso type varies by region · white (shiro) in Kyoto, red (aka) in Nagoya [Source: Japanese culinary tradition]",
}


# ─────────────────────────────────────────────────────────────
# ITALIAN DATA
# Sources: Accademia della Crusca, Treccani dictionary
# ─────────────────────────────────────────────────────────────

ITALIAN_WORDS: dict[str, str] = {
    "ciao":          "from Venetian dialect 'schiavo' (slave) meaning 'I am your servant' · now used as both hello and goodbye worldwide · informal only [Source: Accademia della Crusca]",
    "pizza":         "origin disputed · possibly from Lombardic 'bizzo' (bite) or Latin 'pinsa' (flatbread) · Naples 997 AD first written record · [Source: Accademia della Crusca / Oxford Dictionary]",
    "umbrella":      "from Italian 'ombrella' · ombra = shade/shadow · entered English ~1610 · Italy invented the folding umbrella [Source: Oxford English Dictionary]",
    "soprano":       "from Italian 'sopra' meaning above · literally 'the one above' · highest singing voice · entered musical terminology worldwide [Source: Italian musical heritage]",
    "studio":        "from Italian 'studio' from Latin 'studium' (zeal/study) · place of study/work · entered English ~1819 [Source: Oxford English Dictionary]",
    "fiasco":        "from Italian 'fare fiasco' (to make a bottle) · theatrical term for total failure · origin of exact phrase disputed [Source: Accademia della Crusca]",
    "graffiti":      "plural of 'graffito' · from Italian 'graffiare' (to scratch) · ancient practice · Pompeii walls covered in graffiti · word now global [Source: Accademia della Crusca]",
    "volcano":       "from Vulcano island, Sicily · named for Vulcan, Roman god of fire · island itself still active · term spread globally from Italian [Source: geological history / Italian etymology]",
    "influenza":     "Italian for 'influence' · medieval belief that illness caused by stars' influence · 1743 Italian epidemic named thus · shortened to 'flu' [Source: medical history / Oxford Dictionary]",
    "casino":        "from 'casa' (house) + diminutive · small country house · Italian nobles used for pleasure activities · gambling meaning came later [Source: Accademia della Crusca]",
    "balcony":       "from Italian 'balcone' from Germanic 'balko' (beam) · Juliet's balcony (Romeo and Juliet) made it famous · architectural term worldwide [Source: Italian etymology]",
    "pasta":         "from Latin 'pasta' (dough/pastry) · Marco Polo did NOT bring pasta from China — Italian pasta predates him · [Source: Accademia della Crusca / food history]",
}

ITALIAN_GESTURES: dict[str, str] = {
    "pinched fingers":    "mano a borsa · what do you want?/what are you saying? · most internationally recognized Italian gesture · fingers pinched together moved up and down",
    "chin flick":         "fregarsi il mento · I don't care / get lost · back of fingers flicked under chin · can be offensive · similar to middle finger in some contexts",
    "finger kiss":        "il bacio · magnificent/delicious! · fingers kissed then opened · usually for food appreciation · exaggerated positive response",
    "temple screw":       "dito alla tempia · you're crazy/brilliant · index finger twisted at temple · can mean crazy OR very smart depending on expression",
    "hand purse":         "la mano a borsa · variations mean different things · basic form = 'what do you want?' · speed and context change meaning",
    "talking hands":      "parlare con le mani · Italians use gestures as punctuation · research shows Italian-Americans retained gestures while losing language · deeply embedded in culture",
    "eye pull":           "abbassare la palpebra · be careful / I'm watching you · index finger pulls down lower eyelid · awareness/warning gesture",
    "hand swipe":         "mani a taglio · enough/stop! · one hand slaps across the other · cutting gesture for 'that's it!'",
}

ITALIAN_DIALECTS: dict[str, str] = {
    "neapolitan":   "Napoletano · so distinct linguistically it's sometimes classified as a separate language · 5.7M speakers · UNESCO endangered · 'o surdato 'nnammurato' most famous song [Source: UNESCO / linguistic research]",
    "venetian":     "Veneto · 3.8M speakers · gave world words: ciao, ghetto, arsenal · official regional language · basis of 'ciao' worldwide [Source: Regione Veneto]",
    "sicilian":     "Sicilianu · influenced by Arabic, Greek, Norman French · oldest literary tradition in Italy (Scuola Siciliana) · distinct grammar from Italian [Source: linguistic research]",
    "roman":        "Romanesco · Rome dialect · influenced standard Italian · 'c'è la famo' instead of 'ce la facciamo' · used in Pasolini films [Source: linguistic research]",
    "lombard":      "Lumbaart · Northern Italy · closely related to Venetian · Bergamo dialect almost unintelligible to standard Italian speakers [Source: linguistic research]",
    "sardinian":    "Sardu · considered most conservative Romance language · closer to Latin than Italian · UNESCO classified as distinct language · 1.2M speakers [Source: UNESCO / linguistic research]",
    "piedmontese":  "Piemontèis · Torino region · influenced by French · considerable literary tradition · 1.6M speakers [Source: Regione Piemonte]",
    "ligurian":     "Zeneize · Genova/Liguria · Cristoforo Colombo (Columbus) spoke this · also spoken in Monaco (Monégasque) [Source: linguistic research]",
}

ITALIAN_CONCEPTS: dict[str, str] = {
    "dolce far niente": "sweet doing nothing · the pleasure of doing nothing and enjoying it · not laziness — a mindful pleasure in idleness · deeply Italian value [Source: Italian cultural values]",
    "sprezzatura":      "studied carelessness · the art of making difficult things look effortless · Baldassare Castiglione coined it 1528 in 'Book of the Courtier' · basis of Italian elegance [Source: Il Cortegiano, Castiglione 1528]",
    "abbiocco":         "the drowsy feeling after a big meal · post-lunch sleepiness · no English equivalent · often leads to riposo (afternoon rest) [Source: Italian language / culture]",
    "culaccino":        "the mark left on a table by a wet glass · that ring of condensation · a specific word for a specific moment [Source: Italian language]",
    "meriggiare":       "to rest during the midday heat · from 'meriggio' (noon) · Eugenio Montale poem title · the siesta culture expressed in one word [Source: Italian literary tradition]",
    "gattara":          "a woman (usually elderly) who devotes herself to caring for stray cats · Italy has millions of feral cats · gattare protect them · legally protected colonies [Source: Italian cultural observation]",
    "magari":           "maybe/I wish/if only · one word expressing hope, uncertainty, desire simultaneously · no direct English translation · 'magari fosse vero' = 'if only it were true' [Source: Accademia della Crusca]",
    "boh":              "Italian shrug in word form · complete uncertainty · I don't know and I'm not sure I care · one of the most used Italian expressions [Source: Italian language]",
    "cavolo":           "literally 'cabbage' · used as a polite substitute expletive · 'che cavolo!' = 'what the...!' · vegetable substitution is a common Italian euphemism pattern [Source: Italian language]",
}

ITALIAN_FOOD: dict[str, str] = {
    "carbonara":        "Roman dish · authentic ingredients: guanciale (NOT bacon), eggs, Pecorino Romano, black pepper, NO cream · post-WWII origin likely · name may come from carbonari (charcoal workers) [Source: Accademia Italiana della Cucina]",
    "pizza margherita": "Naples 1889 · Chef Raffaele Esposito for Queen Margherita · tomato (red) + mozzarella (white) + basil (green) = Italian flag colors · STG protected status [Source: Associazione Verace Pizza Napoletana]",
    "risotto":          "Northern Italy · Lombardy and Piedmont · needs constant stirring (mantecatura) · Arborio/Carnaroli/Vialone Nano rice varieties · Milan style with saffron (risotto alla Milanese) [Source: Italian culinary tradition]",
    "tiramisu":         "pick me up · tira (pull) + mi (me) + su (up) · origin disputed between Treviso and Friuli · 1960s-70s · savoiardi, mascarpone, espresso, cocoa [Source: Italian culinary history]",
    "amatriciana":      "from Amatrice, Lazio · bucatini or rigatoni · guanciale + San Marzano tomatoes + Pecorino · NOT onion · 2016 earthquake devastated Amatrice [Source: Comune di Amatrice]",
    "pesto genovese":   "Genova, Liguria · PDO protected · basil DOP + Parmigiano Reggiano + Pecorino + pine nuts + garlic + Ligurian olive oil · mortar and pestle not blender [Source: Consorzio del Pesto Genovese]",
    "gelato":           "Italian ice cream · less fat and air than American ice cream · denser and more intense flavor · served slightly warmer · artisanal gelato (artigianale) vs commercial [Source: Italian Association of Ice Cream Artisans]",
    "prosciutto":       "di Parma or San Daniele · PDO protected · salt-cured aged 12-36 months · no other additives · 10kg pig leg → 7kg finished product [Source: Consorzio del Prosciutto di Parma]",
    "ossobuco":         "Milanese dish · cross-cut veal shank braised · osso=bone, buco=hole · served with gremolata (lemon zest + parsley + garlic) + traditionally risotto alla Milanese [Source: Italian culinary tradition]",
}

LATIN_ROOTS: dict[str, str] = {
    "acqua":    "Latin: aqua (water) · cognates: aquarium, aqueduct, aquamarine · Spanish: agua · French: eau · Portuguese: água [Source: Latin etymology]",
    "sole":     "Latin: sol (sun) · cognates: solar, solstice, parasol · Spanish: sol · French: soleil · Romanian: soare [Source: Latin etymology]",
    "luna":     "Latin: luna (moon) · cognates: lunar, lunatic (moon-madness belief) · Spanish: luna · French: lune · all Romance languages similar [Source: Latin etymology]",
    "terra":    "Latin: terra (earth/land) · cognates: terrain, territory, Mediterranean (middle of the earth), extraterrestrial [Source: Latin etymology]",
    "vita":     "Latin: vita (life) · cognates: vital, vitamin, revive, vivid · Spanish: vida · French: vie [Source: Latin etymology]",
    "mano":     "Latin: manus (hand) · cognates: manual, manufacture, manuscript, manipulate, manage [Source: Latin etymology]",
    "occhio":   "Latin: oculus (eye) · cognates: ocular, binoculars, inoculate · Spanish: ojo · French: œil [Source: Latin etymology]",
    "cuore":    "Latin: cor/cordis (heart) · cognates: cardiac, cordial, courage, accord, discord, record [Source: Latin etymology]",
    "tempo":    "Latin: tempus (time) · cognates: temporary, contemporary, tense (grammar), temperature · French: temps [Source: Latin etymology]",
    "amore":    "Latin: amor (love) · cognates: amorous, enamored, amateur (one who loves) · Spanish: amor · French: amour [Source: Latin etymology]",
}

ITALIAN_IDIOMS: list[str] = [
    "In bocca al lupo · in the mouth of the wolf · said for good luck (before exam, performance) · reply: Crepi il lupo! (may the wolf die!) [Source: Italian cultural tradition]",
    "Non tutte le ciambelle riescono col buco · not all doughnuts come out with a hole · not everything goes as planned · equivalent to 'best laid plans...' [Source: Italian proverb tradition]",
    "Il lupo perde il pelo ma non il vizio · the wolf loses its fur but not its vices · people don't change their fundamental nature · equivalent to 'a leopard can't change its spots' [Source: Italian proverb]",
    "Avere le mani in pasta · to have your hands in the dough · to be deeply involved in something · to have influence [Source: Italian idiom tradition]",
    "Chi dorme non piglia pesci · he who sleeps doesn't catch fish · you miss opportunities if you're lazy · Italian version of 'the early bird catches the worm' [Source: Italian proverb]",
    "Tutto il mondo è paese · all the world is a village · people are the same everywhere · human nature is universal [Source: Italian proverb tradition]",
    "Ride bene chi ride ultimo · he who laughs last laughs best · direct Italian equivalent of the English phrase [Source: Italian proverb]",
    "Acqua in bocca! · water in your mouth! · keep it secret! · equivalent of 'mum's the word' · keep your mouth shut [Source: Italian expression]",
]

ITALIAN_MUSICAL_TERMS: dict[str, str] = {
    "piano":        "soft · full name 'pianoforte' (soft-loud) · Bartolomeo Cristofori invented ~1700 · instrument named for its dynamic capability · contrast with harpsichord [Source: Museo degli Strumenti Musicali]",
    "forte":        "loud/strong · from Italian 'forte' (strong) · f in musical notation · fortissimo (ff) = very loud · one of the most used dynamic markings [Source: music theory]",
    "allegro":      "lively/fast · from Italian 'allegro' (lively/merry) · tempo marking · allegretto = slightly slower than allegro · most common fast tempo [Source: music theory]",
    "adagio":       "slow and stately · from Italian 'adagio' (at ease) · ad + agio (at leisure) · slower than andante · famous: Barber Adagio for Strings [Source: music theory]",
    "crescendo":    "growing louder · from Italian 'crescere' (to grow) · marked with < symbol · common metaphor in English for 'building up' [Source: music theory]",
    "staccato":     "detached · from Italian 'staccare' (to separate) · dots above/below notes · opposite of legato · short clipped notes [Source: music theory]",
    "legato":       "smooth/connected · from Italian 'legare' (to tie) · notes flow smoothly into each other · opposite of staccato [Source: music theory]",
    "vibrato":      "oscillating pitch · from Italian 'vibrare' (to vibrate) · slight pitch variation for expression · all string and vocal performers use it [Source: music theory]",
    "soprano":      "highest voice · from Italian 'sopra' (above) · literally 'the one above' · female voice range · also instrument designation [Source: Italian musical heritage]",
    "tempo":        "speed/time · from Latin 'tempus' (time) · governs the speed of music · conductor sets tempo · metronome measures it in BPM [Source: music theory]",
    "fermata":      "pause/hold · from Italian 'fermare' (to stop) · bird's eye symbol · note held longer than written value · discretion of performer [Source: music theory]",
    "da capo":      "from the head · DC instruction · return to beginning · Da Capo al Fine = return to beginning and play to Fine marking [Source: music theory]",
    "coda":         "tail · concluding section of a piece · added ending material · from Latin 'cauda' (tail) [Source: music theory]",
}


# ─────────────────────────────────────────────────────────────
# CROSS-LANGUAGE DATA
# ─────────────────────────────────────────────────────────────

FALSE_FRIENDS: dict[str, str] = {
    "gift german":      "'Gift' in German means POISON · not a present · Mitgift = dowry (literally 'with-poison' — historical) · classic false friend for English speakers [Source: German etymology]",
    "actual spanish":   "'Actual' in Spanish means CURRENT/PRESENT · not 'real' · 'actualmente' = currently · the real thing is 'real' or 'verdadero' [Source: Spanish linguistics]",
    "pretend french":   "'Prétendre' in French means TO CLAIM · not to pretend · 'Je prétends' = I claim/assert · to pretend = faire semblant [Source: French linguistics]",
    "sympathetic french":"'Sympathique' in French means NICE/LIKEABLE · not sympathetic · to feel sympathy = compatir [Source: French linguistics]",
    "fabric french":    "'Fabrique' in French means FACTORY · not fabric · fabric = tissu [Source: French linguistics]",
    "sensible spanish": "'Sensible' in Spanish means SENSITIVE · not sensible/reasonable · sensible = sensato [Source: Spanish linguistics]",
    "embarrassed spanish":"'Embarazada' in Spanish means PREGNANT · not embarrassed · embarrassed = avergonzado [Source: Spanish linguistics]",
    "constipated spanish":"'Constipado' in Spanish means HAVING A COLD · not constipated · constipated = estreñido [Source: Spanish linguistics]",
    "eventuellement french":"'Éventuellement' in French means POSSIBLY · not eventually · eventually = finalement [Source: French linguistics]",
    "libreria italian": "'Libreria' in Italian means BOOKSHOP · not library · library = biblioteca [Source: Italian linguistics / Accademia della Crusca]",
    "casino french":    "'Casino' in French can mean MESS/CHAOS in informal usage · in addition to the gambling meaning [Source: French linguistics]",
}

LOANWORDS: dict[str, str] = {
    "manga english":    "Manga → English from Japanese 漫画 · now used globally · original meaning: whimsical/impromptu pictures · Hokusai popularized the term [Source: Japanese publishing history]",
    "safari english":   "Safari → English from Arabic 'safar' (journey) via Swahili · meaning evolved from 'journey' to 'wildlife expedition' in Africa [Source: Oxford English Dictionary]",
    "robot english":    "Robot → English from Czech 'robota' (forced labor) · coined by Karel Čapek in play R.U.R. 1920 · now used in every language [Source: Oxford English Dictionary]",
    "algebra english":  "Algebra → English from Arabic 'al-jabr' (the reunion of broken parts) · from Al-Khwarizmi's 9th century treatise [Source: mathematical history]",
    "alcohol english":  "Alcohol → English from Arabic 'al-kuhul' (the kohl) · originally referred to fine powder → distilled essence → spirits [Source: Oxford English Dictionary]",
    "tsunami english":  "Tsunami → English from Japanese 津波 · tsu (harbor) + nami (wave) · became standard scientific term globally after 2004 Indian Ocean tsunami [Source: NOAA]",
    "kindergarten english": "Kindergarten → English from German · kinder (children) + garten (garden) · Friedrich Froebel coined term 1840 · unchanged in English [Source: etymology]",
    "emoji english":    "Emoji → English from Japanese 絵文字 · e (picture) + moji (character) · not from 'emotion' despite similarity · Shigetaka Kurita 1999 [Source: MoMA / Unicode]",
    "loot english":     "Loot → English from Hindi 'lut' (plunder) · entered English during British colonial India · now mainstream English [Source: Oxford English Dictionary]",
    "avatar english":   "Avatar → English from Sanskrit 'avatara' (descent of a deity) · Hindu concept → computing term via Jaron Lanier 1980s → James Cameron film [Source: Oxford English Dictionary]",
}

NUMBERS_DATA: dict[str, list[str]] = {
    "japanese":  ["ichi", "ni", "san", "shi/yon", "go", "roku", "nana/shichi", "hachi", "ku/kyuu", "juu"],
    "italian":   ["uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove", "dieci"],
    "turkish":   ["bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on"],
    "arabic":    ["wahed", "ithnain", "thalatha", "arba", "khamsa", "sitta", "saba", "thamanya", "tisa", "ashra"],
    "russian":   ["odin", "dva", "tri", "chetyre", "pyat", "shest", "sem", "vosem", "devyat", "desyat"],
    "spanish":   ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"],
    "french":    ["un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix"],
    "german":    ["ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn"],
    "mandarin":  ["yi", "er", "san", "si", "wu", "liu", "qi", "ba", "jiu", "shi"],
    "korean":    ["il", "i", "sam", "sa", "o", "yuk", "chil", "pal", "gu", "sip"],
    "greek":     ["ena", "dyo", "tria", "tessera", "pende", "exi", "efta", "okto", "ennia", "deka"],
    "hindi":     ["ek", "do", "teen", "chaar", "paanch", "chhe", "saat", "aath", "nau", "das"],
    "portuguese":["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"],
    "polish":    ["jeden", "dwa", "trzy", "cztery", "pięć", "sześć", "siedem", "osiem", "dziewięć", "dziesięć"],
    "swahili":   ["moja", "mbili", "tatu", "nne", "tano", "sita", "saba", "nane", "tisa", "kumi"],
}

GREETINGS_DATA: dict[str, dict[str, str]] = {
    "japanese": {
        "hello (formal)": "Konnichiwa (こんにちは)",
        "hello (casual)": "Yaa / Ossu (やあ / おっす)",
        "good morning": "Ohayou gozaimasu (おはようございます)",
        "good evening": "Konbanwa (こんばんは)",
        "goodbye": "Sayonara (さようなら) / Ja ne (じゃあね) casual",
        "thank you": "Arigatou gozaimasu (ありがとうございます)",
        "please": "Onegaishimasu (お願いします)",
    },
    "italian": {
        "hello/goodbye (casual)": "Ciao (used for both)",
        "hello (formal)": "Salve / Buongiorno",
        "good morning": "Buongiorno",
        "good evening": "Buonasera",
        "goodbye (formal)": "Arrivederci",
        "thank you": "Grazie / Grazie mille (a thousand thanks)",
        "please": "Per favore / Per piacere",
    },
    "turkish": {
        "hello": "Merhaba",
        "good morning": "Günaydın",
        "good evening": "İyi akşamlar",
        "goodbye": "Güle güle (said by the one staying) / Hoşça kal (said by the one leaving)",
        "thank you": "Teşekkür ederim / Sağ ol (casual)",
        "please": "Lütfen",
    },
    "arabic": {
        "hello": "Marhaba / As-salamu alaykum (formal, Islamic)",
        "good morning": "Sabah al-khayr",
        "good evening": "Masa al-khayr",
        "goodbye": "Ma'a as-salama",
        "thank you": "Shukran",
        "please": "Min fadlak (to male) / Min fadlik (to female)",
    },
    "russian": {
        "hello (formal)": "Zdravstvuyte (Здравствуйте)",
        "hello (casual)": "Privet (Привет)",
        "good morning": "Dobroye utro (Доброе утро)",
        "goodbye": "Do svidaniya (До свидания) / Poka (Пока) casual",
        "thank you": "Spasibo (Спасибо)",
        "please": "Pozhaluysta (Пожалуйста)",
    },
    "greek": {
        "hello": "Geia sas (Γεια σας) formal / Yia sou (Γεια σου) casual",
        "good morning": "Kalimera (Καλημέρα)",
        "good evening": "Kalispera (Καλησπέρα)",
        "goodbye": "Antio (Αντίο) / Yia sou (Γεια σου) casual",
        "thank you": "Efcharisto (Ευχαριστώ)",
        "please": "Parakalo (Παρακαλώ)",
    },
    "hindi": {
        "hello": "Namaste (नमस्ते) — hands together",
        "good morning": "Suprabhat (सुप्रभात)",
        "goodbye": "Namaste / Alvida (अलविदा) formal",
        "thank you": "Dhanyavaad (धन्यवाद) / Shukriya (informal, Urdu-influenced)",
        "please": "Kripaya (कृपया)",
    },
    "swahili": {
        "hello": "Jambo / Habari (what news?)",
        "good morning": "Habari ya asubuhi",
        "goodbye": "Kwaheri",
        "thank you": "Asante / Asante sana (very much)",
        "please": "Tafadhali",
    },
}


class LanguageCog(commands.Cog):

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

    # ── JAPANESE ─────────────────────────────────────────────

    @commands.command(name="kanji")
    async def kanji(self, ctx: commands.Context, *, query: str = "") -> None:
        """Kanji meaning, readings, stroke count. Usage: !kanji 木"""
        if not query:
            await self._respond(ctx, "Usage: !kanji [character or meaning] — e.g. !kanji 木 or !kanji tree")
            return
        if not await self._check_cooldown(ctx, "kanji", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, KANJI_DATA)
        if result:
            await self._respond(ctx, f"Kanji {query}: {result} [Source: JLPT / Kenkyusha]")
        else:
            keys = "、".join(list(KANJI_DATA.keys())[:8])
            await self._respond(ctx, f"Kanji '{query}' not in database. Available: {keys}")

    @commands.command(name="japaneseconcept")
    async def japaneseconcept(self, ctx: commands.Context, *, query: str = "") -> None:
        """Untranslatable Japanese concepts. Usage: !japaneseconcept ikigai"""
        if not query:
            keys = ", ".join(list(JAPANESE_CONCEPTS.keys())[:5])
            await self._respond(ctx, f"Usage: !japaneseconcept [name] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "japaneseconcept", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, JAPANESE_CONCEPTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(JAPANESE_CONCEPTS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="japaneseword", aliases=["nihongoword", "wordinjapanese"])
    async def japaneseword(self, ctx: commands.Context, *, query: str = "") -> None:
        """Japanese word breakdown and etymology. Usage: !japaneseword sakura"""
        if not query:
            await self._respond(ctx, "Usage: !japaneseword [word] — e.g. !japaneseword kawaii")
            return
        if not await self._check_cooldown(ctx, "japaneseword", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, JAPANESE_WORDS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(JAPANESE_WORDS.keys())[:6])
            await self._respond(ctx, f"'{query}' not in database. Try: {keys}...")

    @commands.command(name="honorific")
    async def honorific(self, ctx: commands.Context, *, query: str = "") -> None:
        """Japanese honorifics explained. Usage: !honorific san"""
        if not query:
            keys = ", ".join(list(HONORIFICS.keys()))
            await self._respond(ctx, f"Usage: !honorific [term] — available: {keys}")
            return
        if not await self._check_cooldown(ctx, "honorific", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, HONORIFICS)
        if result:
            await self._respond(ctx, f"!{query}: {result}")
        else:
            await self._respond(ctx, f"Honorific '{query}' not found. Try: san, kun, chan, sama, sensei, senpai")

    @commands.command(name="japanesecount")
    async def japanesecount(self, ctx: commands.Context, *, query: str = "") -> None:
        """Japanese counter words. Usage: !japanesecount animals"""
        if not query:
            keys = ", ".join(list(JAPANESE_COUNTERS.keys())[:5])
            await self._respond(ctx, f"Usage: !japanesecount [type] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "japanesecount", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, JAPANESE_COUNTERS)
        if result:
            await self._respond(ctx, f"Counter for {query}: {result} [Source: JLPT reference]")
        else:
            keys = ", ".join(list(JAPANESE_COUNTERS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="japaneseproverb", aliases=["kotowaza", "japanesewisdom"])
    async def japaneseproverb(self, ctx: commands.Context) -> None:
        """Random Japanese proverb. Usage: !japaneseproverb"""
        if not await self._check_cooldown(ctx, "japaneseproverb", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(JAPANESE_PROVERBS))

    @commands.command(name="jlpt")
    async def jlpt(self, ctx: commands.Context, *, query: str = "") -> None:
        """JLPT level of a Japanese word. Usage: !jlpt ありがとう"""
        if not query:
            await self._respond(ctx, "Usage: !jlpt [word] — e.g. !jlpt ありがとう or !jlpt daijoubu")
            return
        if not await self._check_cooldown(ctx, "jlpt", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, JLPT_WORDS)
        if result:
            level, desc = result
            await self._respond(ctx, f"'{query}' — JLPT {level} | {desc} [Source: JLPT official word lists]")
        else:
            await self._respond(ctx, f"'{query}' not in JLPT database. Try: ありがとう, 大丈夫, 醸造, 忖度, 曖昧")

    @commands.command(name="japanesefood", aliases=["washoku"])
    async def japanesefood(self, ctx: commands.Context, *, query: str = "") -> None:
        """Japanese dish deep dive. Usage: !japanesefood ramen"""
        if not query:
            keys = ", ".join(list(JAPANESE_FOOD.keys())[:5])
            await self._respond(ctx, f"Usage: !japanesefood [dish] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "japanesefood", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, JAPANESE_FOOD)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(JAPANESE_FOOD.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    # ── ITALIAN ──────────────────────────────────────────────

    @commands.command(name="italianword", aliases=["vocabolario", "wordsinitalian"])
    async def italianword(self, ctx: commands.Context, *, query: str = "") -> None:
        """Italian word origin and history. Usage: !italianword ciao"""
        if not query:
            await self._respond(ctx, "Usage: !italianword [word] — e.g. !italianword ciao or !italianword pizza")
            return
        if not await self._check_cooldown(ctx, "italianword", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, ITALIAN_WORDS)
        if result:
            await self._respond(ctx, f"'{query}': {result}")
        else:
            keys = ", ".join(list(ITALIAN_WORDS.keys())[:6])
            await self._respond(ctx, f"'{query}' not found. Try: {keys}...")

    @commands.command(name="italiangesture")
    async def italiangesture(self, ctx: commands.Context, *, query: str = "") -> None:
        """Italian hand gesture meanings. Usage: !italiangesture pinched fingers"""
        if not query:
            keys = ", ".join(list(ITALIAN_GESTURES.keys())[:4])
            await self._respond(ctx, f"Usage: !italiangesture [name] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "italiangesture", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, ITALIAN_GESTURES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(ITALIAN_GESTURES.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="italiandialect", aliases=["dialetto"])
    async def italiandialect(self, ctx: commands.Context, *, query: str = "") -> None:
        """Italian regional dialect facts. Usage: !italiandialect neapolitan"""
        if not query:
            keys = ", ".join(list(ITALIAN_DIALECTS.keys())[:5])
            await self._respond(ctx, f"Usage: !italiandialect [region] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "italiandialect", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, ITALIAN_DIALECTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(ITALIAN_DIALECTS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="italianconcept")
    async def italianconcept(self, ctx: commands.Context, *, query: str = "") -> None:
        """Untranslatable Italian concepts. Usage: !italianconcept dolce far niente"""
        if not query:
            keys = ", ".join(list(ITALIAN_CONCEPTS.keys())[:4])
            await self._respond(ctx, f"Usage: !italianconcept [concept] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "italianconcept", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, ITALIAN_CONCEPTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(ITALIAN_CONCEPTS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="italianfood")
    async def italianfood(self, ctx: commands.Context, *, query: str = "") -> None:
        """Italian dish deep dive with authentic details. Usage: !italianfood carbonara"""
        if not query:
            keys = ", ".join(list(ITALIAN_FOOD.keys())[:5])
            await self._respond(ctx, f"Usage: !italianfood [dish] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "italianfood", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, ITALIAN_FOOD)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(ITALIAN_FOOD.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="latinroot")
    async def latinroot(self, ctx: commands.Context, *, query: str = "") -> None:
        """Latin root of Italian words and cognates. Usage: !latinroot acqua"""
        if not query:
            await self._respond(ctx, "Usage: !latinroot [word] — e.g. !latinroot acqua or !latinroot vita")
            return
        if not await self._check_cooldown(ctx, "latinroot", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, LATIN_ROOTS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(LATIN_ROOTS.keys())[:6])
            await self._respond(ctx, f"'{query}' not found. Try: {keys}...")

    @commands.command(name="italianidiom")
    async def italianidiom(self, ctx: commands.Context) -> None:
        """Random Italian idiom or proverb. Usage: !italianidiom"""
        if not await self._check_cooldown(ctx, "italianidiom", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(ITALIAN_IDIOMS))

    @commands.command(name="italianmusicalterm")
    async def italianmusicalterm(self, ctx: commands.Context, *, query: str = "") -> None:
        """Italian musical terms used worldwide. Usage: !italianmusicalterm allegro"""
        if not query:
            keys = ", ".join(list(ITALIAN_MUSICAL_TERMS.keys())[:6])
            await self._respond(ctx, f"Usage: !italianmusicalterm [term] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "italianmusicalterm", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, ITALIAN_MUSICAL_TERMS)
        if result:
            await self._respond(ctx, f"'{query}': {result}")
        else:
            keys = ", ".join(list(ITALIAN_MUSICAL_TERMS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    # ── CROSS-LANGUAGE ───────────────────────────────────────

    @commands.command(name="falsefriend", aliases=["falsewords", "deceptiveword"])
    async def falsefriend(self, ctx: commands.Context, *, query: str = "") -> None:
        """Words that look similar across languages but mean different things. Usage: !falsefriend gift german"""
        if not query:
            keys = ", ".join(list(FALSE_FRIENDS.keys())[:4])
            await self._respond(ctx, f"Usage: !falsefriend [word language] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "falsefriend", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, FALSE_FRIENDS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(FALSE_FRIENDS.keys())[:5])
            await self._respond(ctx, f"'{query}' not found. Try: {keys}...")

    @commands.command(name="loanword", aliases=["borrowedword"])
    async def loanword(self, ctx: commands.Context, *, query: str = "") -> None:
        """Words borrowed between languages. Usage: !loanword manga english"""
        if not query:
            keys = ", ".join(list(LOANWORDS.keys())[:4])
            await self._respond(ctx, f"Usage: !loanword [word language] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "loanword", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, LOANWORDS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(LOANWORDS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    @commands.command(name="numbers", aliases=["countingto10", "numbersin"])
    async def numbers(self, ctx: commands.Context, *, language: str = "") -> None:
        """Numbers 1-10 in any language. Usage: !numbers japanese"""
        if not language:
            keys = ", ".join(list(NUMBERS_DATA.keys()))
            await self._respond(ctx, f"Usage: !numbers [language] — available: {keys}")
            return
        if not await self._check_cooldown(ctx, "numbers", DEFAULT_COOLDOWN):
            return
        lang = language.strip().lower()
        if lang in NUMBERS_DATA:
            nums = NUMBERS_DATA[lang]
            result = " · ".join(f"{i+1}={n}" for i, n in enumerate(nums))
            await self._respond(ctx, f"{language.title()} 1-10: {result}")
        else:
            keys = ", ".join(list(NUMBERS_DATA.keys()))
            await self._respond(ctx, f"Language '{language}' not found. Available: {keys}")

    @commands.command(name="greeting", aliases=["greetingin", "helloin", "howtosay"])
    async def greeting(self, ctx: commands.Context, *, language: str = "") -> None:
        """How to say hello, goodbye, thank you in any language. Usage: !greeting japanese"""
        if not language:
            keys = ", ".join(list(GREETINGS_DATA.keys()))
            await self._respond(ctx, f"Usage: !greeting [language] — available: {keys}")
            return
        if not await self._check_cooldown(ctx, "greeting", DEFAULT_COOLDOWN):
            return
        lang = language.strip().lower()
        if lang in GREETINGS_DATA:
            greets = GREETINGS_DATA[lang]
            parts  = [f"{k}: {v}" for k, v in list(greets.items())[:4]]
            await self._respond(ctx, f"{language.title()} greetings — " + " | ".join(parts))
        else:
            keys = ", ".join(list(GREETINGS_DATA.keys()))
            await self._respond(ctx, f"Language '{language}' not found. Available: {keys}")


def prepare(bot):
    bot.add_cog(LanguageCog(bot))
