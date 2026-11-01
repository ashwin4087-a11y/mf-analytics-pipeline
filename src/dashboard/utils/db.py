import os
import sqlite3
import pandas as pd
import streamlit as st

def find_db():
    cur = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        for candidate in [
            os.path.join(cur, "data", "nifty100.db"),
            os.path.join(cur, "w3", "data", "nifty100.db")
        ]:
            if os.path.exists(candidate):
                return candidate
        cur = os.path.dirname(cur)
    return "data/nifty100.db"

DB_PATH = find_db()

def find_output_dir():
    cur = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        for candidate in [
            os.path.join(cur, "output"),
            os.path.join(cur, "w3", "output")
        ]:
            if os.path.exists(candidate):
                return candidate
        cur = os.path.dirname(cur)
    return "output"

OUTPUT_DIR = find_output_dir()

@st.cache_resource
def get_connection():
    """Cached thread-safe connection to SQLite database."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=600)
def get_companies():
    """Retrieve all 92 Nifty 100 companies with metadata."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM companies ORDER BY company_name ASC", conn)

@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    """
    Retrieve financial ratios.
    Handles flexible year input (e.g. 2024 matches '2024-03' and '2024-09').
    """
    conn = get_connection()
    query = "SELECT * FROM financial_ratios"
    params = []
    conditions = []
    
    if ticker:
        conditions.append("company_id = ?")
        params.append(ticker)
    if year is not None:
        year_str = str(year).strip()
        if len(year_str) == 4 and year_str.isdigit():
            conditions.append("(year LIKE ? OR year = ?)")
            params.extend([f"{year_str}%", year_str])
        else:
            conditions.append("year = ?")
            params.append(year_str)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    df = pd.read_sql(query, conn, params=params)
    
    # If filtered by year, ensure 1 row per company (latest year in case of multiples)
    if year is not None and not df.empty and 'company_id' in df.columns:
        df = df.sort_values('year', ascending=False).groupby('company_id').head(1).reset_index(drop=True)
        
    return df

@st.cache_data(ttl=600)
def get_pl(ticker=None):
    """
    Retrieve P&L history with aliased sales_cr and net_profit_cr for backward compatibility.
    """
    conn = get_connection()
    query = """
    SELECT *, 
           sales as sales_cr, 
           net_profit as net_profit_cr 
    FROM profitandloss
    """
    if ticker:
        query += " WHERE company_id = ? ORDER BY year ASC"
        return pd.read_sql(query, conn, params=(ticker,))
    return pd.read_sql(query + " ORDER BY year ASC", conn)

@st.cache_data(ttl=600)
def get_bs(ticker=None):
    """Retrieve balance sheet records."""
    conn = get_connection()
    query = "SELECT * FROM balancesheet"
    if ticker:
        query += " WHERE company_id = ? ORDER BY year ASC"
        return pd.read_sql(query, conn, params=(ticker,))
    return pd.read_sql(query + " ORDER BY year ASC", conn)

@st.cache_data(ttl=600)
def get_cf(ticker=None):
    """Retrieve cash flow records."""
    conn = get_connection()
    query = "SELECT * FROM cashflow"
    if ticker:
        query += " WHERE company_id = ? ORDER BY year ASC"
        return pd.read_sql(query, conn, params=(ticker,))
    return pd.read_sql(query + " ORDER BY year ASC", conn)

@st.cache_data(ttl=600)
def get_market_cap(year=None):
    """Retrieve market cap records."""
    conn = get_connection()
    if year is not None:
        try:
            year_int = int(str(year)[:4])
            return pd.read_sql("SELECT * FROM market_cap WHERE year = ?", conn, params=(year_int,))
        except ValueError:
            return pd.read_sql("SELECT * FROM market_cap WHERE year = ?", conn, params=(year,))
    return pd.read_sql("SELECT * FROM market_cap ORDER BY year DESC", conn)

