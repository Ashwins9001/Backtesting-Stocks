import matplotlib.pyplot as plt
import os
import pandas as pd

def plot_backtest_results(df: pd.DataFrame, output_path: str, strategy_name: str):
    """
    Plot equity curve and strategy returns.
    """
    os.makedirs(output_path, exist_ok=True)

    # Equity curve
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['equity'], label='Equity Curve', color='blue')
    plt.title(f"{strategy_name} Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f"{strategy_name}_equity.png"))
    plt.close()

    # Optional: cumulative strategy returns
    plt.figure(figsize=(12, 6))
    cumulative_returns = (1 + df['strategy_returns']).cumprod() - 1
    plt.plot(df.index, cumulative_returns, label='Cumulative Returns', color='green')
    plt.title(f"{strategy_name} Cumulative Returns")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f"{strategy_name}_cumulative_returns.png"))
    plt.close()