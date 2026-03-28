# PiicaBot — twitch_bot/commands/cooking.py
# Cooking and food knowledge commands.
# !dish !ingredient !technique !foodorigin !pairing
# !oldestrecipe !streetfood !fermented !umami
# Sources: Oxford Companion to Food, Larousse Gastronomique,
#          FAO databases, UNESCO cultural heritage lists

import random
from twitchio.ext import commands
from loguru import logger

import database.db as db
from config import DEFAULT_COOLDOWN


DISHES: dict[str, str] = {
    "baklava":          "Origin disputed between Ottoman Empire, Greece, and Middle East · phyllo dough + honey + pistachios or walnuts · sugar syrup added after baking · eaten across 30+ countries [Source: Oxford Companion to Food]",
    "moussaka":         "Greece and Middle East · layered eggplant + minced meat + béchamel · Greek version codified by chef Nikolaos Tselementes 1930s · each country has variations [Source: Oxford Companion to Food]",
    "biryani":          "South Asia · Mughal Empire origin · layered fragrant rice + meat/vegetables + spices · over 80 regional varieties in India alone · dum cooking technique [Source: Oxford Companion to Food / Indian culinary history]",
    "paella":           "Valencia, Spain · originally a peasant dish cooked over open fire · authentic: rabbit + chicken + snails + green beans + saffron · NO chorizo in traditional paella [Source: Denominación de Origen Arroz de Valencia]",
    "sushi":            "Japan · originally preserved fish in fermented rice · modern vinegared rice sushi ~1820s Edo (Tokyo) · nigiri style created by Hanaya Yohei · now global [Source: Japanese culinary history]",
    "pasta carbonara":  "Rome, Italy · post-WWII origin likely · authentic: guanciale + eggs + Pecorino Romano + black pepper · NO cream · named possibly for charcoal workers (carbonari) [Source: Accademia Italiana della Cucina]",
    "tacos":            "Mexico · pre-Columbian origin · taco means 'plug' in Spanish · corn or flour tortilla · enormous regional variation · Mexico City alone has hundreds of taco varieties [Source: food history]",
    "pho":              "Vietnam · Hanoi origin ~1900s · rice noodles + broth (beef or chicken) · spices: star anise, cloves, cinnamon · French influence debated · national dish [Source: Vietnamese culinary history]",
    "pad thai":         "Thailand · government-promoted in 1940s to reduce rice consumption · rice noodles + shrimp/tofu + egg + bean sprouts + peanuts + tamarind · relatively modern dish [Source: Thai culinary history]",
    "hummus":           "Middle East · origin disputed (Lebanon, Israel, Palestine all claim it) · chickpeas + tahini + lemon + garlic · hummus bi tahini = hummus with tahini · 10,000+ years of chickpea cultivation [Source: Oxford Companion to Food]",
    "croissant":        "French in execution, Austrian in origin · Viennese kipferl crescent pastry · brought to France by August Zang 1838-1839 · French bakers perfected laminated dough [Source: Oxford Companion to Food]",
    "ramen":            "Japan · Chinese origin (lamian pulled noodles) · arrived Japan via Chinese immigrants · each region distinct: Sapporo (miso), Hakata (tonkotsu), Tokyo (shoyu) · UNESCO heritage candidate [Source: Japan Ramen Association]",
    "kimchi":           "Korea · fermented vegetables (usually napa cabbage) + gochugaru + garlic + ginger · 200+ varieties · UNESCO Intangible Cultural Heritage 2013 · kimjang (making kimchi) is community tradition [Source: UNESCO]",
    "falafel":          "Middle East · origin disputed: Egypt (made from fava beans), Levant (chickpeas) · street food tradition · now global · vegan protein source [Source: Oxford Companion to Food]",
    "dim sum":          "Cantonese China · yum cha (drinking tea) culture · small dishes shared at tea houses · over 1000 types of dim sum exist · Sunday family tradition in Hong Kong [Source: Cantonese culinary tradition]",
    "tagine":           "Morocco and North Africa · named for the conical clay pot it's cooked in · slow-cooked meat + preserved lemons + olives + spices · Berber origin · UNESCO heritage [Source: UNESCO / Moroccan culinary tradition]",
    "pierogi":          "Poland · dumplings with various fillings: potato+cheese, sauerkraut+mushroom, meat, sweet fillings · Ukrainian varenyky is closely related · feast day tradition [Source: Polish culinary history]",
    "börek":            "Turkey and Ottoman-descended cuisines · phyllo pastry + various fillings · su böreği (water börek) considered finest · eaten from Morocco to the Balkans [Source: Turkish culinary tradition]",
    "goulash":          "Hungary · herdsmen's (gulyás) dish · beef + paprika · paprika only added after 16th century · became Hungarian national dish · many regional European variations [Source: Hungarian culinary history]",
    "risotto":          "Northern Italy (Lombardy, Piedmont) · Arborio/Carnaroli rice · constant stirring (mantecatura) · broth added gradually · risotto alla Milanese uses saffron [Source: Italian culinary tradition]",
}

