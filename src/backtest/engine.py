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
        if 'volume' not in self.data.columns:
            self.data['volume'] = 1

    def run(self):
        df = self.data.copy()

        # --- Generate signals ---
        signals = self.strategy.generate_signals(df)
        signals = signals.reindex(df.index).fillna(0)

        # --- Remove lookahead bias ---
        df['signal'] = signals.shift(1).fillna(0)

        prices = df['price'].to_numpy()
        signal_values = df['signal'].to_numpy()

        cash = self.initial_cash
        position = 0  # INTEGER shares only
        equity = []
        shares_owned = []

        for i in range(len(prices)):
            price = prices[i]
            signal = signal_values[i]

            # --- Current total equity ---
            total_equity = cash + position * price

            # --- Target allocation ---
            target_value = total_equity * signal

            # --- Convert to INTEGER shares ---
            target_shares = int(np.floor(target_value / price))

            # --- Compute trade ---
            shares_to_trade = target_shares - position

            # --------------------------
            # BUY LOGIC (cannot exceed cash)
            # --------------------------
            if shares_to_trade > 0:
                max_affordable = int(np.floor(cash / price))
                shares_to_trade = min(shares_to_trade, max_affordable)

            # --------------------------
            # SELL LOGIC (cannot sell more than owned)
            # --------------------------
            elif shares_to_trade < 0:
                shares_to_trade = max(shares_to_trade, -position)

            trade_cost = shares_to_trade * price

            # --- Apply fees ---
            fee_cost = abs(trade_cost) * self.fee

            # --- Update cash & position ---
            cash -= trade_cost + fee_cost
            position += shares_to_trade

            # --- Track ---
            current_equity = cash + position * price
            equity.append(current_equity)
            shares_owned.append(position)

        # --- Save columns ---
        df['position'] = signal_values     # still fractional signal
        df['shares'] = shares_owned        # INTEGER shares now
        df['equity'] = equity

        # --- Returns ---
        df['returns'] = df['price'].pct_change().fillna(0)
        df['strategy_returns'] = df['equity'].pct_change().fillna(0)

        # --- Metrics ---
        self._compute_metrics(df)

        self.data = df
        return df

    def _compute_metrics(self, df):
        returns = df['strategy_returns']

        sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(252)

        total_periods = len(df)
        years = total_periods / 252
        cagr = (df['equity'].iloc[-1] / df['equity'].iloc[0]) ** (1 / years) - 1

        equity = df['equity']
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min()

        wins = (returns > 0).sum()
        losses = (returns < 0).sum()
        win_loss_ratio = wins / max(losses, 1)

        var_95 = np.percentile(returns, 5)

        self.metrics = {
            "sharpe": sharpe,
            "cagr": cagr,
            "max_drawdown": max_drawdown,
            "win_loss_ratio": win_loss_ratio,
            "VaR_95": var_95
        }