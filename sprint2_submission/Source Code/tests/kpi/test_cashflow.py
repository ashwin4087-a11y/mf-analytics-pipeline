"""Unit tests for cash flow KPIs."""
import pytest
from src.analytics.cashflow_kpis import (
    free_cash_flow, cfo_quality_ratio, capex_intensity,
    fcf_conversion, capital_allocation_label, _sign
)

# --- Cash Flow KPI Tests (3) ---

def test_free_cash_flow():
    assert free_cash_flow(100, -40) == 60
    assert free_cash_flow(100, 40) == 140
    assert free_cash_flow(-100, -40) == -140
    assert free_cash_flow(None, -40) is None

def test_cfo_quality_and_fcf_conversion():
    # cfo_quality_ratio
    pairs = [(100, 50), (120, 60), (None, 50), (100, 0), (150, 75)]
    # valid: 100/50=2, 120/60=2, 150/75=2 (the 100,0 is skipped)
    # mean = 2.0
    ratio, label = cfo_quality_ratio(pairs)
    assert ratio == 2.0
    assert label == "High Quality"
    
    ratio, label = cfo_quality_ratio([])
    assert ratio is None
    
    # fcf_conversion
    assert fcf_conversion(60, 100) == 60.0
    assert fcf_conversion(60, 0) is None
    assert fcf_conversion(None, 100) is None

def test_capital_allocation_label():
    # priority rule (+,-,-) with high CFO quality (>= 1.0)
    label, _, _, _ = capital_allocation_label(100, -50, -30, 1.2)
    assert label == "Shareholder Returns"
    
    # priority rule (+,-,-) with low CFO quality (< 1.0)
    label, _, _, _ = capital_allocation_label(100, -50, -30, 0.8)
    assert label == "Reinvestor"
    
    # Distress Signal
    label, _, _, _ = capital_allocation_label(-100, 50, 20, 0)
    assert label == "Distress Signal"
    
    # With a zero (Mixed)
    label, _, _, _ = capital_allocation_label(100, 0, -30, 1.2)
    assert label == "Mixed"
    
    # _sign helper
    assert _sign(100) == "+"
    assert _sign(-50) == "-"
    assert _sign(0) == "0"
    assert _sign(None) is None
