-- PiicaBot — schema.sql
-- Run once to create all tables.
-- db.py calls this automatically on first start.
-- SQLite with WAL mode for concurrent reads from both bots.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;


-- ─────────────────────────────────────────────────────────────
-- USERS
-- One row per viewer. Created on first seen in chat.
-- Shared between Twitch bot and Discord bot via discord_id.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    twitch_username  TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    discord_id       TEXT    UNIQUE,                      -- linked Discord account
    points           INTEGER NOT NULL DEFAULT 0,
    total_points     INTEGER NOT NULL DEFAULT 0,          -- lifetime earned (never decreases)
    watch_minutes    INTEGER NOT NULL DEFAULT 0,
    messages_sent    INTEGER NOT NULL DEFAULT 0,
    times_subbed     INTEGER NOT NULL DEFAULT 0,
    times_gifted     INTEGER NOT NULL DEFAULT 0,          -- gift subs given
    first_seen       TEXT    NOT NULL DEFAULT (datetime('now')),
    last_seen        TEXT    NOT NULL DEFAULT (datetime('now')),
    is_mod           INTEGER NOT NULL DEFAULT 0,          -- 0/1 boolean
    is_banned        INTEGER NOT NULL DEFAULT 0           -- 0/1 boolean
);

CREATE INDEX IF NOT EXISTS idx_users_points ON users(points DESC);
CREATE INDEX IF NOT EXISTS idx_users_discord ON users(discord_id);


-- ─────────────────────────────────────────────────────────────
-- POINTS TRANSACTIONS
-- Full audit log of every points change.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS points_transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    amount      INTEGER NOT NULL,                         -- positive = earned, negative = spent
    reason      TEXT    NOT NULL,                         -- 'watch', 'message', 'sub', 'raid', 'give', 'mod_add', 'gamble'
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_user ON points_transactions(user_id);


-- ─────────────────────────────────────────────────────────────
-- STREAM QUOTES (!quote, !addquote — streamer only)
-- Majopiica's own stream moment quotes.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stream_quotes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT    NOT NULL,
    added_by    TEXT    NOT NULL DEFAULT 'majopiica',     -- always streamer
    context     TEXT,                                     -- optional note about the moment
    game        TEXT,                                     -- what was being played
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- WISDOM QUOTES (!wisdom and all 7 aliases)
-- Verified philosophy/literature quotes with full source.
-- Populated from JSON files, never from chat.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wisdom_quotes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT    NOT NULL,
    author      TEXT    NOT NULL,
    source      TEXT    NOT NULL,                         -- book, dialogue, letter — must be verifiable
    era         TEXT,                                     -- 'ancient', 'medieval', 'renaissance', 'modern'
    tags        TEXT,                                     -- JSON array: ["courage","time","happiness"]
    language    TEXT    NOT NULL DEFAULT 'english',
    verified    INTEGER NOT NULL DEFAULT 1                -- 1 = source confirmed, 0 = needs review
);

CREATE INDEX IF NOT EXISTS idx_wisdom_author ON wisdom_quotes(author);
CREATE INDEX IF NOT EXISTS idx_wisdom_era    ON wisdom_quotes(era);


-- ─────────────────────────────────────────────────────────────
-- CUSTOM COMMANDS (!addcmd, !editcmd, !delcmd — streamer only)
-- Live-editable text commands with variable support.
-- Variables: {user} {count} {channel} {date}
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS custom_commands (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE COLLATE NOCASE,   -- without the !
    response    TEXT    NOT NULL,
    use_count   INTEGER NOT NULL DEFAULT 0,
    cooldown    INTEGER NOT NULL DEFAULT 30,              -- seconds
    enabled     INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- COMMAND COOLDOWNS
-- Tracks last used time per user per command for cooldown enforcement.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS command_cooldowns (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    command     TEXT    NOT NULL,
    last_used   TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, command)
);

CREATE INDEX IF NOT EXISTS idx_cooldowns_user_cmd ON command_cooldowns(user_id, command);


