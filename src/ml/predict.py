import os
import pandas as pd
import numpy as np
import mlflow.xgboost
from sqlalchemy import create_engine, text
import logging
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Predictor:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL", 
            "postgresql+psycopg2://airflow:airflow@postgres/airflow"
        )
        self.engine = create_engine(self.db_url)
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        mlflow.set_tracking_uri(self.tracking_uri)
        
        self.model = None

    def load_model(self, model_name="pm25_xgboost_v1", stage="None"):
        """
        Load model from MLflow. Tries to load specific stage, else latest.
        """
        try:
            # If stage is None, typically gets latest version.
            # Constructed URI: models:/<name>/<stage> or <version>
            # For simplicity, let's try to load 'latest' or specifically a run if we had it.
            # 'models:/pm25_xgboost_v1/Production' is validating stages.
            # If not using Model Registry extensively, we can verify with runs.
            # Let's assume user calls this after training or we pick latest run.
            
            # For this MVP, we might load from the latest run ID if Registry is not fully set up in free tier local?
            # MLflow Registry works with SQLite backend.
            
            # Fallback: Load latest run
            client = mlflow.tracking.MlflowClient()
            versions = client.search_model_versions(f"name='{model_name}'")
            if not versions:
                logger.error("No model found.")
                return None
            
            # Sort by version
            latest = sorted(versions, key=lambda x: int(x.version))[-1]
            model_uri = f"models:/{model_name}/{latest.version}"
            
            logger.info(f"Loading model from {model_uri}")
            self.model = mlflow.xgboost.load_model(model_uri)
            return self.model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None

    def get_latest_features(self, city="London"):
        """
        Get the most recent row from features table for a city.
        """
        query = text(f"SELECT * FROM gold.pm25_features WHERE city = :city ORDER BY feature_timestamp DESC LIMIT 1")
        df = pd.read_sql(query, self.engine, params={"city": city})
        return df

    def predict_next_24h(self, city="London"):
        if not self.model:
            self.load_model()
        
        current_features = self.get_latest_features(city=city)
        if current_features.empty:
            logger.warning("No live features available.")
            return []
            
        # Prepare for recursion
        # Dropping metadata not used by model
        # Identify feature columns expected by model
        # We can inspect model signature or just rely on column names matching training
        
        # Assumption: The model was trained on all cols in gold.pm25_features EXCEPT 'pm25' (target), 'feature_timestamp', 'created_at'
        # We must align input.
        
        predictions = []
        
        # We process as a single row DataFrame
        input_row = current_features.iloc[0].copy()
        start_time = input_row['feature_timestamp']
        
        # We need the list of features used in training.
        # Ideally, we saved this list or we infer.
        # Hardcoding the update logic for known features.
        
        current_pm25 = input_row['pm25'] # This is y(t)
        
        # We need to simulate t+1
        # Lags need to shift.
        # lag_1h gets current_pm25
        # lag_3h gets value that was lag_2h... but wait, we only stored 1,3,6.
        # If we didn't store 2h, we can't accurately propagate lag_3h without a richer state.
        # Simplified Recursive Strategy:
        # Update lag_1h = prediction (or last actual).
        # Keep other lags constant (Poor man's recursion) OR 
        # Better: We only really trust lag_1h for immediate, others matter less?
        # CORRECT WAY: We need a history buffer of past 24h values to properly calculate lags at each step.
        # But `input_row` only has specific lags.
        # LIMITATION ACCEPTED: We will update `pm25_lag_1h` with the new prediction.
        # We will keep `pm25_lag_3h` etc. roughly constant or degrade them -> This is a known approximation in limited state recursion.
        
        # Iteration
        current_vec = input_row.drop(['pm25', 'feature_timestamp', 'created_at', 'city'], errors='ignore')
        
        for i in range(1, 25):
            # Predict
            pred_df = pd.DataFrame([current_vec])
            pred = self.model.predict(pred_df)[0]
            predictions.append({
                "forecast_timestamp": start_time + timedelta(hours=i),
                "predicted_pm25": float(pred)
            })
            
            # Update State for next step
            # 1. Shift Lags (Approximate)
            # We assume lag_24h ~= lag_24h (slow moving?) No, lag_24h is yesterday this time.
            # lag_1h becomes the prediction we just made
            current_vec['pm25_lag_1h'] = pred 
            
            # 2. Update Time
            next_time = start_time + timedelta(hours=i)
            current_vec['hour_sin'] = np.sin(2 * np.pi * next_time.hour / 24)
            current_vec['hour_cos'] = np.cos(2 * np.pi * next_time.hour / 24)
            current_vec['day_sin'] = np.sin(2 * np.pi * next_time.dayofweek / 7)
            current_vec['day_cos'] = np.cos(2 * np.pi * next_time.dayofweek / 7)
            
            # 3. Weather - Persistence (No change)
            
        return predictions

    def save_predictions(self, predictions, city="London"):
        if not predictions:
            return
            
        df = pd.DataFrame(predictions)
        # Add metadata
        df['city'] = city
        df['model_version'] = "xgboost_v1" # simplified
        df['created_at'] = datetime.now()
        df['confidence_interval_lower'] = df['predicted_pm25'] * 0.9 # Mock CI
        df['confidence_interval_upper'] = df['predicted_pm25'] * 1.1
        
        logger.info(f"Saving {len(df)} predictions.")
        df.to_sql('pm25_predictions', self.engine, schema='gold', if_exists='append', index=False)

from datetime import datetime

if __name__ == "__main__":
    p = Predictor()
    preds = p.predict_next_24h(city="London")
    p.save_predictions(preds, city="London")
    print(preds)
