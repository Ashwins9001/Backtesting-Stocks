class MeanReversionStrategy:
    def generate_signals(self, data):
        ma = data['price'].rolling(20).mean()
        return (data['price'] < ma).astype(int)