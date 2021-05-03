from typing import Union

import discord


async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if user.bot:
        return
    emoji: Union[discord.Emoji, discord.PartialEmoji, str] = reaction.emoji
    reaction.message: discord.Message = reaction.message
    if emoji == "◀️":
        await reaction.message.edit(content="aaaaaaaaaa")
        await reaction.remove(user)
    elif emoji == "▶️":
        await reaction.message.edit(content="AAAAAAAAAAAAAAAAAAAAAAAAA")
        await reaction.remove(user)
