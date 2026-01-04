from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import logging

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://airflow:airflow@postgres/airflow")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EcoStream ML Service",
    description="PM2.5 Forecasting API",
    version="1.0.0"
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class Prediction(BaseModel):
    forecast_timestamp: datetime
    predicted_pm25: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    
class PredictionResponse(BaseModel):
    city: str
    model_version: str
    predictions: List[Prediction]

class ModelMetadata(BaseModel):
    run_id: str
    model_type: str
    training_date: datetime
    rmse: float
    mae: float

# Routes
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now()}

@app.get("/predict/pm25", response_model=PredictionResponse)
def get_prediction(city: str = Query("London", description="City to get forecast for"), db: Session = Depends(get_db)):
    """
    Get the latest 24h forecast for independent city.
    """
    # Get latest batch of predictions
    # Assumption: We want the predictions generated most recently.
    # Group by created_at? Or just take the last 24 rows?
    # Better: Get the max(created_at) for the city, then get rows with that created_at.
    
    try:
        # Find latest creation time
        max_time_query = text("SELECT MAX(created_at) FROM gold.pm25_predictions WHERE city = :city")
        result = db.execute(max_time_query, {"city": city}).scalar()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No predictions found for {city}")
            
        # Get predictions for that batch
        query = text("""
            SELECT 
                forecast_timestamp, 
                predicted_pm25, 
                confidence_interval_lower, 
                confidence_interval_upper,
                model_version
            FROM gold.pm25_predictions 
            WHERE city = :city AND created_at = :created_at
            ORDER BY forecast_timestamp ASC
        """)
        
        rows = db.execute(query, {"city": city, "created_at": result}).fetchall()
        
        predictions = []
        model_version = "unknown"
        if rows:
            model_version = rows[0].model_version
            for row in rows:
                predictions.append({
                    "forecast_timestamp": row.forecast_timestamp,
                    "predicted_pm25": row.predicted_pm25,
                    "confidence_interval_lower": row.confidence_interval_lower,
                    "confidence_interval_upper": row.confidence_interval_upper
                })
        
        return {
            "city": city,
            "model_version": model_version,
            "predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/metadata", response_model=List[ModelMetadata])
def get_model_metadata(limit: int = 5, db: Session = Depends(get_db)):
    """
    Get recent model training metrics.
    """
    try:
        query = text("""
            SELECT run_id, model_type, training_date, rmse, mae 
            FROM gold.model_metrics 
            ORDER BY training_date DESC 
            LIMIT :limit
        """)
        rows = db.execute(query, {"limit": limit}).fetchall()
        
        results = []
        for row in rows:
            results.append({
                "run_id": row.run_id,
                "model_type": row.model_type,
                "training_date": row.training_date,
                "rmse": row.rmse,
                "mae": row.mae
            })
        return results
    except Exception as e:
        logger.error(f"Error fetching metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))
