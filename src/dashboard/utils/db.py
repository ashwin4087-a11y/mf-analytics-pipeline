import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data/nifty100.db"

@st.cache_data(ttl=600)
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=600)
def get_companies():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM companies", conn)

@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    conn = get_connection()
    query = "SELECT * FROM financial_ratios"
    params = []
    conditions = []
    
    if ticker:
        conditions.append("company_id = ?")
        params.append(ticker)
    if year:
        conditions.append("year = ?")
        params.append(year)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    return pd.read_sql(query, conn, params=params)

@st.cache_data(ttl=600)
def get_pl(ticker):
    conn = get_connection()
    return pd.read_sql("SELECT * FROM profitandloss WHERE company_id = ?", conn, params=(ticker,))

@st.cache_data(ttl=600)
def get_bs(ticker):
    conn = get_connection()
    return pd.read_sql("SELECT * FROM balancesheet WHERE company_id = ?", conn, params=(ticker,))

@st.cache_data(ttl=600)
def get_cf(ticker):
    conn = get_connection()
    return pd.read_sql("SELECT * FROM cashflow WHERE company_id = ?", conn, params=(ticker,))

@st.cache_data(ttl=600)
def get_market_cap(year=None):
    conn = get_connection()
    if year:
        return pd.read_sql("SELECT * FROM market_cap WHERE year = ?", conn, params=(year,))
    return pd.read_sql("SELECT * FROM market_cap", conn)

@st.cache_data(ttl=600)
def get_sectors():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM sectors", conn)

@st.cache_data(ttl=600)
def get_peers(group_name=None):
    conn = get_connection()
    if group_name:
        return pd.read_sql("SELECT * FROM peer_percentiles WHERE peer_group = ?", conn, params=(group_name,))
    return pd.read_sql("SELECT * FROM peer_percentiles", conn)

@st.cache_data(ttl=600)
def get_valuation(ticker=None):
    conn = get_connection()
    try:
        if ticker:
            return pd.read_sql("SELECT * FROM valuation WHERE company_id = ?", conn, params=(ticker,))
        return pd.read_sql("SELECT * FROM valuation", conn)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_prosandcons(ticker):
    conn = get_connection()
    return pd.read_sql("SELECT * FROM prosandcons WHERE company_id = ?", conn, params=(ticker,))
