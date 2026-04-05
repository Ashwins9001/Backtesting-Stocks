import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, data, strategy, initial_cash=10000, fee=0.0):
        """
        data: pd.DataFrame with 'price' and optionally 'volume'
        strategy: strategy object with generate_signals(df) -> 0..1 signals
        initial_cash: starting capital
        fee: proportional transaction fee (e.g., 0.001 = 0.1%)
        """
        self.data = data.copy()
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.fee = fee
        self.metrics = {}

        if 'price' not in self.data.columns:
            raise ValueError("Data must contain a 'price' column")
        if 'volume' not in self.data.columns:
            self.data['volume'] = 1  # default volume if missing

    def run(self):
        df = self.data.copy()

        # --- Generate signals (fractional 0..1) ---
        signals = self.strategy.generate_signals(df)
        signals = signals.reindex(df.index).fillna(0)

        # --- Remove lookahead bias ---
        df['signal'] = signals.shift(1).fillna(0)

        # --- Initialize equity calculation ---
        prices = df['price'].to_numpy()
        signal_values = df['signal'].to_numpy()
        cash = self.initial_cash
        position = 0.0
        equity = []

        for i in range(len(prices)):
            # --- Target position in $ based on fractional signal ---
            target_position_value = self.initial_cash * signal_values[i]
            target_shares = target_position_value / prices[i]

            # --- Shares to buy/sell ---
            shares_to_trade = target_shares - position
            trade_cost = shares_to_trade * prices[i]

            # --- Apply transaction fee and update cash ---
            cash -= trade_cost + abs(trade_cost) * self.fee
            position = target_shares

            # --- Total equity = cash + position value ---
            equity.append(cash + position * prices[i])

        df['position'] = signal_values       # fractional position
        df['equity'] = equity

        # --- Market returns ---
        df['returns'] = df['price'].pct_change().fillna(0)

        # --- Strategy returns (equity curve changes) ---
        df['strategy_returns'] = df['equity'].pct_change().fillna(0)

        # --- Compute metrics ---
        self._compute_metrics(df)

        self.data = df
        return df

    def _compute_metrics(self, df):
        returns = df['strategy_returns']

        # --- Sharpe ratio (annualized) ---
        sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(252)

        # --- CAGR ---
        total_periods = len(df)
        years = total_periods / 252
        cagr = (df['equity'].iloc[-1] / df['equity'].iloc[0]) ** (1 / years) - 1

        # --- Max drawdown ---
        equity = df['equity']
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min()

        # --- Win/loss ratio ---
        wins = (returns > 0).sum()
        losses = (returns < 0).sum()
        win_loss_ratio = wins / max(losses, 1)

        # --- 95% Value at Risk (VaR) ---
        var_95 = np.percentile(returns, 5)

        # --- Store metrics ---
        self.metrics = {
            "sharpe": sharpe,
            "cagr": cagr,
            "max_drawdown": max_drawdown,
            "win_loss_ratio": win_loss_ratio,
            "VaR_95": var_95
        }