import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.dashboard.utils.db import get_peers, get_companies

st.set_page_config(page_title="Peer Comparison", layout="wide")
st.title("Peer Comparison")

df_peers = get_peers()
if df_peers.empty:
    st.error("No peer data available.")
    st.stop()

groups = df_peers['peer_group'].unique().tolist()
selected_group = st.selectbox("Select Peer Group", options=groups)

if selected_group:
    group_df = df_peers[df_peers['peer_group'] == selected_group]
    
    # Merge company names
    df_comp = get_companies()
    group_df = group_df.merge(df_comp[['id', 'company_name']], left_on='company_id', right_on='id', how='left')
    
    # Company selector for radar chart
    companies = group_df['company_name'].unique().tolist()
    selected_company = st.selectbox("Select Company for Radar Chart", options=companies)
    
    if selected_company:
        comp_row = group_df[group_df['company_name'] == selected_company].iloc[0]
        
        # Calculate group averages
        numeric_cols = group_df.select_dtypes(include='number').columns
        # Drop is_benchmark from radar if present
        metrics = [c for c in numeric_cols if c not in ['is_benchmark']]
        
        avg_row = group_df[metrics].mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[comp_row[m] for m in metrics],
            theta=metrics,
            fill='toself',
            name=selected_company
        ))
        fig.add_trace(go.Scatterpolar(
            r=[avg_row[m] for m in metrics],
            theta=metrics,
            fill='toself',
            name=f"{selected_group} Average"
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Peer Group KPI Table")
    # Highlight benchmark row
    def highlight_benchmark(row):
        if row.get('is_benchmark', 0) == 1:
            return ['background-color: gold'] * len(row)
        return [''] * len(row)
        
    st.dataframe(group_df.style.apply(highlight_benchmark, axis=1), use_container_width=True)
