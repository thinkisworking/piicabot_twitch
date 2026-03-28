# PiicaBot — discord_bot/cogs/roles.py
# Role management with polished UX.
# /linktwitch /mypoints /leaderboard /giverole

import discord
from discord.ext import commands
from loguru import logger

import database.db as db
from discord_bot.ui import (
    link_success_embed, role_granted_embed,
    points_embed, leaderboard_embed,
    error_embed, success_embed,
)
from config import DISCORD_GUILD_ID

ROLE_SUBSCRIBER = "Subscriber"
ROLE_FOLLOWER   = "Follower"
ROLE_VIP        = "VIP"
ROLE_COMMUNITY  = "Community"


class RolesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def _get_guild(self) -> discord.Guild | None:
        return self.bot.get_guild(DISCORD_GUILD_ID)

    async def _get_or_create_role(
        self,
        guild: discord.Guild,
        name: str,
        color: discord.Color
    ) -> discord.Role | None:
        role = discord.utils.get(guild.roles, name=name)
        if not role:
            try:
                role = await guild.create_role(
                    name=name,
                    color=color,
                    reason="PiicaBot auto-created role"
                )
                logger.info(f"Created role: {name}")
            except discord.Forbidden:
                logger.error(f"Cannot create role: {name}")
                return None
        return role

    async def grant_subscriber_role(self, discord_id: int) -> bool:
        guild  = self._get_guild()
        member = guild.get_member(discord_id) if guild else None
        if not member:
            return False
        role = await self._get_or_create_role(guild, ROLE_SUBSCRIBER, discord.Color.from_rgb(194, 24, 91))
        if not role:
            return False
        try:
            await member.add_roles(role, reason="Twitch subscriber")
            conn = db.get()
            await conn.execute(
                """INSERT INTO discord_roles (discord_id, role_name)
                   VALUES (?, ?)
                   ON CONFLICT(discord_id, role_name) DO NOTHING""",
                (str(discord_id), ROLE_SUBSCRIBER)
            )
            await conn.commit()
            logger.info(f"Granted {ROLE_SUBSCRIBER} to {member.name}")
            return True
        except discord.Forbidden:
            return False

    async def grant_vip_role(self, discord_id: int) -> bool:
        guild  = self._get_guild()
        member = guild.get_member(discord_id) if guild else None
        if not member:
            return False
        role = await self._get_or_create_role(guild, ROLE_VIP, discord.Color.purple())
        if not role:
            return False
        try:
            await member.add_roles(role, reason="Twitch VIP")
            conn = db.get()
            await conn.execute(
                """INSERT INTO discord_roles (discord_id, role_name)
                   VALUES (?, ?)
                   ON CONFLICT(discord_id, role_name) DO NOTHING""",
                (str(discord_id), ROLE_VIP)
            )
            await conn.commit()
            return True
        except discord.Forbidden:
            return False

    # ── /linktwitch ──────────────────────────────────────────

    @discord.app_commands.command(
        name="linktwitch",
        description="Link your Twitch account to get roles and sync PiicaPoints"
    )
    async def linktwitch(
        self,
        interaction: discord.Interaction,
        twitch_username: str
    ) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)

        twitch_username = twitch_username.strip().lower()

        conn = db.get()
        async with conn.execute(
            "SELECT * FROM users WHERE twitch_username = ?",
            (twitch_username,)
        ) as cur:
            user = await cur.fetchone()

        if not user:
            await conn.execute(
                "INSERT OR IGNORE INTO users (twitch_username, discord_id) VALUES (?, ?)",
                (twitch_username, str(interaction.user.id))
            )
        else:
            await conn.execute(
                "UPDATE users SET discord_id = ? WHERE twitch_username = ?",
                (str(interaction.user.id), twitch_username)
            )
        await conn.commit()

        # Grant community role
        guild = self._get_guild()
        if guild:
            member = guild.get_member(interaction.user.id)
            role   = await self._get_or_create_role(
                guild, ROLE_COMMUNITY,
                discord.Color.from_rgb(194, 24, 91)
            )
            if member and role:
                try:
                    await member.add_roles(role, reason="Linked Twitch account")
                except discord.Forbidden:
                    pass

        embed = link_success_embed(twitch_username, interaction.user)
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Linked {interaction.user.name} → {twitch_username}")

    # ── /mypoints ────────────────────────────────────────────

    @discord.app_commands.command(
        name="mypoints",
        description="Check your PiicaPoints balance"
    )
    async def mypoints(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        conn = db.get()
        async with conn.execute(
            "SELECT * FROM users WHERE discord_id = ?",
            (str(interaction.user.id),)
        ) as cur:
            user = await cur.fetchone()

        if not user:
            embed = error_embed(
                "Account not linked.",
                "Use `/linktwitch [your_twitch_username]` to connect your accounts."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Get rank
        async with conn.execute(
            "SELECT COUNT(*) as rank FROM users WHERE points > ?",
            (user["points"],)
        ) as cur:
            rank_row = await cur.fetchone()
        rank = (rank_row["rank"] + 1) if rank_row else 0

        embed = points_embed(
            username=user["twitch_username"],
            balance=user["points"],
            total_earned=user["total_points"],
            rank=rank,
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    # ── /leaderboard ─────────────────────────────────────────

    @discord.app_commands.command(
        name="leaderboard",
        description="Show the PiicaPoints leaderboard"
    )
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        leaders = await db.get_leaderboard(10)
        embed   = leaderboard_embed(leaders)
        await interaction.followup.send(embed=embed)

    # ── /giverole ────────────────────────────────────────────

    @discord.app_commands.command(
        name="giverole",
        description="Manually assign a role to a member (mod only)"
    )
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def giverole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role_name: str
    ) -> None:
        guild = self._get_guild()
        role  = discord.utils.get(guild.roles, name=role_name) if guild else None

        if not role:
            await interaction.response.send_message(
                embed=error_embed(
                    f"Role `{role_name}` not found.",
                    "Check the spelling or create the role first."
                ),
                ephemeral=True,
            )
            return

        try:
            await member.add_roles(role, reason=f"Manual grant by {interaction.user.name}")
            embed = role_granted_embed(role_name, member)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "Permission denied.",
                    "PiicaBot's role must be higher than the role you're trying to assign."
                ),
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(RolesCog(bot))