INGREDIENTS_DATA: dict[str, str] = {
    "saffron":      "Most expensive spice by weight · Iran produces 90% of world supply (~430 tons/year) · used in paella (Spain), risotto alla Milanese (Italy), biryani (India), bouillabaisse (France) · from Crocus sativus · 150,000 flowers for 1kg saffron [Source: FAO / Larousse Gastronomique]",
    "sumac":        "Deep red berry ground into powder · intensely tart and citrusy · native to Middle East and Mediterranean · used in za'atar spice blend, fattoush salad, sprinkled on hummus · Lebanon, Syria, Iran, Turkey [Source: Oxford Companion to Food]",
    "miso":         "Japanese fermented soybean paste · made with koji mold · white (shiro) = mild/sweet, red (aka) = stronger/saltier · used in soup, marinades, glazes · 3,000+ year history [Source: Japanese culinary tradition]",
    "tahini":       "Sesame seed paste · Middle Eastern staple · essential in hummus, baba ganoush, halva · high sesame cultivation in Ethiopia, Sudan, India · also used in Chinese, Japanese, Korean cuisine [Source: Oxford Companion to Food]",
    "mirin":        "Japanese sweet rice wine · essential to teriyaki, sukiyaki, glazes · adds gloss and mild sweetness · 14% alcohol · cannot be substituted with sake+sugar [Source: Japanese culinary tradition]",
    "harissa":      "North African chili paste · Tunisia national condiment · red chiles + caraway + coriander + garlic + olive oil · UNESCO Intangible Cultural Heritage of Tunisia 2022 [Source: UNESCO 2022]",
    "amchur":       "Dried green mango powder · India · intensely sour · used to add tartness without liquid · chaat masala contains it · tenderizes meat [Source: Indian culinary tradition]",
    "preserved lemon": "North African and Moroccan staple · whole lemons cured in salt and lemon juice · intense flavor, nothing like fresh lemon · essential in tagine · 30+ days to cure [Source: Moroccan culinary tradition]",
    "bonito flakes": "Katsuobushi · Japan · dried, smoked, fermented skipjack tuna · shaved into thin flakes · essential dashi broth ingredient · used as topping (okonomiyaki, takoyaki) · umami powerhouse [Source: Japanese culinary tradition]",
    "za'atar":      "Middle Eastern spice blend · dried thyme/oregano/marjoram + sumac + sesame seeds + salt · each family/country has different blend · eaten with olive oil and bread · also a plant (wild thyme) [Source: Oxford Companion to Food]",
    "gochugaru":    "Korean red pepper flakes · essential to kimchi, gochujang, tteokbokki · fruity and smoky rather than purely hot · Korean cooking nearly unrecognizable without it [Source: Korean culinary tradition]",
    "asafoetida":   "Hing · Indian spice from resin of Ferula plant · smells sulfurous raw, transforms to garlic-onion flavor when cooked · used in Jain cooking (no onion/garlic allowed) [Source: Indian culinary tradition]",
    "fenugreek":    "Methi · seeds and leaves used · bittersweet maple-like flavor · essential in Indian, Ethiopian, Egyptian, Turkish cuisine · used in maple syrup flavor compounds [Source: Oxford Companion to Food]",
    "star anise":   "China primarily · licorice-like flavor · essential in Chinese five-spice powder, Vietnamese pho broth, French pastis · main commercial source of shikimic acid (Tamiflu precursor) [Source: Oxford Companion to Food]",
    "pomegranate molasses": "Middle East · reduced pomegranate juice · intensely sour-sweet · used in Persian (fesenjan), Lebanese, Syrian cooking · muhammara walnut dip requires it [Source: Levantine culinary tradition]",
}

