# Sprint 6 Submission Checklist & Verification Audit

| Requirement | Expected File/Path | Actual Location in Submission | Status | Validation Method & Result |
|---|---|---|---|---|
| **D-19: Cluster Labels Table** | `output/cluster_labels.csv` | `Sprint_6_Submission/Datasets/cluster_labels.csv` | **VERIFIED COMPLETE** | 100 companies assigned across 5 distinct clusters using StandardScaler & KMeans(k=5) |
| **D-20: FastAPI REST Server** | `src/api/main.py` | `Sprint_6_Submission/Source Code/api/main.py` | **VERIFIED COMPLETE** | All 16 routes operational; includes X-Response-Time-ms headers and filter support |
| **D-21: Pytest HTML Test Report** | `reports/pytest_report.html` | `Sprint_6_Submission/Documentation/pytest_report.html` | **VERIFIED COMPLETE** | 130 tests executed across ETL, DQ01-16, APIs, & KPIs; 130 passed, 0 failed in 6.30s |
| **D-22: Analyst Guide PDF** | `docs/analyst_guide.pdf` | `Sprint_6_Submission/Documentation/analyst_guide.pdf` | **VERIFIED COMPLETE** | 10-topic operational manual covering screener, clustering, radar, and REST API |
| **D-23: Acceptance Checklist PDF** | `docs/acceptance_checklist.pdf` | `Sprint_6_Submission/Documentation/acceptance_checklist.pdf` | **VERIFIED COMPLETE** | 17-gate criteria verified covering data pipelines, accuracy, models, and delivery |
| **Elbow Optimization Plot** | `reports/elbow_plot.png` | `Sprint_6_Submission/Documentation/elbow_plot.png` | **VERIFIED COMPLETE** | Clear inflection point at k=5 across inertia curve evaluated for k=1..9 |
| **Feature Correlation Heatmap** | `reports/correlation_heatmap.png` | `Sprint_6_Submission/Documentation/correlation_heatmap.png` | **VERIFIED COMPLETE** | Correlation matrix heatmap rendered across ROE, D/E, Revenue Growth, OPM, and FCF |
| **Outlier Detection Report** | `output/outlier_report.csv` | `Sprint_6_Submission/Datasets/outlier_report.csv` | **VERIFIED COMPLETE** | Statistical outliers (|z-score| > 3.0 vs sector median) detected and logged |
| **Portfolio Cluster Stats** | `output/portfolio_stats.csv` | `Sprint_6_Submission/Datasets/portfolio_stats.csv` | **VERIFIED COMPLETE** | Mean and median metric profiles calculated for each of the 5 clusters |
| **OpenAPI 3.1.0 Specification** | `docs/openapi.json` | `Sprint_6_Submission/Documentation/openapi.json` | **VERIFIED COMPLETE** | Validated OpenAPI 3.1.0 JSON schema (18.1 KB) for all 16 endpoints |
| **Postman Collection v2.1** | `docs/postman_collection.json` | `Sprint_6_Submission/Documentation/postman_collection.json` | **VERIFIED COMPLETE** | Exported Postman collection (6.8 KB) containing pre-configured request calls |
| **Presentation Deck** | PPT - Slides | `Sprint_6_Submission/PPT - Slides/sprint6_presentation_deck.md` | **COMPLETE (MARKDOWN)** | Slide-by-slide presentation deck notes; dedicated PPTX not recorded |
| **Demo Video Walkthrough** | Demo Video | `Sprint_6_Submission/Demo Video/Sprint6_Demo_Script.md` | **COMPLETE (SCRIPT)** | 5-minute timed walkthrough script; video file (.mp4) not pre-recorded |
| **Overall Sprint Status** | Full Sprint 6 Delivery | `Sprint_6_Submission/` | **VERIFIED COMPLETE** | All deliverables present, tested, and submission-ready |
