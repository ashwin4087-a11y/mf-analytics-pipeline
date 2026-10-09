"""
Deep inspect: get ALL columns, full row counts, sample data.
"""
import pandas as pd
import os

DATA_DIR = 'data'

files_config = {
    'companies.xlsx':        {'header': 1},
    'balancesheet.xlsx':     {'header': 1},
    'profitandloss.xlsx':    {'header': 1},
    'cashflow.xlsx':         {'header': 1},
    'analysis.xlsx':         {'header': 1},
    'documents.xlsx':        {'header': 1},
    'prosandcons.xlsx':      {'header': 1},
    'sectors.xlsx':          {'header': 0},
    'stock_prices.xlsx':     {'header': 0},
    'market_cap.xlsx':       {'header': 0},
    'financial_ratios.xlsx': {'header': 0},
    'peer_groups.xlsx':      {'header': 0},
}

for fname, cfg in files_config.items():
    actual = None
    for f in os.listdir(DATA_DIR):
        if f.endswith(fname):
            actual = os.path.join(DATA_DIR, f)
            break
    if not actual:
        print(f"[MISSING] {fname}")
        continue

    xl = pd.ExcelFile(actual)
    sheet = xl.sheet_names[0]
    df = pd.read_excel(actual, sheet_name=sheet, header=cfg['header'])
    print(f"=== {fname} (header={cfg['header']}) ===")
    print(f"  Rows: {len(df)}")
    print(f"  Cols ({len(df.columns)}): {list(df.columns)}")
    # sample first 2 rows
    for _, row in df.head(2).iterrows():
        print(f"  Sample: {dict(list(row.items())[:6])}")
    print()
