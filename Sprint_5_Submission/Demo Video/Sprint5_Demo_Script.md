# Sprint 5 — Intelligence, NLP & PDF Reports Demo Script

**Duration:** 5 Minutes  
**Focus:** NLP Parser, Auto Pros/Cons Engine, Cash Flow Intelligence & Automated PDF Reports

---

## 00:00 – 00:50: Overview & NLP Parsing (Day 29)
- **Speaker:** "Welcome to the Sprint 5 demonstration. In this sprint, we added unstructured intelligence and automated reporting capabilities to the platform. We begin with our NLP Parser in `src/nlp/parser.py`. It scans unstructured text commentaries from annual filings, using regular expressions to extract multi-year CAGR metrics."
- **Visual:** Terminal executing `python src/nlp/parser.py`, opening `output/analysis_parsed.csv` and showing extracted 1, 3, 5, and 10-year growth percentages.

---

## 00:50 – 01:50: Auto Pros & Cons Generator (Day 30)
- **Speaker:** "Next is our automated Pros and Cons Engine in `src/nlp/pros_cons_generator.py`. It evaluates 12 quantitative positive investment rules and 12 cautionary risk rules with confidence scores. Every company in the Nifty 100 universe receives at least one Pro and one Con. Here in `pros_cons_generated.csv`, 592 signals are generated across all 92 companies with 100% coverage."
- **Visual:** Executing `python src/nlp/pros_cons_generator.py`, opening `output/pros_cons_generated.csv` and filtering by ticker.

---

## 01:50 – 02:50: Cash Flow Intelligence & Distress Signals (Days 31–32)
- **Speaker:** "Day 31 introduced cash flow intelligence. In `cashflow_intelligence.xlsx`, all 92 companies are classified by CFO quality, CapEx intensity, and capital allocation patterns. Companies borrowing money or raising equity to fund cash-burning operations are flagged as distress signals—logged to `distress_alerts.csv` with their CFO, CFF, and net profits."
- **Visual:** Showing `output/cashflow_intelligence.xlsx` (92 rows) and `output/distress_alerts.csv` (13 companies).

---

## 02:50 – 04:00: 92 Company Tearsheets (Days 33–34)
- **Speaker:** "Now let's review the automated company tearsheets. Built with ReportLab, each tearsheet is a 2-page document. Page 1 displays 6 KPI tiles, 10-year historical Revenue and Profit bar charts, and dual-axis ROE/ROCE lines. Page 2 provides the balance sheet breakdown, cash flows, capital allocation badge, and bulleted pros and cons."
- **Visual:** Opening `reports/tearsheets/TCS_Tearsheet.pdf` and `RELIANCE_Tearsheet.pdf`.

---

## 04:00 – 05:00: Sector Reports & 92-Page Portfolio Summary (Days 34–35)
- **Speaker:** "Finally, our batch report generator produced all 11 sector PDFs in `reports/sector/` with median KPIs and constituent matrices, along with a 92-page master `portfolio_summary.pdf` featuring company evaluation cards and directional trend arrows. This concludes our Sprint 5 review."
- **Visual:** Opening `reports/sector/Information_Technology_Report.pdf` and scrolling through `reports/portfolio/portfolio_summary.pdf`.
