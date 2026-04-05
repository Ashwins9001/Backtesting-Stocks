import yfinance as yf
import pandas as pd

def fetch_prices(symbol="AAPL", start="2020-01-01"):
    data = yf.download(symbol, start=start)
    data = data[['Close']]
    data.rename(columns={'Close': 'price'}, inplace=True)

    data['returns'] = data['price'].pct_change()
    return data