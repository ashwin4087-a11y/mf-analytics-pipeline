import pytest
from src.analytics.ratios import (
    gross_margin, ebitda_margin, pre_tax_margin, net_profit_to_ebitda,
    return_on_invested_capital, debt_to_assets_ratio, debt_to_capital_ratio,
    equity_multiplier_ratio, fixed_asset_turnover_ratio, working_capital_to_sales,
    interest_bearing_debt_ratio_calc, tax_rate_calc, cash_flow_to_debt_ratio,
    operating_cash_flow_margin, operating_cash_flow_to_net_income,
    retained_earnings_to_assets, net_debt_to_equity_ratio, net_debt_to_ebitda_ratio,
    ebit_to_total_assets, cash_flow_coverage_ratio_calc, interest_to_sales_ratio
)

def test_gross_margin():
    assert gross_margin(100, 40) == 60.0
    assert gross_margin(0, 40) is None
    assert gross_margin(None, 40) is None

def test_ebitda_margin():
    assert ebitda_margin(20, 5, 100) == 25.0
    assert ebitda_margin(20, 5, 0) is None

def test_pre_tax_margin():
    assert pre_tax_margin(15, 100) == 15.0

def test_net_profit_to_ebitda():
    assert net_profit_to_ebitda(10, 20, 5) == 10 / 25
    assert net_profit_to_ebitda(10, 0, 0) is None

def test_return_on_invested_capital():
    assert return_on_invested_capital(10, 50, 25, 25) == 10.0
    assert return_on_invested_capital(10, 0, 0, 0) is None

def test_debt_to_assets_ratio():
    assert debt_to_assets_ratio(20, 100) == 0.2
    assert debt_to_assets_ratio(20, 0) is None

def test_debt_to_capital_ratio():
    assert debt_to_capital_ratio(25, 50, 25) == 0.25
    assert debt_to_capital_ratio(25, 0, 0) == 1.0

def test_equity_multiplier_ratio():
    assert equity_multiplier_ratio(100, 40, 10) == 2.0
    assert equity_multiplier_ratio(100, 0, 0) is None

def test_fixed_asset_turnover_ratio():
    assert fixed_asset_turnover_ratio(200, 100) == 2.0

def test_working_capital_to_sales():
    assert working_capital_to_sales(50, 30, 100) == 0.2

def test_tax_rate_calc():
    assert tax_rate_calc(100, 75) == 25.0
    assert tax_rate_calc(0, 75) is None
