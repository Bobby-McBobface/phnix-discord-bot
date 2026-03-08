"""Miscellaneous functionality."""

from __future__ import annotations

import random
import typing

import discord
from discord import app_commands
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
        embed = discord.Embed(description=reply, colour=discord.Colour(3066993))

        await ctx.reply(embed=embed)

    @app_commands.command()
    async def replytome(self, ctx: discord.Interaction, *, message: str):
        """Echos the user provided message."""
        await ctx.response.send_message(message)

    @commands.hybrid_command(aliases=["a" * x for x in range(3, 10)])
    async def aaaaaaaaaa(
        self,
        ctx: commands.Context[MyBot],
    ):
        """AAAAAAAAAAAAAAAAAAAAAAAA"""
        await ctx.reply(content="AAAAAAAAAAAAAAAAAAAAAAAA")

    @commands.command()
    @commands.is_owner()
    async def synccommandtree(self, ctx: commands.Context[MyBot]):
        """Syncs the command tree (make slash commands show up)."""
        await ctx.bot.tree.sync()

    @commands.command()
    @commands.is_owner()
    async def mimic(
        self,
        ctx: commands.Context[MyBot],
        user: discord.User | discord.Member,
        *,
        message: str,
    ):
        "Mimics a user invoking a command."
        ctx.message.author = user
        ctx.message.content = message
        await ctx.bot.on_message(ctx.message)
