# PiicaBot — discord_bot/ui.py
# Shared design system. All embeds go through here.
# Imports all emojis from emoji.py — never hardcode emojis here.

import discord
from datetime import datetime
from config import TWITCH_CHANNEL
from discord_bot.emoji import (
    WELCOME, LIVE, OFFLINE, POLL, GIVEAWAY, GIVEAWAY_WINNER,
    POINTS, LEADERBOARD, QUOTE, WISDOM, WISDOM_FOOTER, PIICASAYS,
    LINKTWITCH, FOOTERS,
)

# ─────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────

class Color:
    PRIMARY     = 0xFFB6C1   # baby pink      — main brand
    SOFT        = 0xFFC0CB   # soft pink      — piicasays, gentle
    GOLD        = 0xFFB347   # warm orange    — points, gaming, giveaway
    SUCCESS     = 0xFFD700   # warm yellow    — confirmations, poll results
    ERROR       = 0xC0392B   # red            — errors only
    DARK        = 0x1A1A1A   # near black     — serious mod actions
    NEUTRAL     = 0xD4C5B0   # natural beige  — offline, no results
    STREAM_LIVE = 0xFF4500   # orange-red     — live alert only
    WISDOM      = 0xAEC6CF   # baby blue      — philosophy, calm knowledge
    KNOWLEDGE   = 0xC8A882   # warm sand      — history, science, culture
    LANGUAGE    = 0xB5D5C5   # sage green     — language commands
    COOKING     = 0xFFD59E   # warm peach     — food and cooking

# ─────────────────────────────────────────────────────────────
# FOOTER ROTATION
# ─────────────────────────────────────────────────────────────

_footer_index = 0

def _next_footer() -> str:
    global _footer_index
    footer = FOOTERS[_footer_index % len(FOOTERS)]
    _footer_index += 1
    return footer

# ─────────────────────────────────────────────────────────────
# BASE EMBED
# ─────────────────────────────────────────────────────────────

def base_embed(
    title: str = "",
    description: str = "",
    color: int = Color.PRIMARY,
    url: str = "",
    timestamp: bool = True,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        url=url if url else discord.utils.MISSING,
    )
    if timestamp:
        embed.timestamp = datetime.utcnow()
    embed.set_footer(text=_next_footer())
    return embed

# ─────────────────────────────────────────────────────────────
# STREAM ALERT EMBEDS
# ─────────────────────────────────────────────────────────────

def live_alert_embed(
    title: str,
    game: str,
    viewer_count: int,
    thumbnail_url: str = "",
    stream_url: str = "",
) -> discord.Embed:
    embed = discord.Embed(
        title=f"{LIVE}  {TWITCH_CHANNEL} is live",
        description=f"### {title}",
        color=Color.STREAM_LIVE,
        url=stream_url or f"https://twitch.tv/{TWITCH_CHANNEL}",
    )
    embed.add_field(name="Now Playing", value=game or "Just Chatting", inline=True)
    embed.add_field(name="Viewers", value=f"{viewer_count:,}", inline=True)
    embed.add_field(
        name="Watch",
        value=f"[Open stream ↗]({stream_url or f'https://twitch.tv/{TWITCH_CHANNEL}'})",
        inline=True,
    )
    if thumbnail_url:
        embed.set_image(url=thumbnail_url)
    embed.set_footer(text=f"{LIVE}  PiicaBot · live now")
    embed.timestamp = datetime.utcnow()
    return embed


def offline_embed() -> discord.Embed:
    return base_embed(
        title=f"{OFFLINE}  Stream ended",
        description=f"Thank you for watching **{TWITCH_CHANNEL}**.\nSee you next time.",
        color=Color.NEUTRAL,
    )


def live_status_embed(stream: dict) -> discord.Embed:
    return live_alert_embed(
        title=stream.get("title", "No title"),
        game=stream.get("game_name", "Unknown"),
        viewer_count=stream.get("viewer_count", 0),
        thumbnail_url=stream.get("thumbnail_url", ""),
        stream_url=f"https://twitch.tv/{TWITCH_CHANNEL}",
    )


