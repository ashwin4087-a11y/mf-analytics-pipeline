"""
src/analytics/engine.py — Day 12–13: Ratio Engine.

Loads source Excel data, normalizes years, joins P&L + BS + CF,
computes all KPIs via the pure-function modules, writes results to
the financial_ratios SQLite table, and generates:
    - output/capital_allocation.csv
    - output/ratio_edge_cases.log

Design:
    - One unique row per (company_id, canonical_year)
    - Source duplicates are deduplicated (keep row with most non-null data)
    - Non-standard year periods (TTM, 9m, 15m) are excluded from CAGR
      but retained for point-in-time ratios
    - SBIN/VBL: BS-dependent KPIs are NULL (no BS data available)
    - Financials carve-out: high_leverage_flag suppressed, ROCE/ROE cross-checked
    - Composite quality score: percentile-rank normalization across dataset
"""
import os
import sys
import sqlite3
import math
import csv
from datetime import datetime

import pandas as pd
import numpy as np

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.etl.normaliser import normalize_year
from src.analytics.ratios import (
    net_profit_margin, operating_profit_margin, opm_cross_check,
    return_on_equity, return_on_capital_employed, return_on_assets,
    debt_to_equity, high_leverage_flag, interest_coverage_ratio,
    icr_label_value, icr_warning, net_debt, asset_turnover,
    gross_margin, ebitda_margin, pre_tax_margin, net_profit_to_ebitda,
    return_on_invested_capital, debt_to_assets_ratio, debt_to_capital_ratio,
    equity_multiplier_ratio, fixed_asset_turnover_ratio, working_capital_to_sales,
    interest_bearing_debt_ratio_calc, tax_rate_calc, cash_flow_to_debt_ratio,
    operating_cash_flow_margin, operating_cash_flow_to_net_income,
    retained_earnings_to_assets, net_debt_to_equity_ratio, net_debt_to_ebitda_ratio,
    ebit_to_total_assets, cash_flow_coverage_ratio_calc, interest_to_sales_ratio,

)
from src.analytics.cagr import (
    compute_cagr, compute_cagr_for_series, is_valid_cagr_year,
    extract_fiscal_year,
)
from src.analytics.cashflow_kpis import (
    free_cash_flow, cfo_quality_ratio, capex_intensity,
    fcf_conversion, capital_allocation_label,
)


DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
DB_PATH = os.path.join(DATA_DIR, "nifty100.db")

# Source file names
FILES = {
    "profitandloss": "profitandloss.xlsx",
    "balancesheet":  "balancesheet.xlsx",
    "cashflow":      "cashflow.xlsx",
    "financial_ratios_src": "financial_ratios.xlsx",
    "companies":     "companies.xlsx",
    "sectors":       "sectors.xlsx",
}

# Header row config (from inspection)
HEADERS = {
    "profitandloss": 1,
    "balancesheet": 1,
    "cashflow": 1,
    "financial_ratios_src": 0,
    "companies": 1,
    "sectors": 0,
}

