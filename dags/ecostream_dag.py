from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add src to path if not already (though we set PYTHONPATH in docker-compose)
sys.path.append('/opt/airflow/src')

try:
    from src.ingestion.producer import DataProducer
    from src.processing.silver_cleaner import SilverCleaner
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback to prevent DAG import errors if dependencies aren't ready yet
    DataProducer = None
    SilverCleaner = None

default_args = {
    'owner': 'ecostream',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_ingestion():
    if DataProducer:
        producer = DataProducer()
        producer.produce_data()
    else:
        raise ImportError("DataProducer application code not found")

def run_silver_cleaner():
    if SilverCleaner:
        cleaner = SilverCleaner()
        print("Processing Weather Data...")
        cleaner.process_weather()
        print("Processing AQ Data...")
        cleaner.process_aq()
    else:
        raise ImportError("SilverCleaner application code not found")

with DAG(
    'ecostream_pipeline',
    default_args=default_args,
    description='EcoStream AI Ingestion and Processing Pipeline',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ecostream', 'bronze', 'silver'],
) as dag:

    # Task 1: Fetch data from APIs and push to Redpanda (Kafka)
    # Note: In a real "continuous" streaming world, this might be a separate service.
    # Here we schedule it to run every hour to simulate periodic updates.
    ingest_task = PythonOperator(
        task_id='ingest_api_data',
        python_callable=run_ingestion,
    )

    # Task 2: Process Bronze Parquet files into Silver Postgres
    # This runs after ingestion. Note that Bronze Writer (Kafka consumer) runs continuously in 'bronze-worker' service.
    # So 'ingest_task' produces data -> Kafka -> (Worker) -> Parquet.
    # We wait a bit or just run the cleaner. The cleaner picks up whatever Parquet files exist.
    process_silver_task = PythonOperator(
        task_id='process_silver_layer',
        python_callable=run_silver_cleaner,
    )

    ingest_task >> process_silver_task
