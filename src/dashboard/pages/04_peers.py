import sys
import os
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.dashboard.utils.theme import apply_terminal_theme, render_sidebar_header
from src.dashboard.screens import render_screen_peers

st.set_page_config(page_title="Nifty 100 — Peer Comparison", layout="wide", initial_sidebar_state="expanded")
apply_terminal_theme()
render_sidebar_header()
render_screen_peers()
