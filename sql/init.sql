-- Create a separate user and database for the application if we want to separate from Airflow metadata
-- However, for simplicity in this dev environment, we can use the same postgres instance.
-- We will create a comprehensive setup here.

-- Connect to the default database to create the application DB
-- Note: The container starts with user 'airflow' and db 'airflow'.
-- We will create the 'ecostream_db' and schemas inside it, OR just use 'airflow' db for now.
-- Better to separate.

CREATE USER ecostream WITH PASSWORD 'ecostream';
CREATE DATABASE ecostream_db OWNER ecostream;

\connect ecostream_db;

-- Schemas for Medallion Architecture
CREATE SCHEMA IF NOT EXISTS bronze; -- Raw Metadata
CREATE SCHEMA IF NOT EXISTS silver; -- Cleaned Data
CREATE SCHEMA IF NOT EXISTS gold;   -- Analytics

-- Grant usage to ecostream user
GRANT ALL PRIVILEGES ON DATABASE ecostream_db TO ecostream;
GRANT ALL PRIVILEGES ON SCHEMA bronze TO ecostream;
GRANT ALL PRIVILEGES ON SCHEMA silver TO ecostream;
GRANT ALL PRIVILEGES ON SCHEMA gold TO ecostream;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bronze TO ecostream;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA silver TO ecostream;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gold TO ecostream;

-- ----------------------------------------
-- Silver Layer Tables
-- ----------------------------------------

-- Dimension: Location/Station
CREATE TABLE IF NOT EXISTS silver.dim_location (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    country VARCHAR(10),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    source_name VARCHAR(100),
    UNIQUE(city, country, source_name)
);

-- Fact: Air Quality
CREATE TABLE IF NOT EXISTS silver.fact_air_quality (
    fact_id SERIAL PRIMARY KEY,
    location_id INT REFERENCES silver.dim_location(location_id),
    timestamp TIMESTAMP,
    pm25 DECIMAL(10, 2), -- PM 2.5
    pm10 DECIMAL(10, 2), -- PM 10
    no2 DECIMAL(10, 2),  -- Nitrogen Dioxide
    so2 DECIMAL(10, 2),  -- Sulfur Dioxide
    o3 DECIMAL(10, 2),   -- Ozone
    co DECIMAL(10, 2),   -- Carbon Monoxide
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, timestamp)
);

-- Fact: Weather
CREATE TABLE IF NOT EXISTS silver.fact_weather (
    fact_id SERIAL PRIMARY KEY,
    location_id INT REFERENCES silver.dim_location(location_id),
    timestamp TIMESTAMP,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    pressure DECIMAL(8, 2),
    wind_speed DECIMAL(5, 2),
    wind_deg INT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, timestamp)
);