def offline_status_embed() -> discord.Embed:
    return base_embed(
        title=f"{OFFLINE}  Currently offline",
        description=(
            f"**{TWITCH_CHANNEL}** is not streaming right now.\n"
            f"Follow [on Twitch](https://twitch.tv/{TWITCH_CHANNEL}) "
            f"to be notified when they go live."
        ),
        color=Color.NEUTRAL,
    )

# ─────────────────────────────────────────────────────────────
# WELCOME
# ─────────────────────────────────────────────────────────────

def welcome_embed(member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title=f"{WELCOME}  A new presence arrives",
        description=(
            f"Welcome, {member.mention}.\n\n"
            f"You have found your way to **{TWITCH_CHANNEL}'s** community. "
            f"Make yourself at home — explore the channels, read the rules, "
            f"and join us in stream when the lights come on.\n\n"
            f"*The archive of knowledge awaits you.*"
        ),
        color=Color.PRIMARY,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="Get started",
        value=(
            "📌 Read the rules\n"
            "🎭 Grab your roles\n"
            f"🔴 Watch live at [twitch.tv/{TWITCH_CHANNEL}](https://twitch.tv/{TWITCH_CHANNEL})"
        ),
        inline=False,
    )
    embed.set_footer(text=f"🐿️  Member #{member.guild.member_count} · PiicaBot")
    embed.timestamp = datetime.utcnow()
    return embed

# ─────────────────────────────────────────────────────────────
# POINTS & LEADERBOARD
# ─────────────────────────────────────────────────────────────

def points_embed(username: str, balance: int, total_earned: int, rank: int = 0) -> discord.Embed:
    embed = base_embed(
        title=f"{POINTS}  PiicaPoints",
        color=Color.GOLD,
    )
    embed.add_field(name="Viewer", value=f"`{username}`", inline=True)
    embed.add_field(name="Balance", value=f"**{balance:,}** pts", inline=True)
    embed.add_field(name="Lifetime", value=f"{total_earned:,} pts", inline=True)
    if rank:
        embed.add_field(name="Rank", value=f"#{rank}", inline=True)

    if balance == 0:
        embed.description = "*Watch the stream and chat to earn your first PiicaPoints.*"
    elif balance < 500:
        embed.description = "*Keep watching — you're just getting started.*"
    elif balance < 5000:
        embed.description = "*A modest collection. The leaderboard awaits.*"
    else:
        embed.description = "*A considerable fortune in PiicaPoints.*"
    return embed


def leaderboard_embed(leaders: list) -> discord.Embed:
    embed = base_embed(
        title=f"{LEADERBOARD}  PiicaPoints — Hall of Patrons",
        color=Color.GOLD,
    )
    if not leaders:
        embed.description = "*The leaderboard is empty. Be the first to claim a place.*"
        return embed

    medals  = ["🥇", "🥈", "🥉"] + ["◆"] * 7
    entries = []
    for i, row in enumerate(leaders):
        entries.append(f"{medals[i]}  **{row['twitch_username']}** — {row['points']:,} pts")
    embed.description = "\n".join(entries)
    embed.add_field(
        name="How to earn",
        value="+1 pt / min watching  ·  +2 pts per message  ·  +500 pts on sub",
        inline=False,
    )
    return embed

# ─────────────────────────────────────────────────────────────
# QUOTE EMBEDS
# ─────────────────────────────────────────────────────────────

def stream_quote_embed(row) -> discord.Embed:
    embed = base_embed(
        title=f"{QUOTE}  From the archive",
        description=f'*"{row["text"]}"*',
        color=Color.PRIMARY,
    )
    parts = []
    if row.get("context"):
        parts.append(row["context"])
    if row.get("game"):
        parts.append(f"playing {row['game']}")
    if row.get("created_at"):
        parts.append(row["created_at"][:10])
    note = f"Quote #{row['id']}"
    if parts:
        note += "  ·  " + "  ·  ".join(parts)
    embed.set_footer(text=f"{note}  ·  PiicaBot")
    return embed


def wisdom_quote_embed(row) -> discord.Embed:
    embed = discord.Embed(
        description=f'*"{row["text"]}"*',
        color=Color.WISDOM,
    )
    source = f", {row['source']}" if row.get("source") else ""
    embed.set_author(name=f"— {row['author']}{source}")
    embed.set_footer(text=f"{WISDOM_FOOTER}  PiicaBot · !wisdom for another")
    embed.timestamp = datetime.utcnow()
    return embed

