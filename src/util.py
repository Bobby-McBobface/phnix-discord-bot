from random import choice
import asyncio
from typing import Callable

import discord
import configuration


def get_member_by_id_or_name(message, user: str) -> discord.Member or None:
    if user == "":
        return None

    member = None
    try:
        member = message.guild.get_member(int(user.strip('<@!>')))
    except ValueError:
        pass

    if member == None:
        member = message.guild.get_member_named(user)

    return member


async def split_into_member_and_reason(message: discord.Message, parameters: str) -> tuple:
    """
    Splits parameters into member and reason.
    Used for most moderation commands.
    """

    if parameters == "":
        return (None, None)

    split_params = parameters.split(maxsplit=1)
    member = get_member_by_id_or_name(message, split_params[0])
    try:
        reason = split_params[1].lstrip('| ')
    except IndexError:
        reason = None

    if member == None:
        # Reversed to split the last | in case someone has | in their name
        split_params_pipe = parameters[::-1].split("|", 1)

        member = get_member_by_id_or_name(message,
                                          split_params_pipe[len(split_params_pipe) - 1][::-1].rstrip())

        if len(split_params_pipe) == 2:
            # Unreverse
            reason = split_params_pipe[0][::-1].lstrip()
        else:
            reason = None

    return (member, reason)


def try_get_valid_user_id(id: str) -> int:
    try:
        user_id = id.strip("<@!>")
        user_id = int(user_id)
    except ValueError:
        return 0
    if len(str(user_id)) not in range(17, 20):
        return 0

    return user_id


def choose_random(choices: list):
    """Returns a random item from `choices`"""
    return choice(choices)


def check_if_string_invisible(string: str) -> bool:
    """Returns True if the string is comprised entirely of non-visible characters."""
    for char in string:
        if char not in configuration.INVISIBLE_CHARACTERS:
            # String must be visible if this is the case
            return False
    # If the for loop ended, then every character must be invisible.
    return True


def check_mod_or_test_server(message: discord.Message) -> bool:
    if message.guild.get_role(configuration.MODERATOR_ROLE) in message.author.roles \
            or message.guild.id != configuration.GUILD_ID:
        return True
    return False


class ReactionPageHandle():
    def __init__(self, client: discord.Client, message: discord.Message, op: discord.Member,
                       data_source: Callable[[int, int], discord.Embed], page: int, total_pages: int):

        self.client = client
        self.message = message
        self.op = op
        self.data_source = data_source
        self.page = page
        self.total_pages = total_pages
    
    async def start(self):
        await self.message.add_reaction("◀️")
        await self.message.add_reaction("▶️")

        await self.page_change()


    def check(self, reaction: discord.Reaction, user: discord.Member):
        if self.op.id != user.id or reaction.message.id != self.message.id:
            return False

        emoji = reaction.emoji

        if emoji != "◀️" and emoji != "▶️":
            return False

        asyncio.get_running_loop().create_task(reaction.remove(user))

        if emoji == "◀️" and self.page > 0:
            self.page += -1
        elif emoji == "▶️" and self.page < self.total_pages:
            self.page += 1
        else:
            return False
        return True

    async def page_change(self):
        new_page_embed = self.data_source(self.page, self.total_pages)
        await self.message.edit(embed=new_page_embed)
        try:
            await self.client.wait_for('reaction_add', timeout=30.0, check=self.check)
            await self.page_change()
        except asyncio.TimeoutError:
            await self.message.clear_reactions()
