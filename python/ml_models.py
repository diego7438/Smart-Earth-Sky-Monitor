import pandas as pd
import sqlite3
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report
from logger import logger

# Path to models folder
MODELS_DIR = "/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/models"
os.makedirs(MODELS_DIR, exist_ok = True)

def run_ml_models():
    # Open a connection to the local monitoring SQLite database.
    conn = sqlite3.connect("/Users/diegoanderson/Desktop/Smart Earth and Sky Monitor/monitor.db")
    
    try:
        # Load earthquake and the latest weather records per location.
        earthquakes = pd.read_sql("SELECT * FROM earthquakes", conn)
        weather = pd.read_sql("""
            SELECT * FROM weather
            WHERE time IN (
                SELECT MAX(time)
                FROM weather
                GROUP BY latitude, longitude
            )
        """, conn)

        # Merge the tables so each earthquake row has associated weather features.
        combined = earthquakes.merge(weather, on=["latitude", "longitude"], suffixes=("_quake", "_weather"))

        # Check magnitude distribution before running:
        print(combined["magnitude"].describe())
        print("Above 5.0:", (combined["magnitude"] >= 5.0).sum())
        print("Below 5.0:", (combined["magnitude"] < 5.0).sum())

        # Feature engineering - extract temporal features and simple interactions.
        # These help regression and classification models capture time-of-day
        # effects and depth×magnitude interactions.
        combined["hour"] = pd.to_datetime(combined["collected_at_quake"]).dt.hour
        combined["day_of_week"] = pd.to_datetime(combined["collected_at_quake"]).dt.dayofweek
        combined["depth_x_magnitude"] = combined["depth"] * combined["magnitude"]

        # Require a minimum dataset size to produce meaningful model results.
        if len(earthquakes) < 100:
            logger.info(f"Not enough data yet - have {len(earthquakes)} rows, need 100+")
        else:
            features = ["temperature", "pressure", "humidity", 
            "wind_speed", "clouds", "depth", "hour", "day_of_week", "depth_x_magnitude"]
            
            X = combined[features]
            y = combined["magnitude"]

            # Split data - 80% training, 20% testing. Keep a fixed random state
            # for reproducible metric comparisons.
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size = 0.2, random_state = 42
            )

            # Train a simple baseline linear regression model.
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Evaluate on the held-out test set.
            y_pred = model.predict(X_test)

            # Evaluate
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            logger.info(f"Linear Regression R²: {r2:.3f}")
            logger.info(f"Linear Regression RMSE: {rmse:.3f}")

            # Log learned linear coefficients as a simple feature importance.
            for feat, coef in zip(features, model.coef_):
                logger.info(F" {feat}: {coef:.4f}")

            # Save full-set predictions and residuals back to the database so
            # dashboards and reports can consume model outputs.
            combined["predicted_magnitude"] = model.predict(X)
            combined["residual"] = combined["magnitude"] - combined["predicted_magnitude"]

            combined[["id", "predicted_magnitude", "residual"]].to_sql(
                "magnitude_predictions",
                conn,
                if_exists = "replace",
                index = False
            )

            logger.info("Predictions saved to database")

            # Neural networks typically require feature scaling; reuse the same
            # training/test split but with standardized features for the MLP.
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

            # Evaluate the neural network on the test split and log metrics.
            nn_pred = nn_model.predict(X_test_scaled)
            nn_r2 = r2_score(y_test, nn_pred)
            nn_rmse = np.sqrt(mean_squared_error(y_test, nn_pred))

            # Logger info for neural net
            logger.info(f"Neural Network R²: {nn_r2:.3f}")
            logger.info(f"Neural Network RMSE: {nn_rmse:.3f}")

            # Create a binary classification target: is magnitude >= 5.0?
            combined["above_5"] = (combined["magnitude"] >= 5.0). astype(int) 
            y_class = combined["above_5"]

            # Same train/test split but for classification
            X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
                X, y_class, test_size = 0.2, random_state = 42
            )

            # Train a Random Forest classifier to predict large earthquakes.
            rf_model = RandomForestClassifier(
                n_estimators = 100, 
                random_state = 42
            )
            rf_model.fit(X_train_c, y_train_c)

            # Evaluate classification performance and log standard metrics.
            y_pred_class = rf_model.predict(X_test_c)
            accuracy = accuracy_score(y_test_c, y_pred_class)
            precision = precision_score(y_test_c, y_pred_class, zero_division = 0)
            recall = recall_score(y_test_c, y_pred_class, zero_division = 0)

            # Adding logging info
            logger.info(f"Random Forest Accuracy: {accuracy:.3f}")
            logger.info(f"Random Forest Precision: {precision:.3f}")
            logger.info(f"Random Forest Recall: {recall:.3f}")
            logger.info("\n" + classification_report(y_test_c, y_pred_class, zero_division = 0))

            # Feature importance - inspect which features the Random Forest
            # relied on most for classification decisions.
            importances = pd.DataFrame({
                "feature": features,
                "importance": rf_model.feature_importances_
            }).sort_values("importance", ascending = False)

            for _, row in importances.iterrows():
                logger.info(f"  {row['feature']}: {row['importance']:.4f}")

            # Save classification results to database
            classification_results = pd.DataFrame({
                "model" : ["linear_regression", "neural_network", "random_forest"],
                "r2" : [r2, nn_r2, None],
                "rmse" : [rmse, nn_rmse, None],
                "accuracy" : [None, None, accuracy],
                "precision" : [None, None, precision],
                "recall" : [None, None, recall],
                "run_at" : [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3 
            })

            classification_results.to_sql(
                "model_performance",
                conn, 
                if_exists = "append",
                index = False
            )
            logger.info("Model performance saved to database correctly.")

            # Serialize trained models to disk
            with open(f"{MODELS_DIR}/linear_regression.pkl", "wb") as f:
                pickle.dump(model, f)

            with open(f"{MODELS_DIR}/neural_network.pkl", "wb") as f:
                pickle.dump(nn_model, f)
            
            with open(f"{MODELS_DIR}/random_forest.pkl", "wb") as f:
                pickle.dump(rf_model, f)

            with open(f"{MODELS_DIR}/scaler.pkl", "wb") as f:
                pickle.dump(scaler, f)
            
            logger.info("All models serialized to disk. Nice work.")

    except Exception as e:
        logger.error(f"ML models failed: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    run_ml_models()