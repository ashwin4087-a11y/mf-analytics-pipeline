import sys
import os
import importlib
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import src.dashboard.utils.db as db_mod
importlib.reload(db_mod)
import src.dashboard.screens as screens_mod
importlib.reload(screens_mod)

from src.dashboard.utils.theme import apply_terminal_theme, render_sidebar_header

st.set_page_config(page_title="Nifty 100 — Capital Allocation", layout="wide", initial_sidebar_state="expanded")
apply_terminal_theme()
render_sidebar_header()
screens_mod.render_screen_capital()
