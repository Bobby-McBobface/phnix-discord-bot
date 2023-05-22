import sys

import database_handle

print("CHECK CONTENTS OF THIS SCRIPT BEFORE RUNNING!!!")
answer = input("Are you sure you want to run this? (y/n)")
if answer != "y":
    sys.exit(code=0)

print("Setting up data...")

# database_handle.cursor.execute('''DROP TABLE LEVELS''')
# database_handle.cursor.execute('''DROP TABLE WARNS''')
# database_handle.cursor.execute('''DROP TABLE MUTES''')

database_handle.cursor.execute('''CREATE TABLE IF NOT EXISTS LEVELS ( \
    ID INT PRIMARY KEY NOT NULL, \
    XP INT             NOT NULL, \
    LEVEL INT          NOT NULL  \
    );''')
database_handle.client.commit()
database_handle.cursor.execute('''CREATE TABLE IF NOT EXISTS WARNS ( \
    ID INT             NOT NULL, \
    TIMESTAMP INT      NOT NULL, \
    REASON TEXT        NOT NULL  \
    );''')
database_handle.client.commit()
database_handle.cursor.execute('''CREATE TABLE IF NOT EXISTS MUTES ( \
    ID INT PRIMARY KEY NOT NULL, \
    TIMESTAMP INT      NOT NULL, \
    ROLES TEXT         NOT NULL  \
    );''')
database_handle.client.commit()

"""import urllib3
import json
http = urllib3.PoolManager()
r = http.request("GET", "https://mee6.xyz/api/plugins/levels/leaderboard/329226224759209985?page=0&limit=1000")
data = json.loads(r.data.decode('utf-8'))
users = data["players"]
for user in users:
    database_handle.cursor.execute(f'''INSERT INTO LEVELS (ID, XP, LEVEL) \
            VALUES(:id, :xp, :level) \
            ON CONFLICT(ID) \
            DO UPDATE SET XP=:xp, LEVEL=:level''',
            {'id': user["id"],
            'xp': user["xp"],
            'level': user["level"]})
    print(user["id"],user["xp"],user["level"])
    database_handle.client.commit()

database_handle.cursor.execute(f'''INSERT INTO LEVELS (ID, XP, LEVEL) \
    VALUES(:id, :xp, :level) \
    ON CONFLICT(ID) \
    DO UPDATE SET XP=:xp, LEVEL=:level''',
                      {'id': 381634036357136391,
                       'xp': 1216823182500,
                       'level': 9000})
database_handle.client.commit()"""

'''import database_handle as db
for i in range(67):
  db.cursor.execute(f"""UPDATE LEVELS SET LEVEL={i-1} WHERE LEVEL={i}""")
  db.client.commit()'''
