# PiicaBot — database/db.py
# Async SQLite helper using aiosqlite.
# Both the Twitch bot and Discord bot import this.
# Call db.init() once on startup — it creates all tables if they don't exist.

import os
import aiosqlite
from loguru import logger
from config import DB_PATH


# Single shared connection — both bots use the same file
_db: aiosqlite.Connection | None = None


async def init() -> None:
    """
    Open the database connection and run schema.sql.
    Creates the database file and all tables if they don't exist.
    Call this once at startup before either bot starts.
    """
    global _db

    # Make sure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = aiosqlite.Row           # rows behave like dicts
    await _db.execute("PRAGMA journal_mode = WAL")
    await _db.execute("PRAGMA foreign_keys = ON")

    # Run schema — CREATE IF NOT EXISTS is safe to call every startup
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    await _db.executescript(schema)
    await _db.commit()

    logger.info(f"Database ready: {DB_PATH}")


async def close() -> None:
    """Close the database connection cleanly on shutdown."""
    global _db
    if _db:
        await _db.close()
        _db = None
        logger.info("Database connection closed")


def get() -> aiosqlite.Connection:
    """Return the active database connection. Raises if not initialised."""
    if _db is None:
        raise RuntimeError("Database not initialised — call db.init() first")
    return _db


# ── User helpers ─────────────────────────────────────────────

async def get_or_create_user(username: str) -> aiosqlite.Row:
    """
    Return a user row, creating it if this is their first appearance.
    Call this any time a viewer interacts with the bot.
    """
    db = get()
    async with db.execute(
        "SELECT * FROM users WHERE twitch_username = ?",
        (username.lower(),)
    ) as cursor:
        row = await cursor.fetchone()

    if row is None:
        await db.execute(
            "INSERT INTO users (twitch_username) VALUES (?)",
            (username.lower(),)
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM users WHERE twitch_username = ?",
            (username.lower(),)
        ) as cursor:
            row = await cursor.fetchone()
        logger.debug(f"New user created: {username}")

    return row


async def update_last_seen(username: str) -> None:
    """Update last_seen timestamp for a user."""
    db = get()
    await db.execute(
        "UPDATE users SET last_seen = datetime('now') WHERE twitch_username = ?",
        (username.lower(),)
    )
    await db.commit()


# ── Points helpers ───────────────────────────────────────────

async def get_points(username: str) -> int:
    """Return a viewer's current PiicaPoints balance."""
    user = await get_or_create_user(username)
    return user["points"]


async def add_points(username: str, amount: int, reason: str) -> int:
    """
    Add points to a viewer's balance and log the transaction.
    Returns their new balance.
    """
    db = get()
    user = await get_or_create_user(username)
    user_id = user["id"]

    await db.execute(
        """UPDATE users
           SET points = points + ?,
               total_points = total_points + ?
           WHERE id = ?""",
        (amount, max(0, amount), user_id)
    )
    await db.execute(
        "INSERT INTO points_transactions (user_id, amount, reason) VALUES (?, ?, ?)",
        (user_id, amount, reason)
    )
    await db.commit()

    async with db.execute(
        "SELECT points FROM users WHERE id = ?", (user_id,)
    ) as cursor:
        row = await cursor.fetchone()

    logger.debug(f"Points: {username} +{amount} ({reason}) → {row['points']}")
    return row["points"]


async def remove_points(username: str, amount: int, reason: str) -> tuple[bool, int]:
    """
    Remove points from a viewer's balance.
    Returns (success, new_balance).
    Fails if they don't have enough points.
    """
    db = get()
    user = await get_or_create_user(username)

    if user["points"] < amount:
        return False, user["points"]

    await db.execute(
        "UPDATE users SET points = points - ? WHERE id = ?",
        (amount, user["id"])
    )
    await db.execute(
        "INSERT INTO points_transactions (user_id, amount, reason) VALUES (?, ?, ?)",
        (user["id"], -amount, reason)
    )
    await db.commit()

    new_balance = user["points"] - amount
    logger.debug(f"Points: {username} -{amount} ({reason}) → {new_balance}")
    return True, new_balance


