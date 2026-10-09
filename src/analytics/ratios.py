"""
src/analytics/ratios.py — Day 08 & 09: Profitability, Leverage & Efficiency ratios.

All ratio functions are pure functions that accept scalar values and return
the computed ratio or None when the calculation is undefined.

EBIT derivation decision:
    EBIT = profit_before_tax + interest
    (Accounting identity: PBT = EBIT - Interest, therefore EBIT = PBT + Interest)
    This is internally consistent with the P&L structure in the source data.
"""
import math


# ---------------------------------------------------------------------------
# Day 08 — Profitability Ratios
# ---------------------------------------------------------------------------

def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (net_profit / sales) * 100

    Returns None if sales == 0 (division undefined).
    """
    if sales is None or net_profit is None:
        return None
    if sales == 0:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = (operating_profit / sales) * 100

    Returns None if sales == 0 or if operating_profit is None.
    """
    if operating_profit is None or sales is None:
        return None
    if sales == 0:
        return None
    return (operating_profit / sales) * 100


def opm_cross_check(computed_opm, source_opm):
    """
    Compare computed OPM against the source opm_percentage field.

    Returns a tuple: (matches: bool, abs_difference: float or None)
    If either value is None, returns (None, None) — cannot compare.
    A mismatch is flagged when abs difference > 1%.
    """
    if computed_opm is None or source_opm is None:
        return None, None
    diff = abs(computed_opm - source_opm)
    return diff <= 1.0, diff


def return_on_equity(net_profit, equity_capital, reserves):
    """
    ROE = (net_profit / (equity_capital + reserves)) * 100

    Returns None if:
    - equity_capital + reserves <= 0 (negative or zero equity)
    - any input is None
    """
    if net_profit is None or equity_capital is None or reserves is None:
        return None
    equity = equity_capital + reserves
    if equity <= 0:
        return None
    return (net_profit / equity) * 100


def return_on_capital_employed(profit_before_tax, interest, equity_capital,
                                reserves, borrowings):
    """
    ROCE = (EBIT / capital_employed) * 100

    Where:
        EBIT = profit_before_tax + interest
        capital_employed = equity_capital + reserves + borrowings

    Returns None if capital_employed <= 0 or any input is None.

    Note on Financials sector:
        ROCE is still computed for Financials companies using the same formula.
        However, the absolute ROCE threshold should NOT be applied for screening
        Financials companies. The engine layer handles sector-relative benchmarking.
        This function is formula-only and sector-agnostic.
    """
    if any(v is None for v in [profit_before_tax, interest, equity_capital,
                                reserves, borrowings]):
        return None
    ebit = profit_before_tax + interest
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets):
    """
    ROA = (net_profit / total_assets) * 100

    Returns None if total_assets == 0 or any input is None.
    """
    if net_profit is None or total_assets is None:
        return None
    if total_assets == 0:
        return None
    return (net_profit / total_assets) * 100


