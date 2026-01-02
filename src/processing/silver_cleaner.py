import os
import pandas as pd
import glob
from sqlalchemy import create_engine, text
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
DATA_DIR = os.getenv('DATA_DIR', 'data/bronze')
PG_CONN = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN', 'postgresql+psycopg2://ecostream:ecostream@localhost:5432/ecostream_db')

# If running outside airflow container against localhost mapped port
if 'localhost' in PG_CONN:
    # Ensure we use the correct user/db if different
    pass

class SilverCleaner:
    def __init__(self):
        self.engine = create_engine(PG_CONN)

    def process_weather(self):
        path = os.path.join(DATA_DIR, 'weather-raw', '**', '*.parquet')
        files = glob.glob(path, recursive=True)
        logger.info(f"Found {len(files)} weather files")
        
        for f in files:
            try:
                df = pd.read_parquet(f)
                self._load_weather(df)
            except Exception as e:
                logger.error(f"Error processing {f}: {e}")

    def process_aq(self):
        path = os.path.join(DATA_DIR, 'airquality-raw', '**', '*.parquet')
        files = glob.glob(path, recursive=True)
        logger.info(f"Found {len(files)} AQ files")
        
        for f in files:
            try:
                df = pd.read_parquet(f)
                self._load_aq(df)
            except Exception as e:
                logger.error(f"Error processing {f}: {e}")

    def _get_or_create_location(self, conn, loc_id, city, country, lat, lon, source):
        # Very basic dimension handling
        query = text("""
            INSERT INTO silver.dim_location (city, country, latitude, longitude, source_name)
            VALUES (:city, :country, :lat, :lon, :source)
            ON CONFLICT (city, country, source_name) 
            DO UPDATE SET latitude = EXCLUDED.latitude 
            RETURNING location_id
        """)
        result = conn.execute(query, {
            "city": city,
            "country": country,
            "lat": lat,
            "lon": lon,
            "source": source
        })
        return result.scalar()

    def _load_weather(self, df):
        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                try:
                    data = row['data']
                    source = row['source']
                    loc_id = row['location_id'] # e.g. London-GB
                    
                    # Extract fields
                    city = data.get('name', 'Unknown')
                    coord = data.get('coord', {})
                    lat = coord.get('lat', 0)
                    lon = coord.get('lon', 0)
                    timestamp = datetime.fromtimestamp(data.get('dt', time.time()))
                    
                    # 1. Dimension
                    db_loc_id = self._get_or_create_location(conn, loc_id, city, loc_id.split('-')[-1], lat, lon, source)
                    
                    # 2. Fact
                    main = data.get('main', {})
                    wind = data.get('wind', {})
                    weather_desc = data.get('weather', [{}])[0].get('description', '')
                    
                    fact_query = text("""
                        INSERT INTO silver.fact_weather 
                        (location_id, timestamp, temperature, humidity, pressure, wind_speed, wind_deg, description)
                        VALUES (:loc_id, :ts, :temp, :hum, :pres, :ws, :wd, :desc)
                        ON CONFLICT (location_id, timestamp) DO NOTHING
                    """)
                    conn.execute(fact_query, {
                        "loc_id": db_loc_id,
                        "ts": timestamp,
                        "temp": main.get('temp'),
                        "hum": main.get('humidity'),
                        "pres": main.get('pressure'),
                        "ws": wind.get('speed'),
                        "wd": wind.get('deg'),
                        "desc": weather_desc
                    })
                    conn.commit()
                except Exception as e:
                    logger.error(f"Error inserting weather row: {e}")
                    conn.rollback()

    def _load_aq(self, df):
        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                try:
                    data = row['data']
                    source = row['source']
                    
                    city = data.get('city')
                    country = data.get('country')
                    # OpenAQ location lat/lon is sometimes in 'coordinates' or separate
                    # For simplicity, we assume we might lack lat/lon or need to lookup
                    coords = data.get('coordinates', {})
                    lat = coords.get('latitude', 0)
                    lon = coords.get('longitude', 0)
                    
                    date_dict = data.get('date', {})
                    timestamp = date_dict.get('utc')
                    
                    # 1. Dimension
                    db_loc_id = self._get_or_create_location(conn, f"{city}-{country}", city, country, lat, lon, source)
                    
                    # 2. Fact - Pivot measurements
                    measurements = {m['parameter']: m['value'] for m in data.get('measurements', [])}
                    
                    fact_query = text("""
                        INSERT INTO silver.fact_air_quality
                        (location_id, timestamp, pm25, pm10, no2, so2, o3, co)
                        VALUES (:loc_id, :ts, :pm25, :pm10, :no2, :so2, :o3, :co)
                        ON CONFLICT (location_id, timestamp) DO NOTHING
                    """)
                    conn.execute(fact_query, {
                        "loc_id": db_loc_id,
                        "ts": timestamp,
                        "pm25": measurements.get('pm25'),
                        "pm10": measurements.get('pm10'),
                        "no2": measurements.get('no2'),
                        "so2": measurements.get('so2'),
                        "o3": measurements.get('o3'),
                        "co": measurements.get('co')
                    })
                    conn.commit()
                except Exception as e:
                    logger.error(f"Error inserting AQ row: {e}")
                    conn.rollback()

if __name__ == "__main__":
    import time
    cleaner = SilverCleaner()
    cleaner.process_weather()
    cleaner.process_aq()
