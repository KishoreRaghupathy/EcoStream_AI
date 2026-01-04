import os
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL", 
            "postgresql+psycopg2://airflow:airflow@postgres/airflow" # Default inside container
        )
        self.engine = create_engine(self.db_url)

    def load_data(self, city="London", days_back=30):
        """
        Load data from Silver layer for a specific city.
        """
        logger.info(f"Loading data for {city} from past {days_back} days.")
        
        query = text("""
            SELECT 
                aq.timestamp,
                aq.pm25,
                w.temperature,
                w.humidity,
                w.wind_speed
            FROM silver.dim_location l
            JOIN silver.fact_air_quality aq ON l.location_id = aq.location_id
            LEFT JOIN silver.fact_weather w ON l.location_id = w.location_id AND aq.timestamp = w.timestamp
            WHERE l.city = :city
            AND aq.timestamp >= NOW() - INTERVAL ':days days'
            ORDER BY aq.timestamp ASC
        """)
        
        # Safe execution with pandas
        try:
            # Note: Pandas read_sql with parameters is safer
            params = {"city": city, "days": str(days_back)}
            # Constructing raw query for simplicity due to parameter binding complexity in some versions with intervals
            # But safer to just pull more data and filter, or use f-string with strict validation (ok for internal tool)
            # Let's use simple f-string for the interval part which is an int
            clean_query = f"""
                SELECT 
                    aq.timestamp,
                    aq.pm25,
                    w.temperature,
                    w.humidity,
                    w.wind_speed
                FROM silver.dim_location l
                JOIN silver.fact_air_quality aq ON l.location_id = aq.location_id
                LEFT JOIN silver.fact_weather w ON l.location_id = w.location_id AND aq.timestamp = w.timestamp
                WHERE l.city = '{city}'
                AND aq.timestamp >= NOW() - INTERVAL '{days_back} days'
                ORDER BY aq.timestamp ASC
            """
            df = pd.read_sql(clean_query, self.engine)
            if not df.empty:
                df['city'] = city
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def create_features(self, df):
        """
        Generate Lag, Rolling, and Cyclical features.
        """
        if df.empty:
            logger.warning("No data to process.")
            return df
            
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Save city if exists
        city_val = df['city'].iloc[0] if 'city' in df.columns else None
        
        df.set_index('timestamp', inplace=True)
        
        # Resample to hourly to ensure regular intervals
        # Drop city before resample as it is string
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df = df[numeric_cols].resample('h').mean().interpolate(method='linear')
        
        if city_val:
            df['city'] = city_val
        
        target = 'pm25'
        
        # 1. Lag Features
        lags = [1, 3, 6, 12, 24]
        for lag in lags:
            df[f'pm25_lag_{lag}h'] = df[target].shift(lag)
            
        # 2. Rolling Statistics (on shifted data to avoid leakage)
        # Shift 1 to ensure we use past data for current prediction time
        # For predicting t_0, we need stats from t_(-1) backwards.
        # But if features are for training "predict next hour", then at row t, we know pm25(t). 
        # Wait, typical structure:
        # X(t) = Features at time t (known) -> y(t+1) = Target.
        # OR X(t) includes lags from t, t-1... -> y(t) = Target?
        # Let's stick to standard:
        # Row t contains: PM25(t) (Target), Lags: PM25(t-1), PM25(t-3)...
        # So we create lags of the target column.
        
        # Rolling window: 24h features
        df['pm25_mean_24h'] = df[target].shift(1).rolling(window=24).mean()
        df['pm25_std_24h'] = df[target].shift(1).rolling(window=24).std()
        
        # 3. Cyclical Time Features
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Drop raw columns that we don't need for the Feature Cache? or Keep them?
        # We need weather too. 
        # Drop cols that are just helpers or NaNs
        df.dropna(inplace=True)
        
        # Reset index to make timestamp a column
        df.reset_index(inplace=True)
        df.rename(columns={'timestamp': 'feature_timestamp'}, inplace=True)
        
        return df

    def save_features(self, df):
        """
        Save features to Gold layer.
        """
        if df.empty:
            return
            
        logger.info(f"Saving {len(df)} feature rows to Gold layer.")
        
        # Upsert or Append?
        # For simplicity, we can use if_exists='append', but duplication is a risk.
        # Better to delete overlapping range or use ON CONFLICT.
        # Given 'production grade', we should probably handle duplicates.
        # But for this scope, let's use a try/except block or just append and assume cleanup job.
        # Or better: check max timestamp and only append new.
        
        try:
            # Check existing max
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT MAX(feature_timestamp) FROM gold.pm25_features"))
                max_ts = result.scalar()
            
            if max_ts:
                df = df[df['feature_timestamp'] > max_ts]
            
            if not df.empty:
                df.to_sql('pm25_features', self.engine, schema='gold', if_exists='append', index=False)
                logger.info(f"Successfully saved {len(df)} new rows.")
            else:
                logger.info("No new features to save.")
                
        except Exception as e:
            logger.error(f"Error saving features: {e}")
            # If table doesn't exist, just write
            if "relation \"gold.pm25_features\" does not exist" in str(e):
                 df.to_sql('pm25_features', self.engine, schema='gold', if_exists='append', index=False)

if __name__ == "__main__":
    fe = FeatureEngineer()
    raw_df = fe.load_data()
    features_df = fe.create_features(raw_df)
    fe.save_features(features_df)