# ─────────────────────────────────────────────────────────────
# POLL & GIVEAWAY
# ─────────────────────────────────────────────────────────────

def poll_embed(question: str, option_a: str, option_b: str, created_by: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"{POLL}  A question is posed",
        description=f"### {question}",
        color=Color.PRIMARY,
    )
    embed.add_field(name="🅰  Option A", value=option_a, inline=True)
    embed.add_field(name="🅱  Option B", value=option_b, inline=True)
    embed.set_footer(text=f"Poll by {created_by}  ·  PiicaBot")
    embed.timestamp = datetime.utcnow()
    return embed


def poll_results_embed(
    question: str,
    votes_a: int,
    votes_b: int,
    option_a: str = "A",
    option_b: str = "B",
) -> discord.Embed:
    total = votes_a + votes_b
    pct_a = round(votes_a / total * 100) if total else 0
    pct_b = round(votes_b / total * 100) if total else 0
    if votes_a > votes_b:
        winner = option_a
    elif votes_b > votes_a:
        winner = option_b
    else:
        winner = "Tie"

    embed = discord.Embed(
        title=f"{POLL}  The verdict",
        description=f"### {question}",
        color=Color.SUCCESS,
    )
    embed.add_field(
        name=f"🅰  {option_a}",
        value=f"{_progress_bar(pct_a)}  {pct_a}%  ({votes_a})",
        inline=False,
    )
    embed.add_field(
        name=f"🅱  {option_b}",
        value=f"{_progress_bar(pct_b)}  {pct_b}%  ({votes_b})",
        inline=False,
    )
    embed.add_field(name="Winner", value=f"**{winner}**", inline=True)
    embed.add_field(name="Total votes", value=str(total), inline=True)
    embed.set_footer(text="PiicaBot · poll closed")
    embed.timestamp = datetime.utcnow()
    return embed


def giveaway_embed(prize: str, duration_minutes: int, host: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"{GIVEAWAY}",
        description=(
            f"### {prize}\n\n"
            f"Click the button below to enter.\n"
            f"A winner will be chosen in **{duration_minutes} minute(s)**."
        ),
        color=Color.GOLD,
    )
    embed.set_footer(text=f"Hosted by {host}  ·  PiicaBot")
    embed.timestamp = datetime.utcnow()
    return embed


def giveaway_winner_embed(prize: str, winner: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title=f"{GIVEAWAY_WINNER}  The chosen one",
        description=(
            f"{winner.mention} has been selected.\n\n"
            f"**Prize:** {prize}\n\n"
            f"*Fortune favors those who show up.*"
        ),
        color=Color.GOLD,
    )
    embed.set_thumbnail(url=winner.display_avatar.url)
    embed.set_footer(text="PiicaBot · giveaway complete")
    embed.timestamp = datetime.utcnow()
    return embed


def giveaway_no_entries_embed(prize: str) -> discord.Embed:
    return base_embed(
        title="No one claimed it",
        description=(
            f"The giveaway for **{prize}** ended with no entries.\n"
            f"*Perhaps next time.*"
        ),
        color=Color.NEUTRAL,
    )

# ─────────────────────────────────────────────────────────────
# ROLE EMBEDS
# ─────────────────────────────────────────────────────────────

def link_success_embed(twitch_username: str, member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title=f"{LINKTWITCH}  Connection established",
        description=(
            f"Your Discord has been linked to Twitch account "
            f"**{twitch_username}**.\n\n"
            f"Your PiicaPoints will now sync across both platforms."
        ),
        color=Color.SUCCESS,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="Next steps",
        value=(
            "Watch the stream to earn points\n"
            "Use `/mypoints` to check your balance\n"
            "Type `!points` in Twitch chat anytime"
        ),
        inline=False,
    )
    embed.set_footer(text="PiicaBot · accounts linked")
    embed.timestamp = datetime.utcnow()
    return embed


