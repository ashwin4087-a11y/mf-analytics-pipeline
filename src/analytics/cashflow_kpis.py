"""
src/analytics/cashflow_kpis.py — Day 11: Cash Flow KPIs.

Implements:
    1. Free Cash Flow (CFO + CFI)
    2. CFO Quality (5-year average CFO/PAT)
    3. CapEx Intensity (|CFI| / sales * 100)
    4. FCF Conversion (FCF / operating_profit * 100)
    5. Capital Allocation Classifier (based on CFO/CFI/CFF signs)

Sign convention:
    CFO (operating_activity): positive = cash inflow from operations
    CFI (investing_activity): negative = capital expenditure (cash outflow)
    CFF (financing_activity): negative = debt repayment / dividends
"""


def free_cash_flow(cfo, cfi):
    """
    FCF = CFO + CFI

    Negative FCF is valid and must NOT be converted to None.
    Returns None only if inputs are None.
    """
    if cfo is None or cfi is None:
        return None
    return cfo + cfi


def cfo_quality_ratio(cfo_pat_pairs):
    """
    CFO Quality = mean(CFO/PAT) over trailing 5 available full-year observations.

    Args:
        cfo_pat_pairs: list of (cfo, pat) tuples for the trailing years,
                       ordered from most recent to oldest. Maximum 5 entries.

    Processing:
        - Exclude observations where PAT == 0 (avoid division by zero).
        - If fewer than 2 valid observations remain, return None.

    Returns:
        (ratio, label) tuple:
        - ratio: float average CFO/PAT or None
        - label: 'High Quality' / 'Moderate' / 'Accrual Risk' / None
    """
    if not cfo_pat_pairs:
        return None, None

    valid_ratios = []
    for cfo, pat in cfo_pat_pairs[:5]:  # Take at most 5 observations
        if cfo is None or pat is None:
            continue
        if pat == 0:
            # Document: PAT==0 observation excluded from mean
            continue
        valid_ratios.append(cfo / pat)

    if len(valid_ratios) < 2:
        return None, None

    avg_ratio = sum(valid_ratios) / len(valid_ratios)
    label = _cfo_quality_label(avg_ratio)
    return avg_ratio, label


def _cfo_quality_label(ratio):
    """Classify CFO quality ratio into label."""
    if ratio is None:
        return None
    if ratio > 1.0:
        return "High Quality"
    elif ratio >= 0.5:
        return "Moderate"
    else:
        return "Accrual Risk"


def capex_intensity(cfi, sales):
    """
    CapEx Intensity = abs(CFI) / sales * 100

    Returns:
        (pct, label) tuple:
        - pct: float percentage or None
        - label: 'Asset Light' / 'Moderate' / 'Capital Intensive' / None
    """
    if cfi is None or sales is None:
        return None, None
    if sales == 0:
        return None, None

    pct = abs(cfi) / sales * 100
    label = _capex_intensity_label(pct)
    return pct, label


def _capex_intensity_label(pct):
    """Classify capex intensity percentage into label."""
    if pct is None:
        return None
    if pct < 3.0:
        return "Asset Light"
    elif pct <= 8.0:
        return "Moderate"
    else:
        return "Capital Intensive"


def fcf_conversion(fcf, operating_profit):
    """
    FCF Conversion = (FCF / operating_profit) * 100

    Returns None if operating_profit == 0 or any input is None.
    """
    if fcf is None or operating_profit is None:
        return None
    if operating_profit == 0:
        return None
    return (fcf / operating_profit) * 100


def _sign(value):
    """
    Return the sign character for a cash flow component.
    Zero is treated as neutral — documented as '0'.
    """
    if value is None:
        return None
    if value > 0:
        return "+"
    elif value < 0:
        return "-"
    else:
        return "0"


