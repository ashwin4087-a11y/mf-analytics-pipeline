import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_connection

st.set_page_config(page_title="Annual Reports", layout="wide")
st.title("Annual Reports")

conn = get_connection()
query = """
SELECT c.company_name, d.year, d.annual_report
FROM companies c
JOIN documents d ON c.id = d.company_id
WHERE d.annual_report IS NOT NULL AND d.annual_report != 'NA'
ORDER BY c.company_name, d.year DESC
"""
df = pd.read_sql(query, conn)

if not df.empty:
    st.subheader("Available Annual Reports")
    # Make links clickable using st.data_editor or st.write
    st.dataframe(
        df,
        column_config={
            "annual_report": st.column_config.LinkColumn("Annual Report Link")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No annual reports available.")
