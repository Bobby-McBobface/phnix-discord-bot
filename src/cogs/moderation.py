"""Moderation related functionality."""
from datetime import timedelta

import discord
from discord.ext import commands

from util import Paginator, async_db_execute


class WarnPaginator(Paginator):
    """Paginator for warns."""

    def __init__(self, target: discord.User | discord.Member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target

    async def get_content(self, ctx):
        assert isinstance(ctx.guild, discord.Guild)
        warns = await async_db_execute(
            "SELECT rowid, reason, date FROM warns WHERE user_id=? AND server_id=?",
            (self.target.id, ctx.guild.id),
        )
        return {"content": "Warns: " + str(warns)}


class Moderation(commands.Cog):
    """Cog for moderation related functionality."""

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def warn(
        self, ctx: commands.Context, user: discord.User | discord.Member, reason: str
    ):
        """Warn someone for breaking the rules."""
        assert isinstance(ctx.guild, discord.Guild)
        await async_db_execute(
            "INSERT INTO warns(reason, user_id, server_id) values(?, ?, ?)",
            (reason, user.id, ctx.guild.id),
        )
        response = await ctx.reply(
            f"Warned <@{user.id}> for {reason}.",
            allowed_mentions=discord.AllowedMentions(users=False),
        )

        if not (dm_channel := user.dm_channel):
            dm_channel = await user.create_dm()
        try:
            await dm_channel.send(
                f"You've been warned in `{ctx.guild.name}` for `{reason}`!"
            )
        except discord.HTTPException:
            await response.edit(content=response.content + "\nUnable to DM user.")

    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(
        self, ctx: commands.Context, user: discord.Member, reason: str, seconds: int
    ):
        """Timeout someone with a custom duration and warn them."""
        await user.timeout(timedelta(seconds=seconds))
        await ctx.reply(f"timeouted {user.id} for {seconds}s")
        await ctx.invoke(self.warn, user, reason)

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx: commands.Context, user: discord.User | discord.Member):
        """See a user's warns."""
        assert isinstance(ctx.guild, discord.Guild)
        view = WarnPaginator(user, invoker_id=ctx.author.id, page=1, page_total=1)
        await ctx.reply(**await view.get_content(ctx), view=view)

    @commands.hybrid_command()
    @commands.cooldown(1, 2)
    async def mywarns(self, ctx: commands.Context):
        """See a user's warns."""
        await ctx.invoke(self.warns, ctx.author)
