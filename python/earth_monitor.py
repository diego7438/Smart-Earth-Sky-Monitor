import requests
import sqlite3
from datetime import datetime
from logger import logger

def fetch_and_save():
    # Databse setup
    conn = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
    cursor = conn.cursor()

    # To see total rows in databse
    # print("Total rows in database:", cursor.fetchone()[0])
    try:
        # Fetch data from USGS
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "minmagnitude": 4.5,
            "limit": 10
        }
        response = requests.get(url, params=params)
        data = response.json()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS earthquakes (
                id TEXT PRIMARY KEY, 
                magnitude REAL,
                place TEXT,
                time INTEGER,
                latitude REAL,
                longitude REAL,
                depth REAL,
                collected_at TEXT
            )""")
        # primary key means this field must be unique

        for earthquake in data["features"]:
            id = earthquake["id"]
            mag = earthquake["properties"]["mag"]
            place = earthquake["properties"]["place"]
            time = earthquake["properties"]["time"]
            lat = earthquake["geometry"]["coordinates"][1]
            lon = earthquake["geometry"]["coordinates"][0]
            depth = earthquake["geometry"]["coordinates"][2] # depth
            cursor.execute("""
            INSERT OR IGNORE INTO earthquakes VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", # or ignore tells SQLite 
            # "if this row already exists, skip it silently"
            (id, mag, place, time, lat, lon, depth, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            logger.info(f"Saved earthquake: M{mag} - {place}")
        conn.commit()

    except Exception as e:
        logger.error(f"Failed to fetch earthquake data: {e}")
        logger.info("Restart scheduler with: python3 scheduler.py")
    
    finally:
        conn.close()

# this part calls the function once immediately
if __name__ == "__main__":
    fetch_and_save()