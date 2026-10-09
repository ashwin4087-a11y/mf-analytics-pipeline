"""
src/analytics/cagr.py — Day 10: CAGR Engine.

Computes Compound Annual Growth Rate for Revenue, PAT, and EPS over
3-year, 5-year, and 10-year horizons.

CAGR = ((end / start) ** (1/n) - 1) * 100

Six edge cases are handled explicitly:
    1. Positive -> Positive: compute normally
    2. Positive -> Negative: None, flag=DECLINE_TO_LOSS
    3. Negative -> Positive: None, flag=TURNAROUND
    4. Negative -> Negative: None, flag=BOTH_NEGATIVE
    5. Zero base:            None, flag=ZERO_BASE
    6. Insufficient years:   None, flag=INSUFFICIENT

Year selection:
    A 5-year CAGR uses values separated by exactly 5 calendar years,
    NOT merely 5 available rows. If the required start/end year is
    missing from the dataset, the flag is INSUFFICIENT.

Non-standard periods (TTM, 9m, 15m) are excluded from CAGR calculations.
"""


def compute_cagr(start_value, end_value, n_years):
    """
    Compute CAGR given start and end values over n_years.

    Returns:
        (value, flag) tuple where:
        - value is the CAGR percentage (float) or None
        - flag is a string edge-case label or None if computed normally

    Handles all six specified edge cases.
    """
    # Validate inputs
    if start_value is None or end_value is None or n_years is None:
        return None, "INSUFFICIENT"

    if n_years <= 0:
        return None, "INSUFFICIENT"

    # Edge case 5: Zero base
    if start_value == 0:
        return None, "ZERO_BASE"

    # Edge case 4: Both negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Edge case 3: Negative -> Positive (turnaround)
    if start_value < 0 and end_value >= 0:
        return None, "TURNAROUND"

    # Edge case 2: Positive -> Negative (decline to loss)
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Edge case: end is zero (positive -> zero is a valid decline, not a loss)
    # Treat as decline to loss since the company went from profit to zero
    if start_value > 0 and end_value == 0:
        return None, "DECLINE_TO_LOSS"

    # Edge case 1: Positive -> Positive — compute normally
    ratio = end_value / start_value
    cagr = (ratio ** (1.0 / n_years) - 1) * 100
    return cagr, None


def extract_fiscal_year(year_norm):
    """
    Extract the calendar year from a normalized year string (YYYY-MM format).

    Returns integer year or None if parsing fails.
    For fiscal years ending in March (YYYY-03), the fiscal year label
    is the calendar year itself (e.g., '2024-03' -> 2024).
    """
    if not year_norm or year_norm == "PARSE_ERROR":
        return None
    try:
        parts = year_norm.split("-")
        return int(parts[0])
    except (ValueError, IndexError):
        return None


def is_valid_cagr_year(year_raw):
    """
    Check whether a raw year string represents a full-year period
    suitable for CAGR calculations.

    Excludes:
    - TTM (trailing twelve months — not a fixed period)
    - 9m periods (e.g., 'Mar 2016 9m')
    - 15m periods (e.g., 'Mar 2023 15')

    Returns True if the year is valid for CAGR.
    """
    if year_raw is None:
        return False
    year_str = str(year_raw).strip()
    if not year_str:
        return False

    # Exclude TTM
    if year_str.upper() == "TTM":
        return False

    # Exclude 9m periods
    if "9m" in year_str.lower():
        return False

    # Exclude 15-month periods (ends with ' 15' pattern like 'Mar 2023 15')
    # Be careful not to exclude years containing '15' as part of the year
    # like 'Mar 2015' — only match standalone ' 15' suffix
    if year_str.endswith(" 15"):
        return False

    return True


def compute_cagr_for_series(company_data, value_column, n_years, latest_year_norm):
    """
    Compute CAGR for a specific metric over n_years for a given company.

    Args:
        company_data: list of dicts with keys 'year_norm', 'year_raw', and
                      the value_column. Must be pre-filtered to a single company.
        value_column: string key for the metric (e.g., 'sales', 'net_profit', 'eps')
        n_years: number of years for CAGR (3, 5, or 10)
        latest_year_norm: the end year in YYYY-MM format (e.g., '2024-03')

    Returns:
        (value, flag) tuple — see compute_cagr docstring.
    """
    # Determine start year
    end_fiscal = extract_fiscal_year(latest_year_norm)
    if end_fiscal is None:
        return None, "INSUFFICIENT"

    start_fiscal = end_fiscal - n_years

    # Build lookup of fiscal_year -> value, filtering out invalid CAGR years
    year_lookup = {}
    for row in company_data:
        if not is_valid_cagr_year(row.get("year_raw")):
            continue
        fy = extract_fiscal_year(row.get("year_norm"))
        if fy is not None:
            year_lookup[fy] = row.get(value_column)

    # Look up start and end values
    end_value = year_lookup.get(end_fiscal)
    start_value = year_lookup.get(start_fiscal)

    if end_value is None or start_value is None:
        return None, "INSUFFICIENT"

    return compute_cagr(start_value, end_value, n_years)
