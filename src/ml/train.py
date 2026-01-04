import os
import pandas as pd
import numpy as np
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sqlalchemy import create_engine
from sklearn.metrics import mean_squared_error, mean_absolute_error
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL", 
            "postgresql+psycopg2://airflow:airflow@postgres/airflow"
        )
        self.engine = create_engine(self.db_url)
        
        # Set MLflow tracking
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment("pm25_forecasting")

    def load_training_data(self):
        """
        Load features from Gold layer.
        """
        logger.info("Loading training data from gold.pm25_features...")
        query = "SELECT * FROM gold.pm25_features ORDER BY feature_timestamp ASC"
        df = pd.read_sql(query, self.engine)
        return df

    def train(self, df):
        if df.empty:
            logger.warning("No data to train on.")
            return

        # Prepare X and y
        # Target: Predict Next Hour? 
        # Standard approach for 24h recursive: Model predicts y(t) given X(t-1) features?
        # NO. My features at row `t` already include lags like `pm25_lag_1h` (which is t-1).
        # So row `t` contains:
        #   pm25 (the value at t) -> TARGET
        #   pm25_lag_1h (value at t-1)
        #   weather (at t? or t-1?)
        #   
        # If I want to predict "Next 24h", I need a model that output (t).
        # So, Target = 'pm25'. Features = all others.
        
        target_col = 'pm25'
        drop_cols = ['feature_timestamp', 'created_at', 'city'] # Metadata
        
        X = df.drop(columns=[target_col] + [c for c in drop_cols if c in df.columns])
        y = df[target_col]
        
        # Time-based split (Last 20% as holdout)
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        logger.info(f"Training shapes: X_train={X_train.shape}, X_test={X_test.shape}")
        
        with mlflow.start_run():
            params = {
                "objective": "reg:squarederror",
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 6
            }
            
            mlflow.log_params(params)
            
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            
            # Evaluate
            preds = model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            mae = mean_absolute_error(y_test, preds)
            
            logger.info(f"Test RMSE: {rmse:.4f}, MAE: {mae:.4f}")
            
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mae", mae)
            
            # Log Model with signature
            signature = mlflow.models.infer_signature(X_train, model.predict(X_train))
            
            mlflow.xgboost.log_model(
                xgb_model=model,
                artifact_path="model",
                signature=signature,
                registered_model_name="pm25_xgboost_v1"
            )
            
            # Log metrics to DB
            self.save_metrics(mlflow.active_run().info.run_id, "xgboost", rmse, mae, params)

    def save_metrics(self, run_id, model_type, rmse, mae, params):
        query = text("""
            INSERT INTO gold.model_metrics (run_id, model_type, training_date, rmse, mae, param_hash)
            VALUES (:run_id, :model_type, NOW(), :rmse, :mae, :params)
            ON CONFLICT (run_id) DO NOTHING
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(query, {
                    "run_id": run_id,
                    "model_type": model_type,
                    "rmse": rmse,
                    "mae": mae,
                    "params": str(params)
                })
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

from sqlalchemy import text # Missing import fix

if __name__ == "__main__":
    trainer = ModelTrainer()
    df = trainer.load_training_data()
    trainer.train(df)
