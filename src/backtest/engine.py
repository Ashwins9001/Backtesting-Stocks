import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, data, strategy, initial_cash=10000):
        self.data = data.copy()  # work on a copy
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.metrics = {}  # store performance metrics

    def run(self):
        signals = self.strategy.generate_signals(self.data)  # Series of 0/1

        # Initialize columns
        self.data['position'] = 0.0
        self.data['cash'] = self.initial_cash
        self.data['equity'] = self.initial_cash

        cash = self.initial_cash
        position = 0.0
        equity = []

        prices = self.data['price'].to_numpy()
        signals = signals.to_numpy()

        # Loop through prices and signals
        for price, signal in zip(prices, signals):
            if signal == 1 and cash > 0:
                position = cash / price
                cash = 0
            elif signal == 0 and position > 0:
                cash = position * price
                position = 0
            equity.append(cash + position * price)

        self.data['equity'] = equity  # scalar values only

        # --- Compute performance metrics ---
        # Daily returns
        self.data['returns'] = self.data['equity'].pct_change().fillna(0)

        # Sharpe ratio (annualized)
        daily_returns = self.data['returns']
        self.metrics['sharpe'] = daily_returns.mean() / (daily_returns.std() + 1e-9) * np.sqrt(252)

        # CAGR
        start_val = self.data['equity'].iloc[0]
        end_val = self.data['equity'].iloc[-1]
        total_days = (self.data.index[-1] - self.data.index[0]).days if isinstance(self.data.index[0], pd.Timestamp) else len(self.data)
        total_years = max(total_days / 365.25, 1e-9)
        self.metrics['cagr'] = (end_val / start_val) ** (1 / total_years) - 1

        # Win/loss ratio
        wins = (daily_returns > 0).sum()
        losses = (daily_returns < 0).sum()
        self.metrics['win_loss_ratio'] = wins / max(losses, 1)

        # RSI
        delta = self.data['price'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        roll_gain = gain.rolling(14).mean()
        roll_loss = loss.rolling(14).mean()
        rs = roll_gain / (roll_loss + 1e-9)
        self.data['RSI'] = 100 - (100 / (1 + rs))

        return self.data