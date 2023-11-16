"""Miscellaneous functionality."""
from __future__ import annotations

import os
import random
import subprocess
import sys
import typing

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

if typing.TYPE_CHECKING:
    from bot import MyBot


class Miscellaneous(commands.Cog):
    """Cog for miscellaneous functionality."""

    @commands.hybrid_command()
    @commands.cooldown(rate=1, per=7 * 60 * 60 * 24, type=BucketType.guild)
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

    @commands.hybrid_command()
    async def hug(self, ctx: commands.Context[MyBot], *, target: str):
        """Hug someone! (or something)"""
        hugger = ctx.author.mention
        reply = random.choice(
            [
                "{hugger} hugs {target}",
                "{hugger} gives a big hug to {target}",
                "{hugger} 🫂 {target}",
            ]
        ).format(hugger=hugger, target=target)
        # Make a fancy embed so people don't complain about getting pinged twice
        R, G, B = 256 * 256, 256, 1
        embed = discord.Embed(description=reply, colour=(46 * R + 204 * G + 113 * B))

        await ctx.reply(embed=embed)

    @commands.hybrid_command()
    async def replytome(self, ctx: commands.Context[MyBot], *, message: str):
        await ctx.reply(message)

    @commands.hybrid_command(aliases=["a" * x for x in range(3, 10)])
    async def aaaaaaaaaa(
        self,
        ctx: commands.Context[MyBot],
    ):
        await ctx.reply(content="AAAAAAAAAAAAAAAAAAAAAAAA")

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
