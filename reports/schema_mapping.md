# SPRINT 3 — Metric Mapping Report

| Metric | Source Table / File | Source Column | Transformation / Formula | Available? |
|--------|----------------------|---------------|---------------------------|------------|
| 1. ROE | `financial_ratios` | `return_on_equity_pct` | Direct pull | ✅ Yes |
| 2. D/E | `financial_ratios` | `debt_to_equity` | Direct pull (Note: Financials sector bypass required) | ✅ Yes |
| 3. FCF | `financial_ratios` | `free_cash_flow_cr` | Direct pull | ✅ Yes |
| 4. Revenue CAGR 5yr | `financial_ratios` | `revenue_cagr_5yr` | Direct pull | ✅ Yes |
| 5. PAT CAGR 5yr | `financial_ratios` | `pat_cagr_5yr` | Direct pull | ✅ Yes |
| 6. OPM | `financial_ratios` | `operating_profit_margin_pct`| Direct pull | ✅ Yes |
| 7. P/E | `market_cap` | `pe_ratio` | Direct pull | ✅ Yes |
| 8. P/B | `market_cap` | `pb_ratio` | Direct pull | ✅ Yes |
| 9. Dividend Yield | `market_cap` | `dividend_yield_pct` | Direct pull | ✅ Yes |
| 10. ICR | `financial_ratios` | `interest_coverage` / `icr_label` | If `icr_label` == "Debt Free", treat as `float('inf')` | ✅ Yes |
| 11. Market Cap | `market_cap` | `market_cap_crore` | Direct pull | ✅ Yes |
| 12. Net Profit | `profitandloss` | `net_profit` | Direct pull | ✅ Yes |
| 13. EPS CAGR | `financial_ratios` | `eps_cagr_5yr` | Direct pull (assuming 5yr as standard CAGR metric) | ✅ Yes |
| 14. Asset Turnover | `financial_ratios` | `asset_turnover` | Direct pull | ✅ Yes |
| 15. Sales | `profitandloss` | `sales` | Direct pull | ✅ Yes |

**Additional Sources required for engine rules:**
* `sectors` table (`broad_sector`) for D/E Financials exclusion and sector-relative scoring.
* `companies` table (`company_name`) for result output.
