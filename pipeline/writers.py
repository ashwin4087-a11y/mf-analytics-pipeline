from .config import PROCESSED_PATH
import pandas as pd

def _write_one(name, df):
    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
    csv_path = PROCESSED_PATH / f"{name}.csv"
    parquet_path = PROCESSED_PATH / f"{name}.parquet"

    df.to_csv(csv_path, index=False)

    try:
        df.to_parquet(parquet_path, index=False)
        parquet = f"{parquet_path.stat().st_size / 1024:.1f} KB"
    except ImportError:
        parquet = "NOT WRITTEN (install pyarrow)"

    return {
        "table": name,
        "rows": len(df),
        "columns": len(df.columns),
        "csv_size": f"{csv_path.stat().st_size / 1024:.1f} KB",
        "parquet_size": parquet,
    }

def write_all(data):
    results = [_write_one(name, df) for name, df in data.items()]
    print("\n" + "=" * 78)
    print("PROCESSED DATASET SUMMARY")
    print("=" * 78)
    print(pd.DataFrame(results).to_string(index=False))
