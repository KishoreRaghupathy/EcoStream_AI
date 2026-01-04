-- Gold Layer: Feature Store
CREATE TABLE IF NOT EXISTS gold.pm25_features (

    feature_timestamp TIMESTAMP PRIMARY KEY,
    city VARCHAR(50), -- Partition key
    pm25 FLOAT, 
    pm25_lag_1h FLOAT,
    pm25_lag_3h FLOAT,
    pm25_lag_6h FLOAT,
    pm25_lag_12h FLOAT,
    pm25_lag_24h FLOAT,
    pm25_mean_24h FLOAT,
    pm25_std_24h FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    hour_sin FLOAT,
    hour_cos FLOAT,
    day_sin FLOAT,
    day_cos FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gold Layer: Predictions
CREATE TABLE IF NOT EXISTS gold.pm25_predictions (
    prediction_id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    model_version VARCHAR(50),
    forecast_timestamp TIMESTAMP, -- The time the prediction is FOR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When the prediction was MADE
    predicted_pm25 FLOAT,
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT
);

-- Gold Layer: Model Metrics
CREATE TABLE IF NOT EXISTS gold.model_metrics (
    run_id VARCHAR(50) PRIMARY KEY,
    model_type VARCHAR(50),
    training_date TIMESTAMP,
    rmse FLOAT,
    mae FLOAT,
    r2_score FLOAT,
    param_hash TEXT
);
