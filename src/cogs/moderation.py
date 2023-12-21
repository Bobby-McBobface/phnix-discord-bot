"""Moderation related functionality."""
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from util import Paginator, async_db_execute, parse_timeframe_ms


class WarnPaginator(Paginator):
    """Paginator for warns."""

    def __init__(self, target: discord.User | discord.Member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target

    async def get_content(self, ctx) -> Paginator.GetContentReturnType:
        assert isinstance(ctx.guild, discord.Guild)
        warns = await async_db_execute(
            "SELECT rowid, reason, timestamp FROM warns "
            "WHERE user_id=? AND server_id=? "
            "LIMIT 10 OFFSET ?",
            (self.target.id, ctx.guild.id, (self.page - 1) * 10),
        )
        # return {"content": "Warns: " + str(warns)}

        embed = discord.Embed()
        embed.set_thumbnail(url=self.target.avatar.url if self.target.avatar else None)
        description = ""
        for index, data in enumerate(warns):
            _, reason, timestamp = data
            index += (self.page - 1) * 10 + 1
            description += f"**#{index:,}**: {reason} <t:{timestamp}>\n"
        embed.title = f"Warns for {self.target.name}"
        embed.description = description
        embed.timestamp = datetime.now()

        return {"embed": embed}


class Moderation(commands.Cog):
    """Cog for moderation related functionality."""

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def warn(
        self, ctx: commands.Context, user: discord.User | discord.Member, *, reason: str
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
        self,
        ctx: commands.Context,
        user: discord.Member,
        timeframe: str,
        *,
        reason: str,
    ):
        """Timeout someone with a custom duration and warn them."""
        timeout_duration = parse_timeframe_ms(timeframe)
        if not timeout_duration:
            return ctx.reply(f"The timeframe you provided, {timeframe}, is invalid.")
        await user.timeout(timedelta(milliseconds=timeout_duration))
        await ctx.reply(f"timeouted {user.id} for {timeout_duration}ms")
        await ctx.invoke(self.warn, user, reason=reason)

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx: commands.Context, user: discord.User | discord.Member):
        """See a user's warns."""
        assert isinstance(ctx.guild, discord.Guild)

        ((warns_count,),) = await async_db_execute(
            "SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?",
            (user.id, ctx.guild.id),
        )
        if warns_count == 0:
            await ctx.reply("The user has no warns! :tada:")

        page_total = warns_count // 10 + 1
        view = WarnPaginator(
            user, invoker_id=ctx.author.id, page=1, page_total=page_total
        )
        msg = await ctx.reply(**await view.get_content(ctx), view=view)  # type: ignore
        await view.wait()
        await view.disable_buttons()
        await msg.edit(view=view)

    @commands.hybrid_command()
    @commands.cooldown(1, 2)
    async def mywarns(self, ctx: commands.Context):
        """See a user's warns."""
        await ctx.invoke(self.warns, ctx.author)
