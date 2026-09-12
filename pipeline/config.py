from pathlib import Path

RAW_DATA_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

RAW_FILES = {
    "transactions": "1788499980509-304c1255-08_investor_transactions.csv",
    "holdings": "1788499982117-e3d6ab98-09_portfolio_holdings.csv",
    "benchmark": "1788499982615-f9647ab2-10_benchmark_indices.csv",
    "funds": "1788499983024-b042c300-01_fund_master.csv",
    "nav": "1788499983331-4389156d-02_nav_history.csv",
    "aum": "1788499984134-b0cbf625-03_aum_by_fund_house.csv",
    "sip": "1788499984405-d702a6c6-04_monthly_sip_inflows.csv",
    "category_inflows": "1788499984721-4b860901-05_category_inflows.csv",
    "folio": "1788499985036-da4a0c4a-06_industry_folio_count.csv",
    "performance": "1788499985420-bb134abf-07_scheme_performance.csv",
}

MFAPI_BASE_URL = "https://api.mfapi.in/mf/{amfi_code}"
MFAPI_TIMEOUT = 5
MFAPI_MAX_RETRIES = 2
LIVE_NAV_DAYS = 30

KNOWN_TRANSACTION_TYPES = {"SIP", "Lumpsum", "Redemption"}