COOKING_TECHNIQUES: dict[str, str] = {
    "confit":       "French · slow cooking submerged in fat at low temperature (70-80°C) · preserves and tenderizes · duck confit is classic · originally a preservation method before refrigeration [Source: Larousse Gastronomique]",
    "sous vide":    "Under vacuum · French · vacuum-sealed food cooked in precisely controlled water bath · developed by Georges Pralus 1974 for foie gras · now mainstream · precise temperature control [Source: culinary arts / Harold McGee]",
    "maillard reaction": "Browning reaction between amino acids and sugars at 140-165°C · responsible for seared meat, toast, coffee, bread crust flavor · Louis-Camille Maillard described 1912 · essential to 'meaty' flavors [Source: food science / Harold McGee]",
    "fermentation": "Anaerobic microbial transformation of food · lactic acid fermentation (yogurt, kimchi, sauerkraut) · alcoholic fermentation (wine, beer, bread) · 10,000+ year history · preserves and creates new flavors [Source: food science]",
    "tempering":    "Chocolate: controlled heating and cooling to create stable crystal structure (Form V cocoa butter) · gives chocolate snap, gloss, melt · without it: chocolate blooms (grey streaks) [Source: food science / cocoa chemistry]",
    "mise en place":"French: everything in its place · professional kitchen preparation · all ingredients prepped before cooking begins · discipline of cooking [Source: culinary arts / Escoffier]",
    "emulsification":"Combining immiscible liquids (oil + water) with an emulsifier · mayonnaise: egg yolk lecithin emulsifies oil + vinegar · hollandaise, vinaigrette, aioli all rely on this [Source: food science]",
    "brining":      "Soaking meat in saltwater solution · salt draws moisture in and denatures proteins slightly · chicken breast stays juicier · used for thousands of years as preservation [Source: food science / Harold McGee]",
    "smoke":        "Preserves and flavors via phenols, carbonyls, organic acids in smoke · cold smoke (< 30°C) for salmon, charcuterie · hot smoke (>74°C) cooks and smokes simultaneously · each wood gives different flavor [Source: food science]",
    "caramelization": "Pure sugar heated to 160-180°C breaks down and creates hundreds of new flavor compounds · distinct from Maillard (requires protein) · caramel color: amber then dark brown then bitter [Source: food science / Harold McGee]",
    "resting":      "Meat resting after cooking · muscle fibers relax and reabsorb juices · cutting immediately loses 40%+ of juice · rest time = half the cooking time roughly · most overlooked technique [Source: food science]",
    "blanching":    "Brief boiling followed by ice bath · preserves color and texture of vegetables · partially cooks · stops enzyme activity · essential step before freezing vegetables [Source: culinary arts]",
}

FOOD_ORIGINS: dict[str, str] = {
    "french fries":     "NOT French · most likely Belgian origin · name comes from 'French' as in julienne/cut thin · Belgians have eaten fried potatoes since 17th century · Thomas Jefferson noted 'potatoes, fried in the French manner' 1802 [Source: Oxford Companion to Food]",
    "croissant":        "NOT originally French · Austrian kipferl crescent pastry · brought to Paris by August Zang 1838-1839 · French bakers added laminated dough technique [Source: Oxford Companion to Food]",
    "danish pastry":    "NOT Danish · invented by Austrian bakers (wienerbrød = Viennese bread) brought to Denmark in 1850s labor strike · Danes hired Austrians · Danes called them Viennese [Source: Oxford Companion to Food]",
    "german chocolate cake": "NOT German origin · named after Sam German, an American baker who created Baker's German's Sweet Chocolate in 1852 [Source: General Foods / historical record]",
    "buffalo wings":    "Buffalo, New York 1964 · invented by Teressa Bellissimo at Anchor Bar · covered in hot sauce and butter · served with celery and blue cheese · became American icon [Source: Anchor Bar historical record]",
    "fortune cookies":  "NOT Chinese · invented in USA by Japanese immigrants in California ~1890s-1900s · never eaten in China until recently as novelty for tourists [Source: historical research / Jennifer 8. Lee 'The Fortune Cookie Chronicles']",
    "pasta":            "NOT brought from China by Marco Polo · Italian pasta documented before Marco Polo's journey · different traditions evolved independently · Arabs brought pasta to Sicily ~8th century [Source: Oxford Companion to Food]",
    "worcestershire sauce": "NOT made in India · invented in Worcester, England by Lea & Perrins 1837 · they claim a recipe from India inspired it but it's a British invention [Source: Lea & Perrins historical record]",
    "napoleon cake":    "NOT named for Napoleon Bonaparte · name possibly from 'Napolitain' (Neapolitan) · French mille-feuille is the original · Napoleon connection is likely a folk etymology [Source: culinary history research]",
    "caesar salad":     "NOT Roman or Italian · invented 1924 in Tijuana, Mexico by Italian immigrant Caesar Cardini on July 4th, running low on supplies [Source: Rosa Cardini / historical record]",
}

