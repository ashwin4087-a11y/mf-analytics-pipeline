import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Institutional Terminal Color Palette
COLOR_BG_PRIMARY = "#080d1a"
COLOR_BG_SURFACE = "#0f172a"
COLOR_BG_CARD = "#131d31"
COLOR_BORDER = "#1e2e4a"
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_ACCENT_CYAN = "#0ea5e9"
COLOR_POSITIVE = "#10b981"
COLOR_NEGATIVE = "#f43f5e"
COLOR_WARNING = "#f59e0b"
COLOR_PURPLE = "#8b5cf6"

def apply_terminal_theme():
    """
    Injects ultra-premium institutional financial terminal styling.
    Combines Bloomberg-grade aesthetics with modern institutional research UI.
    """
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global Foundation */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #080d1a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f8fafc !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(8, 13, 26, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #1e2e4a !important;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid #1e2e4a !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    /* Typography Hierarchy */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
        letter-spacing: -0.02em !important;
    }

    p, span, label {
        font-family: 'Inter', sans-serif !important;
        color: #cbd5e1;
    }

    /* Terminal Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #0f172a !important;
        border: 1px solid #1e2e4a !important;
        border-radius: 8px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
        transition: transform 0.15s ease, border-color 0.15s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #0ea5e9 !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #94a3b8 !important;
        margin-bottom: 0.35rem !important;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }

    /* Custom Terminal Cards */
    .terminal-card {
        background-color: #0f172a;
        border: 1px solid #1e2e4a;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    .terminal-card-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #38bdf8;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Badges */
    .terminal-badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.04em;
    }

    .badge-discount {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-caution {
        background-color: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.3);
    }

    .badge-neutral {
        background-color: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* Tables & DataFrames */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1e2e4a !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }

    button[kind="secondary"] {
        background-color: #131d31 !important;
        color: #e2e8f0 !important;
        border: 1px solid #1e2e4a !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }

    button[kind="secondary"]:hover {
        border-color: #0ea5e9 !important;
        color: #38bdf8 !important;
    }

    /* Navigation Radio Pills */
    div[role="radiogroup"] > label {
        background-color: #0f172a !important;
        border: 1px solid #1e2e4a !important;
        border-radius: 6px !important;
        padding: 0.6rem 0.9rem !important;
        margin-bottom: 0.35rem !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }

    div[role="radiogroup"] > label:hover {
        border-color: #0ea5e9 !important;
        background-color: #131d31 !important;
    }

    /* Selectbox & Inputs */
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border-color: #1e2e4a !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
    }

    div[data-baseweb="input"] > div {
        background-color: #0f172a !important;
        border-color: #1e2e4a !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #080d1a;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e2e4a;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #0ea5e9;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_sidebar_header():
    """Renders the persistent institutional terminal sidebar header."""
    header_html = """
    <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid #1e2e4a; margin-bottom: 1.25rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: #0ea5e9; box-shadow: 0 0 10px #0ea5e9;"></div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 800; letter-spacing: 0.08em; color: #f8fafc;">
                NIFTY 100
            </span>
        </div>
        <div style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; margin-top: 0.2rem;">
            FINANCIAL INTELLIGENCE TERMINAL
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.75rem; padding: 0.35rem 0.6rem; background-color: rgba(14, 165, 233, 0.08); border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 4px;">
            <span style="font-size: 0.68rem; font-weight: 600; color: #38bdf8; font-family: 'JetBrains Mono', monospace;">
                ● VERIFIED 92 EQUITIES
            </span>
            <span style="font-size: 0.68rem; font-weight: 600; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                FY2019-2024
            </span>
        </div>
    </div>
    """
    st.sidebar.markdown(header_html, unsafe_allow_html=True)

def get_terminal_chart_layout():
    """
    Returns unified institutional layout parameters for Plotly figures.
    """
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.5)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=40, r=30, t=50, b=40),
        xaxis=dict(
            gridcolor="#1e2e4a",
            zerolinecolor="#24324a",
            tickfont=dict(color="#94a3b8", size=11),
            linecolor="#1e2e4a"
        ),
        yaxis=dict(
            gridcolor="#1e2e4a",
            zerolinecolor="#24324a",
            tickfont=dict(color="#94a3b8", size=11),
            linecolor="#1e2e4a"
        ),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="#1e2e4a",
            borderwidth=1,
            font=dict(color="#cbd5e1", size=11)
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#0ea5e9",
            font=dict(family="JetBrains Mono, monospace", color="#f8fafc", size=12)
        )
    )
