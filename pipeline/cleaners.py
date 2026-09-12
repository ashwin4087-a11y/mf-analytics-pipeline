import warnings
import pandas as pd
from .config import KNOWN_TRANSACTION_TYPES

def _strip_strings(df):
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()
    return df

# launch_date in the funds master legitimately predates 2000 (e.g. HDFC 1996)
_TIMESERIES_DATE_COLS = {"date", "month", "transaction_date", "portfolio_date"}

def _validate_dates(df, name):
    for col in _TIMESERIES_DATE_COLS:
        if col not in df.columns:
            continue
        dates = pd.to_datetime(df[col], errors="coerce")
        if dates.notna().any():
            if dates.min() < pd.Timestamp("2000-01-01"):
                raise ValueError(f"{name}.{col}: date before 2000 detected")
            if dates.max() > pd.Timestamp.today().normalize() + pd.Timedelta(days=1):
                raise ValueError(f"{name}.{col}: future date detected")

def _validate_keys(df, name):
    keys = {
        "funds": ["amfi_code"],
        "nav": ["amfi_code", "date"],
        "performance": ["amfi_code"],
        "transactions": ["investor_id", "transaction_date", "amfi_code"],
    }.get(name)
    if keys:
        for col in keys:
            if col not in df.columns or df[col].isna().any():
                raise ValueError(f"{name}: invalid key column {col}")

def clean_funds(df):
    df = _strip_strings(df)
    if not df["amfi_code"].is_unique:
        raise ValueError("funds: amfi_code must be unique")
    if not df["expense_ratio_pct"].between(0, 5).all():
        raise ValueError("funds: expense_ratio_pct outside [0, 5]")
    if not df["exit_load_pct"].between(0, 3).all():
        raise ValueError("funds: exit_load_pct outside [0, 3]")
    return df

def clean_nav(df):
    df = _strip_strings(df)
    before = len(df)
    df = df.drop_duplicates(["amfi_code", "date"]).sort_values(["amfi_code", "date"])
    print(f"nav: {before:,} -> {len(df):,} rows")
    gaps = df.groupby("amfi_code")["date"].diff().dt.days
    if (gaps > 10).any():
        warnings.warn("nav: one or more gaps exceed 10 calendar days")
    return df.reset_index(drop=True)

def clean_sip(df):
    df = _strip_strings(df).sort_values("month").copy()
    df["yoy_growth_pct"] = df["yoy_growth_pct"].fillna(
        (df["sip_inflow_crore"] / df["sip_inflow_crore"].shift(12) - 1) * 100
    )
    return df

def clean_transactions(df):
    df = _strip_strings(df)
    if not (df["amount_inr"] > 0).all():
        raise ValueError("transactions: amount_inr must be > 0")
    bad = set(df["transaction_type"].dropna().unique()) - KNOWN_TRANSACTION_TYPES
    if bad:
        raise ValueError(f"transactions: unknown transaction types: {sorted(bad)}")
    return df

def clean_holdings(df):
    df = _strip_strings(df)
    sums = df.groupby("amfi_code")["weight_pct"].sum()
    bad = sums[(sums < 99) | (sums > 101)]
    if not bad.empty:
        warnings.warn(f"holdings: weights outside 99-101% for {len(bad)} funds")
    return df

def clean_benchmark(df):
    return _strip_strings(df).sort_values(["date", "index_name"]).reset_index(drop=True)

def clean_all(raw):
    funcs = {
        "funds": clean_funds,
        "nav": clean_nav,
        "sip": clean_sip,
        "transactions": clean_transactions,
        "holdings": clean_holdings,
        "benchmark": clean_benchmark,
    }
    clean = {}
    for name, df in raw.items():
        before = len(df)
        clean[name] = funcs.get(name, lambda x: _strip_strings(x))(df.copy())
        _validate_dates(clean[name], name)
        _validate_keys(clean[name], name)
        print(f"{name}: {before:,} -> {len(clean[name]):,} rows")
    return clean
