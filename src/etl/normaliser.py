import re
import pandas as pd
from datetime import datetime

def normalize_year(year_str):
    """
    Normalise year strings to 'YYYY-MM' format.
    Handles 'Mar-23', 'Mar 23', 'March-2023', '2023', 'FY23', 'Dec-22', etc.
    Returns 'PARSE_ERROR' for invalid formats.
    """
    if pd.isna(year_str) or year_str is None:
        return "PARSE_ERROR"
        
    year_str = str(year_str).strip()
    
    # Already normalised
    if re.match(r'^\d{4}-\d{2}$', year_str):
        return year_str
        
    # Just year: 2023 -> 2023-03
    if re.match(r'^\d{4}$', year_str):
        return f"{year_str}-03"
        
    # FY format: FY23 -> 2023-03
    m_fy = re.match(r'^FY(\d{2})$', year_str, re.IGNORECASE)
    if m_fy:
        return f"20{m_fy.group(1)}-03"
        
    # Month-Year format: Mar-23, Mar 23, March-2023, Dec-22, Jun-23
    m_month_year = re.match(r'^([a-zA-Z]+)[\s-]*(\d{2,4})$', year_str)
    if m_month_year:
        month_str = m_month_year.group(1)[:3].capitalize()
        year_part = m_month_year.group(2)
        
        # Convert month abbreviation to number
        try:
            month_num = datetime.strptime(month_str, '%b').strftime('%m')
        except ValueError:
            return "PARSE_ERROR"
            
        # Convert year
        if len(year_part) == 2:
            full_year = f"20{year_part}"
        elif len(year_part) == 4:
            full_year = year_part
        else:
            return "PARSE_ERROR"
            
        return f"{full_year}-{month_num}"
        
    return "PARSE_ERROR"


def normalize_ticker(ticker):
    """
    Normalise company ticker by stripping whitespace and uppercasing.
    Returns 'MISSING' if empty or null.
    """
    if pd.isna(ticker) or ticker is None:
        return "MISSING"
        
    ticker_str = str(ticker).strip()
    
    if not ticker_str:
        return "MISSING"
        
    return ticker_str.upper()
