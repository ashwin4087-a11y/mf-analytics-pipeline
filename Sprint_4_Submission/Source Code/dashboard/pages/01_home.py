import streamlit as st
import pandas as pd
import plotly.express as px
from src.dashboard.utils.db import get_ratios, get_companies, get_sectors, get_market_cap

st.set_page_config(page_title="Home", layout="wide")

st.title("Home")

st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", options=[2024, 2023, 2022, 2021, 2020, 2019])

df_ratios = get_ratios(year=selected_year)
df_comp = get_companies()
df_sectors = get_sectors()
df_mc = get_market_cap(year=selected_year)

# Calculate KPIs
if df_ratios.empty:
    st.warning("No data available for the selected year.")
else:
    avg_roe = df_ratios['return_on_equity_pct'].mean() if 'return_on_equity_pct' in df_ratios.columns else 0
    med_de = df_ratios['debt_to_equity'].median() if 'debt_to_equity' in df_ratios.columns else 0
    med_rev_cagr = df_ratios['revenue_cagr_5yr'].median() if 'revenue_cagr_5yr' in df_ratios.columns else 0
    
    total_companies = len(df_ratios['company_id'].unique())
    debt_free_count = len(df_ratios[df_ratios['debt_to_equity'] == 0]) if 'debt_to_equity' in df_ratios.columns else 0
    
    med_pe = df_mc['pe_ratio'].median() if not df_mc.empty and 'pe_ratio' in df_mc.columns else 0
    
    # KPI Tiles
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    col1.metric("Average ROE (%)", f"{avg_roe:.2f}%" if pd.notna(avg_roe) else "N/A")
    col2.metric("Median P/E", f"{med_pe:.2f}" if pd.notna(med_pe) else "N/A")
    col3.metric("Median D/E", f"{med_de:.2f}" if pd.notna(med_de) else "N/A")
    
    col4.metric("Total Companies", total_companies)
    col5.metric("Median Revenue CAGR 5Y (%)", f"{med_rev_cagr:.2f}%" if pd.notna(med_rev_cagr) else "N/A")
    col6.metric("Debt-Free Companies", debt_free_count)
    
    # Sector Breakdown
    st.subheader("Sector Breakdown")
    sector_counts = df_sectors['broad_sector'].value_counts().reset_index()
    sector_counts.columns = ['Sector', 'Count']
    fig = px.pie(sector_counts, names='Sector', values='Count', hole=0.4, title="Companies by Sector")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 5 by Composite Score
    st.subheader("Top 5 Companies by Composite Quality Score")
    if 'composite_quality_score' in df_ratios.columns:
        top_5 = df_ratios[['company_id', 'composite_quality_score']].sort_values('composite_quality_score', ascending=False).head(5)
        # Merge with company names
        top_5 = top_5.merge(df_comp[['id', 'company_name']], left_on='company_id', right_on='id', how='left')
        st.dataframe(top_5[['company_id', 'company_name', 'composite_quality_score']], use_container_width=True)
    else:
        st.info("Composite Score not available in this dataset.")
