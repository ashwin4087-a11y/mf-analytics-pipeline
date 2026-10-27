# Sprint 5 Submission — Intelligence, NLP & PDF Reports

**Nifty 100 Financial Intelligence Platform**  
*Epic 07, 08 & 09: Cash Flow Intelligence + Reports + NLP*  
*Days 29–35 | Target: 70 Story Points*

---

## 1. Executive Summary

Sprint 5 completes the automated intelligence generation and document delivery layer of the Nifty 100 platform:
1. **NLP Text Parser (`Source Code/nlp/parser.py`)**: Automatically extracts CAGR growth numbers and ROE from unstructured text commentary in `analysis.xlsx` using regex extraction with ratio engine cross-validation.
2. **Auto Pros/Cons Generator (`Source Code/nlp/pros_cons_generator.py`)**: Evaluates 12 quantitative Pro rules and 12 Con rules per company with confidence scores (>60%), ensuring 100% company coverage (92/92 companies have >= 1 Pro and >= 1 Con).
3. **Cash Flow Intelligence (`Source Code/analytics/cashflow_kpis.py`)**: Classifies all 92 companies across CFO Quality score, CapEx Intensity, Distress Signals (CFO < 0 & CFF > 0), Deleveraging actions, and Capital Allocation patterns.
4. **Automated Reporting Suite (`Source Code/reports/`)**:
   - **92 Company Tearsheets**: 2-page executive PDFs containing KPI tiles, 10-year revenue/profit bars, ROE/ROCE lines, balance sheet breakdown, cash flows, capital allocation badge, and bulleted pros/cons.
   - **11 Sector Reports**: 11 PDFs covering all GICS sectors with median KPI summaries and company ranking tables.
   - **Portfolio Summary PDF**: 92-page compendium with one page per company featuring top 6 KPIs and directional trend arrows (↑ ↓ →).

---

## 2. Directory Structure

```text
Sprint_5_Submission/
├── Source Code/
│   ├── nlp/
│   │   ├── parser.py
│   │   └── pros_cons_generator.py
│   ├── analytics/
│   │   └── cashflow_kpis.py
│   └── reports/
│       ├── tearsheet.py
│       └── batch_reports.py
├── Datasets/
│   ├── analysis_parsed.csv
│   ├── parse_failures.csv
│   ├── pros_cons_generated.csv
│   ├── cashflow_intelligence.xlsx
│   ├── distress_alerts.csv
│   ├── capital_allocation.csv
│   ├── pattern_changes.csv
│   └── skipped_tearsheets.csv
├── Documentation/
│   ├── Reports/
│   │   ├── tearsheets/          # 92 individual 2-page company tearsheet PDFs
│   │   ├── sector/              # 11 sector intelligence PDFs
│   │   └── portfolio/           # 92-page portfolio_summary.pdf
│   └── sprint5_validation_evidence.txt
├── PPT - Slides/
│   └── sprint5_presentation_deck.md
├── Demo Video/
│   └── Sprint5_Demo_Script.md
├── SUBMISSION_CHECKLIST.md
└── README.md
```

---

## 3. Execution & Reproduction Commands

To reproduce all Sprint 5 deliverables:

```powershell
python "Sprint_5_Submission/Source Code/nlp/parser.py"
python "Sprint_5_Submission/Source Code/nlp/pros_cons_generator.py"
python "Sprint_5_Submission/Source Code/analytics/cashflow_kpis.py"
python "Sprint_5_Submission/Source Code/reports/tearsheet.py"
python "Sprint_5_Submission/Source Code/reports/batch_reports.py"
```
