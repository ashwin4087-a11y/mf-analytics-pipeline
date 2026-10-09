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
