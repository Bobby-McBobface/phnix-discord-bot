import sqlite3

print("CHECK CONTENTS OF THIS SCRIPT BEFORE RUNNING!!!")
answer = input("Are you sure you want to run this? (y/n)")
if answer != "y":
    exit(code=0)
    
print("Setting up data...")

sqlite_client = sqlite3.connect('bot_database.db')
#sqlite_client.execute('''DROP TABLE LEVELS''')
sqlite_client.execute('''DROP TABLE WARNS''')
#sqlite_client.execute('''DROP TABLE MUTES''')
sqlite_client.execute('''CREATE TABLE IF NOT EXISTS LEVELS ( \
    ID INT PRIMARY KEY NOT NULL, \
    XP INT             NOT NULL, \
    LEVEL INT          NOT NULL  \
    );''')
sqlite_client.commit()
sqlite_client.execute('''CREATE TABLE IF NOT EXISTS WARNS ( \
    ID INT             NOT NULL, \
    TIMESTAMP INT      NOT NULL, \
    REASON TEXT        NOT NULL  \
    );''')
sqlite_client.commit()
sqlite_client.execute('''CREATE TABLE IF NOT EXISTS MUTES ( \
    ID INT PRIMARY KEY NOT NULL, \
    TIMESTAMP INT      NOT NULL, \
    ROLES TEXT         NOT NULL  \
    );''')
sqlite_client.commit()
'''
import urllib3
import json
http = urllib3.PoolManager()
r = http.request("GET", "https://mee6.xyz/api/plugins/levels/leaderboard/329226224759209985?page=0&limit=1000")
data = json.loads(r.data.decode('utf-8'))
users = data["players"]
for user in users:
    sqlite_client.execute(f''''''INSERT INTO LEVELS (ID, XP, LEVEL) \
            VALUES(:id, :xp, :level) \
            ON CONFLICT(ID) \
            DO UPDATE SET XP=:xp, LEVEL=:level'''''',
            {'id': user["id"],
            'xp': user["xp"],
            'level': user["level"]})
    print(user["id"],user["xp"],user["level"])'''

sqlite_client.close()

'''sqlite_client = sqlite3.connect('bot_database.db')
sqlite_client.execute(f''''''INSERT INTO LEVELS (ID, XP, LEVELS) \
            VALUES(381634036357136391, 9999999, 9999999) \
            ON CONFLICT(ID) \
            DO UPDATE SET XP=999999, LEVEL=999999''''''
            )
sqlite_client.commit()
sqlite_client.close()'''