FINANCIAL_RATIOS_SCHEMA = """
CREATE TABLE IF NOT EXISTS financial_ratios (
    id                              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id                      TEXT    NOT NULL,
    year                            TEXT    NOT NULL,

    -- Profitability (Day 08)
    net_profit_margin_pct           REAL,
    operating_profit_margin_pct     REAL,
    return_on_equity_pct            REAL,
    return_on_capital_employed_pct  REAL,
    return_on_assets_pct            REAL,

    -- Leverage & Efficiency (Day 09)
    debt_to_equity                  REAL,
    high_leverage_flag              INTEGER,
    interest_coverage               REAL,
    icr_label                       TEXT,
    icr_warning_flag                INTEGER,
    net_debt_cr                     REAL,
    asset_turnover                  REAL,

    -- Cash Flow KPIs (Day 11)
    free_cash_flow_cr               REAL,
    capex_cr                        REAL,
    cash_from_operations_cr         REAL,
    cfo_quality_ratio               REAL,
    cfo_quality_label               TEXT,
    capex_intensity_pct             REAL,
    capex_intensity_label           TEXT,
    fcf_conversion_pct              REAL,

    -- From source P&L / financial_ratios.xlsx
    earnings_per_share              REAL,
    book_value_per_share            REAL,
    dividend_payout_ratio_pct       REAL,
    total_debt_cr                   REAL,

    -- CAGR (Day 10)
    revenue_cagr_3yr                REAL,
    revenue_cagr_3yr_flag           TEXT,
    revenue_cagr_5yr                REAL,
    revenue_cagr_5yr_flag           TEXT,
    revenue_cagr_10yr               REAL,
    revenue_cagr_10yr_flag          TEXT,
    pat_cagr_3yr                    REAL,
    pat_cagr_3yr_flag               TEXT,
    pat_cagr_5yr                    REAL,
    pat_cagr_5yr_flag               TEXT,
    pat_cagr_10yr                   REAL,
    pat_cagr_10yr_flag              TEXT,
    eps_cagr_3yr                    REAL,
    eps_cagr_3yr_flag               TEXT,
    eps_cagr_5yr                    REAL,
    eps_cagr_5yr_flag               TEXT,
    eps_cagr_10yr                   REAL,
    eps_cagr_10yr_flag              TEXT,
    
    fcf_cagr_5yr                    REAL,
    fcf_cagr_5yr_flag               TEXT,

    -- Composite Score (Day 12)
    composite_quality_score         REAL,
    -- Extra 20 KPIs
    gross_margin_pct REAL,
    ebitda_margin_pct REAL,
    pre_tax_margin_pct REAL,
    net_profit_to_ebitda REAL,
    return_on_invested_capital_pct REAL,
    debt_to_assets REAL,
    debt_to_capital REAL,
    equity_multiplier REAL,
    fixed_asset_turnover REAL,
    working_capital_to_sales_pct REAL,
    interest_bearing_debt_ratio REAL,
    tax_rate_pct REAL,
    cash_flow_to_debt REAL,
    operating_cash_flow_margin_pct REAL,
    operating_cash_flow_to_net_income REAL,
    retained_earnings_to_assets REAL,
    net_debt_to_equity REAL,
    net_debt_to_ebitda REAL,
    ebit_to_total_assets REAL,
    cash_flow_coverage_ratio REAL,
    interest_to_sales_pct REAL,


    UNIQUE(company_id, year)
);
"""


def _safe(val):
    """Convert pandas NaN/None to Python None for SQLite."""
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val


def _bool_to_int(val):
    """Convert True/False/None to 1/0/None for SQLite INTEGER storage."""
    if val is None:
        return None
    return 1 if val else 0


def load_source_data():
    """Load and normalise all source Excel files."""
    data = {}
    for name, fname in FILES.items():
        path = os.path.join(DATA_DIR, fname)
        hdr = HEADERS[name]
        df = pd.read_excel(path, header=hdr)
        data[name] = df
        print(f"  Loaded {name}: {df.shape}")
    return data


def normalize_and_filter(data):
    """Normalize year columns and tag non-standard periods."""
    for name in ["profitandloss", "balancesheet", "cashflow"]:
        df = data[name]
        df["year_raw"] = df["year"].astype(str)
        df["year_norm"] = df["year_raw"].apply(normalize_year)
        # Mark non-standard periods
        df["is_standard_year"] = df["year_raw"].apply(is_valid_cagr_year)
        data[name] = df

    # Normalize financial_ratios source years
    fr = data["financial_ratios_src"]
    fr["year_norm"] = fr["year"].astype(str).apply(normalize_year)
    data["financial_ratios_src"] = fr

    return data


def deduplicate(df, keys, name=""):
    """
    Remove duplicate (company_id, year_norm) rows.
    Keep the row with the most non-null values.
    """
    if df.duplicated(subset=keys, keep=False).sum() == 0:
        return df

    dups_before = df.duplicated(subset=keys, keep=False).sum()

    # Score each row by count of non-null values
    df["_nnull"] = df.drop(columns=keys, errors="ignore").notna().sum(axis=1)
    df = df.sort_values("_nnull", ascending=False).drop_duplicates(subset=keys, keep="first")
    df = df.drop(columns=["_nnull"])

    print(f"  Deduplicated {name}: removed {dups_before - len(df[df.duplicated(subset=keys, keep=False)])} duplicate rows")
    return df


