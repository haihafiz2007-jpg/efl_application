import sqlite3

DB_FILE = "efl.db"

with open("schema.sql", encoding ="utf-8") as f:
    script = f.read()
connection = sqlite3.connect(DB_FILE)
connection.executescript(script)
connection.commit()
connection.close()

print("Database created :",DB_FILE)