import os
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'nifty100.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def compute_valuation():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Get latest market_cap data (latest year per company)
    mc_query = """
    SELECT m.company_id, m.year, m.market_cap_crore, m.pe_ratio, m.pb_ratio, m.ev_ebitda
    FROM market_cap m
    INNER JOIN (
        SELECT company_id, MAX(year) as max_year
        FROM market_cap
        GROUP BY company_id
    ) latest ON m.company_id = latest.company_id AND m.year = latest.max_year
    """
    df_mc = pd.read_sql(mc_query, conn)
    
    # 2. Get 5-year median PE
    pe_5yr_query = """
    SELECT company_id, pe_ratio
    FROM market_cap
    WHERE pe_ratio IS NOT NULL
    """
    df_pe_all = pd.read_sql(pe_5yr_query, conn)
    df_pe_5yr = df_pe_all.groupby('company_id')['pe_ratio'].median().reset_index()
    df_pe_5yr.rename(columns={'pe_ratio': '5yr_median_PE'}, inplace=True)
    
    # 3. Get FCF (latest year)
    fcf_query = """
    SELECT f.company_id, f.free_cash_flow_cr
    FROM financial_ratios f
    INNER JOIN (
        SELECT company_id, MAX(year) as max_year
        FROM financial_ratios
        GROUP BY company_id
    ) latest ON f.company_id = latest.company_id AND f.year = latest.max_year
    """
    df_fcf = pd.read_sql(fcf_query, conn)
    
    # 4. Get Company and Sector info
    comp_query = """
    SELECT c.id as company_id, c.company_name, s.broad_sector as sector
    FROM companies c
    LEFT JOIN sectors s ON c.id = s.company_id
    """
    df_comp = pd.read_sql(comp_query, conn)
    
    # Merge everything
    df = df_comp.merge(df_mc, on='company_id', how='inner')
    df = df.merge(df_pe_5yr, on='company_id', how='left')
    df = df.merge(df_fcf, on='company_id', how='left')
    
    # Compute FCF yield
    df['FCF_yield_pct'] = (df['free_cash_flow_cr'] / df['market_cap_crore']) * 100
    
    # Compute Sector median PE (for the latest year)
    sector_pe = df.groupby('sector')['pe_ratio'].median().reset_index()
    sector_pe.rename(columns={'pe_ratio': 'sector_median_PE'}, inplace=True)
    df = df.merge(sector_pe, on='sector', how='left')
    
    # Compute PE vs sector median
    df['PE_vs_sector_median_pct'] = ((df['pe_ratio'] / df['sector_median_PE']) - 1) * 100
    
    # Apply Flags
    def get_flag(row):
        pe = row['pe_ratio']
        sec_pe = row['sector_median_PE']
        if pd.isna(pe) or pd.isna(sec_pe):
            return 'Fair'
        if pe > sec_pe * 1.5:
            return 'Caution'
        if pe < sec_pe * 0.7:
            return 'Discount'
        return 'Fair'
        
    df['flag'] = df.apply(get_flag, axis=1)
    
    # Format output
    cols = [
        'company_id', 'company_name', 'sector', 'pe_ratio', 'pb_ratio', 
        'ev_ebitda', 'FCF_yield_pct', '5yr_median_PE', 'PE_vs_sector_median_pct', 'flag'
    ]
    # some might be missing, so intersect
    out_cols = [c for c in cols if c in df.columns]
    
    # Rename to exact required columns if needed (e.g. pe_ratio -> P/E)
    rename_dict = {
        'pe_ratio': 'P/E',
        'pb_ratio': 'P/B',
        'ev_ebitda': 'EV/EBITDA'
    }
    df_out = df[out_cols].rename(columns=rename_dict)
    
    # Generate valuation_summary.xlsx
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_out.to_excel(os.path.join(OUTPUT_DIR, 'valuation_summary.xlsx'), index=False)
    
    # Generate valuation_flags.csv
    df_flags = df_out[df_out['flag'].isin(['Caution', 'Discount'])]
    df_flags.to_csv(os.path.join(OUTPUT_DIR, 'valuation_flags.csv'), index=False)
    
    # Write to database as well so dashboard can query it
    df_out.to_sql('valuation', conn, if_exists='replace', index=False)
    
    conn.close()
    print("Valuation module executed successfully.")

if __name__ == '__main__':
    compute_valuation()
