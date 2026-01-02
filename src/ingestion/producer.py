import os
import json
import time
import random
import requests
import logging
from datetime import datetime
from src.common.kafka_utils import KafkaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENAQ_API_URL = "https://api.openaq.org/v2/measurements"
# Default locations (London, New York, Delhi, San Francisco)
LOCATIONS = [
    {"city": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278},
    {"city": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060},
    {"city": "Delhi", "country": "IN", "lat": 28.6139, "lon": 77.2090},
    {"city": "San Francisco", "country": "US", "lat": 37.7749, "lon": -122.4194}
]

class DataProducer:
    def __init__(self):
        self.producer = KafkaClient.get_producer()

    def fetch_openaq(self, city, country):
        """Fetch Air Quality data from OpenAQ (Public API)"""
        try:
            params = {
                "city": city,
                "country": country,
                "limit": 5,
                "order_by": "date",
                "sort": "desc"
            }
            # Note: OpenAQ API structure changes often, simpler to use mock if fails or for demo resilience
            response = requests.get(OPENAQ_API_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.warning(f"OpenAQ API failed for {city}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching OpenAQ for {city}: {e}")
            return []

    def fetch_weather(self, lat, lon):
        """Fetch Weather data from OpenWeatherMap"""
        if not OPENWEATHER_API_KEY:
            logger.warning("No OpenWeatherMap API Key found. Generating synthetic data.")
            return self.generate_synthetic_weather(lat, lon)
        
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Weather API failed: {response.status_code}")
                return self.generate_synthetic_weather(lat, lon)
        except Exception as e:
            logger.error(f"Error fetching Weather: {e}")
            return self.generate_synthetic_weather(lat, lon)

    def generate_synthetic_weather(self, lat, lon):
        """Generate mock weather data for testing/demo"""
        return {
            "coord": {"lon": lon, "lat": lat},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "main": {
                "temp": round(random.uniform(10, 35), 2),
                "pressure": 1012,
                "humidity": random.randint(30, 90)
            },
            "wind": {"speed": round(random.uniform(0, 15), 2), "deg": random.randint(0, 360)},
            "dt": int(time.time()),
            "name": "Synthetic City"
        }
    
    def generate_synthetic_aq(self, city, country):
        """Generate mock AQ data"""
        measurements = []
        for parameter in ['pm25', 'pm10', 'no2', 'so2', 'o3', 'co']:
            measurements.append({
                "parameter": parameter,
                "value": round(random.uniform(0, 100), 2),
                "unit": "µg/m³"
            })
        
        return [{
            "location": f"{city}-Station",
            "city": city,
            "country": country,
            "date": {"utc": datetime.utcnow().isoformat()},
            "measurements": measurements
        }]

    def produce_data(self):
        for loc in LOCATIONS:
            # 1. Weather Data
            weather_data = self.fetch_weather(loc['lat'], loc['lon'])
            weather_payload = {
                "source": "openweather",
                "location_id": f"{loc['city']}-{loc['country']}",
                "data": weather_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.producer.send('weather-raw', weather_payload)
            logger.info(f"Sent weather data for {loc['city']}")

            # 2. Air Quality Data
            aq_results = self.fetch_openaq(loc['city'], loc['country'])
            if not aq_results:
                 aq_results = self.generate_synthetic_aq(loc['city'], loc['country'])
            
            for result in aq_results:
                aq_payload = {
                    "source": "openaq",
                    "location_id": f"{loc['city']}-{loc['country']}",
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.producer.send('airquality-raw', aq_payload)
                logger.info(f"Sent AQ data for {loc['city']}")
        
        self.producer.flush()

if __name__ == "__main__":
    producer = DataProducer()
    producer.produce_data()
