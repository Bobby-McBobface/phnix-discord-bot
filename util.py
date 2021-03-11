import random

import discord


async def get_member_by_id_or_name(message, user: str) -> discord.Member:
    if user == None:
        return None

    member = None
    try:
        member = message.guild.get_member(int(user.strip('<@!>')))
    except ValueError:
        pass

    if member == None:
        member = message.guild.get_member_named(user)

    return member


async def split_into_member_and_reason(message, parameters: str) -> tuple:
    """
    Splits parameters into member and reason.
    Used for most moderation commands.
    """

    if parameters == None:
        return (None, None)

    split_params = parameters.split(maxsplit=1)
    member = await get_member_by_id_or_name(message, split_params[0])
    try:
        reason = split_params[1].lstrip('| ')
    except IndexError:
        reason = None

    if member == None:
        # Reversed to split the last | in case someone has | in their name
        split_params_pipe = parameters[::-1].split("|", 1)

        member = await get_member_by_id_or_name(message,
                                                split_params_pipe[len(split_params_pipe) - 1][::-1].rstrip())

        if len(split_params_pipe) == 2:
            reason = split_params_pipe[0][::-1].lstrip()
        else:
            reason = None

    return (member, reason)


async def check_for_and_strip_prefixes(string: str, prefixes: tuple) -> str:
    """
    If `string` starts with one of the given prefixes,
    return the string and the prefix. Otherwise, returns None.
    """

    for prefix in prefixes:
        if string.startswith(prefix):
            return string[len(prefix):].lstrip()
    # If the loop ended, it failed to find a prefix
    return None


def choose_random(choices: list):
    """Returns a random item from `choices`"""
    return random.choice(choices)


def muted(member: discord.Member):
    import sqlite3
    sqlite_client = sqlite3.connect('bot_database.db')
    result = sqlite_client.execute('''SELECT :member_id FROM MUTES WHERE ID=:member_id''',
                                   {'member_id': member.id}).fetchone() is not None
    return result
