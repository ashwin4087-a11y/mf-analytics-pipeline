# Sprint 2 Demo Script / Video Narrative

**1. Introduction**
Hello everyone, and welcome to the Sprint 2 demo for the Nifty 100 Financial Intelligence Platform.

**2. Sprint 2 Objective**
In this sprint, our goal was to build the Financial Ratio Engine, which dynamically computes KPIs, compound annual growth rates (CAGRs), and cash-flow quality metrics from our base financial statements, and integrates them into our SQLite database.

**3. Ratio-Engine Architecture**
Our ratio engine uses a robust pipeline: it first loads P&L, balance sheet, and cash flow data, deduplicates it, and joins the statements into a unified timeline. Then, it runs our core KPI logic over the integrated dataset.

**4. KPI Expansion**
We expanded the ratio engine's calculation logic to meet the project’s complex requirements. We added 21 new pure-function KPIs to our previous 30, expanding the engine’s mathematical coverage.

**5. 51 Computed KPIs / 66 Total Columns**
With this expansion, our engine now successfully produces 51 computed KPIs across 66 total `financial_ratios` columns. This covers extensive profitability, leverage, efficiency, and cash-flow metrics. 

**6. CAGR and Cash-Flow Logic**
We’ve fully implemented 3, 5, and 10-year CAGRs, handling state transitions like "Turnarounds" or "Decline to Loss" without throwing numeric errors. We also implemented advanced cash-flow logic, analyzing trailing 5-year averages of CFO-to-PAT ratios and CapEx intensity to dynamically assign capital allocation patterns to every company.

**7. Edge-Case Handling**
The engine strictly handles edge cases—such as zero or negative equity, and debt-free corporate structures—outputting logical string flags instead of dividing by zero.

**8. Automated Testing — 31/31 Passing**
To ensure the math is absolutely correct, we implemented a comprehensive unit test suite covering all logic and edge cases. I am happy to report that all 31 out of 31 automated tests are passing.

**9. Database Integration — 1,070 Legitimate Rows**
When we run the ETL pipeline with strict data governance rules in place, the engine legitimately integrates 1,070 ratio records into our SQLite database without a single foreign key violation.

**10. Explain the 1,100+ Gate**
However, the Sprint 2 exit gate required 1,100+ integrated rows. 

**11. Explain the 8 Missing Master Records**
The standalone pipeline actually generates 1,161 standalone ratio records, but 91 ratio records could not be integrated because their company IDs are absent from the supplied authoritative 92-company master dataset. There are 8 missing master records (such as ZOMATO, WIPRO, and VEDL).

**12. Explain Why the 91 Rows Were Not Force-Integrated**
These records were not force-integrated because doing so would require fabricating or manually inferring master-data records and would violate the project's established data-governance and foreign-key integrity requirements.

**13. Demonstrate Generated Artifacts**
Despite this, the engine successfully outputs the required artifacts, including `capital_allocation.csv` detailing the capital structures of the dataset, and `ratio_edge_cases.log` which cleanly handles the upstream source discrepancies.

**14. Final Status**
Our final status for this sprint is: **Substantially Complete / Blocked by Source Data Limitation**. 

**15. Conclusion**
The Financial Ratio Engine is substantially complete and its calculation logic has been expanded to 51 computed KPIs, with all 31 automated tests passing. The remaining Sprint 2 exit-gate limitation is the 1,100-plus integrated-row requirement. The supplied authoritative master dataset contains 92 companies, leaving 91 ratio records associated with eight company IDs that cannot be integrated without fabricating master data. We have therefore preserved data integrity and documented the source-data limitation rather than artificially inflating the database.
