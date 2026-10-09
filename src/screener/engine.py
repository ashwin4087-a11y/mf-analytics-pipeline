import sqlite3
import pandas as pd
import numpy as np
import yaml
from typing import Dict, Any, Optional
import os

class ScreenerEngine:
    def __init__(self, db_path: str, config_path: str):
        self.db_path = db_path
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration for screener."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def load_data(self) -> pd.DataFrame:
        """Load and integrate data from SQLite database."""
        query = """
            SELECT 
                f.company_id,
                c.company_name,
                f.return_on_equity_pct as roe,
                f.return_on_capital_employed_pct,
                f.net_profit_margin_pct,
                f.cfo_quality_ratio,
                f.debt_to_equity as de,
                f_prev.debt_to_equity as de_prev,
                f.free_cash_flow_cr as fcf,
                f.fcf_cagr_5yr,
                f.revenue_cagr_5yr,
                f.revenue_cagr_3yr,
                f.pat_cagr_5yr,
                f.operating_profit_margin_pct as opm,
                m.pe_ratio as pe,
                m.pb_ratio as pb,
                m.dividend_yield_pct as dividend_yield,
                f.dividend_payout_ratio_pct as dividend_payout,
                f.interest_coverage as icr,
                f.icr_label,
                m.market_cap_crore as market_cap,
                p.net_profit,
                f.eps_cagr_5yr,
                f.asset_turnover,
                p.sales as revenue,
                s.broad_sector
            FROM financial_ratios f
            LEFT JOIN companies c ON f.company_id = c.id
            LEFT JOIN market_cap m ON f.company_id = m.company_id AND f.year = m.year
            LEFT JOIN profitandloss p ON f.company_id = p.company_id AND f.year = p.year
            LEFT JOIN sectors s ON f.company_id = s.company_id
            JOIN (
                SELECT company_id, MAX(year) as max_year
                FROM financial_ratios
                GROUP BY company_id
            ) f2 ON f.company_id = f2.company_id AND f.year = f2.max_year
            LEFT JOIN financial_ratios f_prev ON f.company_id = f_prev.company_id 
                AND f_prev.year = (
                    SELECT MAX(year) FROM financial_ratios WHERE company_id = f.company_id AND year < f.year
                )
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
            
        # Explicit ICR Rule: if icr_label == "Debt Free", ICR is infinity
        df.loc[df['icr_label'] == 'Debt Free', 'icr'] = np.inf
        
        # Calculate D/E declining flag
        df['de_declining'] = (df['de'] < df['de_prev']).fillna(False)
        
        # Calculate FCF positive latest
        df['fcf_positive_latest'] = (df['fcf'] > 0).fillna(False)
        
        # Add composite score
        df = self.add_composite_score(df)
        
        return df

    def winsorize_scale(self, series, lower=False):
        p10 = series.quantile(0.10)
        p90 = series.quantile(0.90)
        clipped = series.clip(lower=p10, upper=p90)
        if p90 == p10: return pd.Series(50.0, index=series.index)
        scaled = (clipped - p10) / (p90 - p10) * 100
        if lower: scaled = 100 - scaled
        return scaled

    def add_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        score = pd.Series(0.0, index=df.index)
        
        required_metrics = [
            'roe', 'return_on_capital_employed_pct', 'net_profit_margin_pct',
            'fcf_cagr_5yr', 'cfo_quality_ratio', 'fcf',
            'revenue_cagr_5yr', 'pat_cagr_5yr',
            'de', 'icr'
        ]
        
        for metric in required_metrics:
            if metric not in df.columns:
                raise ValueError(f"CRITICAL ERROR: Required metric '{metric}' is genuinely missing from the dataset. Cannot compute composite quality score accurately.")

        # 35% Profitability
        score += self.winsorize_scale(df['roe']) * 0.15
        score += self.winsorize_scale(df['return_on_capital_employed_pct']) * 0.10
        score += self.winsorize_scale(df['net_profit_margin_pct']) * 0.10
        
        # 30% Cash Quality
        score += self.winsorize_scale(df['fcf_cagr_5yr']) * 0.15
        score += self.winsorize_scale(df['cfo_quality_ratio']) * 0.10
        score += (df['fcf'] > 0).astype(float) * 5.0
        
        # 20% Growth
        score += self.winsorize_scale(df['revenue_cagr_5yr']) * 0.10
        score += self.winsorize_scale(df['pat_cagr_5yr']) * 0.10
        
        # 15% Leverage
        score += self.winsorize_scale(df['de'], lower=True) * 0.10
        score += self.winsorize_scale(df['icr'].replace(np.inf, 9999)) * 0.05
        
        # Normalise within sector
        df['composite_quality_score'] = score
        df['composite_quality_score'] = df.groupby('broad_sector')['composite_quality_score'].transform(
            lambda x: (x - x.min()) / (x.max() - x.min()) * 100 if x.max() != x.min() else x
        ).fillna(50.0)
        return df

    def run_screener(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply thresholds from filters."""
        result = df.copy()
        
        if 'roe_min' in filters:
            result = result[result['roe'] >= filters['roe_min']]
            
        if 'de_max' in filters:
            cond = (result['de'] <= filters['de_max']) | (result['broad_sector'] == 'Financials')
            result = result[cond]
            
        if 'fcf_min' in filters:
            result = result[result['fcf'] >= filters['fcf_min']]
            
        if 'revenue_cagr_5yr_min' in filters:
            result = result[result['revenue_cagr_5yr'] >= filters['revenue_cagr_5yr_min']]
            
        if 'revenue_cagr_3yr_min' in filters:
            result = result[result['revenue_cagr_3yr'] >= filters['revenue_cagr_3yr_min']]
            
        if 'pat_cagr_5yr_min' in filters:
            result = result[result['pat_cagr_5yr'] >= filters['pat_cagr_5yr_min']]
            
        if 'opm_min' in filters:
            result = result[result['opm'] >= filters['opm_min']]
            
        if 'pe_max' in filters:
            result = result[result['pe'] <= filters['pe_max']]
            
        if 'pb_max' in filters:
            result = result[result['pb'] <= filters['pb_max']]
            
        if 'dividend_yield_min' in filters:
            result = result[result['dividend_yield'] >= filters['dividend_yield_min']]
            
        if 'dividend_payout_max' in filters:
            result = result[result['dividend_payout'] <= filters['dividend_payout_max']]
            
        if 'icr_min' in filters:
            result = result[result['icr'] >= filters['icr_min']]
            
        if 'market_cap_min' in filters:
            result = result[result['market_cap'] >= filters['market_cap_min']]
            
        if 'net_profit_min' in filters:
            result = result[result['net_profit'] >= filters['net_profit_min']]
            
        if 'eps_cagr_5yr_min' in filters:
            result = result[result['eps_cagr_5yr'] >= filters['eps_cagr_5yr_min']]
            
        if 'asset_turnover_min' in filters:
            result = result[result['asset_turnover'] >= filters['asset_turnover_min']]
            
        if 'revenue_min' in filters:
            result = result[result['revenue'] >= filters['revenue_min']]
            
        if 'fcf_positive_latest' in filters and filters['fcf_positive_latest']:
            result = result[result['fcf_positive_latest'] == True]
            
        if 'de_declining' in filters and filters['de_declining']:
            result = result[result['de_declining'] == True]

        # Sort by composite quality score descending
        if 'composite_quality_score' in result:
            result = result.sort_values(by='composite_quality_score', ascending=False)
        return result

if __name__ == "__main__":
    db_path = "../../data/nifty100.db"
    config_path = "../../config/screener_config.yaml"
    engine = ScreenerEngine(db_path, config_path)
    df = engine.load_data()
    print("Loaded data rows:", len(df))
