import os
import re
import pandas as pd
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DB_PATH = os.path.join(DATA_DIR, 'nifty100.db')

def _find_file(suffix):
    for f in os.listdir(DATA_DIR):
        if f.endswith(suffix):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError(f"Source file not found: *{suffix}")

def run_parser():
    analysis_file = _find_file('analysis.xlsx')
    df_raw = pd.read_excel(analysis_file, header=1) # The core file loader uses header=1
    
    # If the file has 'id', we drop it. The ticker is 'company_id'
    
    pattern = re.compile(r'(\d+)\s*Years?:?\s*([\d.-]+)%')
    
    parsed_rows = []
    failed_rows = []
    
    metrics_map = {
        'compounded_sales_growth': 'Compounded Sales Growth',
        'compounded_profit_growth': 'Compounded Profit Growth',
        'stock_price_cagr': 'Stock Price CAGR',
        'roe': 'Return on Equity'
    }
    
    for _, row in df_raw.iterrows():
        cid = row.get('company_id')
        if pd.isna(cid) or str(cid).strip() == 'MISSING':
            continue
            
        cid = str(cid).strip()
        
        for col_key, col_display in metrics_map.items():
            if col_key in row and pd.notna(row[col_key]):
                val = str(row[col_key])
                if not val.strip():
                    continue
                # The cell could contain multiple lines like:
                # 10 Years: 15%
                # 5 Years: 10%
                lines = val.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    match = pattern.search(line)
                    if match:
                        years = match.group(1)
                        value = match.group(2)
                        parsed_rows.append({
                            'company_id': cid,
                            'metric_type': col_display,
                            'period_years': int(years),
                            'value_pct': float(value)
                        })
                    else:
                        failed_rows.append({
                            'company_id': cid,
                            'metric_type': col_display,
                            'raw_text': line
                        })

    df_parsed = pd.DataFrame(parsed_rows)
    df_failed = pd.DataFrame(failed_rows)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_parsed.to_csv(os.path.join(OUTPUT_DIR, 'analysis_parsed.csv'), index=False)
    df_failed.to_csv(os.path.join(OUTPUT_DIR, 'parse_failures.csv'), index=False)
    
    # Cross-validate CAGR against Ratio Engine (Sprint 2 financial_ratios table)
    # The financial ratios table computes revenue_cagr_5yr, pat_cagr_5yr.
    # Let's cross-validate the 5-year metrics.
    with sqlite3.connect(DB_PATH) as conn:
        try:
            ratios_df = pd.read_sql("SELECT company_id, revenue_cagr_5yr, pat_cagr_5yr FROM financial_ratios", conn)
            # Take the latest available per company
            ratios_df = ratios_df.dropna(subset=['revenue_cagr_5yr', 'pat_cagr_5yr']).groupby('company_id').tail(1)
        except:
            ratios_df = pd.DataFrame()
            
    if not df_parsed.empty and not ratios_df.empty:
        # Check sales growth 5-year
        sales_5y = df_parsed[(df_parsed['metric_type'] == 'Compounded Sales Growth') & (df_parsed['period_years'] == 5)]
        merged_sales = sales_5y.merge(ratios_df, on='company_id')
        merged_sales['diff'] = (merged_sales['value_pct'] - merged_sales['revenue_cagr_5yr']).abs()
        divergent_sales = merged_sales[merged_sales['diff'] > 5.0]
        
        profit_5y = df_parsed[(df_parsed['metric_type'] == 'Compounded Profit Growth') & (df_parsed['period_years'] == 5)]
        merged_profit = profit_5y.merge(ratios_df, on='company_id')
        merged_profit['diff'] = (merged_profit['value_pct'] - merged_profit['pat_cagr_5yr']).abs()
        divergent_profit = merged_profit[merged_profit['diff'] > 5.0]
        
        if not divergent_sales.empty or not divergent_profit.empty:
            print("WARNING: Divergence >5% found between parsed NLP and Ratio Engine.")
            print(f"Sales Divergence: {len(divergent_sales)} rows")
            print(f"Profit Divergence: {len(divergent_profit)} rows")
            
    print("NLP Parser Complete.")
    
if __name__ == '__main__':
    run_parser()
