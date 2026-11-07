# PiicaBot — twitch_bot/bot.py
# Main Twitch bot class. Connects to Twitch IRC, loads all command cogs,
# handles events (messages, subs, raids, follows, bits),
# runs the points scheduler, and processes custom commands.

import asyncio
from twitchio.ext import commands, routines
from loguru import logger

import database.db as db
from config import (
    TWITCH_ACCESS_TOKEN, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET,
    TWITCH_CHANNEL, BOT_NICK,
    POINTS_PER_MINUTE, POINTS_PER_MESSAGE,
    POINTS_ON_SUB, POINTS_ON_RAID,
)
from twitch_bot.commands.fun import add_to_vibe_buffer
from services.ai_service import generate_response


class PiicaBot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_ACCESS_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            nick=BOT_NICK,
            prefix="!",
            initial_channels=[TWITCH_CHANNEL],
        )
        self._channel_name = TWITCH_CHANNEL
        self._viewers: set[str] = set()   # Currently active viewers for points

    # ── Startup / Avvio ──────────────────────────────────────────────

    async def event_ready(self) -> None:
        """
        English: Event triggered when the bot is connected and ready.
        Italiano: Evento attivato quando il bot è connesso e pronto.
        """
        logger.info(f"PiicaBot connected as {self.nick}")
        logger.info(f"Watching channel: {self._channel_name}")

        # Load all command cogs
        self._load_cogs()

        # Start the points scheduler
        self._points_ticker.start()

        channel = self.get_channel(self._channel_name)
        if channel:
            await channel.send("PiicaBot is online! Type !commands to see what I can do.")

    def _load_cogs(self) -> None:
        """
        English: Load all command modules and monitors.
        Italiano: Carica tutti i moduli di comando e i monitor.
        """
        from twitch_bot.commands.general    import GeneralCog
        from twitch_bot.commands.points     import PointsCog
        from twitch_bot.commands.quotes     import QuotesCog
        from twitch_bot.commands.fun        import FunCog
        from twitch_bot.commands.moderation import ModerationCog
        from twitch_bot.commands.monitor    import MonitorCog

        self.add_cog(GeneralCog(self))
        self.add_cog(PointsCog(self))
        self.add_cog(QuotesCog(self))
        self.add_cog(FunCog(self))
        self.add_cog(ModerationCog(self))
        self.add_cog(MonitorCog(self))

        logger.info("All Twitch command cogs and monitors loaded")

    # ── Points ticker (every 60 seconds) / Timer punti ────────────

    @routines.routine(seconds=60)
    async def _points_ticker(self) -> None:
        """
        English: Award watch-time points to all active viewers every minute.
        Italiano: Assegna punti di visualizzazione a tutti gli spettatori attivi ogni minuto.
        """
        if not self._viewers:
            return
        for username in list(self._viewers):
            try:
                await db.add_points(username, POINTS_PER_MINUTE, "watch_time")
                await db.add_watch_minutes(username, 1)
            except Exception as e:
                logger.error(f"Points ticker error for {username}: {e}")

    # ── Message handler / Gestore messaggi ─────────────────────────

    async def event_message(self, message) -> None:
        """
        English: Handle every incoming chat message, including AI mentions and automod.
        Italiano: Gestisce ogni messaggio di chat in arrivo, comprese le menzioni AI e l'automod.
        """
        # Ignore messages from the bot itself
        if message.echo:
            return
        if not message.author:
            return

        username = message.author.name
        content  = message.content

        # Check if the bot is directly mentioned — trigger Groq AI response
        # Controlla se il bot viene menzionato direttamente — attiva la risposta AI di Groq
        if f"@{self.nick.lower()}" in content.lower():
            ai_reply = await generate_response(content, username)
            channel = self.get_channel(self._channel_name)
            if channel and ai_reply:
                await channel.send(f"@{username} {ai_reply}")
            return

        # Track viewer for points
        self._viewers.add(username.lower())

        # Update last seen and message count
        await db.get_or_create_user(username)
        await db.increment_message_count(username)

        # Feed vibe buffer
        add_to_vibe_buffer(content)

        # Run auto-mod check (skip commands)
        if not content.startswith("!"):
            from twitch_bot.commands.moderation import ModerationCog
            mod_cog = self.cogs.get("ModerationCog")
            if mod_cog:
                actioned = await mod_cog.check_message(message)
                if actioned:
                    return

            # Award message points
            await db.add_points(username, POINTS_PER_MESSAGE, "message")

        # Handle poll votes (A or B)
        if content.strip().upper() in ("A", "B") and not content.startswith("!"):
            await self._handle_poll_vote(username, content.strip().upper())

        # Check for custom commands
        if content.startswith("!"):
            cmd_name = content.split()[0][1:].lower()
            custom = await db.get_custom_command(cmd_name)
            if custom:
                await self._run_custom_command(message, custom)
                return

        # Process built-in commands
        await self.handle_commands(message)

    async def _run_custom_command(self, message, command) -> None:
        """
        English: Execute a custom command, replacing variables in the response.
        Italiano: Esegue un comando personalizzato, sostituendo le variabili nella risposta.
        """
        response = command["response"]
        response = response.replace("{user}", message.author.name)
        response = response.replace("{channel}", self._channel_name)
        response = response.replace("{count}", str(command["use_count"] + 1))

        await db.increment_custom_command_count(command["name"])

        channel = self.get_channel(self._channel_name)
        if channel and len(response) <= 500:
            await channel.send(response)

    async def _handle_poll_vote(self, username: str, vote: str) -> None:
        """
        English: Record a poll vote from a viewer.
        Italiano: Registra il voto di un sondaggio da parte di uno spettatore.
        """
        conn = db.get()
        async with conn.execute(
            "SELECT id FROM polls WHERE status = 'open' ORDER BY created_at DESC LIMIT 1"
        ) as cur:
            poll = await cur.fetchone()

        if not poll:
            return

        try:
            await conn.execute(
                "INSERT INTO poll_votes (poll_id, username, vote) VALUES (?, ?, ?)",
                (poll["id"], username, vote)
            )
            col = "votes_a" if vote == "A" else "votes_b"
            await conn.execute(
                f"UPDATE polls SET {col} = {col} + 1 WHERE id = ?",
                (poll["id"],)
            )
            await conn.commit()
        except Exception:
            # Duplicate vote — user already voted / Voto duplicato — utente ha già votato
            pass

    # ── Channel events / Eventi del canale ───────────────────────────

    async def event_join(self, channel, user) -> None:
        """
        English: Track viewers as they join.
        Italiano: Traccia gli spettatori mentre si uniscono.
        """
        if user.name.lower() != self.nick.lower():
            self._viewers.add(user.name.lower())
            await db.get_or_create_user(user.name)

    async def event_part(self, user) -> None:
        """
        English: Remove viewers as they leave.
        Italiano: Rimuove gli spettatori quando se ne vanno.
        """
        self._viewers.discard(user.name.lower())

    async def event_subscription(self, subscription) -> None:
        """
        English: Award points on subscription.
        Italiano: Assegna punti in caso di abbonamento.
        """
        username = subscription.user.name
        await db.add_points(username, POINTS_ON_SUB, "subscription")
        logger.info(f"Sub event: {username} — +{POINTS_ON_SUB} PiicaPoints")

    async def event_raid(self, raid) -> None:
        """
        English: Award points to the raider.
        Italiano: Assegna punti al raider.
        """
        raider   = raid.raider.name
        viewers  = raid.viewer_count
        await db.add_points(raider, POINTS_ON_RAID, "raid")
        logger.info(f"Raid: {raider} brought {viewers} viewers — +{POINTS_ON_RAID} PiicaPoints")

    async def event_bits(self, bits) -> None:
        """
        English: Award points for bits (50 points per 100 bits).
        Italiano: Assegna punti per i bit (50 punti ogni 100 bit).
        """
        username   = bits.user.name
        bits_count = bits.bits_used
        points     = (bits_count // 100) * 50
        if points > 0:
            await db.add_points(username, points, f"bits_{bits_count}")
            logger.info(f"Bits: {username} cheered {bits_count} bits — +{points} PiicaPoints")

    # ── Error handler / Gestore degli errori ────────────────────────

    async def event_command_error(self, ctx, error) -> None:
        """
        English: Handle command errors gracefully.
        Italiano: Gestisce gli errori dei comandi in modo sicuro.
        """
        if isinstance(error, commands.CommandNotFound):
            # Unknown command — check if it might be a typo of a custom command
            return
        logger.error(f"Command error in {ctx.command}: {error}")
