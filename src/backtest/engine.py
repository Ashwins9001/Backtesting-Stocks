import pandas as pd
import numpy as np


class BacktestEngine:
    def __init__(self, data, strategy, initial_cash=10000, fee=0.0):
        self.data = data.copy()
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.fee = fee
        self.metrics = {}

        if 'price' not in self.data.columns:
            raise ValueError("Data must contain a 'price' column")

    def run(self):
        df = self.data

        # --- Generate signals ---
        signals = self.strategy.generate_signals(df)

        # Align + clean
        signals = signals.reindex(df.index).fillna(0)

        # --- Remove lookahead bias ---
        df['signal'] = signals.shift(1).fillna(0)

        # Convert to position (0 or 1)
        df['position'] = df['signal']

        # --- Market returns ---
        df['returns'] = df['price'].pct_change().fillna(0)

        # --- Strategy returns ---
        df['strategy_returns'] = df['position'] * df['returns']

        # --- Transaction costs ---
        trades = df['position'].diff().abs().fillna(0)
        df['strategy_returns'] -= trades * self.fee

        # --- Equity curve ---
        df['equity'] = self.initial_cash * (1 + df['strategy_returns']).cumprod()

        # --- Compute metrics ---
        self._compute_metrics(df)

        self.data = df
        return df

    def _compute_metrics(self, df):
        returns = df['strategy_returns']

        # Sharpe ratio (annualized)
        sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(252)

        # CAGR
        total_periods = len(df)
        years = total_periods / 252  # assumes daily data
        cagr = (df['equity'].iloc[-1] / df['equity'].iloc[0]) ** (1 / years) - 1

        # Max drawdown
        equity = df['equity']
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min()

        # Win/loss ratio
        wins = (returns > 0).sum()
        losses = (returns < 0).sum()
        win_loss_ratio = wins / max(losses, 1)

        # Store metrics cleanly
        self.metrics = {
            "sharpe": sharpe,
            "cagr": cagr,
            "max_drawdown": max_drawdown,
            "win_loss_ratio": win_loss_ratio,
        }