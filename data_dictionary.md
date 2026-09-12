# Bluestock Mutual Fund Analytics Data Dictionary

## Overview
This database contains mutual fund data structured in a star schema, focusing on daily NAVs, investor transactions, performance metrics, and fund metadata.

### `dim_fund`
Dimension table storing static information about mutual fund schemes.
- **amfi_code** (INTEGER, Primary Key): Unique identifier for the fund. Source: `01_fund_master.csv`.
- **fund_house** (TEXT): Name of the AMC/Fund House.
- **scheme_name** (TEXT): Name of the mutual fund scheme.
- **category** (TEXT): Broad category (Equity, Debt, etc.).
- **sub_category** (TEXT): Specific sub-category (Large Cap, Small Cap, etc.).
- **plan** (TEXT): Plan type (Regular, Direct).
- **launch_date** (DATE): Date the fund was launched.
- **benchmark** (TEXT): Benchmark index name.
- **expense_ratio_pct** (REAL): Total expense ratio in percentage.
- **exit_load_pct** (REAL): Exit load percentage.
- **min_sip_amount** (INTEGER): Minimum allowed SIP amount.
- **min_lumpsum_amount** (INTEGER): Minimum allowed lumpsum amount.
- **fund_manager** (TEXT): Name of the primary fund manager.
- **risk_category** (TEXT): Assigned risk level (Low, Moderate, High, etc.).
- **sebi_category_code** (TEXT): SEBI standardized category code.

### `dim_date`
Dimension table representing unique dates across the database.
- **date** (DATE, Primary Key): Date in YYYY-MM-DD format. Derived from transaction and NAV dates.
- **year** (INTEGER): Extracted Year.
- **month** (INTEGER): Extracted Month.
- **day** (INTEGER): Extracted Day.
- **day_of_week** (INTEGER): Day of the week (0 = Monday).
- **is_weekend** (BOOLEAN): True if Saturday or Sunday.

### `fact_nav`
Fact table recording historical Net Asset Values (NAV).
- **amfi_code** (INTEGER, Foreign Key): Refers to `dim_fund`.
- **date** (DATE, Foreign Key): Refers to `dim_date`.
- **nav** (REAL): Net Asset Value.
- **is_trading_day** (BOOLEAN): True if the NAV is an original observation from a trading day, False if it was forward-filled to cover a non-trading day (weekend/holiday).
*Note: Missing weekend/holiday NAVs were forward-filled up to a limit of 4 days to ensure continuous timelines. Filtered for nav > 0. Source: `02_nav_history.csv`.*

### `fact_transactions`
Fact table storing individual investor transactions.
- **transaction_id** (INTEGER, Primary Key): Auto-incrementing identifier.
- **investor_id** (TEXT): Unique investor identifier. Source: `08_investor_transactions.csv`.
- **transaction_date** (DATE, Foreign Key): Date of transaction. Refers to `dim_date`.
- **amfi_code** (INTEGER, Foreign Key): Refers to `dim_fund`.
- **transaction_type** (TEXT): Type of transaction. Standardised to 'SIP', 'Lumpsum', or 'Redemption'.
- **amount_inr** (INTEGER): Transaction amount in INR. Validated to be > 0.
- **state** (TEXT): Investor state.
- **city** (TEXT): Investor city.
- **city_tier** (TEXT): Tier classification of the city.
- **age_group** (TEXT): Investor age group.
- **gender** (TEXT): Investor gender.
- **annual_income_lakh** (REAL): Investor income in Lakhs.
- **payment_mode** (TEXT): Mode of payment (UPI, Netbanking, etc.).
- **kyc_status** (TEXT): KYC Verification status.

### `fact_performance`
Fact table for scheme performance metrics.
- **amfi_code** (INTEGER, Primary Key): Refers to `dim_fund`. Source: `07_scheme_performance.csv`.
- **scheme_name** (TEXT): Scheme Name (denormalized).
- **fund_house** (TEXT): AMC (denormalized).
- **category** (TEXT): Broad category (denormalized).
- **plan** (TEXT): Plan type (denormalized).
- **return_1yr_pct** (REAL): 1-Year annualized return percentage. Validated as numeric.
- **return_3yr_pct** (REAL): 3-Year annualized return percentage.
- **return_5yr_pct** (REAL): 5-Year annualized return percentage.
- **benchmark_3yr_pct** (REAL): 3-Year benchmark return percentage.
- **alpha** (REAL): Alpha metric.
- **beta** (REAL): Beta metric.
- **sharpe_ratio** (REAL): Sharpe ratio.
- **sortino_ratio** (REAL): Sortino ratio.
- **std_dev_ann_pct** (REAL): Annualized standard deviation.
- **max_drawdown_pct** (REAL): Maximum drawdown percentage.
- **aum_crore** (INTEGER): Asset under management in crores.
- **expense_ratio_pct** (REAL): Expense ratio percentage.
- **morningstar_rating** (INTEGER): Rating out of 5.
- **risk_grade** (TEXT): Risk classification.

### `fact_aum`
Fact table tracking AUM at the AMC level over time.
- **date** (DATE, Foreign Key): Refers to `dim_date`. Source: `03_aum_by_fund_house.csv`.
- **fund_house** (TEXT): AMC Name.
- **aum_lakh_crore** (REAL): AUM in Lakh Crores.
- **aum_crore** (INTEGER): AUM in Crores.
- **num_schemes** (INTEGER): Number of schemes managed.

### Other Tables
- `fact_holdings`: Contains portfolio holdings (`09_portfolio_holdings.csv`).
- `fact_benchmark_indices`: Daily values of benchmark indices (`10_benchmark_indices.csv`).
- `fact_monthly_sip`: Monthly SIP industry inflows (`04_monthly_sip_inflows.csv`).
- `fact_category_inflows`: Monthly industry flows by category (`05_category_inflows.csv`).
- `fact_industry_folios`: Total industry folio counts over time (`06_industry_folio_count.csv`).
