import pandas as pd
import sqlite3
import os

def validate_data():
    raw_dir = 'data/raw'
    processed_dir = 'data/processed'
    db_path = 'bluestock_mf.db'
    
    raw_files = {
        '01_fund_master.csv': 'dim_fund',
        '02_nav_history.csv': 'fact_nav',
        '03_aum_by_fund_house.csv': 'fact_aum',
        '04_monthly_sip_inflows.csv': 'fact_monthly_sip',
        '05_category_inflows.csv': 'fact_category_inflows',
        '06_industry_folio_count.csv': 'fact_industry_folios',
        '07_scheme_performance.csv': 'fact_performance',
        '08_investor_transactions.csv': 'fact_transactions',
        '09_portfolio_holdings.csv': 'fact_holdings',
        '10_benchmark_indices.csv': 'fact_benchmark_indices'
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*60)
    print(f"{'Dataset':<35} | {'Raw':<6} | {'Clean':<6} | {'DB':<6}")
    print("="*60)
    
    for prefix, table in raw_files.items():
        # Find raw file
        raw_match = [f for f in os.listdir(raw_dir) if prefix in f][0]
        raw_df = pd.read_csv(os.path.join(raw_dir, raw_match))
        raw_count = len(raw_df)
        
        # Find processed file
        clean_df = pd.read_csv(os.path.join(processed_dir, raw_match))
        clean_count = len(clean_df)
        
        # Check DB
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        db_count = cursor.fetchone()[0]
        
        print(f"{prefix:<35} | {raw_count:<6} | {clean_count:<6} | {db_count:<6}")
        
    print("="*60)
    
    # Foreign Key validation
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    print(f"\nForeign Key Validation Errors: {len(fk_errors)}")
    if fk_errors:
        print(fk_errors)
        
    conn.close()

if __name__ == "__main__":
    validate_data()
