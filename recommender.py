import sqlite3
import pandas as pd
import argparse

def recommend_funds(risk_appetite: str, db_path: str = 'bluestock_mf.db') -> pd.DataFrame:
    """
    Recommends the top 3 mutual funds based on the provided risk appetite.
    Matches against risk_grade and ranks by sharpe_ratio (descending).
    
    Args:
        risk_appetite: 'Low', 'Moderate', or 'High'
        db_path: path to the SQLite database
    
    Returns:
        DataFrame containing the top 3 recommended funds.
    """
    valid_risks = ['Low', 'Moderate', 'High']
    if risk_appetite not in valid_risks:
        raise ValueError(f"risk_appetite must be one of {valid_risks}")
        
    query = """
    SELECT 
        amfi_code, 
        scheme_name, 
        category, 
        risk_grade, 
        sharpe_ratio, 
        return_3yr_pct,
        expense_ratio_pct
    FROM fact_performance
    WHERE risk_grade = ?
    ORDER BY sharpe_ratio DESC
    LIMIT 3
    """
    
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(risk_appetite,))
        return df
    except Exception as e:
        print(f"Error querying database: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Mutual Fund Recommender")
    parser.add_argument('risk_appetite', type=str, choices=['Low', 'Moderate', 'High'], 
                        help="Your risk appetite: Low, Moderate, or High")
    args = parser.parse_args()
    
    print(f"--- Top 3 Recommended Funds for {args.risk_appetite} Risk ---")
    recommendations = recommend_funds(args.risk_appetite)
    
    if recommendations.empty:
        print("No recommendations found or an error occurred.")
    else:
        print(recommendations.to_string(index=False))
