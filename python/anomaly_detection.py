import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest
import numpy as np
from logger import logger

def run_anomaly_detection():
    conn = sqlite3.connect("monitor.db")
    
    try:
        earthquakes = pd.read_sql("SELECT * FROM earthquakes", conn)
        weather = pd.read_sql("""
            SELECT * FROM weather
            WHERE time IN (
                SELECT MAX(time)
                FROM weather
                GROUP BY latitude, longitude
            )
        """, conn)

        combined = earthquakes.merge(weather, on=["latitude", "longitude"], suffixes=("_quake", "_weather"))

        features = ["magnitude", "depth", "temperature",
                    "pressure", "humidity", "wind_speed", "clouds"]

        X = combined[features]

        if len(X) < 100:
            logger.info(f"Not enough data yet - have {len(X)} rows, need 100+")
        else:
            model = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            combined["anomaly_score"] = model.fit_predict(X)
            combined["anomaly"] = combined["anomaly_score"].apply(
                lambda x: "anomaly" if x == -1 else "normal"
            )

            conn2 = sqlite3.connect("monitor.db")
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