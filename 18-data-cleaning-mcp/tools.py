import pandas as pd
import os

def load_csv(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path)

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.strip().lower() for col in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.dropna()
    return df

def summarize_dataframe(df: pd.DataFrame) -> dict:
    summary = df.describe(include='all').to_dict()
    null_counts = df.isnull().sum().to_dict()
    return {
        "summary": summary,
        "null_counts": null_counts
    }

def export_dataframe(df: pd.DataFrame, path: str) -> str:
    df.to_csv(path, index=False)
    return f"Cleaned data saved to: {path}"
