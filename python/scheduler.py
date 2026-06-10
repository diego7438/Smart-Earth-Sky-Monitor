import schedule
import time
import sqlite3
import pandas as pd
from logger import logger
from earth_monitor import fetch_and_save
from weather_monitor import fetch_weather
from anomaly_detection import run_anomaly_detection
from ml_models import run_ml_models

def fetch_weather_for_all_earthquakes():
    # Connect to database and get all unique earthquake locations
    conn = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
    locations = pd.read_sql("SELECT DISTINCT latitude, longitude FROM earthquakes", conn)
    conn.close()

    # Fetch weather for each earthquake location
    for _, row in locations.iterrows():
        fetch_weather(row["latitude"], row["longitude"])
        time.sleep(1) # be polite to the api and let it rest

# Schedule all jobs
schedule.every().hour.do(fetch_and_save)
schedule.every().hour.do(fetch_weather_for_all_earthquakes)
schedule.every().hour.do(run_ml_models)

# Run anomaly detection after each earthquake fetch
schedule.every().hour.do(run_anomaly_detection)

# Run immediately on startup
logger.info("Running first fetch...")
fetch_and_save()
fetch_weather_for_all_earthquakes()
logger.info("Running anomaly detection...")
run_anomaly_detection()
logger.info("Running Machine Learning Models...")
run_ml_models()

logger.info("Scheduler running! Press Ctrl + C to stop")
while True:
    schedule.run_pending()
    time.sleep(60)