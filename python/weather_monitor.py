import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from logger import logger
import os

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

def fetch_weather(lat, lon):
    # Databse setup
    conn = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
    cursor = conn.cursor()

    # To see total rows in databse
    # print("Total rows in database:", cursor.fetchone()[0])
    try: 
        # Fetch data from OpenWeather API
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params)
        data = response.json()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                temperature REAL,
                pressure REAL,
                humidity INTEGER,
                latitude REAL,
                longitude REAL,
                wind_speed REAL,
                clouds REAL,
                weather_main TEXT,
                time INTEGER,
                collected_at TEXT,
                PRIMARY KEY (latitude, longitude, time)
            )""")
        # primary key means this field must be unique

        temp = data["main"]["temp"]
        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        clouds = data["clouds"]["all"]
        weather_main = data["weather"][0]["main"]
        time = data["dt"]
        cursor.execute("""
            INSERT OR IGNORE INTO weather
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (temp, pressure, humidity, lat, lon, wind_speed, clouds, weather_main, time,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        logger.info(f"Weather saved for {lat}, {lon}")
    
    except Exception as e:
        logger.error(f"Failed to fetch weather for {lat}, {lon}: {e}")
        logger.info("Restart scheduler with: python3 scheduler.py")

    finally:
        conn.close()

# this part calls the function once immediately
if __name__ == "__main__":
    fetch_weather(24.4799, 109.2073)