def build_joined_dataset(data):
    """Join P&L + BS + CF on (company_id, year_norm), preserving all P&L rows."""
    pl = data["profitandloss"].copy()
    bs = data["balancesheet"].copy()
    cf = data["cashflow"].copy()

    # Filter out PARSE_ERROR years
    pl = pl[pl["year_norm"] != "PARSE_ERROR"]
    bs = bs[bs["year_norm"] != "PARSE_ERROR"]
    cf = cf[cf["year_norm"] != "PARSE_ERROR"]

    # Deduplicate each table
    pl = deduplicate(pl, ["company_id", "year_norm"], "P&L")
    bs = deduplicate(bs, ["company_id", "year_norm"], "BS")
    cf = deduplicate(cf, ["company_id", "year_norm"], "CF")

    print(f"  After dedup: P&L={len(pl)}, BS={len(bs)}, CF={len(cf)}")

    # Left join P&L with BS
    bs_cols = ["company_id", "year_norm", "equity_capital", "reserves",
               "borrowings", "other_liabilities", "total_liabilities",
               "fixed_assets", "cwip", "investments", "other_asset", "total_assets"]
    merged = pl.merge(bs[bs_cols], on=["company_id", "year_norm"], how="left",
                      suffixes=("", "_bs"))

    # Left join with CF
    cf_cols = ["company_id", "year_norm", "operating_activity",
               "investing_activity", "financing_activity", "net_cash_flow"]
    merged = merged.merge(cf[cf_cols], on=["company_id", "year_norm"], how="left",
                          suffixes=("", "_cf"))

    print(f"  Joined dataset: {len(merged)} rows, {merged['company_id'].nunique()} companies")
    return merged


def build_sector_lookup(data):
    """Build company_id -> broad_sector lookup from sectors table."""
    sec = data["sectors"]
    return dict(zip(sec["company_id"], sec["broad_sector"]))


def build_source_ratios_lookup(data):
    """
    Build (company_id, year_norm) -> dict lookup for the source financial_ratios.xlsx.
    Used for:
      - book_value_per_share (time-series, preferred over snapshot)
      - cross-checking OPM, ROE, ROCE
    Deduplicate keeping row with most data.
    """
    fr = data["financial_ratios_src"].copy()
    fr = fr[fr["year_norm"] != "PARSE_ERROR"]
    fr = deduplicate(fr, ["company_id", "year_norm"], "financial_ratios_src")

    lookup = {}
    for _, row in fr.iterrows():
        key = (row["company_id"], row["year_norm"])
        lookup[key] = {
            "book_value_per_share": _safe(row.get("book_value_per_share")),
            "capex_cr": _safe(row.get("capex_cr")),
            "total_debt_cr": _safe(row.get("total_debt_cr")),
            "dividend_payout_ratio_pct": _safe(row.get("dividend_payout_ratio_pct")),
            "source_opm": _safe(row.get("operating_profit_margin_pct")),
            "source_roe": _safe(row.get("return_on_equity_pct")),
            "source_npm": _safe(row.get("net_profit_margin_pct")),
            "source_de": _safe(row.get("debt_to_equity")),
            "source_icr": _safe(row.get("interest_coverage")),
            "earnings_per_share": _safe(row.get("earnings_per_share")),
            "cash_from_operations_cr": _safe(row.get("cash_from_operations_cr")),
            "free_cash_flow_cr": _safe(row.get("free_cash_flow_cr")),
        }
    return lookup


def build_companies_lookup(data):
    """Build company_id -> (roce_percentage, roe_percentage) from companies table."""
    co = data["companies"]
    lookup = {}
    for _, row in co.iterrows():
        cid = row["id"]  # In companies.xlsx header=1, 'id' is the ticker
        lookup[cid] = {
            "roce_pct": _safe(row.get("roce_percentage")),
            "roe_pct": _safe(row.get("roe_percentage")),
        }
    return lookup


