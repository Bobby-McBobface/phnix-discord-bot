import asyncio
import configuration
import sqlite3
import random

chatted = []


async def add_exp(member: int):
    global chatted

    if member not in chatted:
        xp_gain = random.randint(15, 25)

        chatted.append(member)

        sqlite_client = sqlite3.connect('bot_database.db')
        user_xp = sqlite_client.execute('''SELECT XP FROM LEVELS WHERE ID=:user_id''',
                                        {'user_id': member}).fetchone()

        if user_xp == None:
            user_xp = 0
        else:
            user_xp = user_xp[0]

        user_xp += xp_gain

        sqlite_client.execute('''INSERT INTO LEVELS (ID, XP) \
        VALUES(:member, :user_xp) \
        ON CONFLICT(ID) \
        DO UPDATE SET XP=:user_xp''',
                              {'member': member,
                               'user_xp': user_xp}
                              )
        sqlite_client.commit()
        sqlite_client.close()


# Need a non blocking loop here to reset chatted every INTERVAL seconds
async def clear_chatted_loop():
    global chatted

    while True:
        await asyncio.sleep(configuration.XP_MESSAGE_INTERVAL)
        chatted = []