def capital_allocation_label(cfo, cfi, cff, cfo_pat_ratio=None):
    """
    Classify capital allocation pattern based on signs of CFO, CFI, CFF.

    Priority rule for (+,-,-) overlap:
        If CFO/PAT >= 1.0 (high quality): 'Shareholder Returns'
        Otherwise: 'Reinvestor'

    Zero cash-flow components:
        Treated as neutral. A zero value does not trigger any positive or
        negative pattern match. Rows with any zero component fall into 'Mixed'.

    Args:
        cfo: operating cash flow (positive = inflow)
        cfi: investing cash flow (negative = spending on assets)
        cff: financing cash flow (negative = repaying debt/dividends)
        cfo_pat_ratio: optional CFO/PAT ratio for the (+,-,-) priority rule

    Returns:
        (label, cfo_sign, cfi_sign, cff_sign) tuple
    """
    if cfo is None or cfi is None or cff is None:
        return None, None, None, None

    s_cfo = _sign(cfo)
    s_cfi = _sign(cfi)
    s_cff = _sign(cff)

    pattern = (s_cfo, s_cfi, s_cff)

    # Handle patterns with zero — fall through to Mixed
    if "0" in pattern:
        return "Mixed", s_cfo, s_cfi, s_cff

    LABELS = {
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    # Handle the (+,-,-) overlap with priority rule
    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio >= 1.0:
            return "Shareholder Returns", s_cfo, s_cfi, s_cff
        else:
            return "Reinvestor", s_cfo, s_cfi, s_cff

    label = LABELS.get(pattern, "Mixed")
    return label, s_cfo, s_cfi, s_cff
import os
import sqlite3
import pandas as pd

def generate_cashflow_intelligence():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.path.join(BASE_DIR, 'data', 'nifty100.db')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        companies = pd.read_sql("SELECT c.id as company_id, c.company_name, s.broad_sector as sector FROM companies c LEFT JOIN sectors s ON c.id = s.company_id", conn)
        cf = pd.read_sql("SELECT * FROM cashflow ORDER BY company_id, year", conn)
        pl = pd.read_sql("SELECT * FROM profitandloss ORDER BY company_id, year", conn)
        bs = pd.read_sql("SELECT * FROM balancesheet ORDER BY company_id, year", conn)
        ratios = pd.read_sql("SELECT company_id, fcf_cagr_5yr FROM financial_ratios WHERE fcf_cagr_5yr IS NOT NULL", conn).groupby('company_id').tail(1)
        
    results = []
    distress = []
    
    for _, comp in companies.iterrows():
        cid = comp['company_id']
        c_cf = cf[cf['company_id'] == cid].copy()
        c_pl = pl[pl['company_id'] == cid].copy()
        c_bs = bs[bs['company_id'] == cid].copy()
        
        if c_cf.empty or c_pl.empty:
            continue
            
        latest_cf = c_cf.iloc[-1]
        latest_pl = c_pl.iloc[-1]
        
        # CFO Quality
        cfo_pat_pairs = []
        for _, row in c_cf.tail(5).iterrows():
            y = row['year']
            pl_row = c_pl[c_pl['year'] == y]
            if not pl_row.empty:
                cfo_pat_pairs.append((row['operating_activity'], pl_row.iloc[0]['net_profit']))
        cfo_quality_score, cfo_quality_label = cfo_quality_ratio(cfo_pat_pairs)
        
        # CapEx Intensity
        capex_intensity_pct, capex_label = capex_intensity(latest_cf['investing_activity'], latest_pl['sales'])
        
        # FCF Conversion
        fcf = free_cash_flow(latest_cf['operating_activity'], latest_cf['investing_activity'])
        fcf_conversion_pct = fcf_conversion(fcf, latest_pl['operating_profit'])
        
        # Distress Signal
        distress_flag = False
        if latest_cf['operating_activity'] is not None and latest_cf['financing_activity'] is not None:
            if latest_cf['operating_activity'] < 0 and latest_cf['financing_activity'] > 0:
                distress_flag = True
                
        # Deleveraging flag
        deleveraging_flag = False
        if len(c_bs) >= 2 and latest_cf['financing_activity'] is not None and latest_cf['financing_activity'] < 0:
            if c_bs.iloc[-1]['borrowings'] is not None and c_bs.iloc[-2]['borrowings'] is not None:
                if c_bs.iloc[-1]['borrowings'] < c_bs.iloc[-2]['borrowings']:
                    deleveraging_flag = True
                    
        # Capital Allocation
        capital_allocation_label_str, _, _, _ = capital_allocation_label(
            latest_cf['operating_activity'], 
            latest_cf['investing_activity'], 
            latest_cf['financing_activity'], 
            cfo_quality_score
        )
        
        # FCF CAGR
        fcf_cagr_5yr = ratios[ratios['company_id'] == cid]['fcf_cagr_5yr'].values[0] if not ratios[ratios['company_id'] == cid].empty else None
        
        results.append({
            'company_id': cid,
            'sector': comp['sector'],
            'cfo_quality_score': cfo_quality_score,
            'cfo_quality_label': cfo_quality_label,
            'capex_intensity_pct': capex_intensity_pct,
            'capex_label': capex_label,
            'fcf_cagr_5yr': fcf_cagr_5yr,
            'fcf_conversion_pct': fcf_conversion_pct,
            'distress_flag': distress_flag,
            'deleveraging_flag': deleveraging_flag,
            'capital_allocation_label': capital_allocation_label_str
        })
        
        if distress_flag:
            distress.append({
                'company_id': cid,
                'cfo': latest_cf['operating_activity'],
                'cff': latest_cf['financing_activity'],
                'latest_net_profit': latest_pl['net_profit']
            })
            
    df_res = pd.DataFrame(results)
    df_dist = pd.DataFrame(distress)
    
    df_res.to_excel(os.path.join(OUTPUT_DIR, 'cashflow_intelligence.xlsx'), index=False)
    df_dist.to_csv(os.path.join(OUTPUT_DIR, 'distress_alerts.csv'), index=False)
    print("Cash Flow Intelligence Module generated outputs.")

if __name__ == '__main__':
    generate_cashflow_intelligence()
