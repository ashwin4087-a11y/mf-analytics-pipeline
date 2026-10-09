import os
import pytest
import numpy as pd_np
import pandas as pd
from src.etl.normaliser import normalize_year, normalize_ticker
from src.etl.loader import load_excel

# --- normalize_year tests ---
def test_normalize_year_mar_23():
    assert normalize_year("Mar-23") == "2023-03"

def test_normalize_year_mar_23_space():
    assert normalize_year("Mar 23") == "2023-03"

def test_normalize_year_march_2023():
    assert normalize_year("March-2023") == "2023-03"

def test_normalize_year_2023():
    assert normalize_year("2023") == "2023-03"

def test_normalize_year_fy23():
    assert normalize_year("FY23") == "2023-03"

def test_normalize_year_dec_22():
    assert normalize_year("Dec-22") == "2022-12"

def test_normalize_year_jun_23():
    assert normalize_year("Jun-23") == "2023-06"

def test_normalize_year_already_normalised():
    assert normalize_year("2023-03") == "2023-03"

def test_normalize_year_garbage():
    assert normalize_year("garbage") == "PARSE_ERROR"

def test_normalize_year_none():
    assert normalize_year(None) == "PARSE_ERROR"

def test_normalize_year_nan():
    assert normalize_year(pd_np.nan) == "PARSE_ERROR"

def test_normalize_year_empty():
    assert normalize_year("") == "PARSE_ERROR"

def test_normalize_year_whitespace():
    assert normalize_year("  Mar-23  ") == "2023-03"

def test_normalize_year_full_month_upper():
    assert normalize_year("DECEMBER 2022") == "2022-12"

def test_normalize_year_fy_lower():
    assert normalize_year("fy24") == "2024-03"

def test_normalize_year_three_digits():
    assert normalize_year("123") == "PARSE_ERROR"

def test_normalize_year_jan():
    assert normalize_year("Jan-23") == "2023-01"

def test_normalize_year_feb():
    assert normalize_year("Feb-2023") == "2023-02"

def test_normalize_year_invalid_month():
    assert normalize_year("Xyz-23") == "PARSE_ERROR"

def test_normalize_year_incomplete():
    assert normalize_year("Mar-") == "PARSE_ERROR"


# --- normalize_ticker tests ---
def test_normalize_ticker_standard():
    assert normalize_ticker("TCS") == "TCS"

def test_normalize_ticker_lower():
    assert normalize_ticker("tcs") == "TCS"

def test_normalize_ticker_hyphen():
    assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"

def test_normalize_ticker_ampersand():
    assert normalize_ticker("M&M") == "M&M"

def test_normalize_ticker_whitespace():
    assert normalize_ticker("  TCS  ") == "TCS"

def test_normalize_ticker_none():
    assert normalize_ticker(None) == "MISSING"

def test_normalize_ticker_nan():
    assert normalize_ticker(pd_np.nan) == "MISSING"

def test_normalize_ticker_empty():
    assert normalize_ticker("") == "MISSING"

def test_normalize_ticker_spaces_only():
    assert normalize_ticker("   ") == "MISSING"

def test_normalize_ticker_newline():
    assert normalize_ticker("TCS\n") == "TCS"

def test_normalize_ticker_mixed_case():
    assert normalize_ticker("tCs") == "TCS"

def test_normalize_ticker_numeric():
    assert normalize_ticker("123") == "123"

def test_normalize_ticker_with_spaces():
    assert normalize_ticker("TCS Ltd") == "TCS LTD"

def test_normalize_ticker_hdfc():
    assert normalize_ticker("HDFC BANK") == "HDFC BANK"

def test_normalize_ticker_reliance():
    assert normalize_ticker("RELIANCE") == "RELIANCE"

def test_normalize_ticker_infy():
    assert normalize_ticker("INFY") == "INFY"

def test_normalize_ticker_wipro():
    assert normalize_ticker("WIPRO") == "WIPRO"

def test_normalize_ticker_hindunilvr():
    assert normalize_ticker("HINDUNILVR") == "HINDUNILVR"

def test_normalize_ticker_itc():
    assert normalize_ticker("ITC") == "ITC"

def test_normalize_ticker_lt():
    assert normalize_ticker("LT") == "LT"


# --- load_excel tests ---
def test_load_excel_core(tmp_path):
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    # Write with a dummy metadata row on top so header=1 works properly
    dummy = pd.DataFrame([["meta1", "meta2"]], columns=['col1', 'col2'])
    out_df = pd.concat([dummy, df])
    file_path = tmp_path / "core.xlsx"
    out_df.to_excel(file_path, index=False)
    
    loaded_df = load_excel(file_path, is_core=True)
    assert isinstance(loaded_df, pd.DataFrame)
    # Since header=1, the first row of out_df (meta1, meta2) becomes the header
    assert "meta1" in loaded_df.columns

def test_load_excel_supporting(tmp_path):
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)
    file_path = tmp_path / "supporting.xlsx"
    df.to_excel(file_path, index=False)
    
    loaded_df = load_excel(file_path, is_core=False)
    assert isinstance(loaded_df, pd.DataFrame)
    assert "col1" in loaded_df.columns

def test_load_excel_missing_file():
    with pytest.raises(FileNotFoundError):
        load_excel("nonexistent_file.xlsx")
