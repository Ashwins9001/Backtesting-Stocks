import os

def save_parquet(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path)

def load_parquet(path):
    return pd.read_parquet(path)

def save_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path)