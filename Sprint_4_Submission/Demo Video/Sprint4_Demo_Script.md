# Sprint 4 — Dashboard & Valuation Demo Script

**Duration:** 5 Minutes  
**Focus:** Streamlit Multi-Page Dashboard & Valuation Engine

---

## 00:00 – 00:45: Introduction & Architecture
- **Speaker:** "Welcome to the Sprint 4 demonstration of the Nifty 100 Financial Intelligence Platform. In this sprint, we transitioned our data models into an interactive executive dashboard and automated valuation engine."
- **Visual:** Terminal launching `streamlit run src/dashboard/app.py`, navigating to `http://localhost:8501`.

---

## 00:45 – 01:45: Screen 1 (Home) & Screen 2 (Company Profile)
- **Speaker:** "Screen 1 presents the portfolio pulse—average ROE, median P/E, median D/E, and debt-free counts across years 2019 to 2024. Next, we transition to Screen 2: Company Profile. Selecting TCS shows 10 years of revenue compounding, net margin resilience, and balance sheet capital distribution."
- **Visual:** Slicing years on Home screen, selecting TCS and RELIANCE on Profile screen.

---

## 01:45 – 02:45: Screen 3 (Screener) & Screen 4 (Peer Comparison)
- **Speaker:** "Screen 3 demonstrates our custom screener. Analysts can manipulate 10 sliders or click pre-configured strategy presets like 'Quality' or 'Debt-Free'. Screen 4 allows cohort comparison, rendering radar charts against peer group medians."
- **Visual:** Clicking 'Quality' preset, exporting CSV, selecting 'Private Banks' cohort on Peers screen.

---

## 02:45 – 03:45: Screens 5–8 (Trends, Sectors, Capital Map, Reports)
- **Speaker:** "Screens 5 through 8 provide sector analytics, the capital allocation treemap, and instant access to original annual reports."
- **Visual:** Navigating through Trends, Sectors, Capital Allocation treemap, and Annual Reports.

---

## 03:45 – 05:00: Valuation Engine & Summary
- **Speaker:** "Finally, our valuation pipeline calculates P/E multiples against 5-year and sector medians. It automatically flags companies in discount or caution territory, exported to valuation_summary.xlsx and valuation_flags.csv. This concludes Sprint 4."
- **Visual:** Showing `output/valuation_summary.xlsx` and `valuation_flags.csv`.
