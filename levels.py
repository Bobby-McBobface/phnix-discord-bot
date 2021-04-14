import asyncio
import configuration
import sqlite3
import random
import math

chatted = []


async def add_exp(member: int):
    global chatted

    if member not in chatted:
        xp_gain = random.randint(15, 25)

        chatted.append(member)

        sqlite_client = sqlite3.connect('bot_database.db')
        user_xp = sqlite_client.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                        {'user_id': member}).fetchone()

        if user_xp == None:
            user_xp = (0,0)

        xp = user_xp[0] + xp_gain

        if user_xp[1] > math.floor(5/6*((2*xp**3)+(27*xp**2)+(91*xp))):
            level = user_xp[1]
            level += 1
            #level up
        else:
            level = user_xp[1]

        sqlite_client.execute('''INSERT INTO LEVELS (ID, XP, LEVEL) \
        VALUES(:member, :user_xp, :level) \
        ON CONFLICT(ID) \
        DO UPDATE SET XP=:user_xp, LEVEL=:level''',
                              {'member': member,
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
