import sys
import os
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.dashboard.utils.theme import apply_terminal_theme, render_sidebar_header
from src.dashboard.screens import (
    render_screen_home,
    render_screen_profile,
    render_screen_screener,
    render_screen_peers,
    render_screen_trends,
    render_screen_sectors,
    render_screen_capital,
    render_screen_reports
)

st.set_page_config(
    page_title="NIFTY 100 — Financial Intelligence Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global institutional terminal theme
apply_terminal_theme()
render_sidebar_header()

# Persistent Institutional Navigation
NAV_MAP = {
    "01  📊  Portfolio Pulse (Home)": render_screen_home,
    "02  🏢  Company Profile Audit": render_screen_profile,
    "03  🔍  Quantitative Screener": render_screen_screener,
    "04  👥  Peer Benchmarking & Radars": render_screen_peers,
    "05  📈  Multi-Metric Trend Analytics": render_screen_trends,
    "06  🌐  Sector Intelligence": render_screen_sectors,
    "07  🗺️  Capital Allocation Treemap": render_screen_capital,
    "08  📄  Annual Reports & Filings": render_screen_reports
}

st.sidebar.markdown('<div class="terminal-card-title">NAVIGATION TERMINAL</div>', unsafe_allow_html=True)

if 'active_nav_screen' not in st.session_state:
    st.session_state.active_nav_screen = list(NAV_MAP.keys())[0]

selected_screen = st.sidebar.radio(
    "Terminal Navigation",
    options=list(NAV_MAP.keys()),
    index=list(NAV_MAP.keys()).index(st.session_state.active_nav_screen),
    label_visibility="collapsed"
)

st.session_state.active_nav_screen = selected_screen

# Persistent Institutional Sidebar Footer
st.sidebar.markdown("""
<div style="margin-top: 2rem; padding: 0.75rem; background-color: #0f172a; border: 1px solid #1e2e4a; border-radius: 6px;">
    <div style="font-size: 0.68rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">
        SYSTEM HEALTH
    </div>
    <div style="font-size: 0.72rem; color: #10b981; font-family: 'JetBrains Mono'; margin-top: 0.2rem;">
        ● DATABASE: ACTIVE (1.87 MB)
    </div>
    <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.25rem;">
        FastAPI Backend • SQLite Star Schema
    </div>
</div>
""", unsafe_allow_html=True)

# Render the selected screen
screen_fn = NAV_MAP[selected_screen]
screen_fn()
