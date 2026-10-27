import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_ratios, get_companies, get_sectors, get_market_cap

st.set_page_config(page_title="Screener", layout="wide")
st.title("Screener")

# Initialize session state for sliders if not exists
defaults = {
    'roe_min': 0.0, 'de_max': 5.0, 'fcf_min': -50000.0, 'rev_cagr_min': -20.0,
    'pat_cagr_min': -20.0, 'opm_min': -20.0, 'pe_max': 200.0, 'pb_max': 50.0,
    'div_min': 0.0, 'icr_min': -10.0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def apply_preset(preset):
    if preset == 'Quality':
        updates = {'roe_min': 15.0, 'de_max': 1.0, 'fcf_min': 0.0, 'rev_cagr_min': 10.0}
    elif preset == 'Value':
        updates = {'pe_max': 20.0, 'pb_max': 3.0, 'de_max': 2.0, 'div_min': 1.0}
    elif preset == 'Growth':
        updates = {'pat_cagr_min': 20.0, 'rev_cagr_min': 15.0, 'de_max': 2.0}
    elif preset == 'Dividend':
        updates = {'div_min': 2.0, 'fcf_min': 0.0} # Div payout isn't a slider so we skip it
    elif preset == 'Debt-Free':
        updates = {'de_max': 0.0, 'roe_min': 12.0}
    elif preset == 'Turnaround':
        updates = {'rev_cagr_min': 10.0, 'fcf_min': 0.0}
    
    # reset to defaults first
    for k, v in defaults.items():
        st.session_state[k] = v
    # apply specific updates
    for k, v in updates.items():
        st.session_state[k] = v

st.sidebar.header("Presets")
col1, col2 = st.sidebar.columns(2)
col1.button("Quality", on_click=apply_preset, args=('Quality',))
col2.button("Value", on_click=apply_preset, args=('Value',))
col1.button("Growth", on_click=apply_preset, args=('Growth',))
col2.button("Dividend", on_click=apply_preset, args=('Dividend',))
col1.button("Debt-Free", on_click=apply_preset, args=('Debt-Free',))
col2.button("Turnaround", on_click=apply_preset, args=('Turnaround',))

st.sidebar.header("Custom Filters")
st.sidebar.slider("ROE min (%)", -50.0, 100.0, key='roe_min')
st.sidebar.slider("D/E max", 0.0, 10.0, key='de_max')
st.sidebar.slider("FCF min (Cr)", -100000.0, 100000.0, key='fcf_min')
st.sidebar.slider("Revenue CAGR 5Y min (%)", -50.0, 100.0, key='rev_cagr_min')
st.sidebar.slider("PAT CAGR 5Y min (%)", -50.0, 100.0, key='pat_cagr_min')
st.sidebar.slider("OPM min (%)", -50.0, 100.0, key='opm_min')
st.sidebar.slider("P/E max", 0.0, 500.0, key='pe_max')
st.sidebar.slider("P/B max", 0.0, 100.0, key='pb_max')
st.sidebar.slider("Div Yield min (%)", 0.0, 10.0, key='div_min')
st.sidebar.slider("ICR min", -50.0, 200.0, key='icr_min')

# Get latest data
df_rat = get_ratios(year=2024)
if df_rat.empty:
    df_rat = get_ratios(year=2023) # fallback

df_comp = get_companies()
df_sec = get_sectors()
df_mc = get_market_cap()
if not df_mc.empty:
    df_mc = df_mc.sort_values('year').groupby('company_id').tail(1)

# Merge
df = df_rat.merge(df_comp[['id', 'company_name']], left_on='company_id', right_on='id', how='left')
df = df.merge(df_sec[['company_id', 'broad_sector']], on='company_id', how='left')
if not df_mc.empty:
    df = df.merge(df_mc[['company_id', 'pe_ratio', 'pb_ratio', 'dividend_yield_pct']], on='company_id', how='left')
else:
    df['pe_ratio'] = pd.NA
    df['pb_ratio'] = pd.NA
    df['dividend_yield_pct'] = pd.NA

# Fill missing for filtering
df_f = df.copy()

mask = (
    (df_f['return_on_equity_pct'].fillna(-999) >= st.session_state.roe_min) &
    (df_f['debt_to_equity'].fillna(999) <= st.session_state.de_max) &
    (df_f['free_cash_flow_cr'].fillna(-999999) >= st.session_state.fcf_min) &
    (df_f['revenue_cagr_5yr'].fillna(-999) >= st.session_state.rev_cagr_min) &
    (df_f['pat_cagr_5yr'].fillna(-999) >= st.session_state.pat_cagr_min) &
    (df_f['operating_profit_margin_pct'].fillna(-999) >= st.session_state.opm_min) &
    (df_f['pe_ratio'].fillna(9999) <= st.session_state.pe_max) &
    (df_f['pb_ratio'].fillna(9999) <= st.session_state.pb_max) &
    (df_f['dividend_yield_pct'].fillna(-999) >= st.session_state.div_min) &
    (df_f['interest_coverage'].fillna(-999) >= st.session_state.icr_min)
)

filtered = df_f[mask]

# Show result count
st.markdown(f"**{len(filtered)} companies match your filters**")

display_cols = ['company_id', 'company_name', 'broad_sector', 'composite_quality_score', 
                'return_on_equity_pct', 'debt_to_equity', 'free_cash_flow_cr', 
                'revenue_cagr_5yr', 'pat_cagr_5yr', 'operating_profit_margin_pct',
                'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 'interest_coverage']

out_df = filtered[[c for c in display_cols if c in filtered.columns]]

st.dataframe(out_df, use_container_width=True)

csv = out_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='screener_results.csv',
    mime='text/csv'
)
