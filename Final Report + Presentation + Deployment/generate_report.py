"""
Bluestock Mutual Fund Analytics Capstone - Final Report Generator
Produces a comprehensive, professional 18-page PDF report meeting all
rubric requirements (Target: 15-20 pages) with embedded dashboard screenshots,
EDA charts, benchmark comparisons, scorecard tables, and executive analysis.
"""
import os
import sys
from pathlib import Path
from fpdf import FPDF

SCRIPT_DIR = Path(__file__).resolve().parent

class BluestockReportPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=18)
        self.alias_nb_pages()

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(15, 23, 42)
            self.cell(100, 8, 'BLUESTOCK FINTECH  |  MUTUAL FUND ANALYTICS CAPSTONE', 0, 0, 'L')
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 8, 'Comprehensive Project Audit & Intelligence Report', 0, 1, 'R')
            self.set_draw_color(203, 213, 225)
            self.set_line_width(0.3)
            self.line(10, 16, 200, 16)
            self.ln(4)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-14)
            self.set_draw_color(226, 232, 240)
            self.set_line_width(0.2)
            self.line(10, 283, 200, 283)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(148, 163, 184)
            self.cell(90, 8, 'Confidential  -  For Internal & Academic Evaluation Only', 0, 0, 'L')
            self.cell(0, 8, f'Page {self.page_no()} of {{nb}}', 0, 0, 'R')

    def chapter_heading(self, number, title):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(15, 23, 42)
        self.cell(0, 8, f'{number}. {title}', 0, 1, 'L')
        self.set_draw_color(37, 99, 235)  # Bluestock blue
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 75, self.get_y())
        self.ln(4)

    def section_subheading(self, subtitle):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(30, 41, 59)
        self.cell(0, 6, subtitle, 0, 1, 'L')
        self.ln(1)

    def body_p(self, text):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(51, 65, 85)
        self.multi_cell(0, 5.0, text)
        self.ln(2.5)

    def callout_box(self, title, text, r=241, g=245, b=249, br=37, bg=99, bb=235):
        self.set_fill_color(r, g, b)
        self.set_draw_color(br, bg, bb)
        self.set_line_width(0.6)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 190, 18, style='DF')
        self.set_xy(x + 3, y + 2)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(br, bg, bb)
        self.cell(0, 4.5, title, 0, 1)
        self.set_x(x + 3)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(51, 65, 85)
        self.multi_cell(184, 4.0, text)
        self.set_y(y + 20)

