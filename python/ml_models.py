import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
from logger import logger

def run_ml_models():
    conn = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
    
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

        # Feature engineering - add time and interaction features
        combined["hour"] = pd.to_datetime(combined["collected_at_quake"]).dt.hour
        combined["day_of_week"] = pd.to_datetime(combined["collected_at_quake"]).dt.dayofweek
        combined["depth_x_magnitude"] = combined["depth"] * combined["magnitude"]

        if len(earthquakes) < 100:
            logger.info(f"Not enough data yet - have {len(X)} rows, need 100+")
        else:
            features = ["temperature", "pressure", "humidity", 
            "wind_speed", "clouds", "depth", "hour", "day_of_week", "depth_x_magnitude"]
            
            X = combined[features]
            y = combined["magnitude"]

            # Split data - 80% training, 20% testing
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size = 0.2, random_state = 42
            )

            # Actually training the model
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Testing the model
            y_pred = model.predict(X_test)

            # Evaluate
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            logger.info(f"Linear Regression R²: {r2:.3f}")
            logger.info(f"Linear Regression RMSE: {rmse:.3f}")

            # Feature importance (coefficients)
            for feat, coef in zip(features, model.coef_):
                logger.info(F" {feat}: {coef:.4f}")

            # Save predictions to databse for dashboard visualization
            combined["predicted_magnitude"] = model.predict(X)
            combined["residual"] = combined["magnitude"] - combined["predicted_magnitude"]

            combined[["id", "predicted_magnitude", "residual"]].to_sql(
                "magnitude_predictions",
                conn,
                if_exists = "replace",
                index = False
            )

            logger.info("Predictions saved to database")

            # Neural networks need scaled data unlike linear regression
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Build and train the neural network
            nn_model = MLPRegressor(
                hidden_layer_sizes = (64, 32), # 2 hidden layers
                activation = "relu",
                max_iter = 2000,
                random_state = 42
            )

            nn_model.fit(X_train_scaled, y_train)

            # Evaluate
            nn_pred = nn_model.predict(X_test_scaled)
            nn_r2 = r2_score(y_test, nn_pred)
            nn_rmse = np.sqrt(mean_squared_error(y_test, nn_pred))

            # Logger info for neural net
            logger.info(f"Neural Network R²: {nn_r2:.3f}")
            logger.info(f"Neural Network RMSE: {nn_rmse:.3f}")

    except Exception as e:
        logger.error(f"ML models failed: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    run_ml_models()