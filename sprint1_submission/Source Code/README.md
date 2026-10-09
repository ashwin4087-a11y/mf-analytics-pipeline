# Source Code Deliverables - Sprint 1

This folder contains the actual production source code files and tests for Sprint 1.

## Deliverable Files Included

- **`loader.py`**: Complete 12-table ETL loader engine with deduplication, ticker/year normalization, and foreign-key pre-filtering.
- **`validator.py`**: Data Quality Engine validating rules DQ-01 through DQ-16 and outputting validation reports.
- **`normaliser.py`**: Standardizers for tickers (`normalize_ticker()`) and fiscal years (`normalize_year()`).
- **`schema.sql`**: SQLite DDL schema for all 12 Sprint 1 tables with foreign keys.
- **`tests/`**: Unit test suite containing `tests/etl/` and `tests/dq/`.