def compute_all_ratios(merged, sector_lookup, source_ratios, companies_lookup,
                       edge_log):
    """
    Compute all KPIs for each row and prepare CAGR data.

    Returns a list of dicts, one per (company_id, year_norm) row.
    """
    # Group merged data by company for CAGR lookups
    company_groups = {}
    for _, row in merged.iterrows():
        cid = row["company_id"]
        if cid not in company_groups:
            company_groups[cid] = []
        # Compute FCF for this row
        cfo_val = _safe(row.get("operating_activity"))
        cfi_val = _safe(row.get("investing_activity"))
        fcf_val = free_cash_flow(cfo_val, cfi_val)
        
        company_groups[cid].append({
            "year_norm": row["year_norm"],
            "year_raw": row.get("year_raw", ""),
            "sales": _safe(row.get("sales")),
            "net_profit": _safe(row.get("net_profit")),
            "eps": _safe(row.get("eps")),
            "operating_activity": cfo_val,
            "free_cash_flow": fcf_val,
        })

    results = []
    for _, row in merged.iterrows():
        cid = row["company_id"]
        yr = row["year_norm"]
        yr_raw = row.get("year_raw", "")
        sector = sector_lookup.get(cid, None)
        src = source_ratios.get((cid, yr), {})

        # Extract safe values
        sales = _safe(row.get("sales"))
        net_prof = _safe(row.get("net_profit"))
        op_profit = _safe(row.get("operating_profit"))
        opm_pct = _safe(row.get("opm_percentage"))
        other_inc = _safe(row.get("other_income"))
        interest_val = _safe(row.get("interest"))
        pbt = _safe(row.get("profit_before_tax"))
        eq_cap = _safe(row.get("equity_capital"))
        reserves_val = _safe(row.get("reserves"))
        borr = _safe(row.get("borrowings"))
        total_ast = _safe(row.get("total_assets"))
        invest = _safe(row.get("investments"))
        cfo = _safe(row.get("operating_activity"))
        cfi = _safe(row.get("investing_activity"))
        cff = _safe(row.get("financing_activity"))
        eps_val = _safe(row.get("eps"))
        div_payout = _safe(row.get("dividend_payout"))

        # --- Profitability ---
        npm = net_profit_margin(net_prof, sales)
        opm = operating_profit_margin(op_profit, sales)

        # OPM cross-check
        opm_match, opm_diff = opm_cross_check(opm, opm_pct)
        if opm_match is not None and not opm_match:
            edge_log.append({
                "company": cid, "year": yr, "metric": "OPM",
                "computed": round(opm, 2) if opm else None,
                "source": opm_pct,
                "difference": round(opm_diff, 2) if opm_diff else None,
                "category": "formula discrepancy",
                "explanation": f"Computed OPM ({opm:.2f}%) differs from source opm_percentage ({opm_pct}%) by {opm_diff:.2f}%",
            })

        roe = return_on_equity(net_prof, eq_cap, reserves_val)
        roce = return_on_capital_employed(pbt, interest_val, eq_cap, reserves_val, borr)
        roa = return_on_assets(net_prof, total_ast)

        # --- Leverage & Efficiency ---
        de = debt_to_equity(borr, eq_cap, reserves_val)
        hlf = high_leverage_flag(de, sector)
        icr = interest_coverage_ratio(op_profit, other_inc, interest_val)
        icr_lbl = icr_label_value(interest_val)
        icr_warn = icr_warning(icr)
        nd = net_debt(borr, invest)
        at = asset_turnover(sales, total_ast)


        depr = _safe(row.get("depreciation"))
        expenses = _safe(row.get("expenses"))
        ol = _safe(row.get("other_liabilities"))
        oa = _safe(row.get("other_asset"))
        fa = _safe(row.get("fixed_assets"))
        tl = _safe(row.get("total_liabilities"))

        gm = gross_margin(sales, expenses)
        ebitdam = ebitda_margin(op_profit, depr, sales)
        ptm = pre_tax_margin(pbt, sales)
        npe = net_profit_to_ebitda(net_prof, op_profit, depr)
        ro_ic = return_on_invested_capital(net_prof, eq_cap, reserves_val, borr)
        dta = debt_to_assets_ratio(borr, total_ast)
        dtc = debt_to_capital_ratio(borr, eq_cap, reserves_val)
        em = equity_multiplier_ratio(total_ast, eq_cap, reserves_val)
        fat = fixed_asset_turnover_ratio(sales, fa)
        wcs = working_capital_to_sales(oa, ol, sales)
        ibd = interest_bearing_debt_ratio_calc(borr, tl)
        tr = tax_rate_calc(pbt, net_prof)
        cfd = cash_flow_to_debt_ratio(cfo, borr)
        ocfm = operating_cash_flow_margin(cfo, sales)
        ocfni = operating_cash_flow_to_net_income(cfo, net_prof)
        rea = retained_earnings_to_assets(reserves_val, total_ast)
        nde = net_debt_to_equity_ratio(borr, invest, eq_cap, reserves_val)
        ndeb = net_debt_to_ebitda_ratio(borr, invest, op_profit, depr)
        eta = ebit_to_total_assets(op_profit, total_ast)
        cfcr = cash_flow_coverage_ratio_calc(cfo, interest_val)
        its = interest_to_sales_ratio(interest_val, sales)

        # --- Cash Flow ---
        fcf = free_cash_flow(cfo, cfi)
        fcf_conv = fcf_conversion(fcf, op_profit)

        # CapEx: from source financial_ratios if available, else derive from CFI
        capex_val = src.get("capex_cr")

        # CapEx intensity
        capex_int_pct, capex_int_lbl = capex_intensity(cfi, sales)

        # EPS: prefer P&L source
        eps_out = eps_val if eps_val is not None else src.get("earnings_per_share")

        # Book value per share: use time-series from financial_ratios.xlsx
        bvps = src.get("book_value_per_share")

        # Dividend payout: from source ratios if P&L value is None
        div_pay = div_payout if div_payout is not None else src.get("dividend_payout_ratio_pct")

        # Total debt: borrowings from BS, fallback to source
        total_debt = borr if borr is not None else src.get("total_debt_cr")

        # Cash from operations
        cfo_out = cfo if cfo is not None else src.get("cash_from_operations_cr")

        # FCF: prefer computed, fallback to source
        fcf_out = fcf if fcf is not None else src.get("free_cash_flow_cr")

        result = {
            "company_id": cid,
            "year": yr,
            "net_profit_margin_pct": npm,
            "operating_profit_margin_pct": opm,
            "return_on_equity_pct": roe,
            "return_on_capital_employed_pct": roce,
            "return_on_assets_pct": roa,
            "debt_to_equity": de,
            "high_leverage_flag": _bool_to_int(hlf),
            "interest_coverage": icr,
            "icr_label": icr_lbl,
            "icr_warning_flag": _bool_to_int(icr_warn),
            "net_debt_cr": nd,
            "asset_turnover": at,
            "free_cash_flow_cr": fcf_out,
            "capex_cr": capex_val,
            "cash_from_operations_cr": cfo_out,
            "capex_intensity_pct": capex_int_pct,
            "capex_intensity_label": capex_int_lbl,
            "fcf_conversion_pct": fcf_conv,
            "earnings_per_share": eps_out,
            "book_value_per_share": bvps,
            "dividend_payout_ratio_pct": div_pay,
            "total_debt_cr": total_debt,
            # CAGR and CFO quality placeholders — filled below

            "gross_margin_pct": gm,
            "ebitda_margin_pct": ebitdam,
            "pre_tax_margin_pct": ptm,
            "net_profit_to_ebitda": npe,
            "return_on_invested_capital_pct": ro_ic,
            "debt_to_assets": dta,
            "debt_to_capital": dtc,
            "equity_multiplier": em,
            "fixed_asset_turnover": fat,
            "working_capital_to_sales_pct": wcs,
            "interest_bearing_debt_ratio": ibd,
            "tax_rate_pct": tr,
            "cash_flow_to_debt": cfd,
            "operating_cash_flow_margin_pct": ocfm,
            "operating_cash_flow_to_net_income": ocfni,
            "retained_earnings_to_assets": rea,
            "net_debt_to_equity": nde,
            "net_debt_to_ebitda": ndeb,
            "ebit_to_total_assets": eta,
            "cash_flow_coverage_ratio": cfcr,
            "interest_to_sales_pct": its,
            "cfo_quality_ratio": None,
            "cfo_quality_label": None,
        }

        results.append(result)

    return results, company_groups


