import pandas as pd
import numpy as np
import os
import glob
from sqlalchemy import create_engine
import sqlite3

def clean_fund_master(df):
    df['launch_date'] = pd.to_datetime(df['launch_date']).dt.strftime('%Y-%m-%d')
    return df

def clean_nav_history(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['amfi_code', 'date'])
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    df = df[df['nav'] > 0]
    
    # Keep track of original trading dates
    original_dates = set(zip(df['amfi_code'], df['date']))
    
    # Forward fill missing dates (weekends/holidays)
    # We will resample to daily and ffill, but limit to 4 days to avoid filling large gaps
    df = df.set_index('date').groupby('amfi_code')['nav'].apply(
        lambda x: x.asfreq('D').ffill(limit=4)
    ).reset_index()
    
    # Add is_trading_day indicator
    df['is_trading_day'] = df.apply(lambda row: (row['amfi_code'], row['date']) in original_dates, axis=1)
    
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df

def clean_aum(df):
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df

def clean_monthly_sip(df):
    # Missing values in yoy_growth_pct left as NaN as requested/agreed
    return df

def clean_category_inflows(df):
    return df

def clean_industry_folios(df):
    return df

def clean_performance(df):
    # Validate numeric
    numeric_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Flag anomalous returns (> 150% or < -90%)
    anomalous_returns = df[(df['return_1yr_pct'] > 150) | (df['return_1yr_pct'] < -90) |
                           (df['return_3yr_pct'] > 150) | (df['return_3yr_pct'] < -90) |
                           (df['return_5yr_pct'] > 150) | (df['return_5yr_pct'] < -90)]
    if not anomalous_returns.empty:
        print("WARNING: Anomalous return values detected:")
        print(anomalous_returns[['amfi_code', 'scheme_name'] + numeric_cols])

    # Validate expense ratio
    invalid_expense = df[(df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5)]
    if not invalid_expense.empty:
        print("WARNING: Expense ratios outside expected 0.1% - 2.5% range:")
        print(invalid_expense[['amfi_code', 'scheme_name', 'expense_ratio_pct']])
    
    return df

def clean_transactions(df):
    # Standardise transaction type
    type_map = {
        'sip': 'SIP', 'SIP': 'SIP', 'S.I.P': 'SIP',
        'lumpsum': 'Lumpsum', 'LUMPSUM': 'Lumpsum', 'Lump Sum': 'Lumpsum',
        'redemption': 'Redemption', 'REDEMPTION': 'Redemption', 'Redeem': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].map(lambda x: type_map.get(str(x).strip(), str(x).strip().capitalize()))
    
    # amount > 0
    df = df[df['amount_inr'] > 0]
    
    # Date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # KYC status check
    valid_kyc = ['Verified', 'Pending', 'Rejected']
    invalid_kyc = df[~df['kyc_status'].isin(valid_kyc)]
    if not invalid_kyc.empty:
        print("WARNING: Invalid KYC status values detected:")
        print(invalid_kyc['kyc_status'].value_counts())
    
    return df

def clean_holdings(df):
    df['portfolio_date'] = pd.to_datetime(df['portfolio_date']).dt.strftime('%Y-%m-%d')
    return df

def clean_benchmark(df):
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df

def create_dim_date(nav_df, trans_df):
    dates1 = pd.to_datetime(nav_df['date'])
    dates2 = pd.to_datetime(trans_df['transaction_date'])
    all_dates = pd.concat([dates1, dates2]).dropna().unique()
    
    dim_date = pd.DataFrame({'date': all_dates})
    dim_date['date'] = pd.to_datetime(dim_date['date'])
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['month'] = dim_date['date'].dt.month
    dim_date['day'] = dim_date['date'].dt.day
    dim_date['day_of_week'] = dim_date['date'].dt.dayofweek
    dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
    
    dim_date['date'] = dim_date['date'].dt.strftime('%Y-%m-%d')
    return dim_date

