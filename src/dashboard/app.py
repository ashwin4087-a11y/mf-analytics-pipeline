import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Nifty 100 Financial Intelligence Platform")

st.markdown("""
Welcome to the Nifty 100 Analytics dashboard. Use the sidebar to navigate between screens:
- **01 Home**: High-level KPIs and sector breakdowns
- **02 Profile**: Deep-dive into an individual company's financials
- **03 Screener**: Filter companies based on custom criteria
- **04 Peers**: Compare companies against their sector peers
- **05 Trends**: Multi-metric trend analysis
- **06 Sectors**: Sector-level metrics and bubble charts
- **07 Capital**: Capital allocation treemap
- **08 Reports**: Links to Annual Reports
""")

st.sidebar.success("Select a page above.")
