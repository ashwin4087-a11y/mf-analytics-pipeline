import streamlit as st
import pandas as pd
import plotly.express as px
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

st.set_page_config(page_title="Capital Allocation", layout="wide")
st.title("Capital Allocation Patterns")

ca_path = os.path.join(OUTPUT_DIR, 'capital_allocation.csv')
if not os.path.exists(ca_path):
    st.error("capital_allocation.csv not found. Please run the analytics engine first.")
    st.stop()
    
df_ca = pd.read_csv(ca_path)
# Get the latest year for each company
df_ca = df_ca.sort_values(by='year').groupby('company_id').tail(1).reset_index(drop=True)

# We need to visualize the Treemap. We'll add a root node.
df_ca['Root'] = 'Nifty 100'

# A generic size metric, e.g., 1 if we don't have Market Cap easily merged, 
# but let's try to merge Market Cap from DB for bubble size
import sqlite3
from src.dashboard.utils.db import get_connection
try:
    conn = get_connection()
    mc_df = pd.read_sql("SELECT company_id, market_cap_crore FROM market_cap WHERE year = (SELECT MAX(year) FROM market_cap)", conn)
    df = df_ca.merge(mc_df, on='company_id', how='left')
    df['market_cap_crore'] = df['market_cap_crore'].fillna(1000) # fallback
except:
    df = df_ca.copy()
    df['market_cap_crore'] = 1000

df['market_cap_crore'] = df['market_cap_crore'].abs()

fig = px.treemap(
    df, 
    path=['Root', 'pattern_label', 'company_id'], 
    values='market_cap_crore',
    color='pattern_label',
    title="Treemap of Capital Allocation Patterns (weighted by Market Cap)"
)
fig.update_layout(height=700)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Companies by Pattern")
patterns = sorted(df['pattern_label'].unique())
selected_pattern = st.selectbox("Select Pattern to view companies:", options=patterns)

pattern_df = df[df['pattern_label'] == selected_pattern][['company_id', 'year', 'cfo_sign', 'cfi_sign', 'cff_sign', 'market_cap_crore']]
st.dataframe(pattern_df, use_container_width=True)
