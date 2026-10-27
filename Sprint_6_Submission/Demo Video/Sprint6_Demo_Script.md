# Sprint 6 — API, ML & Quality Assurance Demo Script

**Duration:** 5 Minutes  
**Focus:** FastAPI 16 Endpoints, OpenAPI & Postman, KMeans Clustering, and 130-Test Pytest Suite

---

## 00:00 – 00:50: Introduction & KMeans Clustering (Days 36–37)
- **Speaker:** "Welcome to the Sprint 6 demonstration—the capstone delivery of the Nifty 100 Financial Intelligence Platform. We begin with our unsupervised machine learning clustering pipeline in `src/analytics/clustering.py`. It scales 5 fundamental metrics using `StandardScaler` and fits KMeans with k=5 clusters."
- **Visual:** Executing `python src/analytics/clustering.py`, displaying `reports/elbow_plot.png`, `reports/correlation_heatmap.png`, and `output/cluster_labels.csv`.

---

## 00:50 – 02:30: FastAPI Server & 16 Endpoints (Days 38–40)
- **Speaker:** "Next is our production FastAPI REST service in `src/api/main.py`. It exposes 16 high-performance endpoints. Let's start the server with Uvicorn. Navigating to `http://localhost:8000/docs` reveals the interactive OpenAPI documentation."
- **Visual:** Launching Uvicorn, opening `/docs`, testing `/api/v1/health` (showing DB row counts), `/api/v1/companies`, `/api/v1/screener`, and `/api/v1/companies/TCS/tearsheet` (binary PDF download).

---

## 02:30 – 03:30: OpenAPI Specification & Postman Collection
- **Speaker:** "For external client integration, we automatically export `docs/openapi.json` and a pre-configured `docs/postman_collection.json`. Developers can import this directly into Postman or automated CI pipelines."
- **Visual:** Showing `docs/openapi.json` and `docs/postman_collection.json`.

---

## 03:30 – 04:30: Automated Quality Assurance Test Suite (Days 41–42)
- **Speaker:** "Our testing framework uses pytest. Let's run the full test suite. It executes 130 automated test cases across ETL, Data Quality rules, KPI formulas, screener presets, and API integration. All 130 tests pass with zero failures in under 7 seconds, compiling into a self-contained HTML report."
- **Visual:** Executing `python -m pytest tests/ --html=reports/pytest_report.html`, opening `reports/pytest_report.html` in browser.

---

## 04:30 – 05:00: Analyst Guide & Acceptance Checklist Sign-Off (Days 44–45)
- **Speaker:** "Finally, our delivery documentation includes `docs/analyst_guide.pdf` covering all 10 platform modules and the signed `docs/acceptance_checklist.pdf` completing all 23 project deliverables. Thank you."
- **Visual:** Opening `docs/analyst_guide.pdf` and `docs/acceptance_checklist.pdf`.
