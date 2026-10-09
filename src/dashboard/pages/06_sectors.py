import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_sectors, get_ratios, get_market_cap, get_connection

st.set_page_config(page_title="Sector Analysis", layout="wide")
st.title("Sector Analysis")

df_sec = get_sectors()
sectors = ["All"] + df_sec['broad_sector'].unique().tolist()

selected_sector = st.selectbox("Select Sector", options=sectors)

# We need Revenue, ROE, Market Cap, Sub Sector
# Instead of multiple function calls, let's just do a clean SQL query to get the latest year data
conn = get_connection()
query = """
SELECT c.company_name, s.broad_sector, s.sub_sector, r.return_on_equity_pct, p.sales_cr, m.market_cap_crore
FROM companies c
JOIN sectors s ON c.id = s.company_id
JOIN (
    SELECT company_id, return_on_equity_pct 
    FROM financial_ratios 
    WHERE year = (SELECT MAX(year) FROM financial_ratios)
) r ON c.id = r.company_id
JOIN (
    SELECT company_id, sales_cr 
    FROM profitandloss 
    WHERE year = (SELECT MAX(year) FROM profitandloss)
) p ON c.id = p.company_id
JOIN (
    SELECT company_id, market_cap_crore 
    FROM market_cap 
    WHERE year = (SELECT MAX(year) FROM market_cap)
) m ON c.id = m.company_id
"""
df = pd.read_sql(query, conn)

if selected_sector != "All":
    df = df[df['broad_sector'] == selected_sector]

if not df.empty:
    st.subheader("Revenue vs ROE Bubble Chart")
    
    # Fill NAs to avoid plotly issues
    df = df.fillna(0)
    # Ensure market_cap is positive for bubble size
    df['market_cap_crore'] = df['market_cap_crore'].abs()
    
    fig = px.scatter(
        df, 
        x="sales_cr", 
        y="return_on_equity_pct", 
        size="market_cap_crore", 
        color="sub_sector", 
        hover_name="company_name", 
        size_max=60,
        labels={"sales_cr": "Revenue (Cr)", "return_on_equity_pct": "ROE (%)"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Sector Median KPIs")
    # Median ROE and Revenue by Sub Sector
    median_df = df.groupby('sub_sector')[['return_on_equity_pct', 'sales_cr']].median().reset_index()
    
    col1, col2 = st.columns(2)
    with col1:
        fig_bar_roe = px.bar(median_df, x='sub_sector', y='return_on_equity_pct', title='Median ROE by Sub Sector')
        st.plotly_chart(fig_bar_roe, use_container_width=True)
    with col2:
        fig_bar_rev = px.bar(median_df, x='sub_sector', y='sales_cr', title='Median Revenue by Sub Sector')
        st.plotly_chart(fig_bar_rev, use_container_width=True)
else:
    st.warning("No data available.")
