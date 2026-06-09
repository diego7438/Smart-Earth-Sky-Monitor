import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest
import numpy as np
from logger import logger

def run_anomaly_detection():
    # Read the local monitoring database used by the dashboard and batch jobs.
    conn = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
    
    try:
        # Load the latest earthquake and weather records for matching locations.
        earthquakes = pd.read_sql("SELECT * FROM earthquakes", conn)
        weather = pd.read_sql("""
            SELECT * FROM weather
            WHERE time IN (
                SELECT MAX(time)
                FROM weather
                GROUP BY latitude, longitude
            )
        """, conn)

        # Combine sensor data into one table so the model can score each event.
        combined = earthquakes.merge(weather, on=["latitude", "longitude"], suffixes=("_quake", "_weather"))

        # Use seismic and weather measurements as anomaly detection features.
        features = ["magnitude", "depth", "temperature",
                    "pressure", "humidity", "wind_speed", "clouds"]

        X = combined[features]

        # Avoid training on too little data, which makes the scores unreliable.
        if len(X) < 100:
            logger.info(f"Not enough data yet - have {len(X)} rows, need 100+")
        else:
            # IsolationForest flags records that look unusual compared to the rest.
            model = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            combined["anomaly_score"] = model.fit_predict(X)
            combined["anomaly"] = combined["anomaly_score"].apply(
                lambda x: "anomaly" if x == -1 else "normal"
            )

            # Persist the latest anomaly results for downstream reports and dashboards.
            conn2 = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
            combined[["id", "anomaly", "anomaly_score"]].to_sql(
                "anomalies",
                conn2,
                if_exists="replace",
                index=False
            )
            conn2.close()
            logger.info(f"Anomaly detection complete - {len(combined[combined['anomaly']=='anomaly'])} anomalies found")
            logger.info("Anomaly results saved to database")

    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    run_anomaly_detection()