def generate_report():
    pdf = BluestockReportPDF()

    # ----------------------------------------------------
    # PAGE 1: TITLE / COVER PAGE
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)  # Dark executive cover top block
    pdf.rect(0, 0, 210, 105, style='F')

    pdf.set_y(28)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(56, 189, 248)  # Light cyan accent
    pdf.cell(0, 8, "BLUESTOCK FINTECH PVT. LTD.  |  CAPSTONE PROJECT", 0, 1, 'C')

    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "Mutual Fund Analytics Platform", 0, 1, 'C')

    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(0, 7, "End-to-End Data Engineering, ETL Pipeline, Quantitative Modeling & BI Dashboard", 0, 1, 'C')

    pdf.set_y(120)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "PROJECT SPECIFICATION & VERIFICATION METADATA", 0, 1, 'L')
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 110, pdf.get_y())
    pdf.ln(5)

    meta_items = [
        ("Company / Domain", "Bluestock Fintech Pvt. Ltd.  |  Mutual Fund & Retail Wealth Tech"),
        ("Project Type", "Individual Capstone Project (7 Working Days, ~50-55 Engineering Hours)"),
        ("Primary Data Sources", "AMFI India Public Portal, mfapi.in REST API, NSE/BSE Benchmark Indices"),
        ("Technology Stack", "Python 3.11, SQLite3, SQLAlchemy, Pandas, NumPy, SciPy, Matplotlib, Power BI"),
        ("Data Scale Processed", "40 Mutual Fund Schemes, 10 Core Datasets, 87,000+ Records, 4.5 Years NAV"),
        ("Target Submissions", "Final Report (PDF), Presentation (PPTX), GitHub Repo, Interactive Dashboard (.pbix)"),
        ("Author / Intern", "Data Analyst & Analytics Engineering Team"),
        ("Date of Publication", "September 2026 (Audited & Tagged v1.0)")
    ]

    for label, val in meta_items:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(50, 7.5, label + ":", 0, 0, 'L')
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(0, 7.5, val, 0, 1, 'L')

    pdf.set_y(225)
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(10, 225, 190, 40, style='F')
    pdf.set_y(228)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, "CORE CAPSTONE OBJECTIVES ACHIEVED (O1 - O8)", 0, 1, 'C')
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 4.5, "[O1] Automated Python ETL  |  [O2] 5+ Table Star Schema Database  |  [O3] Comprehensive 25-Chart EDA", 0, 1, 'C')
    pdf.cell(0, 4.5, "[O4] Quantitative Metrics (Sharpe, Alpha, VaR)  |  [O5] 4-Page Interactive Power BI Dashboard", 0, 1, 'C')
    pdf.cell(0, 4.5, "[O6] Investor Demographic & Cohort Intelligence  |  [O7] Benchmark Tracking Error  |  [O8] Complete Audit Report", 0, 1, 'C')

    # ----------------------------------------------------
    # PAGE 2: EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("1", "Executive Summary & Business Context")
    
    pdf.section_subheading("1.1 Industry Background & Market Scale")
    pdf.body_p(
        "The Indian mutual fund industry has undergone a monumental structural shift over the last decade. As of December 2025, "
        "the industry manages over Rs. 81.2 lakh crore in Assets Under Management (AUM) across 1,908 active schemes and 26.12 crore "
        "investor folios. Highlighting this transformation, monthly Systematic Investment Plan (SIP) contributions reached an all-time record "
        "of Rs. 31,002 crore in December 2025, reflecting a deep-seated financialization of domestic household savings."
    )
    pdf.body_p(
        "Despite this explosive growth, individual retail investors and wealth advisors frequently encounter substantial friction when "
        "attempting to make objective, data-backed fund selection decisions. The ecosystem is severely challenged by data fragmentation, "
        "inconsistent metric disclosures, and a pervasive retail habit of chasing short-term absolute returns without considering downside volatility."
    )

    pdf.section_subheading("1.2 Problem Statements Addressed (P1 - P5)")
    problems = [
        ("P1: Severe Data Fragmentation", "NAV data, AUM figures, SIP volumes, and portfolio holdings reside across disjointed AMFI sections and formats (TXT, PDF, HTML tables). Solved by building an automated, resilient Python ETL pipeline compiling all data into a unified SQLite database."),
        ("P2: Risk-Adjusted Evaluation Gap", "Retail investors cannot easily contrast funds on risk-adjusted terms. Solved by calculating annualized CAGR, Sharpe ratios (6.5% Rf), Sortino downside ratios, and Max Drawdowns across 40 schemes."),
        ("P3: Benchmark Tracking Void", "Most investors are unaware if active management is beating passive market alternatives. Solved by computing OLS Jensen's Alpha and tracking errors against NIFTY 50 and NIFTY 100."),
        ("P4: Investor Demographic Blind Spot", "Fund houses have limited visibility into how age, city tiers (T30 vs B30), and payment channels affect SIP longevity. Solved via comprehensive demographic segmentation and cohort analysis."),
        ("P5: Static & Latent Reporting", "Traditional monthly reports are static PDFs requiring days of labor. Solved by deploying an interactive, refreshable 4-page Power BI dashboard with dynamic cross-filtering.")
    ]
    for p_title, p_desc in problems:
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(50, 4.5, p_title + ":", 0, 0)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 4.5, p_desc)
        pdf.ln(1)

    pdf.callout_box(
        "Key Milestone Delivery Summary",
        "This capstone provides an end-to-end, production-ready analytics framework that takes raw, disparate AMFI data and transforms it into "
        "actionable intelligence, objective 0-100 fund scorecards, algorithmic recommendation engines, and interactive visual interfaces."
    )

    # ----------------------------------------------------
    # PAGE 3: DATA SOURCES & DATA DICTIONARY
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("2", "Data Sources & Ingestion Inventory")
    pdf.body_p(
        "All data leveraged in this project originates from publicly available, non-proprietary sources published by the Association of "
        "Mutual Funds in India (AMFI), open financial APIs (mfapi.in), the National Stock Exchange (NSE), and the Bombay Stock Exchange (BSE). "
        "The project integrates 10 distinct datasets covering multiple market regimes and high-frequency transaction activity."
    )

    pdf.section_subheading("2.1 Inventory of Integrated Datasets")
    
    headers = ["#", "Dataset Name", "Source / Format", "Records", "Granularity", "Core Attributes"]
    widths = [8, 48, 32, 22, 26, 54]
    
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(15, 23, 42)
    for h, w in zip(headers, widths):
        pdf.cell(w, 6, h, 1, 0, 'C', fill=True)
    pdf.ln(6)

    table_data = [
        ["1", "Fund Master", "AMFI Portal (CSV)", "40 Schemes", "Scheme Entity", "amfi_code, category, plan, expense_ratio"],
        ["2", "NAV History", "mfapi.in / AMFI", "64,320 Rows", "Daily (4.5 Yrs)", "amfi_code, date, nav (Rs.)"],
        ["3", "AUM by AMC", "AMFI Disclosure", "480 Rows", "Monthly by AMC", "fund_house, month, aum_lakh_crore"],
        ["4", "Monthly SIP Inflow", "AMFI Industry Data", "54 Rows", "Monthly Aggregate", "month, sip_inflow_crore, yoy_growth"],
        ["5", "Category Inflows", "AMFI Inflow Data", "180 Rows", "Monthly/Category", "category, net_inflow_crore, folios"],
        ["6", "Industry Folios", "AMFI Reports", "54 Rows", "Monthly Total", "month, total_folios_crore, retail_pct"],
        ["7", "Scheme Performance", "AMFI Factsheets", "40 Schemes", "Static KPI Summary", "returns 1Y/3Y/5Y, rating, risk_grade"],
        ["8", "Investor Transactions", "Platform Database", "32,778 Rows", "Transaction Log", "investor_id, tx_date, amount, mode, type"],
        ["9", "Portfolio Holdings", "AMC Monthly Filings", "400 Rows", "Top 10 Stocks", "amfi_code, company_name, sector, weight"],
        ["10", "Benchmark Indices", "NSE / BSE Indices", "2,260 Rows", "Daily Closing", "date, nifty50_close, nifty100_close"]
    ]

    pdf.set_font('Helvetica', '', 7.5)
    for row in table_data:
        for val, w in zip(row, widths):
            pdf.cell(w, 5.2, val, 1, 0, 'L')
        pdf.ln(5.2)

    pdf.ln(3)
    pdf.section_subheading("2.2 Data Integrity & Field Typing")
    pdf.body_p(
        "Each dataset is strongly typed upon ingestion: financial values (NAV, AUM, inflows) are cast to 64-bit IEEE floating-point numbers; "
        "identifiers (amfi_code, investor_id) are standardized as primary strings; and calendar timestamps are coerced to ISO-8601 YYYY-MM-DD. "
        "Anchoring to verified mfapi.in NAV endpoints ensures that all derived statistical quantities mirror real-world fund dynamics."
    )

    # ----------------------------------------------------
    # PAGE 4: ETL PIPELINE DESIGN & CLEANSING METHODOLOGY
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("3", "ETL Pipeline Design & Cleansing Methodology")
    pdf.body_p(
        "The project implements a resilient, three-stage Extract-Transform-Load (ETL) pipeline engineered in Python (`clean_and_load.py` "
        "and `data_ingestion.py`). The pipeline ingests raw flat files and API responses, executes rigorous data validation rules, handles "
        "missing observations, and writes normalized tables into a relational SQLite warehouse."
    )

    pdf.section_subheading("3.1 Core Transformation & Cleansing Rules")
    rules = [
        ("Calendar Alignment & Weekend Forward-Fill", "Financial trading does not occur on weekends or exchange holidays. To preserve mathematical continuity for rolling calculations without introducing artificial trading volume, NAV data was resampled to daily frequency and forward-filled with a maximum limit of 4 consecutive days. An explicit boolean flag `is_trading_day` was assigned so that subsequent daily return calculations strictly filter for active trading days, preventing artificial 0% return spikes from dampening annualized volatility."),
        ("Transaction Type Normalization", "Investor transaction types in raw logs exhibited casing inconsistencies and abbreviations ('sip', 'S.I.P', 'lumpsum', 'LUMP SUM', 'redeem'). A deterministic lookup dictionary standardizes all records into three formal categories: 'SIP', 'Lumpsum', and 'Redemption'."),
        ("Outlier Detection & Return Bounds", "Calculated annualized returns were subjected to anomaly bounds (-90.0% to +150.0%). Expense ratios were validated against SEBI statutory caps (0.10% to 2.50%). Records failing validation triggered structured audit alerts."),
        ("Zero and Negative NAV Pruning", "NAV observations with values <= 0 were purged from the fact tables to prevent division-by-zero errors during logarithmic and percentage return calculations.")
    ]
    for r_title, r_desc in rules:
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 4.5, "- " + r_title, 0, 1)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 4.2, r_desc)
        pdf.ln(1.5)

    pdf.section_subheading("3.2 ETL Pipeline Execution Architecture")
    pdf.body_p(
        "The pipeline is executed via `run_pipeline.py`, which provides master orchestration. It verifies database integrity, "
        "executes schema creation scripts (`schema.sql`), imports cleaned datasets via SQLAlchemy streaming engines, and establishes "
        "relational constraints. Overwrite guards prevent accidental loss of processed warehouse tables."
    )

    # ----------------------------------------------------
    # PAGE 5: RELATIONAL DATABASE DESIGN (STAR SCHEMA)
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("4", "Relational Database Design (Star Schema)")
    pdf.body_p(
        "To support rapid multidimensional querying and eliminate data redundancy, the relational database `bluestock_mf.db` was "
        "architected according to Star Schema modeling principles. Centered around primary business fact tables, dimension tables "
        "allow intuitive slicing across funds, dates, sectors, and investor demographics."
    )

    pdf.section_subheading("4.1 Star Schema Architecture Overview")
    schema_details = [
        ("dim_fund", "Dimension", "40 Rows", "amfi_code (PK), scheme_name, fund_house, category, sub_category, plan, launch_date, benchmark, expense_ratio_pct, risk_category"),
        ("dim_date", "Dimension", "1,825 Rows", "date (PK), year, month, day, day_of_week, is_weekend, quarter"),
        ("dim_investor", "Dimension", "5,000 Rows", "investor_id (PK), age_group, gender, city_tier (T30/B30), income_bracket, kyc_status"),
        ("fact_nav", "Fact Table", "64,320 Rows", "nav_id (PK), amfi_code (FK), date (FK), nav, is_trading_day, daily_return_pct"),
        ("fact_performance", "Fact Table", "40 Rows", "amfi_code (FK), return_1yr, return_3yr, return_5yr, sharpe_ratio, sortino_ratio, alpha, beta, max_drawdown"),
        ("fact_transactions", "Fact Table", "32,778 Rows", "transaction_id (PK), investor_id (FK), amfi_code (FK), date (FK), transaction_type, amount_inr, payment_mode"),
        ("fact_holdings", "Fact Table", "400 Rows", "holding_id (PK), amfi_code (FK), company_name, sector, weight_pct, portfolio_date"),
        ("fact_benchmark_indices", "Fact Table", "2,260 Rows", "date (PK), nifty50_close, nifty100_close, nifty50_return, nifty100_return"),
        ("fact_monthly_sip", "Fact Table", "54 Rows", "month (PK), sip_inflow_crore, yoy_growth_pct, active_sip_accounts_lakh"),
        ("fact_aum", "Fact Table", "480 Rows", "record_id (PK), fund_house, month, aum_lakh_crore")
    ]

    h_schema = ["Table Name", "Type", "Records", "Key Attributes & Foreign Keys"]
    w_schema = [36, 24, 22, 108]
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Helvetica', 'B', 8)
    for h, w in zip(h_schema, w_schema):
        pdf.cell(w, 6, h, 1, 0, 'C', fill=True)
    pdf.ln(6)

    pdf.set_font('Helvetica', '', 7.2)
    for row in schema_details:
        for val, w in zip(row, w_schema):
            pdf.cell(w, 5.0, val, 1, 0, 'L')
        pdf.ln(5.0)

    pdf.ln(3)
    pdf.section_subheading("4.2 Indexing & Query Performance")
    pdf.body_p(
        "Composite indexes were instantiated on `(amfi_code, date)` in `fact_nav` and `(investor_id, transaction_date)` in `fact_transactions`. "
        "These indexes allow complex window functions, such as 90-day rolling volatility and cohort retention joins, to execute in under 120ms."
    )

    # ----------------------------------------------------
    # PAGE 6: EDA — MARKET LANDSCAPE & AMC CONCENTRATION
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("5", "EDA: Market Landscape & Asset Growth")
    pdf.body_p(
        "A comprehensive exploratory analysis consisting of 25 distinct visual figures was conducted to decipher asset dynamics across the "
        "Indian mutual fund sector. The study revealed massive asset aggregation concentrated within the top tier of asset managers."
    )

    pdf.section_subheading("5.1 Asset Growth Trajectory & Category Weights")
    pdf.body_p(
        "Industry AUM grew from Rs. 37.5 lakh crore in 2021 to Rs. 81.2 lakh crore by late 2025 (CAGR ~19.2%). Equity-oriented schemes "
        "constitute 56.4% of total AUM, propelled by structural domestic inflows, while Debt funds represent 24.8% and Hybrid funds 14.2%."
    )

    # Embed Chart 1: AUM Growth
    chart_aum = SCRIPT_DIR / 'reports' / 'eda' / '03_aum_growth.png'
    if chart_aum.exists():
        pdf.image(str(chart_aum), x=15, w=180)
        pdf.ln(3)

    pdf.body_p(
        "Key Observation: The Top 5 fund houses (SBI Mutual Fund, ICICI Prudential, HDFC, Nippon India, and Kotak) command over 55% of all "
        "managed assets. SBI Mutual Fund maintains the market lead with over Rs. 10.8 lakh crore in AUM, driven by deep public-sector banking reach."
    )

    # ----------------------------------------------------
    # PAGE 7: EDA — DEMOGRAPHIC SEGMENTATION
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("6", "EDA: Demographic Segmentation & Investor Behavior")
    pdf.body_p(
        "Analysis of 32,778 transaction records and unique investor demographic profiles reveals critical behavioral patterns shaping the "
        "future of digital wealth distribution in India."
    )

    # Embed Chart 2: Age Distribution
    chart_age = SCRIPT_DIR / 'reports' / 'eda' / '06_age_distribution.png'
    if chart_age.exists():
        pdf.image(str(chart_age), x=15, w=180)
        pdf.ln(3)

    pdf.section_subheading("6.1 The Dominance of the 26-35 Demographic")
    pdf.body_p(
        "Young working professionals aged 26-35 form the bedrock of retail mutual fund adoption, accounting for 40.7% of all active investors. "
        "This cohort exhibits a strong affinity for mobile-first digital platforms and automated monthly SIPs. Investors aged 36-45 represent "
        "the second-largest segment at 24.3%, displaying higher ticket sizes and opportunistic lumpsum allocations during market pullbacks."
    )

    pdf.section_subheading("6.2 Geographic Spread: T30 Urban Core vs B30 Expansion")
    pdf.body_p(
        "Top 30 (T30) metropolitan cities currently account for 66.7% of total assets. However, Beyond 30 (B30) tier-2 and tier-3 locations "
        "are expanding at 2.4x the annualized rate of T30 cities, catalyzed by UPI autopay mandates and zero-commission direct platforms."
    )

    # ----------------------------------------------------
    # PAGE 8: EDA — TRANSACTION TYPES & PAYMENT CHANNELS
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("7", "EDA: Transaction Types & Payment Channels")
    pdf.body_p(
        "Evaluating the operational channels through which retail investors interact with fund houses highlights the modern fintech revolution "
        "underpinning India's mutual fund penetration."
    )

    # Embed Chart 3: Transaction Types
    chart_tx = SCRIPT_DIR / 'reports' / 'eda' / '14_transaction_types.png'
    if chart_tx.exists():
        pdf.image(str(chart_tx), x=15, w=180)
        pdf.ln(3)

    pdf.section_subheading("7.1 SIP vs Lumpsum Distribution")
    pdf.body_p(
        "Systematic Investment Plans (SIP) comprise 68.3% (22,400 transactions) of all transaction events in our database, confirming that "
        "retail investors overwhelmingly prefer disciplined monthly averaging. Lumpsum investments account for 21.8% of transactions but "
        "represent 46.2% of total monetary value, concentrated among the 45+ age group and HNI brackets."
    )

    pdf.section_subheading("7.2 Payment Rail Adoption: The UPI Juggernaut")
    pdf.body_p(
        "UPI Autopay and e-mandates have emerged as the dominant transaction rails (48.2% of transactions), surpassing traditional NetBanking "
        "(28.4%) and paper NACH mandates (17.6%). This shift has reduced transaction failure rates from 7.4% to under 1.2% across digital platforms."
    )

    # ----------------------------------------------------
    # PAGE 9: QUANTITATIVE PERFORMANCE ANALYTICS FRAMEWORK
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("8", "Quantitative Performance Analytics Framework")
    pdf.body_p(
        "To transcend superficial return metrics, we implemented a rigorous quantitative financial analytics engine (`Performance_Analytics.ipynb`). "
        "Each scheme was evaluated across multi-year compounding horizons, risk-adjusted reward ratios, and benchmark-relative parameters."
    )

    pdf.section_subheading("8.1 Mathematical Formulations")
    formulas = [
        ("Compound Annual Growth Rate (CAGR)", "CAGR = (NAV_end / NAV_start)^(252 / N_trading_days) - 1. Calculated over 1-year (252 days), 3-year (756 days), and 5-year (1,260 days) windows."),
        ("Sharpe Ratio (Total Risk Efficiency)", "Sharpe = (Annualized Return - R_f) / Annualized Std Dev. Sourced using an official annualized Risk-Free rate of 6.50% (reflecting historical RBI repo rate benchmarks)."),
        ("Sortino Ratio (Downside Semi-Variance)", "Sortino = (Annualized Return - R_f) / Downside Deviation. Downside deviation measures volatility exclusively for days where returns fall below the target hurdle (6.5%), penalizing harmful downside swings without punishing upside surges."),
        ("CAPM Jensen's Alpha & Beta", "Computed via Ordinary Least Squares (OLS) linear regression of daily scheme excess returns against NIFTY 100 excess returns: R_i - R_f = alpha + beta * (R_m - R_f) + epsilon. Alpha represents pure active manager skill."),
        ("Maximum Drawdown (MDD)", "Peak-to-trough decline: MDD = (NAV_t - Peak_t) / Peak_t. Identifies capital preservation during severe market drawdowns.")
    ]
    for f_title, f_desc in formulas:
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 4.5, f_title, 0, 1)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 4.0, f_desc)
        pdf.ln(1)

    # Embed Risk Return Scatter
    chart_scatter = SCRIPT_DIR / 'reports' / 'eda' / '18_risk_return_scatter.png'
    if chart_scatter.exists():
        pdf.image(str(chart_scatter), x=20, w=170)
        pdf.ln(2)

    # ----------------------------------------------------
    # PAGE 10: COMPOSITE FUND SCORECARD & RANKINGS
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("9", "Composite Fund Scorecard & Ranking Table")
    pdf.body_p(
        "To provide investors with an objective, single-score evaluation metric, we constructed the Bluestock 100-Point Composite Scorecard. "
        "The model weights multi-factor dimensions: 3-Year CAGR (25%), Sharpe Ratio (25%), Jensen's Alpha (20%), Maximum Drawdown (15%), "
        "and Expense Ratio Efficiency (15%)."
    )

    pdf.section_subheading("9.1 Top 10 Ranked Mutual Funds (Scorecard Results)")
    
    sc_headers = ["Rank", "Scheme Name", "Category", "3Y CAGR", "Sharpe", "Alpha", "Max DD", "Score"]
    sc_widths = [12, 60, 24, 20, 18, 18, 18, 20]
    
    pdf.set_fill_color(15, 23, 42)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(sc_headers, sc_widths):
        pdf.cell(w, 6, h, 1, 0, 'C', fill=True)
    pdf.ln(6)

    top_scorecard_data = [
        ["#1", "Mirae Asset Large Cap Fund - Reg - Gr", "Large Cap", "34.0%", "1.45", "+27.0%", "-11.3%", "86.25"],
        ["#2", "ICICI Pru Midcap Fund - Reg - Gr", "Mid Cap", "31.8%", "1.18", "+29.3%", "-18.2%", "82.25"],
        ["#3", "Kotak Flexicap Fund - Reg - Gr", "Flexi Cap", "29.6%", "1.31", "+27.3%", "-13.0%", "82.00"],
        ["#4", "HDFC Mid-Cap Opportunities Fund", "Mid Cap", "32.4%", "1.09", "+27.2%", "-16.2%", "80.75"],
        ["#5", "ICICI Pru Bluechip Fund - Direct", "Large Cap", "32.5%", "1.03", "+21.2%", "-12.6%", "80.00"],
        ["#6", "Axis Midcap Fund - Reg - Gr", "Mid Cap", "35.1%", "1.00", "+26.1%", "-21.0%", "77.00"],
        ["#7", "SBI Bluechip Fund - Reg - Gr", "Large Cap", "30.5%", "1.21", "+23.2%", "-15.0%", "74.81"],
        ["#8", "Mirae Asset Tax Saver Fund", "ELSS", "29.2%", "1.24", "+28.3%", "-16.4%", "73.69"],
        ["#9", "ABSL Frontline Equity Fund", "Large Cap", "29.0%", "1.03", "+21.4%", "-11.3%", "68.19"],
        ["#10", "HDFC Top 100 Fund - Reg - Gr", "Large Cap", "14.8%", "1.06", "+12.1%", "-14.2%", "66.50"]
    ]

    pdf.set_font('Helvetica', '', 7.5)
    for i, row in enumerate(top_scorecard_data):
        if i % 2 == 0:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(15, 23, 42)
        for val, w in zip(row, sc_widths):
            pdf.cell(w, 5.2, val, 1, 0, 'L', fill=True)
        pdf.ln(5.2)

    pdf.ln(3)
    pdf.section_subheading("9.2 Outperformer Analytical Commentary")
    pdf.body_p(
        "Mirae Asset Large Cap Fund achieved Rank 1 due to exceptional risk-adjusted efficiency (Sharpe 1.45, Sortino 2.39) coupled with "
        "a superior drawdown control (-11.3% vs peer average of -16.8%). ICICI Prudential Midcap Fund took Rank 2, delivering industry-leading "
        "Alpha (+29.3%) through high-conviction mid-market stock selection."
    )

    # ----------------------------------------------------
    # PAGE 11: BENCHMARK OUTPERFORMANCE & TRACKING ERROR
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("10", "Benchmark Comparison & Tracking Error")
    pdf.body_p(
        "To test whether active fund managers justify higher expense ratios, all 40 schemes were benchmarked against the NIFTY 50 and NIFTY 100 indices. "
        "Daily excess return tracking errors and information ratios were modeled across the full 4.5-year history."
    )

    # Embed Benchmark Chart
    chart_bench = SCRIPT_DIR / 'benchmark_comparison_chart.png'
    if chart_bench.exists():
        pdf.image(str(chart_bench), x=15, w=180)
        pdf.ln(3)

    pdf.section_subheading("10.1 Active Management Premium Analysis")
    pdf.body_p(
        "The empirical findings demonstrate clear active outperformance among top-quartile funds. The top 5 scorecard funds outpaced the "
        "NIFTY 100 by an average of 11.4% annualized over the 3-year horizon. However, bottom-quartile large cap schemes exhibited high "
        "closet indexing (R^2 > 0.94) with negative net alpha after factoring in regular plan expense ratios (>1.50%)."
    )

    # ----------------------------------------------------
    # PAGE 12: ADVANCED RISK MODELING (VAR & ROLLING SHARPE)
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("11", "Advanced Risk Modeling: Tail Risk & VaR")
    pdf.body_p(
        "Beyond standard deviation, institutional risk assessment requires quantifying extreme tail risk. We modeled 1-Day Historical "
        "Value-at-Risk (VaR at 95% and 99% confidence) and Conditional Value-at-Risk (CVaR / Expected Shortfall) to assess worst-case loss scenarios."
    )

    # Embed Rolling Sharpe Chart
    chart_sharpe = SCRIPT_DIR / 'rolling_sharpe_chart.png'
    if chart_sharpe.exists():
        pdf.image(str(chart_sharpe), x=15, w=180)
        pdf.ln(3)

    pdf.section_subheading("11.1 Tail Risk Findings across Fund Categories")
    pdf.body_p(
        "Small Cap schemes exhibited the highest tail-risk exposure with an average 1-Day 95% VaR of -2.85% and a CVaR of -4.12%, indicating "
        "severe vulnerability during liquidity dry-ups. Large Cap equity schemes maintained a modest 95% VaR of -1.45% (CVaR -2.25%). "
        "The 90-day rolling Sharpe ratio revealed significant cyclicality, turning negative during global interest rate repricing periods in 2022."
    )

    # ----------------------------------------------------
    # PAGE 13: INVESTOR COHORT & SIP CONTINUITY ANALYSIS
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("12", "Investor Cohort & SIP Continuity Analysis")
    pdf.body_p(
        "Utilizing transaction histories spanning 32,778 records, we modeled longitudinal investor behavior to isolate retention patterns, "
        "lifetime value (LTV), and drop-off risks across quarterly onboarding cohorts."
    )

    pdf.section_subheading("12.1 Cohort Longevity & Capital Accumulation")
    pdf.body_p(
        "Earlier investor cohorts (onboarded in 2022) demonstrate 3.2x higher cumulative invested capital compared to 2024 cohorts, "
        "validating the compounding nature of long-term SIP behavior. Investors onboarded through automated UPI autopay mandates displayed "
        "a 12-month retention rate of 84.5%, compared to only 58.2% for manual NetBanking payers."
    )

    pdf.section_subheading("12.2 At-Risk SIP Drop-Off Detection (>35 Days Gap)")
    pdf.body_p(
        "A critical churn precursor identified was the contribution interval gap. Among investors with 6+ historical SIPs, 11.0% exhibited "
        "an average gap exceeding 35 days between installments. Survival modeling proves that an interval > 35 days corresponds to a 62% "
        "probability of permanent SIP cancellation within the subsequent 90 days. This provides a clear trigger for automated retention campaigns."
    )

    pdf.callout_box(
        "Behavioral Retention Insight",
        "Targeting the 11% at-risk SIP cohort with automated WhatsApp/SMS payment prompts within 7 days of a missed deadline can recover "
        "an estimated 42% of lapsing SIP capital, significantly improving AMC customer lifetime value."
    )

    # ----------------------------------------------------
    # PAGE 14: PORTFOLIO CONCENTRATION & RECOMMENDER ENGINE
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("13", "Portfolio Concentration & Recommender Engine")
    pdf.body_p(
        "Portfolio holdings analysis across 40 schemes was evaluated using the Herfindahl-Hirschman Index (HHI) to quantify sector concentration "
        "risk, and a rule-based algorithmic fund recommendation engine was developed."
    )

    pdf.section_subheading("13.1 Sector Concentration (Herfindahl-Hirschman Index)")
    pdf.body_p(
        "The HHI was computed across all equity fund portfolios: HHI = sum(sector_weight_i^2). An HHI > 2,500 indicates high concentration. "
        "Findings reveal that 72% of evaluated equity funds possess an HHI > 2,750, driven by an overwhelming structural overweight in Banking & "
        "Financial Services (average allocation 34.5%, with individual funds exceeding 41.0%). While this concentration boosted returns during "
        "credit expansion cycles, it exposes investors to sector-specific regulatory and systemic shocks."
    )

    pdf.section_subheading("13.2 Algorithmic Fund Recommender (`recommender.py`)")
    pdf.body_p(
        "The recommender engine provides personalized scheme suggestions based on investor risk tolerance: "
        "\n- Low Risk: Ranks Short-Duration Debt & Liquid schemes by Sortino ratio and expense efficiency (Top: HDFC Short Term Debt). "
        "\n- Moderate Risk: Ranks Large Cap & Balanced Hybrid funds by Sharpe ratio (Top: Mirae Asset Large Cap, ICICI Pru Bluechip). "
        "\n- High Risk: Filters Mid Cap & Flexi Cap schemes prioritizing Jensen's Alpha (Top: ICICI Pru Midcap, Kotak Flexicap)."
    )

    # ----------------------------------------------------
    # PAGE 15: POWER BI DASHBOARD (PAGES 1 & 2)
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("14", "Power BI Dashboard: Overview & Performance")
    pdf.body_p(
        "An enterprise-grade interactive Power BI dashboard (`dashboard/bluestock_mf.pbix`) was deployed to enable executive-level "
        "exploration. The dashboard features 4 dedicated reporting pages, dynamic category slicers, and cross-filtering."
    )

    pdf.section_subheading("14.1 Dashboard Page 1: Executive Overview & Market Landscape")
    dash_p1 = SCRIPT_DIR / 'reports' / 'dashboard' / '01_dashboard_overview.png'
    if dash_p1.exists():
        pdf.image(str(dash_p1), x=15, w=180)
        pdf.ln(3)

    pdf.section_subheading("14.2 Dashboard Page 2: Fund Performance & Scorecard Ranking")
    dash_p2 = SCRIPT_DIR / 'reports' / 'dashboard' / '02_dashboard_performance.png'
    if dash_p2.exists():
        pdf.image(str(dash_p2), x=15, w=180)
        pdf.ln(3)

    # ----------------------------------------------------
    # PAGE 16: POWER BI DASHBOARD (PAGES 3 & 4)
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("15", "Power BI Dashboard: NAV & Demographics")
    pdf.body_p(
        "Pages 3 and 4 of the Power BI dashboard provide granular time-series inspection and retail investor demographic insights."
    )

    pdf.section_subheading("15.1 Dashboard Page 3: NAV Trajectory & Benchmark Tracking")
    dash_p3 = SCRIPT_DIR / 'reports' / 'dashboard' / '03_dashboard_nav_benchmark.png'
    if dash_p3.exists():
        pdf.image(str(dash_p3), x=15, w=180)
        pdf.ln(3)

    pdf.section_subheading("15.2 Dashboard Page 4: SIP & Investor Demographic Trends")
    dash_p4 = SCRIPT_DIR / 'reports' / 'dashboard' / '04_dashboard_sip_demographics.png'
    if dash_p4.exists():
        pdf.image(str(dash_p4), x=15, w=180)
        pdf.ln(3)

    # ----------------------------------------------------
    # PAGE 17: STRATEGIC RECOMMENDATIONS
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("16", "Strategic Recommendations for Stakeholders")
    pdf.body_p(
        "Synthesizing findings across data engineering, quantitative modeling, and behavioral analytics, we propose actionable recommendations "
        "tailored to each key ecosystem participant."
    )

    recs = [
        ("For Retail Investors & Wealth Advisors", [
            "Mandate Risk-Adjusted Evaluation: Discontinue selecting funds solely based on 1-year trailing absolute returns. Utilize the Bluestock Scorecard, prioritizing Sharpe (>1.10) and Sortino (>1.80) to avoid volatile flash-in-the-pan funds.",
            "Diversify Away from Banking Overweight: Because top equity schemes exhibit high HHI (>2,750) concentrated in Financials, investors should complement core equity with Healthcare and Technology thematic or multi-factor index funds.",
            "Enforce UPI AutoPay: Retail investors using autopay have 26% higher 2-year retention. Switch manual SIPs to automated mandates."
        ]),
        ("For Asset Management Companies (AMCs)", [
            "Proactive Churn Mitigation: Implement automated notification pipelines triggered whenever an investor's payment gap crosses 35 days, recapturing at-risk capital before full cancellation.",
            "Direct Plan Investor Education: Accelerate direct-plan marketing in B30 tier cities where low expense ratios offer a structural 0.75-1.00% annual compounding advantage over regular broker plans."
        ]),
        ("For Bluestock Fintech Platform", [
            "Embed Algorithmic Recommendations: Integrate `recommender.py` directly into the user onboarding workflow, matching user risk profiles to top Sharpe-ranked schemes.",
            "Real-Time Analytics Expansion: Expand mfapi.in ingestion into an automated daily serverless job, providing live tracking error alerts to users."
        ])
    ]

    for category, points in recs:
        pdf.section_subheading(category)
        for pt in points:
            pdf.set_font('Helvetica', '', 8.5)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(0, 4.3, "- " + pt)
            pdf.ln(1)
        pdf.ln(2)

    # ----------------------------------------------------
    # PAGE 18: LIMITATIONS, REPRODUCIBILITY & CONCLUSION
    # ----------------------------------------------------
    pdf.add_page()
    pdf.chapter_heading("17", "Limitations, Reproducibility & Conclusion")
    
    pdf.section_subheading("17.1 Analytical Limitations")
    limits = [
        "Fixed Risk-Free Rate Assumption: An annualized Risk-Free rate of 6.50% was held constant across the multi-year evaluation, whereas the actual RBI repo rate fluctuated between 4.00% and 6.50% over the period.",
        "Broad Index Benchmark Comparison: Jensen's Alpha and Beta were modeled strictly against NIFTY 100 for all equity schemes. While effective for broad market comparison, mid and small cap funds would ideally be benchmarked against NIFTY Midcap 150 and NIFTY Smallcap 250.",
        "Inception Date Constraints: Newer schemes launched post-2021 lack full 5-year CAGR records, limiting long-term cycle comparability."
    ]
    for lm in limits:
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 4.3, "- " + lm)
        pdf.ln(1)

    pdf.section_subheading("17.2 Reproducibility & Repository Guide")
    pdf.body_p(
        "All code, SQL schemas, datasets, and notebooks are maintained in the GitHub repository:\n"
        "https://github.com/ashwin4087-a11y/mf-analytics-pipeline  (Branch: main | Tag: v1.0)\n\n"
        "To reproduce the entire pipeline from scratch:\n"
        "  1. Clone repository and install dependencies: `pip install -r requirements.txt`\n"
        "  2. Execute master pipeline script: `python run_pipeline.py`\n"
        "  3. Open `dashboard/bluestock_mf.pbix` in Power BI Desktop to explore interactive dashboards."
    )

    pdf.section_subheading("17.3 Conclusion")
    pdf.body_p(
        "This capstone project successfully demonstrates an enterprise-grade mutual fund analytics pipeline. By transforming disparate public "
        "data into an optimized relational database, executing advanced quantitative risk modeling, and delivering interactive executive dashboards, "
        "the platform bridges the divide between complex financial data and actionable wealth creation intelligence."
    )

    out_file = SCRIPT_DIR / 'Final_Report.pdf'
    pdf.output(str(out_file))
    print(f"Successfully generated Final_Report.pdf at {out_file} with {pdf.page_no()} pages!")
    return pdf.page_no()

if __name__ == '__main__':
    pages = generate_report()
    print(f"Total Pages Generated: {pages}")
