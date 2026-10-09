# Sprint 3 Submission

This package contains the final deliverables for Sprint 3 (Screener & Peer Comparison Engine).

## Directory Structure
- `Source Code/`: Contains the Screener engine (`screener/`), Peer Analytics (`analytics/`), configuration (`config/`), database schema (`db/`), and tests (`tests/`).
- `Datasets/`: Contains the generated outputs `screener_output.xlsx`, `peer_comparison.xlsx`, and `radar_charts/`.
- `Documentation/`: Contains the Verification Report and Final Report.
- `PPT Slides/`: Contains the presentation slides content.
- `Demo Video/`: Contains the demo script.

## Summary of Implementation
- **Screener Engine**: Implements all 15 specified filterable metrics and supports 6 preset screening strategies (Quality Compounder, Value Pick, Growth Accelerator, Dividend Champion, Debt-Free Blue Chip, Turnaround Watch).
- **Composite Scoring**: Calculates a normalized quality score (0-100) combining profitability, cash quality, growth, and leverage.
- **Peer Percentiles**: Calculates percentile rankings for 10 metrics across 11 peer groups. Lower D/E is appropriately rewarded with a higher percentile. 
- **Radar Charts**: Generated for all 100 benchmark/peer evaluations.

## Verification Results & Limitations
- **Worksheet Counts Verified**: `screener_output.xlsx` contains exactly 6 worksheets matching the preset strategies. `peer_comparison.xlsx` contains exactly 12 worksheets (11 recognized peer groups + 1 unassigned group).
- **Test Results**: The 31 automated KPI tests are present, though programmatic execution during this audit was prevented by the Python environment constraints.
- **Schema Drift Identified**: The `peer_percentiles` table schema and implementation are inconsistent. `peer.py` implements the table dynamically at runtime via Pandas `to_sql(if_exists='replace')`, bypassing strict DDL governance. The formal definition is completely absent from `db/schema.sql`. Per governance rules, the database was not modified just to force a schema match.
- **Binary Packaging Blocked**: The `Sprint3_Final_Report.pdf` and `Sprint3_Screener_Peer_Comparison.pptx` could not be programmatically generated. Systemic local Python environment failures ("Access is denied" on `pythoncore-3.14-64\python.exe`) prevented the execution of `gen_pdf.py` and `create_ppt.py`. The canonical Markdown content was packaged in their place to prevent fabricating missing artifacts.