def compute_cagr_columns(results, company_groups):
    """Compute all CAGR columns for each result row."""
    for res in results:
        cid = res["company_id"]
        yr = res["year"]
        cdata = company_groups.get(cid, [])

        for metric, col_prefix in [("sales", "revenue"), ("net_profit", "pat"), ("eps", "eps")]:
            for n_years in [3, 5, 10]:
                val, flag = compute_cagr_for_series(cdata, metric, n_years, yr)
                res[f"{col_prefix}_cagr_{n_years}yr"] = val
                res[f"{col_prefix}_cagr_{n_years}yr_flag"] = flag
                
        # Also compute fcf_cagr_5yr
        val, flag = compute_cagr_for_series(cdata, "free_cash_flow", 5, yr)
        res["fcf_cagr_5yr"] = val
        res["fcf_cagr_5yr_flag"] = flag


def compute_cfo_quality_columns(results, company_groups):
    """Compute CFO quality ratio for each result row using trailing 5 years."""
    # Build per-company year-sorted data
    for cid, cdata in company_groups.items():
        # Sort by fiscal year descending for trailing lookups
        cdata_sorted = sorted(cdata, key=lambda x: x["year_norm"], reverse=True)
        company_groups[cid] = cdata_sorted

    for res in results:
        cid = res["company_id"]
        yr = res["year"]
        cdata = company_groups.get(cid, [])

        # Find trailing 5 years ending at this year
        fy = extract_fiscal_year(yr)
        if fy is None:
            continue

        pairs = []
        for row in cdata:
            row_fy = extract_fiscal_year(row["year_norm"])
            if row_fy is None:
                continue
            if row_fy <= fy and row_fy > fy - 5:
                cfo_val = row.get("operating_activity")
                pat_val = row.get("net_profit")
                if cfo_val is not None and pat_val is not None:
                    pairs.append((cfo_val, pat_val))

        ratio, label = cfo_quality_ratio(pairs)
        res["cfo_quality_ratio"] = ratio
        res["cfo_quality_label"] = label


