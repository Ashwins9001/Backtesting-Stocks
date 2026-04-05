from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data.fetch import fetch_prices
from data.storage import save_parquet

def fetch_and_store():
    df = fetch_prices("AAPL")
    save_parquet(df, "/opt/airflow/data/raw/aapl.parquet")

with DAG(
    dag_id="market_data_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",  # <- changed from schedule_interval
    catchup=False,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_data",
        python_callable=fetch_and_store
    )