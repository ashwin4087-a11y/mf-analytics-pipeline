import sqlite3
import pandas as pd

class PeerEngine:
    def __init__(self, db_path: str, peer_groups_path: str):
        self.db_path = db_path
        self.peer_groups_path = peer_groups_path
        
    def calculate_percentiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate peer-group percentile rankings for:
        ROE, ROCE, NPM, D/E, FCF, PAT CAGR 5Y, Revenue CAGR 5Y, EPS CAGR 5Y, Interest Coverage, Asset Turnover.
        D/E must use inverse ranking (Lower D/E = better percentile).
        """
        try:
            peer_groups_df = pd.read_excel(self.peer_groups_path)
        except Exception as e:
            # Fallback if db already has peer groups or file missing
            with sqlite3.connect(self.db_path) as conn:
                peer_groups_df = pd.read_sql_query("SELECT * FROM peer_groups", conn)
        
        metrics = ['roe', 'return_on_capital_employed_pct', 'net_profit_margin_pct', 'de', 'fcf', 
                  'pat_cagr_5yr', 'revenue_cagr_5yr', 'eps_cagr_5yr', 'icr', 'asset_turnover']
        
        peer_data = df.merge(peer_groups_df[['company_id', 'peer_group_name', 'is_benchmark']], on='company_id', how='left')
        peer_data['peer_group_name'] = peer_data['peer_group_name'].fillna('No peer group assigned')
        
        percentiles = []
        for pg, group in peer_data.groupby('peer_group_name'):
            if pg == 'No peer group assigned':
                continue
                
            for m in metrics:
                if m not in group:
                    raise ValueError(f"Missing required metric for peer percentiles: {m}")
                    
                # Rank: pct=True gives percentile (0-1). 
                # For D/E, lower is better. So invert the percentile.
                ranks = group[m].rank(pct=True)
                if m == 'de':
                    ranks = 1.0 - ranks
                
                for cid, rnk, val in zip(group['company_id'], ranks, group[m]):
                    percentiles.append({
                        'company_id': cid, 
                        'peer_group_name': pg, 
                        'metric': m, 
                        'value': val, 
                        'percentile_rank': rnk * 100, 
                        'year': 2024
                    })
        
        pct_df = pd.DataFrame(percentiles)
        return pct_df

    def save_percentiles(self, pct_df: pd.DataFrame):
        if not pct_df.empty:
            with sqlite3.connect(self.db_path) as conn:
                pct_df.to_sql('peer_percentiles', conn, if_exists='replace', index=False)