FOOD_PAIRINGS: dict[str, str] = {
    "chocolate strawberry": "Complementary volatile compounds · both contain linalool · chocolate's phenylacetic acid pairs with strawberry esters · scientifically validated food pairing [Source: food chemistry / Heston Blumenthal research]",
    "wine cheese":          "Fats in cheese coat the palate and balance wine's tannins/acidity · protein in cheese binds bitter compounds · high-fat aged cheeses pair with tannic reds · fresh cheese with whites [Source: food science / wine pairing]",
    "lamb rosemary":        "Rosemary's borneol and camphor compounds complement lamb's gaminess · Mediterranean tradition · both from same climate zone · terpenoids enhance fatty meat [Source: food pairing research]",
    "tomato basil":          "Classic Italian combination · shared linalool compound · tomato's glutamates enhanced by basil's aromatic compounds · acidity balanced by basil sweetness [Source: food chemistry]",
    "peanut butter jelly":  "American comfort combination · fat in peanut butter slows sugar absorption from jam · protein + simple sugars = balanced energy · texture contrast [Source: food science]",
    "lemon fish":           "Acid denatures fish proteins (partial 'cooking') · citric acid cuts through fish's amine odor compounds · brightens flavor · also used in ceviche for same reason [Source: food chemistry]",
    "coffee cardamom":      "Middle Eastern tradition · cardamom's volatile compounds complement coffee's 800+ aroma compounds · reduces bitterness perception · Qatar/Saudi/Turkish tradition [Source: food pairing / culinary tradition]",
    "apple cinnamon":       "Classic autumn pairing · cinnamon's cinnamaldehyde complements apple's esters · both contain eugenol · acid in apple balanced by cinnamon warmth [Source: food chemistry]",
    "caramel sea salt":     "Contrast pairing · salt suppresses bitterness perception and enhances sweetness · amplifies caramel complexity · sodium ions block bitter receptors [Source: food science / neurogastronomy]",
    "parmesan truffle":     "Shared aromatic compounds including dimethyl sulfide and other sulfur compounds · umami from parmesan amplifies truffle's earthiness · classic Italian luxury combination [Source: food pairing research]",
}

OLDEST_RECIPES: list[str] = [
    "Sumerian beer recipe ~1800 BCE · Hymn to Ninkasi (goddess of beer) · written in cuneiform on clay tablet · University of Chicago Oriental Institute · archaeologists recreated it [Source: Oriental Institute, University of Chicago]",
    "Babylonian stew recipe ~1750 BCE · Yale Babylonian Collection · clay tablets with 25 recipes · includes lamb stew with onions, garlic, herbs · oldest cookbook fragments [Source: Yale Babylonian Collection]",
    "Ancient Egyptian bread ~3500 BCE · evidence from hieroglyphs and grain remains in tombs · sourdough starter-style fermentation · emmer wheat · found in Deir el-Medina worker village [Source: archaeological record]",
    "Roman garum (fish sauce) recipe · preserved in Apicius 'De Re Coquinaria' ~4th century CE · fermented fish + salt in clay pots · equivalent to modern colatura di alici or fish sauce · predecessor of Worcestershire sauce [Source: Apicius manuscript]",
    "Apicius recipes ~400 CE · oldest known cookbook · 'De Re Coquinaria' (On the Subject of Cooking) · 10 books, 500+ recipes · shows sophisticated Roman cuisine [Source: Apicius manuscript / culinary history]",
    "Medieval Arab cookbook 'Kitab al-Tabikh' 1226 CE · by Muhammad bin Hasan al-Baghdadi · 160 recipes · Abbasid Caliphate cuisine · includes meatballs, stews, desserts [Source: academic manuscript study]",
    "Forme of Cury ~1390 CE · English cookbook commissioned by Richard II's master cooks · 205 recipes · oldest English-language cookbook · includes blancmange origin [Source: British Museum / culinary history]",
]