async def transfer_points(from_user: str, to_user: str, amount: int) -> tuple[bool, str]:
    """
    Transfer points between two viewers (!give command).
    Returns (success, message).
    """
    db = get()
    sender = await get_or_create_user(from_user)

    if sender["points"] < amount:
        return False, f"You only have {sender['points']} PiicaPoints."

    if amount <= 0:
        return False, "Amount must be greater than 0."

    await remove_points(from_user, amount, f"give → {to_user}")
    await add_points(to_user, amount, f"received from {from_user}")
    return True, f"Transferred {amount} PiicaPoints from {from_user} to {to_user}."


async def get_leaderboard(limit: int = 5) -> list[aiosqlite.Row]:
    """Return top N viewers by points."""
    db = get()
    async with db.execute(
        "SELECT twitch_username, points FROM users ORDER BY points DESC LIMIT ?",
        (limit,)
    ) as cursor:
        return await cursor.fetchall()


# ── Cooldown helpers ─────────────────────────────────────────

async def check_cooldown(username: str, command: str, cooldown_secs: int) -> tuple[bool, int]:
    """
    Check if a user is on cooldown for a command.
    Returns (is_on_cooldown, seconds_remaining).
    """
    db = get()
    user = await get_or_create_user(username)

    async with db.execute(
        """SELECT last_used,
                  CAST((julianday('now') - julianday(last_used)) * 86400 AS INTEGER) AS elapsed
           FROM command_cooldowns
           WHERE user_id = ? AND command = ?""",
        (user["id"], command)
    ) as cursor:
        row = await cursor.fetchone()

    if row is None:
        return False, 0

    elapsed = row["elapsed"]
    if elapsed >= cooldown_secs:
        return False, 0

    return True, cooldown_secs - elapsed


async def update_cooldown(username: str, command: str) -> None:
    """Set the last used time for a command to now."""
    db = get()
    user = await get_or_create_user(username)
    await db.execute(
        """INSERT INTO command_cooldowns (user_id, command, last_used)
           VALUES (?, ?, datetime('now'))
           ON CONFLICT(user_id, command) DO UPDATE SET last_used = datetime('now')""",
        (user["id"], command)
    )
    await db.commit()


# ── Custom command helpers ───────────────────────────────────

async def get_custom_command(name: str) -> aiosqlite.Row | None:
    """Look up a custom command by name."""
    db = get()
    async with db.execute(
        "SELECT * FROM custom_commands WHERE name = ? AND enabled = 1",
        (name.lower(),)
    ) as cursor:
        return await cursor.fetchone()


async def add_custom_command(name: str, response: str) -> bool:
    """Add a new custom command. Returns False if name already exists."""
    db = get()
    try:
        await db.execute(
            "INSERT INTO custom_commands (name, response) VALUES (?, ?)",
            (name.lower(), response)
        )
        await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def edit_custom_command(name: str, response: str) -> bool:
    """Edit an existing custom command. Returns False if not found."""
    db = get()
    await db.execute(
        "UPDATE custom_commands SET response = ?, updated_at = datetime('now') WHERE name = ?",
        (response, name.lower())
    )
    await db.commit()
    async with db.execute(
        "SELECT id FROM custom_commands WHERE name = ?", (name.lower(),)
    ) as cursor:
        return await cursor.fetchone() is not None