# ---------------------------------------------------------------------------
# Day 09 — Leverage & Efficiency Ratios
# ---------------------------------------------------------------------------

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    D/E = borrowings / (equity_capital + reserves)

    Special cases:
    - If borrowings == 0: return 0 (NOT None) — company is debt-free.
    - If equity_capital + reserves <= 0: return None (invalid/negative equity).
    - If any input is None: return None.
    """
    if borrowings is None or equity_capital is None or reserves is None:
        return None
    if borrowings == 0:
        return 0.0
    equity = equity_capital + reserves
    if equity <= 0:
        return None
    return borrowings / equity


def high_leverage_flag(de_ratio, broad_sector):
    """
    High leverage flag: D/E > 5 AND company NOT in Financials sector.

    Financials companies have this warning suppressed because high leverage
    is structurally normal for banks/NBFCs/insurers.

    Returns:
        True  — high leverage warning applies
        False — either D/E <= 5 or company is Financials
        None  — D/E is None (cannot determine)
    """
    if de_ratio is None:
        return None
    if broad_sector == "Financials":
        return False  # Always suppress for Financials
    return de_ratio > 5.0


def interest_coverage_ratio(operating_profit, other_income, interest):
    """
    ICR = (operating_profit + other_income) / interest

    Returns None if interest == 0 (debt-free — see icr_label for text label).
    Returns None if any input is None.
    """
    if any(v is None for v in [operating_profit, other_income, interest]):
        return None
    if interest == 0:
        return None
    return (operating_profit + other_income) / interest


def icr_label_value(interest):
    """
    When interest == 0, ICR is None because the company is debt-free.
    This function returns the text label for that case.

    Returns:
        "Debt Free" if interest == 0
        None otherwise (numeric ICR is available)
    """
    if interest is None:
        return None
    if interest == 0:
        return "Debt Free"
    return None


def icr_warning(icr_value):
    """
    ICR warning flag: ICR < 1.5 indicates potential distress.

    Returns:
        True  — ICR < 1.5, warning applies
        False — ICR >= 1.5
        None  — ICR is None (debt-free or unavailable)
    """
    if icr_value is None:
        return None
    return icr_value < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt = borrowings - investments

    Negative net debt indicates cash-rich position.
    Returns None if any input is None.
    """
    if borrowings is None or investments is None:
        return None
    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover = sales / total_assets

    Returns None if total_assets == 0 or any input is None.
    """
    if sales is None or total_assets is None:
        return None
    if total_assets == 0:
        return None
    return sales / total_assets

# ---------------------------------------------------------------------------
# Extra 20 KPIs for Sprint 2 Requirement
# ---------------------------------------------------------------------------

def safe_div(num, den):
    if num is None or den is None or den == 0:
        return None
    return num / den

def gross_margin(sales, expenses):
    if sales is None or expenses is None or sales == 0: return None
    return ((sales - expenses) / sales) * 100

def ebitda_margin(op_profit, depr, sales):
    if op_profit is None or depr is None or sales is None or sales == 0: return None
    return ((op_profit + depr) / sales) * 100

def pre_tax_margin(pbt, sales):
    if pbt is None or sales is None or sales == 0: return None
    return (pbt / sales) * 100

def net_profit_to_ebitda(net_profit, op_profit, depr):
    if net_profit is None or op_profit is None or depr is None: return None
    ebitda = op_profit + depr
    if ebitda == 0: return None
    return net_profit / ebitda

def return_on_invested_capital(net_profit, eq, res, borr):
    if any(x is None for x in [net_profit, eq, res, borr]): return None
    ic = eq + res + borr
    if ic <= 0: return None
    return (net_profit / ic) * 100

def debt_to_assets_ratio(borr, ast):
    return safe_div(borr, ast)

def debt_to_capital_ratio(borr, eq, res):
    if any(x is None for x in [borr, eq, res]): return None
    cap = eq + res + borr
    if cap <= 0: return None
    return borr / cap

def equity_multiplier_ratio(ast, eq, res):
    if any(x is None for x in [ast, eq, res]): return None
    e = eq + res
    if e <= 0: return None
    return ast / e

def fixed_asset_turnover_ratio(sales, fa):
    return safe_div(sales, fa)

def working_capital_to_sales(oa, ol, sales):
    if any(x is None for x in [oa, ol, sales]): return None
    if sales == 0: return None
    return (oa - ol) / sales

def interest_bearing_debt_ratio_calc(borr, tl):
    return safe_div(borr, tl)

def tax_rate_calc(pbt, net_profit):
    if pbt is None or net_profit is None or pbt == 0: return None
    return ((pbt - net_profit) / pbt) * 100

def cash_flow_to_debt_ratio(cfo, borr):
    if cfo is None or borr is None: return None
    if borr == 0: return 0.0
    return cfo / borr

def operating_cash_flow_margin(cfo, sales):
    if cfo is None or sales is None or sales == 0: return None
    return (cfo / sales) * 100

def operating_cash_flow_to_net_income(cfo, net_profit):
    return safe_div(cfo, net_profit)

def retained_earnings_to_assets(res, ast):
    return safe_div(res, ast)

def net_debt_to_equity_ratio(borr, inv, eq, res):
    if any(x is None for x in [borr, inv, eq, res]): return None
    e = eq + res
    if e <= 0: return None
    return (borr - inv) / e

def net_debt_to_ebitda_ratio(borr, inv, op_profit, depr):
    if any(x is None for x in [borr, inv, op_profit, depr]): return None
    ebitda = op_profit + depr
    if ebitda == 0: return None
    return (borr - inv) / ebitda

def ebit_to_total_assets(op_profit, ast):
    return safe_div(op_profit, ast)

def cash_flow_coverage_ratio_calc(cfo, interest):
    if cfo is None or interest is None: return None
    if interest == 0: return None
    return cfo / interest

def interest_to_sales_ratio(interest, sales):
    if interest is None or sales is None or sales == 0: return None
    return (interest / sales) * 100

