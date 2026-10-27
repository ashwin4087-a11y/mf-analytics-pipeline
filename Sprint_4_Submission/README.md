# Sprint 4 Submission — Dashboard & Valuation

**Nifty 100 Financial Intelligence Platform**  
*Epic 05 & 06: Streamlit Interactive Dashboard + Valuation Module*  
*Days 22–28 | Target: 70 Story Points*

---

## 1. Executive Summary

Sprint 4 delivers the interactive frontend and valuation analytics layer of the Nifty 100 platform.
- **Streamlit Interactive Dashboard (`Source Code/dashboard/`)**: 8 complete screens covering Portfolio Overview, Company Profile, Screener with 6 instant presets, Peer Group Comparison with radar charts, Multi-metric Trends, Sector Summaries, Capital Allocation Treemap, and Annual Reports.
- **Valuation Module (`Source Code/analytics/valuation.py`)**: Automatic calculation of P/E, P/B, EV/EBITDA, FCF yield, 5-year median P/E, and sector median comparables. Identifies companies trading at a discount or caution relative to industry peers.

---

## 2. Directory Structure

```text
Sprint_4_Submission/
├── Source Code/
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── 01_home.py
│   │   │   ├── 02_profile.py
│   │   │   ├── 03_screener.py
│   │   │   ├── 04_peers.py
│   │   │   ├── 05_trends.py
│   │   │   ├── 06_sectors.py
│   │   │   ├── 07_capital.py
│   │   │   └── 08_reports.py
│   │   └── utils/
│   │       └── db.py
│   └── analytics/
│       └── valuation.py
├── Datasets/
│   ├── valuation_summary.xlsx
│   └── valuation_flags.csv
├── Documentation/
│   └── sprint4_dashboard_guide.md
├── PPT - Slides/
│   └── sprint4_presentation_deck.md
├── Demo Video/
│   └── Sprint4_Demo_Script.md
├── SUBMISSION_CHECKLIST.md
└── README.md
```

---

## 3. Verification & Execution

To execute the dashboard locally:
```powershell
streamlit run "Sprint_4_Submission/Source Code/dashboard/app.py"
```

To recompute valuation multiples and flags:
```powershell
python "Sprint_4_Submission/Source Code/analytics/valuation.py"
```
