"""Leveling (XP system) related functionality."""

from __future__ import annotations

import asyncio
import bisect
import random
import typing
from datetime import datetime

import discord
from discord import ui
from discord.ext import commands, tasks

from constants import ALLOWED_GUILD_IDS
from util import Paginator, async_db_execute

if typing.TYPE_CHECKING:
    from bot import MyBot


class LeaderboardPaginator(Paginator):
    """Paginator with button for the leaderboard command."""

    async def get_content(self, ctx) -> Paginator.GetContentReturnType:
        assert isinstance(ctx.guild, discord.Guild)
        db_result = await async_db_execute(
            "SELECT user_id, level, xp FROM levels ORDER BY xp DESC LIMIT 10 OFFSET ?",
            ((self.page - 1) * 10,),
        )
        embed = discord.Embed()
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        description = ""
        for index, data in enumerate(db_result):
            user_id, level, xp = data
            index += (self.page - 1) * 10 + 1
            description += (
                f"**#{index:,}** <@{user_id}>\n╰ Level: {level:,} • XP: {xp:,}\n"
            )
        embed.title = f"Leaderboard for {ctx.guild.name}"
        embed.description = description
        embed.timestamp = datetime.now()

        return {"embed": embed}


class ReactionRoleButton(ui.Button):
    """Button to give/remove eternal roles."""

    async def callback(self, interaction: discord.Interaction):
        """Button callback that gives/removes a eternal role."""
        assert self.custom_id
        assert interaction.guild
        assert isinstance(interaction.user, discord.Member)
        await interaction.response.defer()
        role_id, level_required = self.custom_id.split(".")
        role_id = int(role_id)
        # Remove role
        if role_id in [role.id for role in interaction.user.roles]:
            role = interaction.guild.get_role(role_id)
            assert role
            await interaction.user.remove_roles(role)
            await interaction.followup.send("Successfully removed role", ephemeral=True)
            return

        level: list[tuple[int]] = await async_db_execute(
            "SELECT level FROM levels WHERE user_id=? ",
            (interaction.user.id,),
        )
        if int(level_required) > level[0][0]:
            await interaction.followup.send(
                f"You need level {level_required} to do this! You're level {level}.",
                ephemeral=True,
            )
            return

        # Give role
        role = interaction.guild.get_role(int(role_id))
        if not role:
            await interaction.followup.send("Couldn't find role", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.followup.send("Successfully gave role", ephemeral=True)


class EternalReactionRole(ui.View):
    """View for reaction role of eternal roles."""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            ReactionRoleButton(label="Wood", custom_id="827166441882648616.5")
        )
        self.add_item(
            ReactionRoleButton(label="Stone", custom_id="961269588044152872.10")
        )
        self.add_item(
            ReactionRoleButton(label="Iron", custom_id="930919954675552286.15")
        )
        self.add_item(
            ReactionRoleButton(label="Copper", custom_id="957331424904617984.20")
        )
        self.add_item(
            ReactionRoleButton(label="Lapis", custom_id="750344859608547358.25")
        )
        self.add_item(
            ReactionRoleButton(label="Gold", custom_id="861185869759512586.30")
        )
        self.add_item(
            ReactionRoleButton(label="Diamond", custom_id="835280347470102569.35")
        )
        self.add_item(
            ReactionRoleButton(label="Obsidian", custom_id="821734332598059008.40")
        )
        self.add_item(
            ReactionRoleButton(label="Emerald", custom_id="880202615110111302.45")
        )
        self.add_item(
            ReactionRoleButton(label="Netherite", custom_id="907385183043457024.55")
        )
        self.add_item(
            ReactionRoleButton(
                label="Netherite but red", custom_id="846544385134297098.55"
            )
        )
        self.add_item(
            ReactionRoleButton(
                label="Permanent mute", custom_id="846544385134297098.100"
            )
        )


