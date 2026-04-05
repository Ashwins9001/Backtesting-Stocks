import os
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from backtest.engine import BacktestEngine
from strategies.mean_reversion import MeanReversionStrategy
from strategies.rsi import RSIStrategy
from strategies.breakout import BreakoutStrategy
from plot.plot import plot_backtest_results

# --------------------------
# Helper functions
# --------------------------
def save_metrics(metrics: dict, base_path: str, name: str):
    """Save metrics as CSV and Parquet"""
    os.makedirs(base_path, exist_ok=True)
    df = pd.DataFrame([metrics])
    df.to_parquet(f"{base_path}/{name}.parquet")
    df.to_csv(f"{base_path}/{name}.csv", index=False)

# --------------------------
# Task functions
# --------------------------
def run_backtest(ti=None):
    df = pd.read_parquet("/opt/airflow/data/raw/aapl.parquet")

    if 'close_price' in df.columns:
        df.rename(columns={'close_price': 'price'}, inplace=True)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

    strategies = [
        ("mean_reversion", MeanReversionStrategy()),
        ("rsi", RSIStrategy()),
        ("breakout", BreakoutStrategy()),
    ]

    all_results = {}
    all_metrics = {}

    for name, strat in strategies:
        engine = BacktestEngine(df, strat, initial_cash=10000, fee=0.001)
        results = engine.run()

        # Save results to disk
        data_path = f"/opt/airflow/data/results/data/{name}"
        os.makedirs(data_path, exist_ok=True)
        results.to_parquet(f"{data_path}/aapl.parquet")
        results.to_csv(f"{data_path}/aapl.csv", index=True)

        # Store for metrics & plotting
        all_results[name] = results
        all_metrics[name] = engine.metrics

    # Push to XCom
    if ti:
        ti.xcom_push(key='all_results', value=all_results)
        ti.xcom_push(key='all_metrics', value=all_metrics)

def save_backtest_metrics(ti=None):
    metrics_path = "/opt/airflow/data/results/metrics"
    os.makedirs(metrics_path, exist_ok=True)

    all_metrics = ti.xcom_pull(task_ids='run_backtest', key='all_metrics')
    for name, metrics in all_metrics.items():
        save_metrics(metrics, metrics_path, f"aapl_{name}")
        print(f"Saved metrics for {name}: {metrics}")

def plot_backtest(ti=None):
    all_results = ti.xcom_pull(task_ids='run_backtest', key='all_results')
    for name, df in all_results.items():
        plots_path = f"/opt/airflow/data/results/plots/{name}"
        plot_backtest_results(df, plots_path, name)
        print(f"Plotted results for {name}")

# --------------------------
# DAG definition
# --------------------------
with DAG(
    dag_id="backtest_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # Airflow 3.x uses 'schedule'
    catchup=False,
) as dag:

    backtest_task = PythonOperator(
        task_id="run_backtest",
        python_callable=run_backtest
    )

    metrics_task = PythonOperator(
        task_id="save_metrics",
        python_callable=save_backtest_metrics
    )

    plot_task = PythonOperator(
        task_id="plot_results",
        python_callable=plot_backtest
    )

    # Task dependencies
    backtest_task >> metrics_task >> plot_task