# PiicaBot — twitch_bot/commands/quotes.py
# Quote commands: !quote, !addquote (streamer only)
# Wisdom commands: !wisdom and all 7 aliases

from twitchio.ext import commands
from loguru import logger

import database.db as db
from config import DEFAULT_COOLDOWN


class QuotesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def _respond(self, ctx: commands.Context, message: str) -> None:
        if len(message) > 490:
            message = message[:487] + "..."
        await ctx.send(message)

    def _is_streamer(self, ctx: commands.Context) -> bool:
        return ctx.author.name.lower() == ctx.channel.name.lower()

    async def _check_cooldown(
        self,
        ctx: commands.Context,
        command: str,
        cooldown: int = DEFAULT_COOLDOWN
    ) -> bool:
        if ctx.author.is_mod or self._is_streamer(ctx):
            await db.update_cooldown(ctx.author.name, command)
            return True
        on_cd, _ = await db.check_cooldown(ctx.author.name, command, cooldown)
        if on_cd:
            return False
        await db.update_cooldown(ctx.author.name, command)
        await db.increment_command_stat(command)
        return True

    # ── !quote ───────────────────────────────────────────────

    @commands.command(
        name="quote",
        aliases=["streamquote", "majopiicaquote"]
    )
    async def quote(self, ctx: commands.Context) -> None:
        """
        Post a random saved stream quote from Majopiica.
        Usage: !quote
        """
        if not await self._check_cooldown(ctx, "quote", DEFAULT_COOLDOWN):
            return

        row = await db.get_random_stream_quote()
        if not row:
            await self._respond(
                ctx,
                "No quotes saved yet! Majopiica can add one with !addquote [text]"
            )
            return

        context_note = f" ({row['context']})" if row['context'] else ""
        game_note    = f" — playing {row['game']}" if row['game'] else ""
        date         = row['created_at'][:10] if row['created_at'] else ""

        await self._respond(
            ctx,
            f"Quote #{row['id']}: \"{row['text']}\"{context_note}{game_note} [{date}]"
        )

    # ── !addquote (streamer only) ────────────────────────────

    @commands.command(
        name="addquote",
        aliases=["savequote", "quotesave"]
    )
    async def addquote(self, ctx: commands.Context, *, text: str = "") -> None:
        """
        Save a stream quote. Streamer only.
        Usage: !addquote [quote text]
        Optional: !addquote [text] | context: [note] | game: [game name]
        """
        if not self._is_streamer(ctx):
            return  # Silent fail — streamer only

        if not text:
            await self._respond(ctx, "Usage: !addquote [text] — saves a stream quote")
            return

        # Parse optional context and game fields
        # Format: !addquote the text | context: this was during a raid | game: Elden Ring
        context = ""
        game    = ""

        if "| context:" in text.lower():
            parts   = text.lower().split("| context:")
            text    = text[:len(parts[0])].strip()
            context = text.split("| context:")[-1].strip()

        if "| game:" in text.lower():
            parts = text.lower().split("| game:")
            text  = text[:len(parts[0])].strip()
            game  = text.split("| game:")[-1].strip()

        quote_id = await db.add_stream_quote(text.strip(), context, game)
        await self._respond(ctx, f"Quote #{quote_id} saved!")
        logger.info(f"Stream quote #{quote_id} added by {ctx.author.name}: {text[:50]}")

    # ── !wisdom and all aliases ──────────────────────────────

    @commands.command(
        name="wisdom",
        aliases=[
            "notion", "aquote", "fragment", "oracle",
            "logos", "aphorism", "eudaimonia"
        ]
    )
    async def wisdom(self, ctx: commands.Context, *, query: str = "") -> None:
        """
        Post a verified philosophy or literature quote.
        Optionally filter by author, topic tag, or era.
        Usage: !wisdom | !wisdom stoic | !wisdom marcus aurelius | !oracle courage
        Aliases: !notion !aquote !fragment !oracle !logos !aphorism !eudaimonia
        """
        if not await self._check_cooldown(ctx, "wisdom", DEFAULT_COOLDOWN):
            return

        # Parse optional filter from query
        author = ""
        tag    = ""
        era    = ""

        if query:
            q = query.strip().lower()
            # Era keywords
            if q in ("ancient", "medieval", "renaissance", "modern"):
                era = q
            # Stoic/school shortcuts
            elif q in ("stoic", "stoicism", "stoics"):
                author = "marcus aurelius"  # most famous stoic
                tag    = "stoic"
            elif q in ("epicurean", "epicurus"):
                author = "epicurus"
            elif q in ("existential", "existentialism"):
                tag = "existence"
            else:
                # Treat as author name search
                author = q

        row = await db.get_random_wisdom_quote(author=author, tag=tag, era=era)

        if not row:
            if query:
                await self._respond(
                    ctx,
                    f"No verified quotes found for '{query}'. "
                    f"Try: !wisdom stoic, !wisdom ancient, !wisdom courage, or just !wisdom"
                )
            else:
                await self._respond(
                    ctx,
                    "No quotes in the wisdom database yet. "
                    "Ask the streamer to load the quote files!"
                )
            return

        source_note = f" | {row['source']}" if row['source'] else ""
        await self._respond(
            ctx,
            f"\"{row['text']}\" — {row['author']}{source_note}"
        )


def prepare(bot):
    bot.add_cog(QuotesCog(bot))
