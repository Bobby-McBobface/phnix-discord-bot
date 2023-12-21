"""Join and leave messages"""
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from constants import ALLOWED_GUILD_IDS

if TYPE_CHECKING:
    from bot import MyBot


class WelcomeAndFarewell(commands.Cog):
    """Cog for join and leave messages."""

    WELCOME_FAREWELL_CHANNEL_ID = 464772278526148629

    def __init__(self, bot: MyBot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        """Sends a welcome message on member join."""
        if member.guild.id not in ALLOWED_GUILD_IDS:
            return
        welcome_channel = self.bot.fetch_channel(self.WELCOME_FAREWELL_CHANNEL_ID)
        await welcome_channel.send(f"<@{member.id}> has joined the game!")

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member) -> None:
        """Sends a farewell message on member join"""
        if member.guild.id not in ALLOWED_GUILD_IDS:
            return
        farewell_message = f"{member} has left the game."
        farewell_message = discord.utils.escape_markdown(farewell_message)
        farewell_channel = self.bot.fetch_channel(self.WELCOME_FAREWELL_CHANNEL_ID)
        await farewell_channel.send(farewell_message)
