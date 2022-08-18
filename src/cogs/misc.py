"""Miscellaneous functionality."""
from __future__ import annotations

import random
import typing

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

if typing.TYPE_CHECKING:
    from bot import MyBot


class Miscellaneous(commands.Cog):
    """Cog for miscellaneous functionality."""

    @commands.hybrid_command()
    @commands.cooldown(rate=1, per=60 * 60 * 60 * 24, type=BucketType.guild)
    async def poop(self, ctx: commands.Context):
        """Poop."""
        if random.randint(1, 10) == 10:
            await ctx.reply("💩")
        else:
            await ctx.reply(
                random.choice(["Nope", "Nah", "No.", "Better luck next time!", ":("])
            )

    @commands.command()
    @commands.is_owner()
    async def synccommandtree(self, ctx: commands.Context[MyBot]):
        """Syncs the command tree (make slash commands show up)."""
        await ctx.bot.tree.sync()