STREET_FOODS: dict[str, str] = {
    "turkey":       "Simit · sesame-crusted circular bread · sold since Ottoman times · 300+ tons sold daily in Istanbul alone · vendor carts (simitçi) iconic cityscape · perfect with tea [Source: Istanbul Metropolitan Municipality]",
    "mexico":       "Tacos al pastor · spit-roasted pork (inspired by Lebanese shawarma brought by immigrants) · pineapple + cilantro + onion + salsa · Mexico City street food culture UNESCO heritage [Source: UNESCO / Mexican culinary heritage]",
    "india":        "Pani puri (Mumbai) / Golgappa (Delhi) / Puchka (Kolkata) · crispy hollow puri filled with tangy water + tamarind + spices · same concept, fierce regional loyalty · billions sold daily [Source: Indian street food culture]",
    "japan":        "Takoyaki · octopus balls · Osaka street food invented 1935 by Tomekichi Endo · spherical shape from special pan · topped with bonito flakes that 'dance' from heat [Source: Osaka culinary history]",
    "vietnam":      "Bánh mì · French baguette + Vietnamese fillings (pâté, pickled vegetables, cilantro, chili) · fusion born from French colonialism · now global street food [Source: Vietnamese culinary history]",
    "thailand":     "Pad thai · rice noodles + tamarind + fish sauce + peanuts · government promoted in 1940s · Yaowarat (Bangkok Chinatown) serves it 24 hours [Source: Thai culinary history]",
    "morocco":      "Msemen and khobz · flatbreads everywhere · but Jemaa el-Fna square in Marrakech has 100+ food stalls · legendary night market · UNESCO cultural space [Source: UNESCO]",
    "senegal":      "Thiéboudienne (national dish) · rice + fish + tomato + vegetables · but street food: bean sandwiches (sandwiches aux haricots) · Dakar street food thriving economy [Source: Senegalese culinary tradition]",
    "south korea":  "Tteokbokki · chewy rice cakes in spicy gochujang sauce · Seoul street food staple · originally a royal court dish · now available everywhere 24/7 [Source: Korean culinary history]",
    "nigeria":      "Suya · spiced meat skewers (beef, chicken, offal) · ground groundnuts + spices coating · northern Nigeria origin · sold at night by mallam suya sellers [Source: West African culinary tradition]",
    "egypt":        "Koshari · rice + lentils + pasta + tomato sauce + crispy onions + garlic vinegar · all carbohydrates · Cairo national dish · extremely affordable · originated from Italian influence [Source: Egyptian culinary history]",
    "colombia":     "Arepas · cornmeal flatbreads · every region different · Medellín: thick filled · Bogotá: thin simple · Barranquilla: fried · 3,000+ years pre-Columbian history [Source: Colombian culinary heritage]",
}

FERMENTED_FOODS: dict[str, str] = {
    "kimchi":       "Korea · fermented vegetables (primarily napa cabbage) · gochugaru + garlic + ginger + jeotgal (salted seafood) · 200+ varieties · UNESCO Intangible Heritage 2013 · kimjang tradition [Source: UNESCO]",
    "kombucha":     "Fermented tea · SCOBY (symbiotic culture of bacteria and yeast) · originated Northeast China/Manchuria ~220 BCE · 'tea of immortality' · became global health trend [Source: food science history]",
    "kefir":        "Fermented milk drink · originated Caucasus mountains · Lactobacillus kefiri + yeasts · NATO classified it as beneficial probiotic food · 'grains' are actually SCOBY clusters [Source: food science]",
    "miso":         "Japan · fermented soybean paste with koji mold · 3000-year history · white/red/mixed varieties · different fermentation times · used in soup, marinades, glazes · umami powerhouse [Source: Japanese culinary tradition]",
    "sourdough":    "Lactobacillus + wild yeast · oldest leavened bread method · 14,000 years old evidence in Jordan · superior flavor through organic acids · modern revival as artisan bread [Source: archaeological record / food science]",
    "natto":        "Japan · fermented soybeans with Bacillus subtilis · strong smell + sticky texture · highly polarizing · eaten primarily in eastern Japan · extremely high in Vitamin K2 [Source: Japanese food tradition]",
    "tempeh":       "Indonesia · fermented whole soybeans with Rhizopus mold · solid cake form · origin Java ~16th century · high protein · now global plant-based protein [Source: Indonesian culinary history]",
    "kvass":        "Russia and Eastern Europe · fermented beverage from bread (usually rye) · very low alcohol · sold from large yellow tanks on Soviet-era streets · ancient Slavic tradition [Source: Eastern European food history]",
    "sauerkraut":   "Germany but actually ancient Chinese origin · Mongols brought fermented cabbage to Europe · lactic acid fermentation · Captain Cook used it to prevent scurvy on long voyages [Source: food history / Oxford Companion to Food]",
    "fish sauce":   "Southeast Asia and ancient Rome (garum) · fermented fish + salt · months to years · Vietnam (nước mắm), Thailand (nam pla) · Worcestershire sauce contains it [Source: Oxford Companion to Food]",
    "injera":       "Ethiopia and Eritrea · fermented teff flatbread · 2-3 days fermentation · spongy texture · used as both plate and utensil · ancient grain teff native to Ethiopia [Source: Ethiopian culinary tradition]",
}

