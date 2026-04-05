class BacktestEngine:
    def __init__(self, data, strategy, initial_cash=10000):
        self.data = data.copy()  # work on a copy
        self.strategy = strategy
        self.initial_cash = initial_cash

    def run(self):
        signals = self.strategy.generate_signals(self.data)  # Series of 0/1

        # Initialize columns
        self.data['position'] = 0.0
        self.data['cash'] = self.initial_cash
        self.data['equity'] = self.initial_cash

        # Vectorized execution logic
        bought = False
        cash = self.initial_cash
        position = 0.0
        equity = []

        prices = self.data['price'].to_numpy()
        signals = signals.to_numpy()

        for price, signal in zip(prices, signals):
            if signal == 1 and cash > 0:
                position = cash / price
                cash = 0
            elif signal == 0 and position > 0:
                cash = position * price
                position = 0
            equity.append(cash + position * price)

        self.data['equity'] = equity
        self.data['equity'] = self.data['equity'].apply(lambda x: x[0] if isinstance(x, list) else x)
        
        return self.data