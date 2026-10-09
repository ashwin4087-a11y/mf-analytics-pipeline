"""
Inspect all 12 source Excel files - report sheet names, header rows, column names, and row counts.
This drives the ETL implementation.
"""
import pandas as pd
import os

DATA_DIR = 'data'

files = [
    ('companies.xlsx',        'companies',       False),
    ('balancesheet.xlsx',     'balancesheet',    True),
    ('profitandloss.xlsx',    'profitandloss',   True),
    ('cashflow.xlsx',         'cashflow',        True),
    ('analysis.xlsx',         'analysis',        True),
    ('documents.xlsx',        'documents',       False),
    ('prosandcons.xlsx',      'prosandcons',     False),
    ('sectors.xlsx',          'sectors',         False),
    ('stock_prices.xlsx',     'stock_prices',    False),
    ('market_cap.xlsx',       'market_cap',      False),
    ('financial_ratios.xlsx', 'financial_ratios', True),
    ('peer_groups.xlsx',      'peer_groups',     False),
]

for fname, tbl, is_core in files:
    path = os.path.join(DATA_DIR, fname)
    # Check with glob for UUID-prefixed filenames
    actual = None
    for f in os.listdir(DATA_DIR):
        if f.endswith(fname):
            actual = os.path.join(DATA_DIR, f)
            break
    if not actual:
        print(f"[MISSING] {fname}")
        continue

    try:
        xl = pd.ExcelFile(actual)
        sheets = xl.sheet_names
        print(f"=== {fname} (table={tbl}, is_core={is_core}) ===")
        print(f"  File : {os.path.basename(actual)}")
        print(f"  Sheets: {sheets}")
        for sheet in sheets[:2]:  # inspect first 2 sheets
            try:
                # Try header=0 first to see raw layout
                df_raw = pd.read_excel(actual, sheet_name=sheet, header=0, nrows=3)
                df_h1  = pd.read_excel(actual, sheet_name=sheet, header=1, nrows=3)
                df_full = pd.read_excel(actual, sheet_name=sheet, header=(1 if is_core else 0))

                print(f"  Sheet '{sheet}':")
                print(f"    header=0 cols ({len(df_raw.columns)}): {list(df_raw.columns)[:8]}")
                print(f"    header=1 cols ({len(df_h1.columns)}): {list(df_h1.columns)[:8]}")
                print(f"    Rows (header={'1' if is_core else '0'}): {len(df_full)}")
            except Exception as e:
                print(f"    ERROR reading sheet '{sheet}': {e}")
        print()
    except Exception as e:
        print(f"[ERROR] {fname}: {e}\n")
