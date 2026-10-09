import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_sectors, get_ratios, get_pl, get_prosandcons

st.set_page_config(page_title="Company Profile", layout="wide")

df_comp = get_companies()
if df_comp.empty:
    st.error("No companies data available.")
    st.stop()

# Create a list for the dropdown: "Company Name (TICKER)"
comp_options = df_comp.apply(lambda x: f"{x['company_name']} ({x['id']})", axis=1).tolist()

st.title("Company Profile")

selected_option = st.selectbox("Search Company Name or Ticker", options=[""] + comp_options, index=0)

if selected_option:
    # Extract ticker from the selected option e.g., "TCS (TCS)"
    ticker = selected_option.split("(")[-1].replace(")", "").strip()
    
    comp_row = df_comp[df_comp['id'] == ticker]
    if comp_row.empty:
        st.warning("Ticker not found — please try another")
    else:
        comp_info = comp_row.iloc[0]
        
        # Get sector info
        df_sec = get_sectors()
        sector_info = df_sec[df_sec['company_id'] == ticker]
        sector = sector_info.iloc[0]['broad_sector'] if not sector_info.empty else "N/A"
        sub_sector = sector_info.iloc[0]['sub_sector'] if not sector_info.empty else "N/A"
        
        # Company Card
        st.header(f"{comp_info['company_name']}")
        st.caption(f"**NSE Ticker:** {ticker} | **Sector:** {sector} | **Sub-Sector:** {sub_sector}")
        st.markdown(f"*{comp_info['about_company']}*")
        
        # Get KPIs for latest year
        df_rat = get_ratios(ticker=ticker)
        if not df_rat.empty:
            df_rat = df_rat.sort_values('year', ascending=False)
            latest_rat = df_rat.iloc[0]
            
            st.subheader("Key Performance Indicators")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            roe = latest_rat.get('return_on_equity_pct', pd.NA)
            roce = latest_rat.get('return_on_capital_employed_pct', pd.NA)
            npm = latest_rat.get('net_profit_margin_pct', pd.NA)
            de = latest_rat.get('debt_to_equity', pd.NA)
            rev_cagr = latest_rat.get('revenue_cagr_5yr', pd.NA)
            fcf = latest_rat.get('free_cash_flow_cr', pd.NA)
            
            col1.metric("ROE (%)", f"{roe:.2f}%" if pd.notna(roe) else "N/A")
            col2.metric("ROCE (%)", f"{roce:.2f}%" if pd.notna(roce) else "N/A")
            col3.metric("Net Profit Margin (%)", f"{npm:.2f}%" if pd.notna(npm) else "N/A")
            col4.metric("D/E Ratio", f"{de:.2f}" if pd.notna(de) else "N/A")
            col5.metric("Rev CAGR 5Y (%)", f"{rev_cagr:.2f}%" if pd.notna(rev_cagr) else "N/A")
            col6.metric("Free Cash Flow (Cr)", f"₹{fcf:,.2f}" if pd.notna(fcf) else "N/A")
            
            st.divider()
            
            # 10-year bar chart for Revenue and Net Profit
            df_pl = get_pl(ticker=ticker)
            if not df_pl.empty:
                df_pl = df_pl.sort_values('year')
                st.subheader("10-Year Revenue and Net Profit")
                fig_pl = go.Figure()
                fig_pl.add_trace(go.Bar(x=df_pl['year'], y=df_pl['sales_cr'], name='Revenue', marker_color='indigo'))
                fig_pl.add_trace(go.Bar(x=df_pl['year'], y=df_pl['net_profit_cr'], name='Net Profit', marker_color='teal'))
                fig_pl.update_layout(barmode='group', xaxis_title='Year', yaxis_title='Amount (Cr)')
                st.plotly_chart(fig_pl, use_container_width=True)
            
            # ROE and ROCE dual-axis line chart
            st.subheader("10-Year ROE and ROCE")
            df_rat_asc = df_rat.sort_values('year')
            fig_roe = go.Figure()
            if 'return_on_equity_pct' in df_rat_asc.columns:
                fig_roe.add_trace(go.Scatter(x=df_rat_asc['year'], y=df_rat_asc['return_on_equity_pct'], mode='lines+markers', name='ROE (%)'))
            if 'return_on_capital_employed_pct' in df_rat_asc.columns:
                fig_roe.add_trace(go.Scatter(x=df_rat_asc['year'], y=df_rat_asc['return_on_capital_employed_pct'], mode='lines+markers', name='ROCE (%)'))
            fig_roe.update_layout(xaxis_title='Year', yaxis_title='Percentage (%)')
            st.plotly_chart(fig_roe, use_container_width=True)
            
            # Pros and Cons
            df_pc = get_prosandcons(ticker=ticker)
            if not df_pc.empty:
                st.subheader("Pros & Cons")
                col_p, col_c = st.columns(2)
                with col_p:
                    st.markdown("**Pros**")
                    for p in df_pc['pros'].dropna():
                        st.markdown(f"✅ {p}")
                with col_c:
                    st.markdown("**Cons**")
                    for c in df_pc['cons'].dropna():
                        st.markdown(f"❌ {c}")
