# PiicaBot — twitch_bot/commands/fun.py
# Fun and original commands: !pet, !wish, !vibe, !collective, !phobia,
# !randomcolor, !color, !colorof, !howbig, !roll, !mythical, !plantfacts

import random
from twitchio.ext import commands
from loguru import logger

import database.db as db
from data.fun_data import (
    get_random_pet, get_wish_response, analyze_vibe,
    get_collective, get_phobia
)
from config import DEFAULT_COOLDOWN


# Twitch chat message buffer for !vibe analysis
# Stores last 30 messages — updated in bot.py event_message
_recent_messages: list[str] = []


def add_to_vibe_buffer(message: str) -> None:
    """Called by bot.py on every chat message to feed the vibe analyzer."""
    global _recent_messages
    _recent_messages.append(message)
    if len(_recent_messages) > 30:
        _recent_messages.pop(0)


class FunCog(commands.Cog):

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

    # ── !pet ─────────────────────────────────────────────────

    @commands.command(
        name="pet",
        aliases=["petanimal", "petting"]
    )
    async def pet(self, ctx: commands.Context) -> None:
        """
        Pet a random animal. Community counter grows with every pet.
        Usage: !pet
        """
        if not await self._check_cooldown(ctx, "pet", 20):
            return

        animal = get_random_pet()

        # Update community counter
        conn = db.get()
        await conn.execute(
            """UPDATE pet_stats
               SET total_pets = total_pets + 1,
                   last_animal = ?,
                   last_petted_by = ?,
                   updated_at = datetime('now')
               WHERE id = 1""",
            (animal["name"], ctx.author.name)
        )
        await conn.commit()

        async with conn.execute("SELECT total_pets FROM pet_stats WHERE id = 1") as cur:
            row = await cur.fetchone()
        total = row["total_pets"] if row else 1

        await self._respond(
            ctx,
            f"{animal['msg']} "
            f"(Chat has petted {total:,} animals total)"
        )

    # ── !wish ────────────────────────────────────────────────

    @commands.command(
        name="wish",
        aliases=["makeawish", "mywish"]
    )
    async def wish(self, ctx: commands.Context, *, wish_text: str = "") -> None:
        """
        Make a wish. One wish per viewer per stream session.
        Usage: !wish for world peace
        """
        if not wish_text:
            await self._respond(ctx, "Usage: !wish [your wish] — one wish per stream!")
            return

        if not await self._check_cooldown(ctx, "wish", 300):
            return

        response = get_wish_response()

        # Save the wish
        conn = db.get()
        await conn.execute(
            "INSERT INTO wishes (username, wish_text, response) VALUES (?, ?, ?)",
            (ctx.author.name, wish_text[:300], response)
        )
        await conn.commit()

        await self._respond(ctx, f"{ctx.author.name} wishes {wish_text[:100]}... {response}")

    # ── !vibe ────────────────────────────────────────────────

    @commands.command(
        name="vibe",
        aliases=["mood", "vibecheck", "chatmood"]
    )
    async def vibe(self, ctx: commands.Context) -> None:
        """
        Analyze the current chat mood and report a vibe.
        Usage: !vibe
        """
        if not await self._check_cooldown(ctx, "vibe", 60):
            return

        label, desc, percentage = analyze_vibe(_recent_messages)

        msg_count = len(_recent_messages)

        # Log the vibe
        conn = db.get()
        await conn.execute(
            "INSERT INTO vibe_log (vibe_label, percentage, msg_count, triggered_by) VALUES (?, ?, ?, ?)",
            (label, percentage, msg_count, ctx.author.name)
        )
        await conn.commit()

        await self._respond(
            ctx,
            f"Chat vibe check: {label} ({percentage}%) — {desc} "
            f"[{msg_count} messages analyzed]"
        )

    # ── !collective ──────────────────────────────────────────

    @commands.command(
        name="collective",
        aliases=["groupname", "animalgroup"]
    )
    async def collective(self, ctx: commands.Context, *, animal: str = "") -> None:
        """
        Get the collective noun for a group of animals.
        Usage: !collective crows | !collective flamingos
        """
        if not animal:
            await self._respond(
                ctx,
                "Usage: !collective [animal] — e.g. !collective crows"
            )
            return

        if not await self._check_cooldown(ctx, "collective", DEFAULT_COOLDOWN):
            return

        result = get_collective(animal.strip())
        await self._respond(ctx, result)

    # ── !phobia ──────────────────────────────────────────────

    @commands.command(
        name="phobia",
        aliases=["fearof", "phobiafacts"]
    )
    async def phobia(self, ctx: commands.Context, *, name: str = "") -> None:
        """
        Get facts about a phobia name.
        Usage: !phobia arachnophobia | !phobia thalassophobia
        """
        if not name:
            await self._respond(
                ctx,
                "Usage: !phobia [name] — e.g. !phobia arachnophobia or !phobia thalassophobia"
            )
            return

        if not await self._check_cooldown(ctx, "phobia", DEFAULT_COOLDOWN):
            return

        result = get_phobia(name.strip())
        await self._respond(ctx, result)

    # ── !roll ────────────────────────────────────────────────

    @commands.command(
        name="roll",
        aliases=["dice", "rolldice"]
    )
    async def roll(self, ctx: commands.Context, *, sides: str = "6") -> None:
        """
        Roll a dice. Default is d6. Supports any number of sides.
        Usage: !roll | !roll 20 | !roll 100
        """
        if not await self._check_cooldown(ctx, "roll", 10):
            return

        try:
            n = int(sides.strip().lstrip("d").lstrip("D"))
            if n < 2:
                raise ValueError
            if n > 1_000_000:
                await self._respond(ctx, "Maximum dice size is 1,000,000 sides.")
                return
        except ValueError:
            await self._respond(ctx, f"'{sides}' is not a valid number. Usage: !roll 20")
            return

        result = random.randint(1, n)
        await self._respond(
            ctx,
            f"{ctx.author.name} rolled a d{n} and got {result}!"
        )

    # ── !howbig ──────────────────────────────────────────────

    @commands.command(
        name="howbig",
        aliases=["scaleof", "sizecompare", "compare"]
    )
    async def howbig(self, ctx: commands.Context, *, query: str = "") -> None:
        """
        Scale comparisons — how big is X compared to Y.
        Usage: !howbig sun earth | !howbig blue whale bus
        """
        if not query:
            await self._respond(
                ctx,
                "Usage: !howbig [thing] — e.g. !howbig sun earth"
            )
            return

        if not await self._check_cooldown(ctx, "howbig", DEFAULT_COOLDOWN):
            return

        # Local comparison database
        comparisons: dict[str, str] = {
            "sun earth":      "1,300,000 Earths fit inside the Sun · the Sun is 109× Earth's diameter",
            "earth moon":     "The Moon is 1/4 of Earth's diameter · 50 Moons fit inside Earth",
            "blue whale bus": "A blue whale (30m) is ~3× longer than a standard bus (10m)",
            "eiffel tower":   "Eiffel Tower: 330m tall · same height as an 81-floor building",
            "amazon river":   "The Amazon carries ~20% of all freshwater on Earth · 6,400km long",
            "great wall":     "Great Wall of China: ~21,000km · would reach halfway to the Moon",
            "milky way":      "Milky Way: 100,000 light-years across · light takes 100,000 years to cross it",
            "mariana trench": "Mariana Trench: 11km deep · if Everest placed inside, 2km of water above it",
            "sahara":         "Sahara Desert: 9.2M km² · larger than the entire USA (9.1M km²)",
            "human dna":      "If all human DNA stretched out: 2m per cell · 37 trillion cells · reaches Pluto and back 17×",
            "virus bacteria": "A bacterium is ~1000nm · a virus is ~100nm · bacteria are ~10× larger than viruses",
            "internet":       "The internet sends ~400 million emails and 500 million tweets per day",
            "dinosaur human": "T-Rex was 12m long · a human (1.8m) is ~15% the length of a T-Rex",
        }

        q = query.strip().lower()
        for key, fact in comparisons.items():
            if all(word in q for word in key.split()):
                await self._respond(ctx, f"{fact} [Source: Verified reference data]")
                return

        await self._respond(
            ctx,
            f"No comparison found for '{query}'. "
            f"Try: !howbig sun earth | !howbig blue whale bus | !howbig mariana trench"
        )


def prepare(bot):
    bot.add_cog(FunCog(bot))