def role_granted_embed(role_name: str, member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title="A new distinction",
        description=f"{member.mention} has been granted **{role_name}**.",
        color=Color.SUCCESS,
    )
    embed.set_footer(text="PiicaBot · role management")
    embed.timestamp = datetime.utcnow()
    return embed

# ─────────────────────────────────────────────────────────────
# MILESTONE
# ─────────────────────────────────────────────────────────────

def milestone_embed(milestones: list) -> discord.Embed:
    embed = discord.Embed(
        title="Milestones",
        description="*What we are building toward.*",
        color=Color.PRIMARY,
    )
    for m in milestones:
        embed.add_field(
            name=m['label'],
            value=f"Target: **{m['target']:,}** {m['type']}",
            inline=False,
        )
    embed.set_footer(text=f"twitch.tv/{TWITCH_CHANNEL}  ·  PiicaBot")
    embed.timestamp = datetime.utcnow()
    return embed


def no_milestones_embed() -> discord.Embed:
    return base_embed(
        title="No milestones set yet",
        description=(
            f"No milestone goals have been added.\n"
            f"Follow the journey at "
            f"[twitch.tv/{TWITCH_CHANNEL}](https://twitch.tv/{TWITCH_CHANNEL})."
        ),
        color=Color.NEUTRAL,
    )

# ─────────────────────────────────────────────────────────────
# ERROR & STATUS
# ─────────────────────────────────────────────────────────────

def error_embed(message: str, detail: str = "") -> discord.Embed:
    embed = discord.Embed(
        title="Something went wrong",
        description=message,
        color=Color.ERROR,
    )
    if detail:
        embed.add_field(name="Detail", value=detail, inline=False)
    embed.set_footer(text="PiicaBot · if this persists, contact a mod")
    embed.timestamp = datetime.utcnow()
    return embed


def success_embed(message: str, detail: str = "") -> discord.Embed:
    embed = base_embed(title="Done", description=message, color=Color.SUCCESS)
    if detail:
        embed.add_field(name="Detail", value=detail, inline=False)
    return embed


def info_embed(title: str, message: str) -> discord.Embed:
    return base_embed(title=title, description=message, color=Color.NEUTRAL)

# ─────────────────────────────────────────────────────────────
# HELP
# ─────────────────────────────────────────────────────────────

def help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="PiicaBot — Command Reference",
        description=(
            "*An archive of commands at your disposal.*\n"
            "Slash commands work here in Discord. "
            "`!commands` work in Twitch chat."
        ),
        color=Color.PRIMARY,
    )
    embed.add_field(name=f"{LIVE}  Stream",      value="`/livestatus`  `/clip`  `/milestone`", inline=False)
    embed.add_field(name=f"{POINTS}  PiicaPoints", value="`/mypoints`  `/leaderboard`  `/linktwitch`", inline=False)
    embed.add_field(name=f"{WISDOM}  Quotes",     value="`/quote`  `/wisdom`  `/piicasays`", inline=False)
    embed.add_field(name=f"{POLL}  Community",    value="`/poll`  `/giveaway`", inline=False)
    embed.add_field(
        name="🧑‍💻  Twitch-only commands",
        value=(
            "`!weather` `!time` `!define` `!plate` `!space`\n"
            "`!wisdom` `!kanji` `!dish` `!award` `!vibe` `!pet`\n"
            "...and 100+ more — type `!commands` in chat"
        ),
        inline=False,
    )
    embed.set_footer(text=f"PiicaBot  ·  twitch.tv/{TWITCH_CHANNEL}")
    embed.timestamp = datetime.utcnow()
    return embed

# ─────────────────────────────────────────────────────────────
# PIICASAYS
# ─────────────────────────────────────────────────────────────

def piicasays_embed(text: str, use_count: int) -> discord.Embed:
    embed = discord.Embed(
        description=f'*"{text}"*',
        color=Color.SOFT,
    )
    embed.set_author(name=f"{PIICASAYS}  Majopiica says...")
    embed.set_footer(text=f"Said {use_count:,} times  ·  PiicaBot")
    embed.timestamp = datetime.utcnow()
    return embed

# ─────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────

def _progress_bar(percentage: int, length: int = 12) -> str:
    filled = round(percentage / 100 * length)
    empty  = length - filled
    return "█" * filled + "░" * empty