UMAMI_FOODS: dict[str, str] = {
    "parmesan":     "Parmigiano Reggiano · among highest glutamate concentrations of any food · 1200mg/100g · PDO protected · aged 12-36 months · umami crystals (tyrosine) visible in aged cheese [Source: Umami Information Center / food science]",
    "tomatoes":     "Ripe tomatoes: 250mg glutamate per 100g · increases dramatically when cooked · sun-dried tomatoes: 650-1140mg · cooking concentrates and converts glutamates [Source: Umami Information Center]",
    "mushrooms":    "Dried shiitake: highest guanylate content of any food · 150mg per 100g · synergistic effect with glutamates multiplies umami 8x · kombu+shiitake dashi extremely umami-rich [Source: food science / Japanese culinary tradition]",
    "soy sauce":    "780-1090mg glutamate per 100g · fermentation creates free glutamates · shoyu, tamari, liquid aminos all extremely high · ancient condiment 2,500+ years [Source: Umami Information Center]",
    "anchovies":    "670mg glutamate per 100g · secret ingredient in many sauces · dissolves completely in cooking · Worcestershire sauce, Gentilhomme, pasta puttanesca [Source: food science]",
    "miso":         "200-700mg glutamate per 100g depending on type · fermentation creates free amino acids · darker miso = longer fermentation = more umami [Source: Umami Information Center]",
    "kombu":        "Kelp · 1608mg glutamate per 100g · highest natural source of glutamate · Kikunae Ikeda discovered glutamate from kombu 1908 · named umami [Source: Ikeda 1909 paper / food science]",
    "fish sauce":   "High glutamate from fermentation · 950mg per 100g · SE Asian cooking fundamental · ancient Romans used garum similarly · small amounts transform dishes [Source: food science]",
    "worcestershire": "Contains anchovies, tamarind, onion · multiple umami sources combined · even non-anchovy ingredients add complexity · Lea & Perrins since 1837 [Source: food science / manufacturer]",
    "vegemite":     "Australian yeast extract · extremely high glutamate · 3786mg per 100g! · Marmite (UK) similar · very divisive flavors but umami intense [Source: food chemistry research]",
}


