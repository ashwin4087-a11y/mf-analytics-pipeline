"""
src/etl/loader.py — Sprint 1 ETL Loader
Loads all 12 source Excel files into nifty100.db using the authoritative
source-to-table mapping from the Nifty100 Project Document FINAL PDF.

Load order (parent before child to satisfy FK constraints):
  1. companies          — parent for all FK refs
  2. sectors            — refs companies
  3. profitandloss      — refs companies
  4. balancesheet       — refs companies
  5. cashflow           — refs companies
  6. analysis           — refs companies
  7. documents          — refs companies
  8. prosandcons        — refs companies
  9. stock_prices       — refs companies
 10. market_cap         — refs companies
 11. financial_ratios   — refs companies (source cols only; Sprint 2 computed cols preserved separately)
 12. peer_groups        — refs companies
"""
import os
import time
import sqlite3
import csv
import datetime
import pandas as pd

from src.etl.normaliser import normalize_year, normalize_ticker

# ── Path resolution ────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR   = os.path.join(BASE_DIR, 'data')
SCHEMA_SQL = os.path.join(BASE_DIR, 'db', 'schema.sql')
DB_PATH    = os.path.join(DATA_DIR, 'nifty100.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def _find_file(suffix):
    """Find a file in DATA_DIR that ends with suffix (handles UUID prefixes)."""
    for f in os.listdir(DATA_DIR):
        if f.endswith(suffix):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError(f"Source file not found: *{suffix} in {DATA_DIR}")

def load_excel(file_path, is_core=True):
    """
    Loads an Excel file into a pandas DataFrame.
    Core datasets (with title row at row 0) use header=1.
    Supporting datasets use header=0.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    header_row = 1 if is_core else 0
    return pd.read_excel(file_path, header=header_row)

def init_db_schema(db_path, schema_path):
    """Initialize database with the 12-table schema. Drops existing DB."""
    if os.path.exists(db_path):
        os.remove(db_path)
    with sqlite3.connect(db_path) as conn:
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())

def migrate_financial_ratios(old_db_path, new_db_path):
    """Preserve Sprint 2 financial_ratios rows by migrating from backup.
    Only migrates rows whose company_id exists in the companies table (FK-safe).
    """
    if not os.path.exists(old_db_path):
        return 0, 0
    with sqlite3.connect(old_db_path) as conn:
        try:
            df = pd.read_sql("SELECT * FROM financial_ratios", conn)
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
        except sqlite3.OperationalError:
            return 0, 0
    with sqlite3.connect(new_db_path) as conn:
        # Get valid company_ids from already-loaded companies table
        valid_ids = set(r[0] for r in conn.execute("SELECT id FROM companies").fetchall())
        rows_in = len(df)
        if valid_ids:
            df = df[df['company_id'].isin(valid_ids)]
        rows_rejected = rows_in - len(df)

        new_cols = [r[1] for r in conn.execute("PRAGMA table_info(financial_ratios)").fetchall()]
        cols_to_load = [c for c in df.columns if c in new_cols]
        df[cols_to_load].to_sql('financial_ratios', conn, if_exists='append', index=False)
        return len(df), rows_rejected

# ── Shared cleaning helper ────────────────────────────────────────────────

def _clean_df(df, conn, pk_cols=None, reasons=None):
    """
    Apply in order:
    1. Dedup on pk_cols (keep first), log as DQ-02
    2. FK filter on company_id, log as DQ-03
    Returns (cleaned_df, reasons_list)
    """
    if reasons is None:
        reasons = []
    if pk_cols:
        dup_mask = df.duplicated(subset=pk_cols, keep='first')
        n_dups = dup_mask.sum()
        if n_dups > 0:
            reasons.append(f"{n_dups} duplicate ({','.join(pk_cols)}) rows deduplicated [DQ-02]")
            df = df[~dup_mask]
    if 'company_id' in df.columns:
        valid_ids = set(r[0] for r in conn.execute("SELECT id FROM companies").fetchall())
        if valid_ids:
            fk_mask = ~df['company_id'].isin(valid_ids)
            n_fk = fk_mask.sum()
            if n_fk > 0:
                reasons.append(f"{n_fk} rows rejected: company_id not in companies [DQ-03]")
                df = df[~fk_mask]
    return df, reasons

_audit_rows = []

def _audit(table, source_file, rows_in, rows_out, rejected, rejection_reason, runtime_s):
    _audit_rows.append({
        'table': table,
        'source_file': source_file,
        'rows_in': rows_in,
        'rows_out': rows_out,
        'rejected': rejected,
        'rejection_reason': rejection_reason if rejected > 0 else '',
        'timestamp': datetime.datetime.now().isoformat(),
        'runtime_s': round(runtime_s, 3),
    })

def write_load_audit(path=None):
    if path is None:
        path = os.path.join(OUTPUT_DIR, 'load_audit.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = ['table','source_file','rows_in','rows_out','rejected',
                  'rejection_reason','timestamp','runtime_s']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_audit_rows)
    return path

# ── Table loaders ──────────────────────────────────────────────────────────

def _load_companies(conn):
    t0 = time.time()
    src = _find_file('companies.xlsx')
    df = load_excel(src, is_core=True)  # header=1
    rows_in = len(df)

    # normalise ticker id
    df['id'] = df['id'].apply(normalize_ticker)

    # drop rows where id is MISSING
    before = len(df)
    df = df[df['id'] != 'MISSING']
    rejected = before - len(df)
    rejection_reason = f"{rejected} rows with missing/empty ticker" if rejected else ""

    cols = ['id','company_logo','company_name','chart_link','about_company',
            'website','nse_profile','bse_profile','face_value','book_value',
            'roce_percentage','roe_percentage']
    df = df[[c for c in cols if c in df.columns]]
    df.to_sql('companies', conn, if_exists='append', index=False)
    _audit('companies', os.path.basename(src), rows_in, len(df), rejected, rejection_reason, time.time()-t0)
    return len(df)


def _load_timeseries_core(conn, table, source_suffix, extra_cols=None, is_core=True):
    """Generic loader for P&L / BS / CF / analysis."""
    t0 = time.time()
    src = _find_file(source_suffix)
    df = load_excel(src, is_core=is_core)
    rows_in = len(df)

    # drop surrogate id from source
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # normalise keys
    df['company_id'] = df['company_id'].apply(normalize_ticker)
    if 'year' in df.columns:
        df['year'] = df['year'].apply(normalize_year)

    # drop rows where company_id MISSING or year PARSE_ERROR
    before = len(df)
    reasons = []
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]

    if 'year' in df.columns:
        mask_parse = df['year'] == 'PARSE_ERROR'
        if mask_parse.any():
            reasons.append(f"{mask_parse.sum()} unparseable year")
        df = df[~mask_parse]

    # Deduplicate (company_id, year) — keep first, log remainder as DQ-02 violations
    pk_cols = [c for c in ['company_id', 'year'] if c in df.columns]
    if pk_cols:
        dup_mask = df.duplicated(subset=pk_cols, keep='first')
        n_dups = dup_mask.sum()
        if n_dups > 0:
            reasons.append(f"{n_dups} duplicate (company_id,year) rows deduplicated [DQ-02]")
            df = df[~dup_mask]

    # Filter FK violations — only insert rows with valid company_id
    valid_ids = set(
        r[0] for r in conn.execute("SELECT id FROM companies").fetchall()
    )
    if valid_ids:  # only filter if companies table is populated
        fk_mask = ~df['company_id'].isin(valid_ids)
        n_fk = fk_mask.sum()
        if n_fk > 0:
            reasons.append(f"{n_fk} rows rejected: company_id not in companies [DQ-03]")
            df = df[~fk_mask]

    rejected = before - len(df)
    rejection_reason = "; ".join(reasons) if reasons else ""

    # keep only schema columns
    schema_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]

    df.to_sql(table, conn, if_exists='append', index=False)
    _audit(table, os.path.basename(src), rows_in, len(df), rejected, rejection_reason, time.time()-t0)
    return len(df)


def _load_documents(conn):
    t0 = time.time()
    src = _find_file('documents.xlsx')
    df = load_excel(src, is_core=True)  # header=1 — has title row
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # rename columns to match schema
    df = df.rename(columns={'Year': 'year', 'Annual_Report': 'annual_report'})
    df['company_id'] = df['company_id'].apply(normalize_ticker)

    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]

    df, reasons = _clean_df(df, conn, pk_cols=['company_id','year'], reasons=reasons)
    rejected = before - len(df)

    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(documents)").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]
    df.to_sql('documents', conn, if_exists='append', index=False)
    _audit('documents', os.path.basename(src), rows_in, len(df), rejected,
           "; ".join(reasons) if reasons else "", time.time()-t0)
    return len(df)


def _load_prosandcons(conn):
    t0 = time.time()
    src = _find_file('prosandcons.xlsx')
    df = load_excel(src, is_core=True)  # header=1 — has title row
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    df['company_id'] = df['company_id'].apply(normalize_ticker)
    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]
    df, reasons = _clean_df(df, conn, reasons=reasons)
    rejected = before - len(df)

    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(prosandcons)").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]
    df.to_sql('prosandcons', conn, if_exists='append', index=False)
    _audit('prosandcons', os.path.basename(src), rows_in, len(df), rejected,
           "; ".join(reasons) if reasons else "", time.time()-t0)
    return len(df)


def _load_sectors(conn):
    t0 = time.time()
    src = _find_file('sectors.xlsx')
    df = load_excel(src, is_core=False)  # header=0
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    df['company_id'] = df['company_id'].apply(normalize_ticker)
    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]
    df, reasons = _clean_df(df, conn, pk_cols=['company_id'], reasons=reasons)
    rejected = before - len(df)

    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(sectors)").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]
    df.to_sql('sectors', conn, if_exists='append', index=False)
    _audit('sectors', os.path.basename(src), rows_in, len(df), rejected,
           "; ".join(reasons) if reasons else "", time.time()-t0)
    return len(df)


def _load_stock_prices(conn):
    t0 = time.time()
    src = _find_file('stock_prices.xlsx')
    df = load_excel(src, is_core=False)  # header=0
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    df['company_id'] = df['company_id'].apply(normalize_ticker)
    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]
    df, reasons = _clean_df(df, conn, pk_cols=['company_id','date'], reasons=reasons)
    rejected = before - len(df)

    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(stock_prices)").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]
    df.to_sql('stock_prices', conn, if_exists='append', index=False)
    _audit('stock_prices', os.path.basename(src), rows_in, len(df), rejected,
           "; ".join(reasons) if reasons else "", time.time()-t0)
    return len(df)


def _load_market_cap(conn):
    t0 = time.time()
    src = _find_file('market_cap.xlsx')
    df = load_excel(src, is_core=False)  # header=0
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    df['company_id'] = df['company_id'].apply(normalize_ticker)
    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]
    df, reasons = _clean_df(df, conn, pk_cols=['company_id','year'], reasons=reasons)
    rejected = before - len(df)

    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(market_cap)").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]
    df.to_sql('market_cap', conn, if_exists='append', index=False)
    _audit('market_cap', os.path.basename(src), rows_in, len(df), rejected,
           "; ".join(reasons) if reasons else "", time.time()-t0)
    return len(df)


def _load_peer_groups(conn):
    t0 = time.time()
    src = _find_file('peer_groups.xlsx')
    df = load_excel(src, is_core=False)  # header=0
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    df['company_id'] = df['company_id'].apply(normalize_ticker)
    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]
    df, reasons = _clean_df(df, conn, reasons=reasons)
    rejected = before - len(df)

    # normalise is_benchmark to integer 0/1
    if 'is_benchmark' in df.columns:
        df['is_benchmark'] = df['is_benchmark'].apply(
            lambda x: 1 if str(x).strip().lower() in ('true', '1', 'yes') else 0
        )

    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(peer_groups)").fetchall()]
    df = df[[c for c in df.columns if c in schema_cols]]
    df.to_sql('peer_groups', conn, if_exists='append', index=False)
    _audit('peer_groups', os.path.basename(src), rows_in, len(df), rejected,
           "; ".join(reasons) if reasons else "", time.time()-t0)
    return len(df)


def _load_financial_ratios_source(conn):
    """
    Load the *source* financial_ratios.xlsx (1184 rows).
    Strategy: INSERT OR IGNORE to avoid overwriting Sprint 2 computed rows.
    Any source row whose (company_id, year) already exists (from Sprint 2) is skipped.
    Source rows for company/year combos NOT in Sprint 2 are inserted.
    """
    t0 = time.time()
    src = _find_file('financial_ratios.xlsx')
    df = load_excel(src, is_core=False)  # header=0
    rows_in = len(df)

    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    df['company_id'] = df['company_id'].apply(normalize_ticker)
    df['year'] = df['year'].apply(normalize_year)

    reasons = []
    before = len(df)
    mask_missing = df['company_id'] == 'MISSING'
    if mask_missing.any():
        reasons.append(f"{mask_missing.sum()} missing company_id")
    df = df[~mask_missing]

    mask_parse = df['year'] == 'PARSE_ERROR'
    if mask_parse.any():
        reasons.append(f"{mask_parse.sum()} unparseable year")
    df = df[~mask_parse]

    # Clean duplicates and FK violations
    df, reasons = _clean_df(df, conn, pk_cols=['company_id','year'], reasons=reasons)
    rejected_clean = before - len(df)

    # Only insert schema columns
    schema_cols = [r[1] for r in conn.execute("PRAGMA table_info(financial_ratios)").fetchall()]
    cols_to_load = [c for c in df.columns if c in schema_cols]
    df_load = df[cols_to_load]

    # Use INSERT OR IGNORE to preserve Sprint 2 computed rows
    inserted = 0
    skipped = 0
    for _, row in df_load.iterrows():
        placeholders = ', '.join(['?'] * len(row))
        col_names = ', '.join(row.index.tolist())
        sql = f"INSERT OR IGNORE INTO financial_ratios ({col_names}) VALUES ({placeholders})"
        cursor = conn.execute(sql, list(row))
        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    total_rejected = rejected_clean + skipped
    rejection_parts = []
    if rejected_clean > 0:
        rejection_parts.append("; ".join(reasons))
    if skipped > 0:
        rejection_parts.append(f"{skipped} rows skipped (Sprint 2 computed rows preserved)")

    _audit('financial_ratios (source)', os.path.basename(src), rows_in, inserted,
           total_rejected, "; ".join(rejection_parts) if rejection_parts else "", time.time()-t0)
    return inserted


# ── Main orchestrator ──────────────────────────────────────────────────────

def load_all_tables(db_path=None, schema_path=None, backup_db=None):
    """
    Complete Sprint 1 ETL: initialize schema, migrate Sprint 2 data,
    load all 12 source files in FK-safe order.
    Returns dict of {table: row_count}.
    """
    if db_path is None:
        db_path = DB_PATH
    if schema_path is None:
        schema_path = SCHEMA_SQL
    if backup_db is None:
        backup_db = os.path.join(DATA_DIR, 'nifty100_backup.db')

    global _audit_rows
    _audit_rows = []

    # Step 1 – Rebuild schema
    print(f"[ETL] Initialising schema: {db_path}")
    init_db_schema(db_path, schema_path)

    # Step 2 – Migrate Sprint 2 financial_ratios BEFORE loading source data
    # Companies must be loaded first so FK filter works
    print("[ETL] Loading companies...")
    counts = {}
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        counts['companies'] = _load_companies(conn)

    # Now migrate Sprint 2 financial_ratios (FK-filtered against loaded companies)
    print("[ETL] Migrating Sprint 2 financial_ratios from backup...")
    migrated, fk_rejected = migrate_financial_ratios(backup_db, db_path)
    print(f"[ETL]   Migrated {migrated} Sprint 2 rows ({fk_rejected} rejected: orphan company_ids)")
    _audit('financial_ratios (Sprint2 migrate)', os.path.basename(backup_db),
           migrated + fk_rejected, migrated, fk_rejected,
           f"{fk_rejected} rows rejected: company_id not in companies [DQ-03]" if fk_rejected else
           "Sprint 2 computed KPI rows preserved", 0.0)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # 2. Child tables (all reference companies.id)
        print("[ETL] Loading sectors...")
        counts['sectors'] = _load_sectors(conn)

        print("[ETL] Loading profitandloss...")
        counts['profitandloss'] = _load_timeseries_core(
            conn, 'profitandloss', 'profitandloss.xlsx', is_core=True)

        print("[ETL] Loading balancesheet...")
        counts['balancesheet'] = _load_timeseries_core(
            conn, 'balancesheet', 'balancesheet.xlsx', is_core=True)

        print("[ETL] Loading cashflow...")
        counts['cashflow'] = _load_timeseries_core(
            conn, 'cashflow', 'cashflow.xlsx', is_core=True)

        print("[ETL] Loading analysis...")
        counts['analysis'] = _load_timeseries_core(
            conn, 'analysis', 'analysis.xlsx', is_core=True)

        print("[ETL] Loading documents...")
        counts['documents'] = _load_documents(conn)

        print("[ETL] Loading prosandcons...")
        counts['prosandcons'] = _load_prosandcons(conn)

        print("[ETL] Loading stock_prices...")
        counts['stock_prices'] = _load_stock_prices(conn)

        print("[ETL] Loading market_cap...")
        counts['market_cap'] = _load_market_cap(conn)

        print("[ETL] Loading financial_ratios source (INSERT OR IGNORE)...")
        counts['financial_ratios_new'] = _load_financial_ratios_source(conn)

        print("[ETL] Loading peer_groups...")
        counts['peer_groups'] = _load_peer_groups(conn)

        # Final total for financial_ratios
        counts['financial_ratios'] = conn.execute(
            "SELECT COUNT(*) FROM financial_ratios").fetchone()[0]

        # FK check
        print("[ETL] Running foreign key check...")
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        counts['fk_violations'] = len(fk_violations)
        if fk_violations:
            print(f"[ETL] WARNING: {len(fk_violations)} FK violations found!")
            for v in fk_violations[:10]:
                print(f"  {v}")
        else:
            print("[ETL] FK check: PASS (0 violations)")

    # Write audit
    audit_path = write_load_audit()
    print(f"[ETL] Load audit written: {audit_path}")
    return counts


if __name__ == '__main__':
    results = load_all_tables()
    print("\n=== ETL COMPLETE ===")
    for k, v in results.items():
        print(f"  {k}: {v}")
