import asyncio
from random import randint

import configuration
import discord
import database_handle

chatted = []


async def add_exp(member: discord.User, message: discord.Message) -> None:
    global chatted

    if member.id in chatted:
        return

    if len(message.content) < 3:
        return

    chatted.append(member.id)

    user_xp = database_handle.cursor.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                             {'user_id': member.id}).fetchone()

    if user_xp == None:
        user_xp = (0, 0)

    xp_gain = randint(configuration.XP_GAIN_MIN, configuration.XP_GAIN_MAX)

    xp = user_xp[0] + xp_gain
    level = user_xp[1]

    if xp >= xp_needed_for_level(level + 1):
        # Level 0 needs 0 xp, so we start at level 1
        level += 1

        await message.channel.send(f"<@!{member.id}> reached level {level}! <:poglin:798531675634139176>", allowed_mentions=discord.AllowedMentions(users=True))
        await give_level_up_roles(member, level)

    database_handle.cursor.execute('''INSERT INTO LEVELS (ID, XP, LEVEL) \
    VALUES(:member, :user_xp, :level) \
    ON CONFLICT(ID) \
    DO UPDATE SET XP=:user_xp, LEVEL=:level''',
                                   {'member': member.id,
                                    'user_xp': xp,
                                    'level': level}
                                   )
    database_handle.client.commit()


# Need a non blocking loop here to reset chatted every INTERVAL seconds
async def clear_chatted_loop() -> None:
    global chatted

    while True:
        await asyncio.sleep(configuration.XP_MESSAGE_INTERVAL)
        chatted = []


def xp_needed_for_level(level: int) -> int:
    return int(5/6*((2*(level)**3)+(27*(level)**2)+(91*(level))))


async def give_level_up_roles(member, level) -> None:
    # Internally, levels are one more than MEE6 was, so there is a compensation
    ranks = configuration.LEVEL_ROLES.values()

    for index, value in enumerate(ranks):
        if level >= value[1]:
            try:
                await member.add_roles(member.guild.get_role(value[0]))
                await member.remove_roles(member.guild.get_role(list(ranks)[index + 1][0]))
            except IndexError:
                # Wood role, nothing to remove
                pass
            break