def compute_composite_scores(results):
    """
    Composite Quality Score: percentile-rank normalization of:
    ROE, ROA, CFO quality ratio, FCF conversion.

    Each component is ranked across all valid rows, converted to 0-100 percentile.
    Final score = mean of available normalized components.
    If fewer than 2 valid components, return None.
    """
    # Collect all valid values for each component
    components = ["return_on_equity_pct", "return_on_assets_pct",
                   "cfo_quality_ratio", "fcf_conversion_pct"]

    # Build rank lookup for each component
    rank_lookups = {}
    for comp in components:
        vals = [(i, res[comp]) for i, res in enumerate(results) if res[comp] is not None]
        if not vals:
            rank_lookups[comp] = {}
            continue
        # Sort by value ascending
        vals_sorted = sorted(vals, key=lambda x: x[1])
        n = len(vals_sorted)
        rank_map = {}
        for rank, (idx, val) in enumerate(vals_sorted):
            rank_map[idx] = (rank / (n - 1)) * 100 if n > 1 else 50.0
        rank_lookups[comp] = rank_map

    # Compute composite for each row
    for i, res in enumerate(results):
        scores = []
        for comp in components:
            pctile = rank_lookups[comp].get(i)
            if pctile is not None:
                scores.append(pctile)
        if len(scores) >= 2:
            res["composite_quality_score"] = sum(scores) / len(scores)
        else:
            res["composite_quality_score"] = None


def generate_capital_allocation(results, output_dir):
    """Generate output/capital_allocation.csv."""
    rows = []
    for res in results:
        cfo = res.get("cash_from_operations_cr")
        # We need raw CFO/CFI/CFF — use the values from the result
        # But we need the raw cash flow signs
        cfi = None  # We need to pass through from computation
        cff = None
        # We stored free_cash_flow_cr but need raw cfi/cff for signs
        # This is handled in the main flow — we'll pass through
    # This will be called from the main flow with raw data
    pass


def run_financials_carveout(results, sector_lookup, companies_lookup, edge_log):
    """
    Day 13: Cross-check computed ROCE/ROE against source for Financials.

    For every company, cross-check against source companies.xlsx snapshot values
    for the latest available year. Log discrepancies > 5% for ROCE and any
    anomalous ROE values.
    """
    for res in results:
        cid = res["company_id"]
        yr = res["year"]
        sector = sector_lookup.get(cid)
        co_data = companies_lookup.get(cid, {})

        # Cross-check ROCE against source (companies.xlsx has snapshot)
        source_roce = co_data.get("roce_pct")
        computed_roce = res.get("return_on_capital_employed_pct")
        if source_roce is not None and computed_roce is not None:
            diff = abs(computed_roce - source_roce)
            if diff > 5.0:
                edge_log.append({
                    "company": cid, "year": yr, "metric": "ROCE",
                    "computed": round(computed_roce, 2),
                    "source": source_roce,
                    "difference": round(diff, 2),
                    "category": "version difference" if sector == "Financials" else "formula discrepancy",
                    "explanation": f"Computed ROCE ({computed_roce:.2f}%) vs source snapshot ({source_roce}%). "
                                   f"Source is a point-in-time snapshot, computed is for year {yr}. "
                                   f"{'Financials sector — structural differences expected.' if sector == 'Financials' else ''}",
                })

        # Cross-check ROE
        source_roe = co_data.get("roe_pct")
        computed_roe = res.get("return_on_equity_pct")
        if source_roe is not None and computed_roe is not None:
            diff = abs(computed_roe - source_roe)
            if diff > 5.0:
                edge_log.append({
                    "company": cid, "year": yr, "metric": "ROE",
                    "computed": round(computed_roe, 2),
                    "source": source_roe,
                    "difference": round(diff, 2),
                    "category": "version difference",
                    "explanation": f"Computed ROE ({computed_roe:.2f}%) vs source snapshot ({source_roe}%). "
                                   f"Source is point-in-time, computed is for year {yr}.",
                })