class Levels(commands.Cog):
    """Cog for leveling (XP system) related functionality."""

    XP_GAIN_MIN = 19
    XP_GAIN_MAX = 21

    # Sort in ascending order (needed for bisect)
    ROLES = {
        5: 337151269523423236,
        10: 804093931397840906,
        15: 337151464592113664,
        20: 630748385925922856,
        25: 804091179146412052,
        30: 337151525325635586,
        35: 337152398415888385,
        40: 630748573990125595,
        45: 420174387166314506,
        55: 731769341246177340,
        64: 847681970539724851,
        65: 731769341246177340,
    }

    XP_DISALLOWED_CHANNELS = (329235461929435137, 334929304561647617)

    def __init__(self, bot) -> None:
        self.bot = bot
        bot.add_view(EternalReactionRole(), message_id=1009757335977201725)
        self.chatted: set[int] = set()
        self.reset_chatted.start()  # pylint: disable=no-member

    @staticmethod
    async def xp_needed_for_level(level: int):
        """Copy of MEE6's levels formula (a cubic)"""
        return int(5 / 6 * (2 * level**3 + 27 * level**2 + 91 * level))

    @tasks.loop(seconds=60)
    async def reset_chatted(self):
        """Clear chatted set every minute for XP giving cooldown."""
        self.chatted.clear()

    @commands.Cog.listener("on_message")
    async def give_xp(self, message: discord.Message):
        """Adds XP if the user hasn't chatted in this interval."""
        if (
            not message.guild
            or message.guild.id not in ALLOWED_GUILD_IDS
            or message.channel.id in self.XP_DISALLOWED_CHANNELS
            or len(message.content) <= 2
            or message.author.bot
        ):
            return
        if message.author.id in self.chatted:
            return
        self.chatted.add(message.author.id)
        result: list[tuple[int, int]] = await async_db_execute(
            "SELECT xp, level FROM levels WHERE user_id=?",
            (message.author.id,),
        )
        # If there's no result, it means the user chatted for the first time
        if not result:
            xp, level = 0, 0
        else:
            xp, level = result[0]

        xp += random.randint(self.XP_GAIN_MIN, self.XP_GAIN_MAX)
        # Level 0 needs 0 xp, so we start at level 1
        if xp >= await self.xp_needed_for_level(level + 1):
            level += 1
            try:
                asyncio.create_task(self.handle_level_up(message, level))
            except discord.errors.HTTPException:
                pass

        await async_db_execute(
            """INSERT INTO levels(user_id) VALUES (?)
            ON CONFLICT(user_id) DO UPDATE SET xp=?, level=?""",
            (
                message.author.id,
                xp,
                level,
            ),
        )

    @commands.command()
    @commands.is_owner()
    async def fake_rejoin(self, ctx):
        """Simulate user rejoin for level roles."""
        await self.regive_level_roles(ctx.author)

    @commands.Cog.listener("on_member_join")
    async def regive_level_roles(self, member: discord.Member):
        """Regive a user's rank roles on rejoin"""
        if member.guild.id not in ALLOWED_GUILD_IDS:
            return

        result = await async_db_execute(
            "SELECT level FROM levels WHERE user_id=?",
            (member.id,),
        )

        if not result:
            return  # User has no level
        _, level = result[0]

        role_index = bisect.bisect_left(list(self.ROLES.keys()), level)
        role_id = list(self.ROLES.values())[role_index - 1] if role_index > 0 else None

        if role_id and (role := member.guild.get_role(role_id)):
            await member.add_roles(role)

    async def handle_level_up(self, message: discord.Message, level: int):
        """Sends level up message and gives rank reward roles if needed."""
        try:
            await message.channel.send(
                f"<@{message.author.id}> reached level {level:,}!"
                "<:poglin:798531675634139176>"
            )
        except discord.DiscordException as err:
            print(err)

        if (new_role_id := self.ROLES.get(level)) is None:
            return

        old_role_index = bisect.bisect_left(list(self.ROLES.keys()), level)
        old_role_id = (
            list(self.ROLES.values())[old_role_index - 1]
            if old_role_index > 0
            else None
        )
        assert isinstance(message.author, discord.Member)
        assert isinstance(message.guild, discord.Guild)

        new_role = message.guild.get_role(new_role_id)
        assert new_role is not None
        await message.author.add_roles(new_role)

        if old_role_id:
            old_role = message.guild.get_role(old_role_id)
            assert old_role is not None
            await message.author.remove_roles(old_role)

    @commands.hybrid_command(
        aliases=(
            "level",
            "score",
            "lifewasted",
            "bank",
            "wank",
            "tank",
            "frank",  # credit: cobysack1
            "hank",  # credit: masochist#1615
            "wotismyrankplsOwO",  # credit: cobysack1
            "rnk",
        )
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def rank(self, ctx: commands.Context[MyBot], user: discord.User | None):
        """Check your rank!"""
        query_user = user if user else ctx.author
        assert isinstance(ctx.guild, discord.Guild)
        result: list[tuple[int, int]] = await async_db_execute(
            "SELECT xp, level FROM levels WHERE user_id=?",
            (query_user.id,),
        )
        if not result:
            return await ctx.reply("User does not have a rank yet.")
        xp, level = result[0]
        rank: int = (
            await async_db_execute(
                "SELECT COUNT(*)+1 FROM LEVELS WHERE XP > ?",
                (xp,),
            )
        )[0][0]

        xp_for_this_lvl = await self.xp_needed_for_level(level)

        level_xp = xp - xp_for_this_lvl
        next_level_xp = await self.xp_needed_for_level(level + 1) - xp_for_this_lvl

        green_square_amt = round((level_xp / next_level_xp) * 20)
        # progress_bar = (
        #     "<:gs:981226946107154482>" * green_square_amt
        #     + "<:rs:981227291399028777>" * (10 - green_square_amt)
        # )
        progress_bar = (
            "[" + "=" * green_square_amt + "-" * (20 - green_square_amt) + "]"
        )

        embed = discord.Embed().set_author(
            name=query_user.name,
            icon_url=query_user.display_avatar.url,
        )
        embed.timestamp = datetime.now()
        embed.colour = query_user.accent_color
        embed.description = (
            f":trophy: Rank #{rank:,} • {xp:,} xp total\n"
            f"Level {level:,} • {level_xp:,}/{next_level_xp:,} xp\n"
            f"{progress_bar}"
        )

        if query_user.id in (770548285656006666, 603889155147038752):
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/480px-Python-logo-notext.svg.png"  # pylint: disable=line-too-long
            )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(aliases=("lb", "levels", "leaderboards"))
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def leaderboard(self, ctx: commands.Context, page: int = 1):
        """See leaderboard"""
        assert isinstance(ctx.guild, discord.Guild)
        ((users_count,),) = await async_db_execute("SELECT COUNT(*) FROM LEVELS")

        if users_count == 0:
            return await ctx.reply("Start chatting! The database is empty :(")

        # Round up, 10 per page
        page_total = users_count // 10 + 1
        view = LeaderboardPaginator(ctx.author.id, page, page_total)
        msg = await ctx.reply(**await view.get_content(ctx), view=view)  # type: ignore
        await view.wait()
        await view.disable_buttons()
        await msg.edit(view=view)

    @commands.hybrid_command()
    @commands.has_permissions(manage_roles=True)
    async def reactionrolessetup(self, ctx: commands.Context):
        """Sends a reaction role message."""
        await ctx.send(view=EternalReactionRole())

    @commands.command()
    @commands.is_owner()
    async def setxp(
        self, ctx: commands.Context, user: discord.User, xp: int, level: int
    ):
        """Sets a user's XP and level."""
        await async_db_execute(
            "UPDATE levels SET xp = ?, level = ? WHERE user_id = ?",
            (xp, level, user.id),
        )
        await ctx.reply(f"Successfully set {user.mention} to {xp} XP and level {level}")
