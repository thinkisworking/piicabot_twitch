# PiicaBot — twitch_bot/commands/points.py
# PiicaPoints loyalty system commands.
# !points, !top, !give, !addpoints (mod), !removepoints (mod)
# Points are auto-earned via the scheduler in bot.py — these are manual commands.

import random
from twitchio.ext import commands
from loguru import logger

import database.db as db
from config import DEFAULT_COOLDOWN


class PointsCog(commands.Cog):

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
        on_cd, remaining = await db.check_cooldown(ctx.author.name, command, cooldown)
        if on_cd:
            return False
        await db.update_cooldown(ctx.author.name, command)
        await db.increment_command_stat(command)
        return True

    # ── !points ──────────────────────────────────────────────

    @commands.command(
        name="points",
        aliases=["mypoints", "piicapoints", "balance"]
    )
    async def points(self, ctx: commands.Context, *, target: str = "") -> None:
        """
        Check your PiicaPoints balance (or another viewer's).
        Usage: !points | !points username
        """
        if not await self._check_cooldown(ctx, "points", 10):
            return

        username = target.strip().lstrip("@") if target else ctx.author.name
        balance  = await db.get_points(username)
        user     = await db.get_or_create_user(username)

        if username.lower() == ctx.author.name.lower():
            await self._respond(
                ctx,
                f"{ctx.author.name} has {balance:,} PiicaPoints "
                f"(lifetime earned: {user['total_points']:,})"
            )
        else:
            await self._respond(ctx, f"{username} has {balance:,} PiicaPoints")

    # ── !top ─────────────────────────────────────────────────

    @commands.command(
        name="top",
        aliases=["leaderboard", "toppoints", "richest"]
    )
    async def top(self, ctx: commands.Context) -> None:
        """
        Show the PiicaPoints leaderboard (top 5).
        Usage: !top
        """
        if not await self._check_cooldown(ctx, "top", 30):
            return

        leaders = await db.get_leaderboard(5)
        if not leaders:
            await self._respond(ctx, "No PiicaPoints data yet! Chat more to earn points.")
            return

        parts = []
        medals = ["1st", "2nd", "3rd", "4th", "5th"]
        for i, row in enumerate(leaders):
            parts.append(f"{medals[i]} {row['twitch_username']}: {row['points']:,}")

        await self._respond(ctx, "PiicaPoints leaderboard — " + " | ".join(parts))

    # ── !give ────────────────────────────────────────────────

    @commands.command(
        name="give",
        aliases=["givepoints", "transfer", "gift"]
    )
    async def give(self, ctx: commands.Context, target: str = "", amount: str = "") -> None:
        """
        Gift PiicaPoints to another viewer.
        Usage: !give username 100
        """
        if not target or not amount:
            await self._respond(ctx, "Usage: !give [username] [amount] — e.g. !give PiicaBot 100")
            return

        if not await self._check_cooldown(ctx, "give", 30):
            return

        target = target.lstrip("@").lower()

        # Can't give to yourself
        if target == ctx.author.name.lower():
            await self._respond(ctx, "You can't give points to yourself!")
            return

        # Can't give to the bot
        if target == self.bot.nick.lower():
            await self._respond(ctx, "Thanks for the thought, but I don't need PiicaPoints!")
            return

        try:
            amt = int(amount)
        except ValueError:
            await self._respond(ctx, f"'{amount}' is not a valid number. Usage: !give username 100")
            return

        if amt <= 0:
            await self._respond(ctx, "You must give at least 1 PiicaPoint.")
            return

        if amt > 100_000:
            await self._respond(ctx, "Maximum transfer is 100,000 PiicaPoints at once.")
            return

        success, msg = await db.transfer_points(ctx.author.name, target, amt)
        if success:
            new_balance = await db.get_points(ctx.author.name)
            await self._respond(
                ctx,
                f"{ctx.author.name} gifted {amt:,} PiicaPoints to {target}! "
                f"Remaining balance: {new_balance:,}"
            )
        else:
            await self._respond(ctx, f"{ctx.author.name}: {msg}")

    # ── !addpoints (mod only) ────────────────────────────────

    @commands.command(name="addpoints")
    async def addpoints(self, ctx: commands.Context, target: str = "", amount: str = "") -> None:
        """
        Mod command: manually add points to a viewer.
        Usage: !addpoints username 500
        """
        if not ctx.author.is_mod and ctx.author.name.lower() != ctx.channel.name.lower():
            return  # Silent fail for non-mods

        if not target or not amount:
            await self._respond(ctx, "Usage: !addpoints [username] [amount]")
            return

        target = target.lstrip("@").lower()
        try:
            amt = int(amount)
        except ValueError:
            await self._respond(ctx, f"'{amount}' is not a valid number.")
            return

        if amt <= 0:
            await self._respond(ctx, "Amount must be greater than 0.")
            return

        new_balance = await db.add_points(target, amt, f"mod_add by {ctx.author.name}")
        await self._respond(
            ctx,
            f"Added {amt:,} PiicaPoints to {target}. New balance: {new_balance:,}"
        )
        logger.info(f"Mod {ctx.author.name} added {amt} points to {target}")

    # ── !removepoints (mod only) ─────────────────────────────

    @commands.command(name="removepoints")
    async def removepoints(self, ctx: commands.Context, target: str = "", amount: str = "") -> None:
        """
        Mod command: manually remove points from a viewer.
        Usage: !removepoints username 100
        """
        if not ctx.author.is_mod and ctx.author.name.lower() != ctx.channel.name.lower():
            return

        if not target or not amount:
            await self._respond(ctx, "Usage: !removepoints [username] [amount]")
            return

        target = target.lstrip("@").lower()
        try:
            amt = int(amount)
        except ValueError:
            await self._respond(ctx, f"'{amount}' is not a valid number.")
            return

        if amt <= 0:
            await self._respond(ctx, "Amount must be greater than 0.")
            return

        success, new_balance = await db.remove_points(target, amt, f"mod_remove by {ctx.author.name}")
        if success:
            await self._respond(
                ctx,
                f"Removed {amt:,} PiicaPoints from {target}. New balance: {new_balance:,}"
            )
            logger.info(f"Mod {ctx.author.name} removed {amt} points from {target}")
        else:
            await self._respond(
                ctx,
                f"{target} only has {new_balance:,} PiicaPoints — can't remove {amt:,}."
            )


def prepare(bot):
    bot.add_cog(PointsCog(bot))