@st.cache_data(ttl=600)
def get_sectors():
    """Retrieve sector classifications."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM sectors", conn)

@st.cache_data(ttl=600)
def get_peers(group_name=None):
    """
    Retrieve peer percentiles with both peer_group and peer_group_name aliases.
    """
    conn = get_connection()
    query = """
    SELECT company_id, 
           peer_group_name as peer_group, 
           peer_group_name, 
           metric, 
           value, 
           percentile_rank, 
           year 
    FROM peer_percentiles
    """
    if group_name:
        query += " WHERE peer_group_name = ? OR peer_group_name = ?"
        return pd.read_sql(query, conn, params=(group_name, group_name))
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_valuation(ticker=None):
    """Retrieve valuation engine outputs from the database."""
    conn = get_connection()
    try:
        if ticker:
            return pd.read_sql("SELECT * FROM valuation WHERE company_id = ?", conn, params=(ticker,))
        return pd.read_sql("SELECT * FROM valuation", conn)
    except Exception:
        # Fallback to output files if table temporarily unpopulated
        val_csv = os.path.join(OUTPUT_DIR, 'valuation_summary.xlsx')
        if os.path.exists(val_csv):
            df = pd.read_excel(val_csv)
            if ticker and 'company_id' in df.columns:
                return df[df['company_id'] == ticker]
            return df
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_prosandcons(ticker):
    """Retrieve algorithmic and documented pros & cons."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM prosandcons WHERE company_id = ?", conn, params=(ticker,))

@st.cache_data(ttl=600)
def get_documents(ticker=None):
    """Retrieve annual report BSE filings."""
    conn = get_connection()
    query = """
    SELECT c.company_name, 
           d.company_id, 
           d.year, 
           d.annual_report
    FROM documents d
    JOIN companies c ON d.company_id = c.id
    WHERE d.annual_report IS NOT NULL 
      AND d.annual_report != 'NA' 
      AND d.annual_report != ''
    """
    if ticker:
        query += " AND d.company_id = ?"
        return pd.read_sql(query + " ORDER BY d.year DESC", conn, params=(ticker,))
    return pd.read_sql(query + " ORDER BY c.company_name ASC, d.year DESC", conn)

@st.cache_data(ttl=600)
def get_capital_allocation_data():
    """
    Retrieve latest capital allocation classifications merged with Market Cap.
    """
    ca_path = os.path.join(OUTPUT_DIR, 'capital_allocation.csv')
    if not os.path.exists(ca_path):
        return pd.DataFrame()
        
    df_ca = pd.read_csv(ca_path)
    # Get latest year record per company
    df_ca = df_ca.sort_values(by='year').groupby('company_id').tail(1).reset_index(drop=True)
    
    conn = get_connection()
    df_comp = get_companies()
    df_sec = get_sectors()
    
    # Latest market cap
    mc_query = """
    SELECT company_id, market_cap_crore 
    FROM market_cap 
    WHERE year = (SELECT MAX(year) FROM market_cap)
    """
    df_mc = pd.read_sql(mc_query, conn)
    
    merged = df_ca.merge(df_comp[['id', 'company_name']], left_on='company_id', right_on='id', how='left')
    merged = merged.merge(df_sec[['company_id', 'broad_sector', 'sub_sector']], on='company_id', how='left')
    merged = merged.merge(df_mc, on='company_id', how='left')
    
    merged['market_cap_crore'] = merged['market_cap_crore'].fillna(1000).abs()
    merged['broad_sector'] = merged['broad_sector'].fillna('General').astype(str).str.replace('\n', ' ').str.strip()
    merged['pattern_label'] = merged['pattern_label'].fillna('Unclassified').astype(str).str.replace('\n', ' ').str.strip()
    merged['company_name'] = merged['company_name'].fillna(merged['company_id']).astype(str).str.replace('\n', ' ').str.strip()
    merged['Root'] = 'Nifty 100 Universe'
    return merged
