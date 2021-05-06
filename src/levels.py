import asyncio
import sqlite3
from random import randint

import discord

from config import config
from config import config

chatted = []


async def add_exp(member: discord.User, message: discord.Message):
    global chatted

    if member.id not in chatted:
        xp_gain = randint(config['levelSystem']['xpGainMin'], config['levelSystem']['xpGainMax'])

        chatted.append(member.id)

        sqlite_client = sqlite3.connect('data/bot_database.db')
        user_xp = sqlite_client.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                        {'user_id': member.id}).fetchone()

        if user_xp is None:
            user_xp = (0, 0)

        xp = user_xp[0] + xp_gain
        level = user_xp[1]

        if xp >= await xp_needed_for_level(level):
            # level up

            level += 1

            # Internally, levels are one more than MEE6 was, so there is a compensation
            if level - 1 != 0:
                await message.channel.send(f"<@!{member.id}> reached level {level - 1}! <:poglin:798531675634139176>",
                                           allowed_mentions=discord.AllowedMentions(users=True))

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
        await asyncio.sleep(config['levelSystem']['xpMessageInterval'])
        chatted = []


async def xp_needed_for_level(level: int):
    return int(5 / 6 * ((2 * level ** 3) + (27 * level ** 2) + (91 * level)))


async def give_level_up_roles(member, level):
    # Internally, levels are one more than MEE6 was, so there is a compensation
    ranks = config['levelSystem']['levelRoles']

    try:
        if level - 1 >= 55:
            await member.add_roles(member.guild.get_role(ranks["netherite"][0]))
            await member.remove_roles(member.guild.get_role(ranks["emerald"][0]))
        elif level - 1 >= 45:
            await member.add_roles(member.guild.get_role(ranks["emerald"][0]))
            await member.remove_roles(member.guild.get_role(ranks["obsidian"][0]))
        elif level - 1 >= 40:
            await member.add_roles(member.guild.get_role(ranks["obsidian"][0]))
            await member.remove_roles(member.guild.get_role(ranks["diamond"][0]))
        elif level - 1 >= 35:
            await member.add_roles(member.guild.get_role(ranks["diamond"][0]))
            await member.remove_roles(member.guild.get_role(ranks["gold"][0]))
        elif level - 1 >= 30:
            await member.add_roles(member.guild.get_role(ranks["gold"][0]))
            await member.remove_roles(member.guild.get_role(ranks["lapis"][0]))
        elif level - 1 >= 25:
            await member.add_roles(member.guild.get_role(ranks["lapis"][0]))
            await member.remove_roles(member.guild.get_role(ranks["copper"][0]))
        elif level - 1 >= 20:
            await member.add_roles(member.guild.get_role(ranks["copper"][0]))
            await member.remove_roles(member.guild.get_role(ranks["iron"][0]))
        elif level - 1 >= 15:
            await member.add_roles(member.guild.get_role(ranks["iron"][0]))
            await member.remove_roles(member.guild.get_role(ranks["stone"][0]))
        elif level - 1 >= 10:
            await member.add_roles(member.guild.get_role(ranks["stone"][0]))
            await member.remove_roles(member.guild.get_role(ranks["wood"][0]))
        elif level - 1 >= 5:
            await member.add_roles(member.guild.get_role(ranks["wood"][0]))
    except:
       # User probably has the role already
        pass
