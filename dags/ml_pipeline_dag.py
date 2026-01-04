from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'ecostream',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 1. Feature Generation DAG
with DAG(
    'ml_feature_generation',
    default_args=default_args,
    description='Generate Gold features from Silver data',
    schedule_interval='@hourly',
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'features'],
) as feature_dag:

    generate_features = BashOperator(
        task_id='generate_pm25_features',
        bash_command='python -m src.ml.features', # Assumes PYTHONPATH is set in container
        cwd='/opt/airflow', # Working directory where src is visible? PYTHONPATH includes /opt/airflow/src
    )

# 2. Model Training DAG
with DAG(
    'ml_model_training',
    default_args=default_args,
    description='Train XGBoost model on Gold features',
    schedule_interval='@weekly', # Train once a week
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'training'],
) as training_dag:

    train_model = BashOperator(
        task_id='train_xgboost_model',
        bash_command='python -m src.ml.train',
        cwd='/opt/airflow',
    )

# 3. Prediction DAG
with DAG(
    'ml_prediction',
    default_args=default_args,
    description='Generate 24h forecasts',
    schedule_interval='@hourly',
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'prediction'],
) as prediction_dag:
    
    # Ideally should wait for features?
    # For now, just run.
    generate_predictions = BashOperator(
        task_id='predict_next_24h',
        bash_command='python -m src.ml.predict',
        cwd='/opt/airflow',
    )
