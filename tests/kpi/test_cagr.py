"""Unit tests for CAGR calculations and edge cases."""
import pytest
from src.analytics.cagr import compute_cagr, extract_fiscal_year, is_valid_cagr_year

# --- CAGR Tests (5) ---

def test_cagr_positive_to_positive():
    # Edge case 1: Normal compute
    cagr, flag = compute_cagr(100, 161.051, 5)  # 10% for 5 years = 1.1^5 = 1.61051
    assert round(cagr, 1) == 10.0
    assert flag is None

def test_cagr_edge_cases():
    # Edge case 2: Positive -> Negative
    cagr, flag = compute_cagr(100, -50, 5)
    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"
    
    # Positive -> Zero (also decline to loss)
    cagr, flag = compute_cagr(100, 0, 5)
    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"
    
    # Edge case 3: Negative -> Positive
    cagr, flag = compute_cagr(-50, 100, 5)
    assert cagr is None
    assert flag == "TURNAROUND"
    
    # Edge case 4: Negative -> Negative
    cagr, flag = compute_cagr(-50, -10, 5)
    assert cagr is None
    assert flag == "BOTH_NEGATIVE"

def test_cagr_zero_and_insufficient():
    # Edge case 5: Zero base
    cagr, flag = compute_cagr(0, 100, 5)
    assert cagr is None
    assert flag == "ZERO_BASE"
    
    # Edge case 6: Insufficient
    cagr, flag = compute_cagr(None, 100, 5)
    assert cagr is None
    assert flag == "INSUFFICIENT"
    
    cagr, flag = compute_cagr(100, 200, 0)
    assert cagr is None
    assert flag == "INSUFFICIENT"

def test_extract_fiscal_year():
    assert extract_fiscal_year("2024-03") == 2024
    assert extract_fiscal_year("PARSE_ERROR") is None
    assert extract_fiscal_year(None) is None

def test_is_valid_cagr_year():
    assert is_valid_cagr_year("Mar 2024") is True
    assert is_valid_cagr_year("2024") is True
    assert is_valid_cagr_year("TTM") is False
    assert is_valid_cagr_year("Mar 2016 9m") is False
    assert is_valid_cagr_year("Mar 2023 15") is False
    # Don't accidentally exclude regular years with 15
    assert is_valid_cagr_year("Mar 2015") is True
