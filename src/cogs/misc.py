"""Miscellaneous functionality."""
from __future__ import annotations

import os
import random
import subprocess
import sys
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

    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context[MyBot]):
        """Pong! Checks latency between the bot and Discord."""
        ping_message = await ctx.reply("Pong! :ping_pong:")
        start_time = ctx.message.id >> 22
        end_time = ping_message.id >> 22
        await ping_message.edit(
            content=f"Pong! Round trip: {end_time-start_time}ms | "
            f"Websocket: {round(ctx.bot.latency*1000)}ms"
        )

    @commands.command()
    @commands.is_owner()
    async def synccommandtree(self, ctx: commands.Context[MyBot]):
        """Syncs the command tree (make slash commands show up)."""
        await ctx.bot.tree.sync()

    @commands.command()
    @commands.is_owner()
    async def updateandrestart(self, ctx: commands.Context[MyBot]):
        """Pulls the latest commit from GitHub and restart the bot."""
        process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
        process.wait()
        output = process.communicate()[0]
        await ctx.reply(str(output) if output else "No output.")
        os.execv(sys.executable, ["python3"] + sys.argv)
