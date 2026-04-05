class BreakoutStrategy:
    def generate_signals(self, data):
        high = data['price'].rolling(20).max()
        low = data['price'].rolling(20).min()
        return (data['price'] > high.shift(1)).astype(int)  # breakout buy