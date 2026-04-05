import yfinance as yf
import pandas as pd

def fetch_prices(symbol="AAPL", start="2020-01-01"):
    # --- Download data ---
    data = yf.download(symbol, start=start, progress=False)

    # --- Keep only Close price ---
    if 'Close' not in data.columns:
        raise ValueError("Downloaded data does not contain 'Close' column")
    
    df = data

    # --- Flatten MultiIndex columns if needed ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

    # --- Extract needed columns ---
    # Column names after flattening will look like: 'Close_AAPL', 'Volume_AAPL'
    close_col = [c for c in df.columns if c.lower().startswith('close')][0]
    volume_col = [c for c in df.columns if c.lower().startswith('volume')][0]

    df_clean = df[[close_col, volume_col]].copy()
    df_clean.rename(columns={close_col: 'close_price', volume_col: 'volume'}, inplace=True)

    # --- Ensure index is datetime and reset to 'date' column ---
    df_clean.index = pd.to_datetime(df_clean.index)
    df_clean.reset_index(inplace=True)
    df_clean.rename(columns={'Date': 'date'}, inplace=True)

    # --- Compute daily returns ---
    df_clean['returns'] = df_clean['close_price'].pct_change().fillna(0)

    print(df_clean.head())

    return df_clean