class CookingCog(commands.Cog):

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

    # ── !dish ────────────────────────────────────────────────

    @commands.command(name="dish", aliases=["dishorigin", "aboutdish"])
    async def dish(self, ctx: commands.Context, *, query: str = "") -> None:
        """Dish origin, history and key ingredients. Usage: !dish baklava"""
        if not query:
            keys = ", ".join(list(DISHES.keys())[:6])
            await self._respond(ctx, f"Usage: !dish [name] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "dish", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, DISHES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(DISHES.keys())[:8])
            await self._respond(ctx, f"Dish '{query}' not found. Try: {keys}...")

    # ── !ingredient ──────────────────────────────────────────

    @commands.command(name="ingredient", aliases=["ingredientinfo", "aboutingredient"])
    async def ingredient(self, ctx: commands.Context, *, query: str = "") -> None:
        """Which cuisines use an ingredient, native region, flavor profile. Usage: !ingredient saffron"""
        if not query:
            keys = ", ".join(list(INGREDIENTS_DATA.keys())[:5])
            await self._respond(ctx, f"Usage: !ingredient [name] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "ingredient", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, INGREDIENTS_DATA)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(INGREDIENTS_DATA.keys())[:8])
            await self._respond(ctx, f"Ingredient '{query}' not found. Try: {keys}...")

    # ── !technique ───────────────────────────────────────────

    @commands.command(name="technique", aliases=["cookingtechnique", "cookmethod"])
    async def technique(self, ctx: commands.Context, *, query: str = "") -> None:
        """Cooking technique explained with food science. Usage: !technique confit"""
        if not query:
            keys = ", ".join(list(COOKING_TECHNIQUES.keys())[:5])
            await self._respond(ctx, f"Usage: !technique [name] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "technique", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, COOKING_TECHNIQUES)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(COOKING_TECHNIQUES.keys()))
            await self._respond(ctx, f"Technique '{query}' not found. Available: {keys}")

    # ── !foodorigin ──────────────────────────────────────────

    @commands.command(name="foodorigin", aliases=["truefoodorigin", "wherediditcomefrom"])
    async def foodorigin(self, ctx: commands.Context, *, query: str = "") -> None:
        """Where a food was really invented — often not where people think. Usage: !foodorigin croissant"""
        if not query:
            keys = ", ".join(list(FOOD_ORIGINS.keys())[:5])
            await self._respond(ctx, f"Usage: !foodorigin [food] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "foodorigin", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, FOOD_ORIGINS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(FOOD_ORIGINS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    # ── !pairing ─────────────────────────────────────────────

    @commands.command(name="pairing", aliases=["foodpairing", "goeswith"])
    async def pairing(self, ctx: commands.Context, *, query: str = "") -> None:
        """Classic food pairings and the flavor science behind them. Usage: !pairing chocolate strawberry"""
        if not query:
            keys = ", ".join(list(FOOD_PAIRINGS.keys())[:4])
            await self._respond(ctx, f"Usage: !pairing [foods] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "pairing", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, FOOD_PAIRINGS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(FOOD_PAIRINGS.keys()))
            await self._respond(ctx, f"Pairing '{query}' not found. Available: {keys}")

    # ── !oldestrecipe ────────────────────────────────────────

    @commands.command(name="oldestrecipe", aliases=["ancientrecipe", "firstrecipe"])
    async def oldestrecipe(self, ctx: commands.Context) -> None:
        """The oldest known recipes in human history. Usage: !oldestrecipe"""
        if not await self._check_cooldown(ctx, "oldestrecipe", DEFAULT_COOLDOWN):
            return
        await self._respond(ctx, random.choice(OLDEST_RECIPES))

    # ── !streetfood ──────────────────────────────────────────

    @commands.command(name="streetfood", aliases=["streetfoodof", "localfood"])
    async def streetfood(self, ctx: commands.Context, *, country: str = "") -> None:
        """Iconic street food of a country. Usage: !streetfood Turkey"""
        if not country:
            keys = ", ".join(list(STREET_FOODS.keys())[:6])
            await self._respond(ctx, f"Usage: !streetfood [country] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "streetfood", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(country, STREET_FOODS)
        if result:
            await self._respond(ctx, f"{country.title()} street food: {result}")
        else:
            keys = ", ".join(list(STREET_FOODS.keys()))
            await self._respond(ctx, f"No street food data for '{country}'. Available: {keys}")

    # ── !fermented ───────────────────────────────────────────

    @commands.command(name="fermented", aliases=["fermentedfoods", "fermentation"])
    async def fermented(self, ctx: commands.Context, *, query: str = "") -> None:
        """Fermented foods from around the world. Usage: !fermented kimchi"""
        if not query:
            keys = ", ".join(list(FERMENTED_FOODS.keys())[:5])
            await self._respond(ctx, f"Usage: !fermented [food] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "fermented", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, FERMENTED_FOODS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(FERMENTED_FOODS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")

    # ── !umami ───────────────────────────────────────────────

    @commands.command(name="umami", aliases=["umamifoods", "glutamate"])
    async def umami(self, ctx: commands.Context, *, query: str = "") -> None:
        """The science of umami in specific foods. Usage: !umami parmesan"""
        if not query:
            keys = ", ".join(list(UMAMI_FOODS.keys())[:5])
            await self._respond(ctx, f"Usage: !umami [food] — try: {keys}...")
            return
        if not await self._check_cooldown(ctx, "umami", DEFAULT_COOLDOWN):
            return
        result = self._fuzzy(query, UMAMI_FOODS)
        if result:
            await self._respond(ctx, result)
        else:
            keys = ", ".join(list(UMAMI_FOODS.keys()))
            await self._respond(ctx, f"'{query}' not found. Available: {keys}")


def prepare(bot):
    bot.add_cog(CookingCog(bot))
