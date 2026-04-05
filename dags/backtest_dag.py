from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.mean_reversion import MeanReversionStrategy
from strategies.rsi import RSIStrategy
from strategies.momentum import MomentumStrategy

def run_backtest():
    df = pd.read_parquet("/opt/airflow/data/raw/aapl.parquet")

    strategies = [MeanReversionStrategy(), RSIStrategy(), MomentumStrategy()]
    for idx, strat in enumerate(strategies):
        engine = BacktestEngine(df, strat)
        results = engine.run()
        print(engine.metrics)
        results.to_parquet("/opt/airflow/data/results/aapl_backtest_{0}.parquet".format(str(idx)))
        results.to_csv("/opt/airflow/data/results/aapl_backtest_{0}.csv".format(str(idx)))

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