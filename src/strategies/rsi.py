class RSIStrategy:
    def __init__(self, rsi_window=14, vol_window=20):
        self.rsi_window = rsi_window
        self.vol_window = vol_window

    def generate_signals(self, data):
        # --- RSI computation (lookback only)
        delta = data['price'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(self.rsi_window).mean().shift(1)
        avg_loss = loss.rolling(self.rsi_window).mean().shift(1)

        rs = avg_gain / (avg_loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))

        base_signal = (rsi < 30).astype(float)  # buy when oversold

        # --- Lookahead-safe volume scaling
        vol_norm = (data['volume'] / (data['volume'].rolling(self.vol_window).max().shift(1) + 1e-9))
        vol_norm = vol_norm.clip(0,1)

        return base_signal * vol_norm