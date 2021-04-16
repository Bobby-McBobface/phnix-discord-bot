import asyncio
import configuration
import sqlite3
import random
import discord

chatted = []


async def add_exp(member: int, message: discord.Message):
    global chatted

    if member.id not in chatted:
        xp_gain = random.randint(configuration.XP_GAIN_MIN, configuration.XP_GAIN_MAX)

        chatted.append(member.id)

        sqlite_client = sqlite3.connect('bot_database.db')
        user_xp = sqlite_client.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                        {'user_id': member.id}).fetchone()

        if user_xp == None:
            user_xp = (0,0)

        xp = user_xp[0] + xp_gain
        level = user_xp[1]

        if xp >= await xp_needed_for_level(level):
            #level up

            level += 1

            message.channel.send(f"You reached level {level-1}! :poglin:")
            # Give level roles
            # Internally, levels are one more than MEE6 was, so there is a compensation
            if level - 1 == 55:
                member.add_roles(member.guild.get_role(configuration.NETHERITE), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.EMERALD), reason="Level up!")
            elif level - 1 == 45:
                member.add_roles(member.guild.get_role(configuration.EMERALD), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.OBSIDIAN), reason="Level up!")
            elif level - 1 == 40:
                member.add_roles(member.guild.get_role(configuration.OBSIDIAN), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.DIAMOND), reason="Level up!")
            elif level - 1 == 35:
                member.add_roles(member.guild.get_role(configuration.DIAMOND), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.GOLD), reason="Level up!")
            elif level - 1 == 30:
                member.add_roles(member.guild.get_role(configuration.GOLD), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.LAPIS), reason="Level up!")
            elif level - 1 == 25:
                member.add_roles(member.guild.get_role(configuration.LAPIS), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.COPPER), reason="Level up!")
            elif level - 1 == 20:
                member.add_roles(member.guild.get_role(configuration.COPPER), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.IRON), reason="Level up!")
            elif level - 1 == 15:
                member.add_roles(member.guild.get_role(configuration.IRON), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.STONE), reason="Level up!")
            elif level - 1 == 10:
                member.add_roles(member.guild.get_role(configuration.STONE), reason="Level up!")
                member.remove_roles(member.guild.get_role(configuration.WOOD), reason="Level up!")
            elif level - 1 == 5:
                member.add_roles(member.guild.get_role(configuration.WOOD), reason="Level up!")
                     
        
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