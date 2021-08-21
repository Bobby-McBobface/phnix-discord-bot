from __future__ import annotations

from typing import Union, TYPE_CHECKING
import functools

from discord import Member
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

if TYPE_CHECKING:
    from discord_slash import SlashContext

import configuration

class Misc(commands.Cog):

    async def _test(self, ctx) -> None:
        """A command named 'test'"""
        result = 2 + 2
        await ctx.send(f"Two plus two is {result}")

    @commands.command(name="test")
    # WTF, including only 1 '__doc__' won't work
    @functools.wraps(_test, assigned=("__doc__", "__doc__"))
    async def _message_test(self, ctx: commands.Context) -> None:
        await self._test(ctx)

    @cog_ext.cog_slash(name="test", guild_ids=[configuration.GUILD_ID])
    @functools.wraps(_test, assigned=("__doc__", "__doc__"))
    async def _slash_test(self, ctx: SlashContext) -> None:
        await self._test(ctx)


    async def _pad(self, ctx, *, args) -> None:
        """Spaces out your text"""
        if args == "":
            await ctx.send("No args")
        elif len(args) > 1000:
            await ctx.send("Message must not surpass 1000 characters")
        else:
            await ctx.send(" ".join(args))

    @commands.command(name="pad", rest_is_raw=True)
    @functools.wraps(_pad, assigned=("__doc__", "__doc__"))
    async def _message_pad(self, ctx: commands.Context, *, args: str) -> None:
        await self._pad(ctx, args=args)

    @cog_ext.cog_slash(name="pad", options=[
               create_option(
                 name="text",
                 description="Text to space out",
                 option_type=3,
                 required=True
               )
             ], guild_ids=[configuration.GUILD_ID])
    @functools.wraps(_pad, assigned=("__doc__", "__doc__"))
    async def _slash_pad(self, ctx: SlashContext, *, text: str) -> None:
        await self._pad(ctx, args=text)


    async def _hug(self, ctx: commands.Context, *, target: Union[Member, str]):
        """Hug someone! (or something)"""
        if target == ctx.me:
            await ctx.send('thanks')
        elif target == ctx.author:
            await ctx.send('tangled')
        else:
            await ctx.send('success')

    @commands.command(name="hug", rest_is_raw=True)
    @functools.wraps(_hug, assigned=("__doc__", "__doc__"))
    async def _message_hug(self, ctx: commands.Context, *, target: Union[Member, str]) -> None:
        await self._hug(ctx, target=target)

    @cog_ext.cog_slash(name="hug", options=[
               create_option(
                 name="person",
                 description="Person to hug",
                 option_type=6,
                 required=True
               )
             ], guild_ids=[configuration.GUILD_ID])
    @functools.wraps(_hug, assigned=("__doc__", "__doc__"))
    async def _slash_hug(self, ctx: SlashContext, *, person: Member) -> None:
        await self._hug(ctx, target=person)

    @commands.command(aliases=["a"*a for a in range(3, 12)])
    async def aa(self, ctx: commands.Context):
        """AAAAAAAAAAAAAAA"""
        await ctx.send("AAAAAAAAAAAAAAAAAAAAAA")
