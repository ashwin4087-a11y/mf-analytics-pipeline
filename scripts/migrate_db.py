"""
Helper script: inspect backup DB schema and migrate financial_ratios
to the new nifty100.db with the correct schema.
"""
import sqlite3
import pandas as pd
import os

BACKUP_DB = 'data/nifty100_backup.db'
NEW_DB    = 'data/nifty100.db'
SCHEMA    = 'db/schema.sql'

# --- 1. Inspect backup ---
with sqlite3.connect(BACKUP_DB) as conn:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='financial_ratios'"
    ).fetchone()
    print("=== BACKUP financial_ratios schema ===")
    print(row[0] if row else "TABLE NOT FOUND")
    print()

    count_backup = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    print(f"Backup row count: {count_backup}")
    print()

    df = pd.read_sql("SELECT * FROM financial_ratios", conn)
    print(f"Backup columns: {list(df.columns)}")
    print()

# --- 2. Build new DB ---
if os.path.exists(NEW_DB):
    os.remove(NEW_DB)
    print(f"Removed existing {NEW_DB}")

with open(SCHEMA) as f:
    schema_sql = f.read()

with sqlite3.connect(NEW_DB) as conn:
    conn.executescript(schema_sql)
    print("Schema applied.")

    # verify tables
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Tables created ({len(tables)}): {tables}")
    print()

# --- 3. Align columns: keep only those in the new schema, then insert ---
with sqlite3.connect(NEW_DB) as conn:
    new_cols = [r[1] for r in conn.execute("PRAGMA table_info(financial_ratios)").fetchall()]
    print(f"New schema columns: {new_cols}")
    print()

    # Keep only columns that exist in new schema
    cols_to_load = [c for c in df.columns if c in new_cols]
    missing_from_backup = [c for c in new_cols if c not in df.columns]
    extra_in_backup = [c for c in df.columns if c not in new_cols]
    print(f"Columns to load    : {cols_to_load}")
    print(f"Missing in backup  : {missing_from_backup}")
    print(f"Extra in backup    : {extra_in_backup}")
    print()

    df_load = df[cols_to_load]
    df_load.to_sql('financial_ratios', conn, if_exists='append', index=False)
    count_new = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    print(f"Rows loaded into new DB: {count_new}")

# --- 4. Final comparison report ---
print()
print("=== PRESERVATION REPORT ===")
print(f"  Original DB (nifty100_backup.db) row count : {count_backup}")
print(f"  New DB (nifty100.db) row count             : {count_new}")
print(f"  Difference                                 : {count_new - count_backup}")
if count_new == count_backup:
    print("  STATUS: OK - all rows preserved")
else:
    print("  STATUS: WARNING - row counts differ")
