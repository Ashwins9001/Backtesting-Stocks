class BreakoutStrategy:
    def __init__(self, window=20):
        self.window = window

    def generate_signals(self, data):
        # --- Lookback high/low
        high = data['price'].rolling(self.window).max().shift(1)
        low = data['price'].rolling(self.window).min().shift(1)

        # --- Base breakout signal
        base_signal = (data['price'] > high).astype(float)

        # --- Lookahead-safe volume scaling (fractional)
        vol_norm = (data['volume'] / (data['volume'].rolling(self.window).max().shift(1) + 1e-9))
        vol_norm = vol_norm.clip(0,1)

        return base_signal * vol_norm