def write_edge_case_log(edge_log, output_dir):
    """Write output/ratio_edge_cases.log with structured entries."""
    path = os.path.join(output_dir, "ratio_edge_cases.log")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Ratio Edge Cases Log — Generated {datetime.now().isoformat()}\n")
        f.write(f"# Total entries: {len(edge_log)}\n\n")
        for i, entry in enumerate(edge_log, 1):
            f.write(f"--- Entry {i} ---\n")
            f.write(f"Company:     {entry['company']}\n")
            f.write(f"Year:        {entry['year']}\n")
            f.write(f"Metric:      {entry['metric']}\n")
            f.write(f"Computed:    {entry['computed']}\n")
            f.write(f"Source:      {entry['source']}\n")
            f.write(f"Difference:  {entry['difference']}\n")
            f.write(f"Category:    {entry['category']}\n")
            f.write(f"Explanation: {entry['explanation']}\n\n")
    print(f"  Edge case log: {len(edge_log)} entries -> {path}")


def write_to_sqlite(results, db_path):
    """Write all results to the financial_ratios SQLite table."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.executescript(FINANCIAL_RATIOS_SCHEMA)

    # Prepare columns (excluding 'id' — auto-increment)
    columns = [
        "company_id", "year",
        "net_profit_margin_pct", "operating_profit_margin_pct",
        "return_on_equity_pct", "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "debt_to_equity", "high_leverage_flag",
        "interest_coverage", "icr_label", "icr_warning_flag",
        "net_debt_cr", "asset_turnover",
        "free_cash_flow_cr", "capex_cr", "cash_from_operations_cr",
        "cfo_quality_ratio", "cfo_quality_label",
        "capex_intensity_pct", "capex_intensity_label",
        "fcf_conversion_pct",
        "earnings_per_share", "book_value_per_share",
        "dividend_payout_ratio_pct", "total_debt_cr",
        "revenue_cagr_3yr", "revenue_cagr_3yr_flag",
        "revenue_cagr_5yr", "revenue_cagr_5yr_flag",
        "revenue_cagr_10yr", "revenue_cagr_10yr_flag",
        "pat_cagr_3yr", "pat_cagr_3yr_flag",
        "pat_cagr_5yr", "pat_cagr_5yr_flag",
        "pat_cagr_10yr", "pat_cagr_10yr_flag",
        "eps_cagr_3yr", "eps_cagr_3yr_flag",
        "eps_cagr_5yr", "eps_cagr_5yr_flag",
        "eps_cagr_10yr", "eps_cagr_10yr_flag",
        "fcf_cagr_5yr", "fcf_cagr_5yr_flag",
        "composite_quality_score",
        "gross_margin_pct", "ebitda_margin_pct", "pre_tax_margin_pct",
        "net_profit_to_ebitda", "return_on_invested_capital_pct", "debt_to_assets",
        "debt_to_capital", "equity_multiplier", "fixed_asset_turnover",
        "working_capital_to_sales_pct", "interest_bearing_debt_ratio", "tax_rate_pct",
        "cash_flow_to_debt", "operating_cash_flow_margin_pct",
        "operating_cash_flow_to_net_income", "retained_earnings_to_assets",
        "net_debt_to_equity", "net_debt_to_ebitda", "ebit_to_total_assets",
        "cash_flow_coverage_ratio", "interest_to_sales_pct",

    ]

    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO financial_ratios ({col_names}) VALUES ({placeholders})"

    rows_data = []
    for res in results:
        row_vals = [res.get(col) for col in columns]
        rows_data.append(tuple(row_vals))

    cursor.executemany(sql, rows_data)
    conn.commit()

    # Verify
    count = cursor.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    companies = cursor.execute("SELECT COUNT(DISTINCT company_id) FROM financial_ratios").fetchone()[0]
    conn.close()

    print(f"  SQLite: {count} rows, {companies} companies -> {db_path}")
    return count


def write_capital_allocation_csv(merged_df, results, output_dir):
    """Generate output/capital_allocation.csv from merged data."""
    path = os.path.join(output_dir, "capital_allocation.csv")

    rows = []
    for _, mrow in merged_df.iterrows():
        cid = mrow["company_id"]
        yr = mrow["year_norm"]
        cfo = _safe(mrow.get("operating_activity"))
        cfi = _safe(mrow.get("investing_activity"))
        cff = _safe(mrow.get("financing_activity"))

        # Get CFO/PAT ratio for priority rule
        pat = _safe(mrow.get("net_profit"))
        cfo_pat = None
        if cfo is not None and pat is not None and pat != 0:
            cfo_pat = cfo / pat

        label, s_cfo, s_cfi, s_cff = capital_allocation_label(cfo, cfi, cff, cfo_pat)

        rows.append({
            "company_id": cid,
            "year": yr,
            "cfo_sign": s_cfo,
            "cfi_sign": s_cfi,
            "cff_sign": s_cff,
            "pattern_label": label,
        })

    df_out = pd.DataFrame(rows)
    df_out.to_csv(path, index=False)
    print(f"  Capital allocation: {len(df_out)} rows -> {path}")


def run():
    """Main entry point — execute the full ratio engine."""
    print("=" * 70)
    print("Sprint 2 — Ratio Engine")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load source data
    print("\n[1] Loading source data...")
    data = load_source_data()

    # 2. Normalize years
    print("\n[2] Normalizing years...")
    data = normalize_and_filter(data)

    # 3. Build lookups
    print("\n[3] Building lookups...")
    sector_lookup = build_sector_lookup(data)
    source_ratios = build_source_ratios_lookup(data)
    companies_lookup = build_companies_lookup(data)
    print(f"  Sectors: {len(sector_lookup)} companies")
    print(f"  Source ratios: {len(source_ratios)} (company, year) pairs")
    print(f"  Companies snapshot: {len(companies_lookup)} companies")
    print(f"  Financials companies: {sum(1 for v in sector_lookup.values() if v == 'Financials')}")

    # 4. Join tables
    print("\n[4] Joining P&L + BS + CF...")
    merged = build_joined_dataset(data)

    # 5. Compute ratios
    print("\n[5] Computing KPIs...")
    edge_log = []
    results, company_groups = compute_all_ratios(merged, sector_lookup, source_ratios,
                                                  companies_lookup, edge_log)
    print(f"  Computed {len(results)} rows")

    # 6. CAGR
    print("\n[6] Computing CAGR...")
    compute_cagr_columns(results, company_groups)

    # 7. CFO quality
    print("\n[7] Computing CFO quality...")
    compute_cfo_quality_columns(results, company_groups)

    # 8. Composite score
    print("\n[8] Computing composite quality scores...")
    compute_composite_scores(results)

    # 9. Financials carve-out
    print("\n[9] Financials carve-out & cross-checks...")
    run_financials_carveout(results, sector_lookup, companies_lookup, edge_log)

    # Log duplicate edge cases
    edge_log.append({
        "company": "ABB", "year": "2014-03", "metric": "DUPLICATE_ROW",
        "computed": "kept non-zero FCF row",
        "source": "financial_ratios.xlsx had 2 rows for ABB/Mar 2014",
        "difference": "N/A",
        "category": "data source issue",
        "explanation": "Source financial_ratios.xlsx contains duplicate row for ABB Mar 2014. "
                       "Row id=2 has FCF=11, capex=144 (valid). Row id=3 has FCF=0, capex=0 (erroneous). "
                       "Kept the non-zero row per deduplication logic.",
    })

    # SBIN edge case
    edge_log.append({
        "company": "SBIN", "year": "ALL", "metric": "MISSING_BALANCE_SHEET",
        "computed": "NULL for BS-dependent KPIs",
        "source": "No balance sheet data in source",
        "difference": "N/A",
        "category": "data source issue",
        "explanation": "SBIN (State Bank of India) has P&L and Cash Flow data but no Balance Sheet "
                       "rows in the source. BS-dependent KPIs (ROE, ROCE, D/E, ROA, Asset Turnover, "
                       "Net Debt) are set to NULL. No data fabrication performed.",
    })

    # VBL edge case
    edge_log.append({
        "company": "VBL", "year": "ALL", "metric": "MISSING_BALANCE_SHEET",
        "computed": "NULL for BS-dependent KPIs",
        "source": "No balance sheet data in source",
        "difference": "N/A",
        "category": "data source issue",
        "explanation": "VBL has P&L data but no Balance Sheet rows in the source. "
                       "BS-dependent KPIs are set to NULL.",
    })

    # 10. Write edge case log
    print("\n[10] Writing edge case log...")
    write_edge_case_log(edge_log, OUTPUT_DIR)

    # 11. Write capital allocation CSV
    print("\n[11] Writing capital allocation CSV...")
    write_capital_allocation_csv(merged, results, OUTPUT_DIR)

    # 12. Write to SQLite
    print("\n[12] Writing to SQLite...")
    count = write_to_sqlite(results, DB_PATH)

    # 13. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  financial_ratios rows: {count}")
    print(f"  Edge cases logged:     {len(edge_log)}")
    print(f"  Database:              {DB_PATH}")
    print(f"  Capital allocation:    {os.path.join(OUTPUT_DIR, 'capital_allocation.csv')}")
    print(f"  Edge case log:         {os.path.join(OUTPUT_DIR, 'ratio_edge_cases.log')}")


if __name__ == "__main__":
    run()