def main():
    raw_dir = 'data/raw'
    processed_dir = 'data/processed'
    os.makedirs(processed_dir, exist_ok=True)
    
    # Load raw
    raw_files = {
        'fund_master': '1788499983024-b042c300-01_fund_master.csv',
        'nav_history': '1788499983331-4389156d-02_nav_history.csv',
        'aum': '1788499984134-b0cbf625-03_aum_by_fund_house.csv',
        'monthly_sip': '1788499984405-d702a6c6-04_monthly_sip_inflows.csv',
        'category_inflows': '1788499984721-4b860901-05_category_inflows.csv',
        'industry_folios': '1788499985036-da4a0c4a-06_industry_folio_count.csv',
        'performance': '1788499985420-bb134abf-07_scheme_performance.csv',
        'transactions': '1788499980509-304c1255-08_investor_transactions.csv',
        'holdings': '1788499982117-e3d6ab98-09_portfolio_holdings.csv',
        'benchmark': '1788499982615-f9647ab2-10_benchmark_indices.csv'
    }
    
    dfs = {}
    for name, filename in raw_files.items():
        dfs[name] = pd.read_csv(os.path.join(raw_dir, filename))
        
    print("Cleaning data...")
    cleaned_dfs = {
        'dim_fund': clean_fund_master(dfs['fund_master']),
        'fact_nav': clean_nav_history(dfs['nav_history']),
        'fact_aum': clean_aum(dfs['aum']),
        'fact_monthly_sip': clean_monthly_sip(dfs['monthly_sip']),
        'fact_category_inflows': clean_category_inflows(dfs['category_inflows']),
        'fact_industry_folios': clean_industry_folios(dfs['industry_folios']),
        'fact_performance': clean_performance(dfs['performance']),
        'fact_transactions': clean_transactions(dfs['transactions']),
        'fact_holdings': clean_holdings(dfs['holdings']),
        'fact_benchmark_indices': clean_benchmark(dfs['benchmark'])
    }
    
    # Drop duplicates for all
    for name in cleaned_dfs:
        cleaned_dfs[name] = cleaned_dfs[name].drop_duplicates()
        # Save to processed
        out_name = list(raw_files.keys())[list(cleaned_dfs.keys()).index(name)] + "_cleaned.csv"
        # We need to map back to original names basically, let's keep it simple
        original_file = raw_files[list(raw_files.keys())[list(cleaned_dfs.keys()).index(name)]]
        cleaned_dfs[name].to_csv(os.path.join(processed_dir, original_file), index=False)
        
    cleaned_dfs['dim_date'] = create_dim_date(cleaned_dfs['fact_nav'], cleaned_dfs['fact_transactions'])
    
    print("Setting up SQLite database...")
    db_path = 'bluestock_mf.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create schema
    with open('schema.sql', 'r') as f:
        schema_sql = f.read()
    
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)
        
    print("Loading data into SQLite...")
    # Map DataFrames to Table Names
    table_mappings = {
        'dim_fund': 'dim_fund',
        'dim_date': 'dim_date',
        'fact_nav': 'fact_nav',
        'fact_transactions': 'fact_transactions',
        'fact_performance': 'fact_performance',
        'fact_aum': 'fact_aum',
        'fact_holdings': 'fact_holdings',
        'fact_benchmark_indices': 'fact_benchmark_indices',
        'fact_monthly_sip': 'fact_monthly_sip',
        'fact_category_inflows': 'fact_category_inflows',
        'fact_industry_folios': 'fact_industry_folios'
    }
    
    for df_key, table_name in table_mappings.items():
        if df_key == 'fact_transactions':
            # drop transaction_id if we created it, or let sqlite auto increment
            pass
        cleaned_dfs[df_key].to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Loaded {len(cleaned_dfs[df_key])} rows into {table_name}")

if __name__ == "__main__":
    main()
