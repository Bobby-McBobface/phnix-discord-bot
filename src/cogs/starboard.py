"""Starboard related functionality."""

import bisect

import discord
from discord.ext import commands

from constants import ALLOWED_GUILD_IDS
from util import async_db_execute


class Starboard(commands.Cog):
    """Cog for starboard related functionality."""

    STARBOARD_THRESHOLD = 7
    STAR_EMOTE_MAP = {0: "⭐", 10: "🌟", 20: "💫", 30: "✨"}

    STARBOARD_CHANNEL_ID = 782430559862915114

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def emote_from_count(self, count: int):
        """Get which star emote to use based on how many stars are on the message."""
        index = bisect.bisect_left(list(self.STAR_EMOTE_MAP.keys()), count) - 1
        return list(Starboard.STAR_EMOTE_MAP.values())[index]

    @commands.Cog.listener("on_raw_reaction_add")
    async def check_for_stars(self, payload: discord.RawReactionActionEvent):
        """Check if a reaction is a star and maybe update starboard"""
        if payload.guild_id not in ALLOWED_GUILD_IDS:
            return
        if str(payload.emoji) != "⭐":
            return
        channel = self.bot.get_channel(payload.channel_id)
        assert isinstance(channel, (discord.Thread, discord.TextChannel))
        message = await channel.fetch_message(payload.message_id)
        # print(message.attachments, message.embeds[0].url)
        if message.author.bot:
            return
        # possible TOCTOU error?
        try:
            count = next(x for x in message.reactions if str(x.emoji) == "⭐").count
        except StopIteration:
            count = 0
        starboard_info = await async_db_execute(
            "SELECT message_id, channel_id FROM starboard WHERE original_id=?",
            (payload.message_id,),
        )
        if starboard_info:
            starboard_info: list[tuple[int, int]]
            (message_id, channel_id) = starboard_info[0]

            starboard_channel = self.bot.get_channel(channel_id)
            if starboard_channel is None:
                return
            assert isinstance(starboard_channel, discord.TextChannel)
            starboard_message = starboard_channel.get_partial_message(message_id)

            if count < self.STARBOARD_THRESHOLD:
                await self._delete_starboard_entry(starboard_message)
            else:
                await self._update_starboard_entry(payload, starboard_message, count)
        elif count >= self.STARBOARD_THRESHOLD:
            await self._new_starboard_entry(payload, message, count)

    async def _delete_starboard_entry(
        self,
        starboard_message: discord.PartialMessage,
    ):
        await async_db_execute(
            "DELETE FROM starboard WHERE message_id=? AND channel_id=?",
            (
                starboard_message.id,
                starboard_message.channel.id,
            ),
        )
        try:
            await starboard_message.delete()
        except discord.HTTPException:
            return

    async def _update_starboard_entry(
        self,
        payload: discord.RawReactionActionEvent,
        starboard_message: discord.PartialMessage,
        star_count: int,
    ):
        try:
            await starboard_message.edit(
                content=f"{await self.emote_from_count(star_count)}"
                f"{star_count} <#{payload.channel_id}>"
            )
        except discord.HTTPException:
            return

    async def _new_starboard_entry(
        self,
        payload: discord.RawReactionActionEvent,
        original_message: discord.Message,
        star_count: int,
    ):
        starboard_channel = self.bot.get_partial_messageable(self.STARBOARD_CHANNEL_ID)
        embed = discord.Embed()
        embed.set_author(
            name=original_message.author.display_name,
            icon_url=original_message.author.display_avatar.url,
        ).set_footer(text=original_message.author.id).add_field(
            name="Source",
            value="[Jump](https://discord.com/channels/"
            f"{payload.guild_id}/{payload.channel_id}/{payload.message_id})",
            inline=False,
        )
        try:
            embed_url = original_message.embeds[0].url
        except (AttributeError, IndexError):
            pass
        else:
            embed.set_image(url=embed_url)

        attachment_strings: list[str] = []
        for attachment in original_message.attachments:
            if attachment.content_type:
                if attachment.content_type.startswith("image"):
                    if not embed.image:
                        embed.set_image(url=attachment.url)
                        continue
            attachment_strings.append(f"[{attachment.filename}]({attachment.url})")

        if attachment_strings:
            embed.add_field(
                name="Attachments", value="\n".join(attachment_strings), inline=False
            )

        embed.timestamp = original_message.created_at
        embed.description = original_message.content
        embed.color = 16633188  # (255, 203, 48)
        new_starboard_message = await starboard_channel.send(
            (
                f"{await self.emote_from_count(star_count)}"
                f"{star_count} <#{payload.channel_id}>"
            ),
            embed=embed,
        )
        await async_db_execute(
            "INSERT INTO starboard(original_id, message_id, channel_id) "
            "values (?, ?, ?)",
            (
                payload.message_id,
                new_starboard_message.id,
                new_starboard_message.channel.id,
            ),
        )
