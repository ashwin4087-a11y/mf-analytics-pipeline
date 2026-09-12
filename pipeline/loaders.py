import pandas as pd
from .config import RAW_DATA_PATH, RAW_FILES

DATE_COLUMNS = {
    "transactions": ["transaction_date"],
    "holdings": ["portfolio_date"],
    "benchmark": ["date"],
    "funds": ["launch_date"],
    "nav": ["date"],
    "aum": ["date"],
    "sip": ["month"],
    "category_inflows": ["month"],
    "folio": ["month"],
    "performance": [],
}

def _read(name):
    path = RAW_DATA_PATH / RAW_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Missing raw file for '{name}': {path}")
    df = pd.read_csv(path)

    for col in DATE_COLUMNS[name]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="raise")

    if "amfi_code" in df.columns:
        df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="raise").astype("int64")

    return df

def load_all():
    return {name: _read(name) for name in RAW_FILES}
