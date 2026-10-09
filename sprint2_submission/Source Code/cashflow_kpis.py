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
