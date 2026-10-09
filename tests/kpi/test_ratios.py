"""Unit tests for profitability and leverage ratios."""
import pytest
from src.analytics.ratios import (
    net_profit_margin, operating_profit_margin, opm_cross_check,
    return_on_equity, return_on_capital_employed, return_on_assets,
    debt_to_equity, high_leverage_flag, interest_coverage_ratio,
    icr_label_value, icr_warning, net_debt, asset_turnover
)

# --- Profitability Tests (8) ---

def test_net_profit_margin():
    assert net_profit_margin(100, 1000) == 10.0
    assert net_profit_margin(-50, 1000) == -5.0
    assert net_profit_margin(100, 0) is None
    assert net_profit_margin(None, 1000) is None

def test_operating_profit_margin():
    assert operating_profit_margin(150, 1000) == 15.0
    assert operating_profit_margin(None, 1000) is None
    assert operating_profit_margin(150, 0) is None

def test_opm_cross_check():
    match, diff = opm_cross_check(15.2, 15.0)
    assert match is True
    assert diff == pytest.approx(0.2)
    
    match, diff = opm_cross_check(15.2, 12.0)
    assert match is False
    assert diff == pytest.approx(3.2)
    
    match, diff = opm_cross_check(None, 15.0)
    assert match is None
    assert diff is None

def test_return_on_equity():
    assert return_on_equity(100, 200, 300) == 20.0
    assert return_on_equity(100, 200, -300) is None  # negative equity
    assert return_on_equity(100, None, 300) is None

def test_return_on_capital_employed():
    # EBIT = PBT (150) + Interest (50) = 200
    # CE = Equity (200) + Reserves (300) + Borrowings (500) = 1000
    assert return_on_capital_employed(150, 50, 200, 300, 500) == 20.0
    assert return_on_capital_employed(150, 50, -100, 0, 0) is None  # CE <= 0
    assert return_on_capital_employed(None, 50, 200, 300, 500) is None

def test_return_on_assets():
    assert return_on_assets(100, 1000) == 10.0
    assert return_on_assets(100, 0) is None

# --- Leverage & Efficiency Tests (8) ---

def test_debt_to_equity():
    assert debt_to_equity(500, 200, 300) == 1.0
    assert debt_to_equity(0, 200, 300) == 0.0
    assert debt_to_equity(500, 100, -200) is None  # negative equity
    assert debt_to_equity(None, 200, 300) is None

def test_high_leverage_flag():
    assert high_leverage_flag(6.0, "Technology") is True
    assert high_leverage_flag(4.0, "Technology") is False
    assert high_leverage_flag(8.0, "Financials") is False  # Suppressed for Financials
    assert high_leverage_flag(None, "Technology") is None

def test_interest_coverage_ratio():
    # ICR = (OP + OI) / interest = (100 + 20) / 40 = 3.0
    assert interest_coverage_ratio(100, 20, 40) == 3.0
    assert interest_coverage_ratio(100, 20, 0) is None  # debt-free

def test_icr_helpers():
    assert icr_label_value(0) == "Debt Free"
    assert icr_label_value(40) is None
    
    assert icr_warning(1.0) is True
    assert icr_warning(2.0) is False
    assert icr_warning(None) is None

def test_net_debt():
    assert net_debt(500, 200) == 300
    assert net_debt(200, 500) == -300  # Cash rich
    assert net_debt(None, 200) is None

def test_asset_turnover():
    assert asset_turnover(2000, 1000) == 2.0
    assert asset_turnover(2000, 0) is None
    assert asset_turnover(None, 1000) is None

# This gives 12 tests so far. I will distribute the 20 across the 3 files.
