from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.mean_reversion import MeanReversionStrategy

def run_backtest():
    df = pd.read_parquet("/opt/airflow/data/raw/aapl.parquet")

    strategy = MeanReversionStrategy()
    engine = BacktestEngine(df, strategy)

    results = engine.run()
    results.to_parquet("/opt/airflow/data/results/aapl_backtest.parquet")
    results.to_csv("/opt/airflow/data/results/aapl_backtest.csv")

with DAG(
    dag_id="backtest_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # <- updated from schedule_interval
    catchup=False,
) as dag:

    backtest_task = PythonOperator(
        task_id="run_backtest",
        python_callable=run_backtest
    )