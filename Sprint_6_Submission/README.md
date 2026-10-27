# Sprint 6 Submission — API, ML & Quality Assurance

**Nifty 100 Financial Intelligence Platform**  
*Epic 10, 11 & 12: Machine Learning Clustering + REST API + QA & Delivery*  
*Days 36–45 | Target: 80 Story Points*

---

## 1. Executive Summary

Sprint 6 completes the core delivery and quality assurance layers of the Nifty 100 platform. It introduces:
1. **Machine Learning Clustering Module (`src/analytics/clustering.py`)**:
   - Applies `StandardScaler` and `KMeans(n_clusters=5)` to company fundamentals (ROE, D/E, Revenue Growth, FCF Growth, OPM).
   - Generates Elbow optimization plot (`Documentation/elbow_plot.png`), Correlation Heatmap (`Documentation/correlation_heatmap.png`), Outlier Report (`Datasets/outlier_report.csv`), and Cluster Statistics (`Datasets/portfolio_stats.csv`).
2. **Production-Ready REST API (`src/api/main.py`)**:
   - FastAPI server exposing all 16 specified endpoints across health, companies, financial statements, ratios, screener, sectors, peers, radar comparisons, valuation, and documents.
   - Comprehensive OpenAPI 3.1.0 schema (`Documentation/openapi.json`) and Postman collection (`Documentation/postman_collection.json`).
3. **Automated Test Suite & QA (`tests/`)**:
   - 130 comprehensive unit and integration tests across ETL normalisers, Data Quality rules (DQ01–DQ16), KPI formulas, screener logic, and API endpoints.
   - 100% test pass rate (130 passed, 0 failed in 6.30s), documented in `Documentation/pytest_report.html`.
4. **Documentation & Delivery (`Documentation/`)**:
   - `Documentation/analyst_guide.pdf`: Operational manual for equity research analysts.
   - `Documentation/acceptance_checklist.pdf`: Formal 17-gate sign-off checklist.

---

## 2. Deliverables Inventory

| Deliverable ID | Requirement | Submission Location | Verification Status |
|---|---|---|---|
| **D-19** | Cluster Labels Table | `Datasets/cluster_labels.csv` | **VERIFIED COMPLETE** (100 cos assigned to 5 clusters) |
| **D-20** | FastAPI Server (16 Endpoints) | `Source Code/api/main.py` | **VERIFIED COMPLETE** (All 16 routes operational) |
| **D-21** | Pytest HTML Test Report | `Documentation/pytest_report.html` | **VERIFIED COMPLETE** (130/130 passed, 0 failed) |
| **D-22** | Analyst Guide PDF | `Documentation/analyst_guide.pdf` | **VERIFIED COMPLETE** (10 topics rendered) |
| **D-23** | Acceptance Checklist PDF | `Documentation/acceptance_checklist.pdf` | **VERIFIED COMPLETE** (17 criteria evaluated) |
| — | Elbow Optimization Plot | `Documentation/elbow_plot.png` | **VERIFIED COMPLETE** (Inertia curve k=1..9) |
| — | Correlation Heatmap | `Documentation/correlation_heatmap.png` | **VERIFIED COMPLETE** (Feature correlation matrix) |
| — | Outlier Detection Report | `Datasets/outlier_report.csv` | **VERIFIED COMPLETE** (|z-score| > 3.0 vs sector) |
| — | Portfolio Cluster Stats | `Datasets/portfolio_stats.csv` | **VERIFIED COMPLETE** (5 cluster distributions) |
| — | OpenAPI 3.1.0 Specification | `Documentation/openapi.json` | **VERIFIED COMPLETE** (18.1 KB) |
| — | Postman Collection v2.1 | `Documentation/postman_collection.json` | **VERIFIED COMPLETE** (6.8 KB) |
| — | Presentation Deck | `PPT - Slides/sprint6_presentation_deck.md` | **COMPLETE (MARKDOWN)** (Slide-by-slide deck) |
| — | Demo Walkthrough Script | `Demo Video/Sprint6_Demo_Script.md` | **COMPLETE (SCRIPT)** (5-minute timed demo script) |

---

## 3. Directory Structure

```text
Sprint_6_Submission/
├── Datasets/
│   ├── cluster_labels.csv
│   ├── outlier_report.csv
│   └── portfolio_stats.csv
├── Demo Video/
│   └── Sprint6_Demo_Script.md
├── Documentation/
│   ├── acceptance_checklist.pdf
│   ├── analyst_guide.pdf
│   ├── correlation_heatmap.png
│   ├── elbow_plot.png
│   ├── openapi.json
│   ├── postman_collection.json
│   ├── pytest_report.html
│   └── sprint6_validation_evidence.txt
├── PPT - Slides/
│   └── sprint6_presentation_deck.md
├── Source Code/
│   ├── analytics/
│   │   └── clustering.py
│   ├── api/
│   │   ├── generate_openapi.py
│   │   └── main.py
│   ├── reports/
│   │   └── generate_docs.py
│   └── tests/
│       ├── test_api.py
│       ├── test_dq.py
│       ├── test_kpis.py
│       ├── test_normalisers.py
│       ├── test_screener.py
│       └── test_sprints_4_5_6.py
├── README.md
└── SUBMISSION_CHECKLIST.md
```

---

## 4. Verification & Reproduction Commands

To reproduce the Sprint 6 outputs from the root project environment:

```powershell
# 1. Run Machine Learning Clustering Pipeline
.venv_final\Scripts\python.exe -m src.analytics.clustering

# 2. Run Test Suite (130 Tests)
.venv_final\Scripts\python.exe -m pytest tests/ -o pythonpath=. --html=reports/pytest_report.html --self-contained-html

# 3. Export OpenAPI & Postman specs
.venv_final\Scripts\python.exe -m src.api.generate_openapi

# 4. Generate Analyst Guide and Acceptance Checklist PDFs
.venv_final\Scripts\python.exe -m src.reports.generate_docs

# 5. Start FastAPI Server
.venv_final\Scripts\uvicorn.exe src.api.main:app --host 127.0.0.1 --port 8000
```
