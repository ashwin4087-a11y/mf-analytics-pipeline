-- Nifty 100 Financial Intelligence Platform - Database Schema
-- 12 tables as per Day 1 implementation requirements.

CREATE TABLE companies (
    id VARCHAR PRIMARY KEY,
    company_logo TEXT,
    company_name VARCHAR NOT NULL,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value NUMERIC,
    book_value NUMERIC,
    roce_percentage NUMERIC,
    roe_percentage NUMERIC
);

CREATE TABLE profitandloss (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    sales NUMERIC,
    expenses NUMERIC,
    operating_profit NUMERIC,
    opm_percentage NUMERIC,
    other_income NUMERIC,
    interest NUMERIC,
    depreciation NUMERIC,
    profit_before_tax NUMERIC,
    tax_percentage NUMERIC,
    net_profit NUMERIC,
    eps NUMERIC,
    dividend_payout NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE balancesheet (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    equity_capital NUMERIC,
    reserves NUMERIC,
    borrowings NUMERIC,
    other_liabilities NUMERIC,
    total_liabilities NUMERIC,
    fixed_assets NUMERIC,
    cwip NUMERIC,
    investments NUMERIC,
    other_asset NUMERIC,
    total_assets NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE cashflow (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    operating_activity NUMERIC,
    investing_activity NUMERIC,
    financing_activity NUMERIC,
    net_cash_flow NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE analysis (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    PRIMARY KEY (company_id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE documents (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    annual_report TEXT,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    pros TEXT,
    cons TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE sectors (
    company_id VARCHAR PRIMARY KEY,
    broad_sector VARCHAR,
    sub_sector VARCHAR,
    index_weight_pct NUMERIC,
    market_cap_category VARCHAR,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE stock_prices (
    company_id VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    volume INTEGER,
    adjusted_close NUMERIC,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE market_cap (
    company_id VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    market_cap_crore NUMERIC,
    enterprise_value_crore NUMERIC,
    pe_ratio NUMERIC,
    pb_ratio NUMERIC,
    ev_ebitda NUMERIC,
    dividend_yield_pct NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE financial_ratios (
    company_id                      VARCHAR NOT NULL,
    year                            VARCHAR NOT NULL,

    -- Sprint 1 source columns (from financial_ratios.xlsx)
    net_profit_margin_pct           NUMERIC,
    operating_profit_margin_pct     NUMERIC,
    return_on_equity_pct            NUMERIC,
    debt_to_equity                  NUMERIC,
    interest_coverage               NUMERIC,
    asset_turnover                  NUMERIC,
    free_cash_flow_cr               NUMERIC,
    capex_cr                        NUMERIC,
    cash_from_operations_cr         NUMERIC,
    earnings_per_share              NUMERIC,
    book_value_per_share            NUMERIC,
    dividend_payout_ratio_pct       NUMERIC,
    total_debt_cr                   NUMERIC,

    -- Sprint 2 computed columns (preserved from nifty100_backup.db)
    return_on_capital_employed_pct  NUMERIC,
    return_on_assets_pct            NUMERIC,
    high_leverage_flag              INTEGER,
    icr_label                       TEXT,
    icr_warning_flag                INTEGER,
    net_debt_cr                     NUMERIC,
    cfo_quality_ratio               NUMERIC,
    cfo_quality_label               TEXT,
    capex_intensity_pct             NUMERIC,
    capex_intensity_label           TEXT,
    fcf_conversion_pct              NUMERIC,
    revenue_cagr_3yr                NUMERIC,
    revenue_cagr_3yr_flag           TEXT,
    revenue_cagr_5yr                NUMERIC,
    revenue_cagr_5yr_flag           TEXT,
    revenue_cagr_10yr               NUMERIC,
    revenue_cagr_10yr_flag          TEXT,
    pat_cagr_3yr                    NUMERIC,
    pat_cagr_3yr_flag               TEXT,
    pat_cagr_5yr                    NUMERIC,
    pat_cagr_5yr_flag               TEXT,
    pat_cagr_10yr                   NUMERIC,
    pat_cagr_10yr_flag              TEXT,
    eps_cagr_3yr                    NUMERIC,
    eps_cagr_3yr_flag               TEXT,
    eps_cagr_5yr                    NUMERIC,
    eps_cagr_5yr_flag               TEXT,
    eps_cagr_10yr                   NUMERIC,
    eps_cagr_10yr_flag              TEXT,
    composite_quality_score         NUMERIC,

    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE peer_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_group_name VARCHAR NOT NULL,
    company_id VARCHAR NOT NULL,
    is_benchmark BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
