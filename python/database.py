import sqlite3

conn = sqlite3.connect("earthquakes.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS earthquakes (
        id TEXT,
        magnitude REAL,
        place TEXT,
        time INTEGER,
        latitude REAL,
        longitude REAL,
        depth REAL
    )
""")

conn.commit()
print("Database ready!")