-- ─────────────────────────────────────────────────────────────
-- SONG REQUEST QUEUE (!songrequest, !queue, !skipsong...)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS song_queue (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    requested_by TEXT    NOT NULL,                        -- twitch username
    title        TEXT    NOT NULL,
    url          TEXT    NOT NULL,
    duration_sec INTEGER,
    position     INTEGER NOT NULL DEFAULT 0,
    status       TEXT    NOT NULL DEFAULT 'queued',       -- 'queued', 'playing', 'played', 'skipped', 'removed'
    requested_at TEXT    NOT NULL DEFAULT (datetime('now')),
    played_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_song_status ON song_queue(status, position);


-- ─────────────────────────────────────────────────────────────
-- MODERATION — BANNED WORDS
-- Auto-mod silent background filter.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS banned_words (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    word        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    added_by    TEXT    NOT NULL,
    action      TEXT    NOT NULL DEFAULT 'timeout',       -- 'timeout', 'ban', 'delete'
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- MODERATION — PERMITTED LINKS (!permit)
-- Temporary link permission for a user.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS permitted_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    permitted_by TEXT   NOT NULL,
    expires_at  TEXT    NOT NULL,                         -- 30 seconds from grant
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- MODERATION LOG
-- Every auto-mod and manual mod action.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS moderation_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL,
    action      TEXT    NOT NULL,                         -- 'timeout', 'ban', 'delete', 'permit'
    reason      TEXT    NOT NULL,
    moderator   TEXT,                                     -- NULL = auto-mod
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- STREAM SESSIONS
-- One row per stream. Used for !streak, !milestone, stats.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stream_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    ended_at        TEXT,
    peak_viewers    INTEGER NOT NULL DEFAULT 0,
    total_messages  INTEGER NOT NULL DEFAULT 0,
    new_followers   INTEGER NOT NULL DEFAULT 0,
    new_subs        INTEGER NOT NULL DEFAULT 0,
    clips_created   INTEGER NOT NULL DEFAULT 0
);


-- ─────────────────────────────────────────────────────────────
-- CHANNEL MILESTONES (!milestone)
-- Follower goals, sub goals, custom milestones.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS milestones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    type          TEXT    NOT NULL,                       -- 'followers', 'subs', 'custom'
    target        INTEGER NOT NULL,
    label         TEXT    NOT NULL,                       -- "1000 followers goal!"
    achieved      INTEGER NOT NULL DEFAULT 0,
    achieved_at   TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- PIICASAYS (!piicasays, !catchphrase, !classicpiica)
-- Majopiica's saved catchphrases and recurring stream moments.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS piicasays (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT    NOT NULL,
    context     TEXT,                                     -- optional note
    use_count   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- WISHES (!wish — one per viewer per stream)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wishes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL,
    wish_text   TEXT    NOT NULL,
    response    TEXT    NOT NULL,                         -- bot's poetic reply
    session_id  INTEGER REFERENCES stream_sessions(id),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_wishes_user_session ON wishes(username, session_id);


-- ─────────────────────────────────────────────────────────────
-- PET COUNTER (!pet — community global counter)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pet_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    total_pets      INTEGER NOT NULL DEFAULT 0,           -- global community counter
    last_animal     TEXT,
    last_petted_by  TEXT,
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Seed the single row
INSERT OR IGNORE INTO pet_stats (id, total_pets) VALUES (1, 0);


-- ─────────────────────────────────────────────────────────────
-- VIBE LOG (!vibe — stores recent analyses)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vibe_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    vibe_label  TEXT    NOT NULL,
    percentage  INTEGER NOT NULL,
    msg_count   INTEGER NOT NULL,
    triggered_by TEXT   NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- CHAT MIRROR LOG (Discord ↔ Twitch bridge)
-- Stores mirrored messages for Discord display.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mirror_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT    NOT NULL,                         -- 'twitch' or 'discord'
    username    TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ─────────────────────────────────────────────────────────────
-- DISCORD ROLE ASSIGNMENTS
-- Tracks which Discord roles have been given for Twitch events.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS discord_roles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id      TEXT    NOT NULL,
    twitch_username TEXT,
    role_name       TEXT    NOT NULL,                     -- 'subscriber', 'follower', 'vip'
    granted_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    revoked_at      TEXT,
    UNIQUE(discord_id, role_name)
);


-- ─────────────────────────────────────────────────────────────
-- COMMAND USAGE STATS
-- Tracks how often each command is used. Useful for analytics.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS command_stats (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    command     TEXT    NOT NULL UNIQUE,
    use_count   INTEGER NOT NULL DEFAULT 0,
    last_used   TEXT
);


-- ─────────────────────────────────────────────────────────────
-- POLL STATE (!poll — one active poll at a time)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS polls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question    TEXT    NOT NULL,
    option_a    TEXT    NOT NULL DEFAULT 'A',
    option_b    TEXT    NOT NULL DEFAULT 'B',
    votes_a     INTEGER NOT NULL DEFAULT 0,
    votes_b     INTEGER NOT NULL DEFAULT 0,
    status      TEXT    NOT NULL DEFAULT 'open',          -- 'open', 'closed'
    created_by  TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    closed_at   TEXT
);

CREATE TABLE IF NOT EXISTS poll_votes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id     INTEGER NOT NULL REFERENCES polls(id),
    username    TEXT    NOT NULL,
    vote        TEXT    NOT NULL,                         -- 'A' or 'B'
    voted_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(poll_id, username)
);
