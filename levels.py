import asyncio
import configuration
import sqlite3
from random import randint
import discord

chatted = []


async def add_exp(member: discord.User, message: discord.Message):
    global chatted

    if member.id not in chatted:
        xp_gain = randint(configuration.XP_GAIN_MIN, configuration.XP_GAIN_MAX)

        chatted.append(member.id)

        sqlite_client = sqlite3.connect('bot_database.db')
        user_xp = sqlite_client.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                        {'user_id': member.id}).fetchone()

        if user_xp == None:
            user_xp = (0, 0)

        xp = user_xp[0] + xp_gain
        level = user_xp[1]

        if xp >= await xp_needed_for_level(level):
            # level up

            level += 1

            # Internally, levels are one more than MEE6 was, so there is a compensation
            if level - 1 != 0:
                await message.channel.send(f"<@!{member.id}> reached level {level-1}! <:poglin:798531675634139176>", allowed_mentions=discord.AllowedMentions(users=True))

            # Give level roles
            await give_level_up_roles(member, level)

        sqlite_client.execute('''INSERT INTO LEVELS (ID, XP, LEVEL) \
        VALUES(:member, :user_xp, :level) \
        ON CONFLICT(ID) \
        DO UPDATE SET XP=:user_xp, LEVEL=:level''',
                              {'member': member.id,
                               'user_xp': xp,
                               'level': level}
                              )
        sqlite_client.commit()
        sqlite_client.close()


# Need a non blocking loop here to reset chatted every INTERVAL seconds
async def clear_chatted_loop():
    global chatted

    while True:
        await asyncio.sleep(configuration.XP_MESSAGE_INTERVAL)
        chatted = []


async def xp_needed_for_level(level: int):
    return int(5/6*((2*(level)**3)+(27*(level)**2)+(91*(level))))


async def give_level_up_roles(member, level):
    # Internally, levels are one more than MEE6 was, so there is a compensation
    ranks = configuration.LEVEL_ROLES.values()

    for index, value in enumerate(ranks):
        if level - 1 >= value[1]:
            try:
                await member.add_roles(member.guild.get_role(value[0]))
                await member.remove_roles(member.guild.get_role(list(ranks)[index + 1][0]))
            except IndexError:
                # Wood role, nothing to remove
                pass
            break
