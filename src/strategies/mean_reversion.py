class MeanReversionStrategy:
    def __init__(self, window=20):
        self.window = window

    def generate_signals(self, data):
        # --- Lookback mean
        ma = data['price'].rolling(self.window).mean().shift(1)

        # --- Base mean-reversion signal
        base_signal = (data['price'] < ma).astype(float)

        # --- Lookahead-safe volume scaling
        vol_norm = (data['volume'] / (data['volume'].rolling(self.window).max().shift(1) + 1e-9))
        vol_norm = vol_norm.clip(0,1)

        return base_signal * vol_norm