async def delete_custom_command(name: str) -> bool:
    """Delete a custom command. Returns False if not found."""
    db = get()
    async with db.execute(
        "SELECT id FROM custom_commands WHERE name = ?", (name.lower(),)
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        return False

    await db.execute(
        "DELETE FROM custom_commands WHERE name = ?", (name.lower(),)
    )
    await db.commit()
    return True


async def increment_custom_command_count(name: str) -> None:
    """Increment the use count for a custom command."""
    db = get()
    await db.execute(
        "UPDATE custom_commands SET use_count = use_count + 1 WHERE name = ?",
        (name.lower(),)
    )
    await db.commit()


# ── Quote helpers ────────────────────────────────────────────

async def get_random_stream_quote() -> aiosqlite.Row | None:
    """Return a random stream quote from Majopiica."""
    db = get()
    async with db.execute(
        "SELECT * FROM stream_quotes ORDER BY RANDOM() LIMIT 1"
    ) as cursor:
        return await cursor.fetchone()


async def add_stream_quote(text: str, context: str = "", game: str = "") -> int:
    """Add a stream quote. Returns the new quote ID."""
    db = get()
    await db.execute(
        "INSERT INTO stream_quotes (text, context, game) VALUES (?, ?, ?)",
        (text, context, game)
    )
    await db.commit()
    async with db.execute("SELECT last_insert_rowid() AS id") as cursor:
        row = await cursor.fetchone()
    return row["id"]


async def get_random_wisdom_quote(
    author: str = "",
    tag: str = "",
    era: str = ""
) -> aiosqlite.Row | None:
    """
    Return a random wisdom quote, optionally filtered.
    Used by !wisdom and all its aliases.
    """
    db = get()
    conditions = ["verified = 1"]
    params: list = []

    if author:
        conditions.append("LOWER(author) LIKE ?")
        params.append(f"%{author.lower()}%")
    if era:
        conditions.append("era = ?")
        params.append(era.lower())
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f"%{tag.lower()}%")

    where = " AND ".join(conditions)
    async with db.execute(
        f"SELECT * FROM wisdom_quotes WHERE {where} ORDER BY RANDOM() LIMIT 1",
        params
    ) as cursor:
        return await cursor.fetchone()


# ── Song queue helpers ───────────────────────────────────────

async def add_to_queue(username: str, title: str, url: str, duration: int = 0) -> int:
    """Add a song to the queue. Returns queue position."""
    db = get()
    async with db.execute(
        "SELECT COALESCE(MAX(position), 0) + 1 AS next_pos FROM song_queue WHERE status = 'queued'"
    ) as cursor:
        row = await cursor.fetchone()
    pos = row["next_pos"]

    await db.execute(
        "INSERT INTO song_queue (requested_by, title, url, duration_sec, position) VALUES (?, ?, ?, ?, ?)",
        (username, title, url, duration, pos)
    )
    await db.commit()
    return pos


async def get_current_song() -> aiosqlite.Row | None:
    """Return the currently playing song."""
    db = get()
    async with db.execute(
        "SELECT * FROM song_queue WHERE status = 'playing' LIMIT 1"
    ) as cursor:
        return await cursor.fetchone()


async def get_queue(limit: int = 5) -> list[aiosqlite.Row]:
    """Return next N songs in queue."""
    db = get()
    async with db.execute(
        "SELECT * FROM song_queue WHERE status = 'queued' ORDER BY position LIMIT ?",
        (limit,)
    ) as cursor:
        return await cursor.fetchall()


# ── Stats helpers ────────────────────────────────────────────

async def increment_command_stat(command: str) -> None:
    """Track command usage statistics."""
    db = get()
    await db.execute(
        """INSERT INTO command_stats (command, use_count, last_used)
           VALUES (?, 1, datetime('now'))
           ON CONFLICT(command) DO UPDATE
           SET use_count = use_count + 1,
               last_used = datetime('now')""",
        (command,)
    )
    await db.commit()


async def increment_message_count(username: str) -> None:
    """Increment message count and update last seen for a viewer."""
    db = get()
    await db.execute(
        """UPDATE users
           SET messages_sent = messages_sent + 1,
               last_seen = datetime('now')
           WHERE twitch_username = ?""",
        (username.lower(),)
    )
    await db.commit()


async def add_watch_minutes(username: str, minutes: int) -> None:
    """Add watch time minutes to a viewer (called by the scheduler)."""
    db = get()
    await db.execute(
        "UPDATE users SET watch_minutes = watch_minutes + ? WHERE twitch_username = ?",
        (minutes, username.lower())
    )
    await db.commit()
