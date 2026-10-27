import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_ratios

st.set_page_config(page_title="Trend Analysis", layout="wide")
st.title("Trend Analysis")

df_comp = get_companies()
comp_options = df_comp.apply(lambda x: f"{x['company_name']} ({x['id']})", axis=1).tolist()

selected_option = st.selectbox("Search Company Name or Ticker", options=[""] + comp_options)

if selected_option:
    ticker = selected_option.split("(")[-1].replace(")", "").strip()
    df_rat = get_ratios(ticker=ticker)
    
    if not df_rat.empty:
        df_rat = df_rat.sort_values('year')
        
        numeric_cols = df_rat.select_dtypes(include='number').columns.tolist()
        # Filter out years if it's numeric
        numeric_cols = [c for c in numeric_cols if c not in ['year', 'company_id']]
        
        selected_metrics = st.multiselect("Select up to 3 metrics to overlay", options=numeric_cols, max_selections=3)
        
        if selected_metrics:
            fig = go.Figure()
            for metric in selected_metrics:
                # Calculate YoY
                yoy = df_rat[metric].pct_change() * 100
                text_annotations = [f"{v:.1f}%" if pd.notna(v) else "" for v in yoy]
                
                fig.add_trace(go.Scatter(
                    x=df_rat['year'],
                    y=df_rat[metric],
                    mode='lines+markers+text',
                    name=metric,
                    text=text_annotations,
                    textposition="top center"
                ))
            
            fig.update_layout(xaxis_title="Year", yaxis_title="Value", height=600)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found for this company.")
