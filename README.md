# EcoStream AI

EcoStream AI is a real-time air quality prediction and analytics platform.

## Phase 1: Data Ingestion & Pipeline

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local development)

### Architecture
- **Infratructure**: Docker Compose
- **Event Streaming**: Redpanda (Kafka API)
- **Database**: PostgreSQL (Silver/Gold layers)
- **Storage**: Local Filesystem (Bronze Parquet)
- **Orchestration**: Apache Airflow (LocalExecutor)

### Setup Instructions

1.  **Initialize Infrastructure**
    ```bash
    docker-compose up -d --build
    ```
    This will start:
    - Redpanda (Ports 8081, 8082, 9092, 9644)
    - PostgreSQL (Port 5432)
    - Airflow Webserver (Port 8080) & Scheduler
    - Bronze Worker (Python service for Kafka -> Parquet)

2.  **Access Airflow**
    - URL: `http://localhost:8080`
    - User: `admin`
    - Pass: `admin`

3.  **Trigger Pipeline**
    - Enable the `ecostream_pipeline` DAG using the toggle switch.
    - Manually trigger the DAG to test immediate execution.

4.  **Verify Data**
    - **Bronze**: Check `data/bronze` folder for Parquet files.
    - **Silver**: Connect to Postgres (`localhost:5432`, user `airflow`, pass `airflow`, db `airflow` or `ecostream_db` if configured) and query:
      ```sql
      SELECT * FROM silver.fact_air_quality LIMIT 10;
      SELECT * FROM silver.fact_weather LIMIT 10;
      ```

### Environment Variables
You can create a `.env` file in the root if you want to use real API keys:
```
OPENWEATHER_API_KEY=your_key_here
```
(If not provided, the system generates synthetic mock data for demonstration).

### Project Structure
- `dags/`: Airflow DAGs
- `src/ingestion`: API Fetchers & Kafka Producer
- `src/processing`: Bronze Writer & Silver Cleaner
- `src/common`: Shared utilities
- `sql/`: Database initialization
- `data/`: Local storage for Bronze layer
