"""miscellaneous functionality."""
import random

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Miscellaneous(commands.Cog):
    """Cog for miscellaneous functionality."""

    @commands.command()
    @commands.cooldown(rate=1, per=60 * 60 * 60 * 24, type=BucketType.guild)
    async def poop(self, ctx: commands.Context):
        """Poop."""
        if random.randint(1, 10) == 10:
            await ctx.reply("💩")
        else:
            await ctx.reply(
                random.choice(["Nope", "Nah", "No.", "Better luck next time!", ":("])
            )
