import sqlite3

sqlite_client = sqlite3.connect('bot_database.db')
sqlite_client.execute('''CREATE TABLE IF NOT EXISTS LEVELS ( \
    ID INT PRIMARY KEY NOT NULL, \
    XP INT             NOT NULL \
    );''')

sqlite_client.execute('''CREATE TABLE IF NOT EXISTS WARNS ( \
    ID INT             NOT NULL, \
    TIMESTAMP NUMERIC  NOT NULL, \
    REASON TEXT        NOT NULL  \
    );''')
sqlite_client.execute('''CREATE TABLE IF NOT EXISTS MUTES ( \
    ID INT PRIMARY KEY NOT NULL, \
    TIMESTAMP NUMERIC  NOT NULL, \
    ROLES TEXT         NOT NULL  \
    );''')
sqlite_client.commit()
sqlite_client.close()
    
'''sqlite_client = sqlite3.connect('bot_database.db')
sqlite_client.execute(f''''''INSERT INTO LEVELS (ID, XP) \
            VALUES(381634036357136391, 5) \
            ON CONFLICT(ID) \
            DO UPDATE SET XP=5''''''
            )
sqlite_client.commit()
sqlite_client.close()'''
