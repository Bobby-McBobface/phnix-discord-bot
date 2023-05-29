import sqlite3

import configuration

client = sqlite3.connect(configuration.DATABASE_PATH)
cursor = client.cursor()
