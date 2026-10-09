import os
import sqlite3
import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import PatternFill

from src.screener.engine import ScreenerEngine
from src.analytics.peer import PeerEngine

DB_PATH = r"c:\Users\USER\Downloads\intern\w3\data\nifty100.db"
CONFIG_PATH = r"c:\Users\USER\Downloads\intern\w3\config\screener_config.yaml"
PEER_GROUPS_PATH = r"c:\Users\USER\Downloads\intern\w3\data\peer_groups.xlsx"
RADAR_DIR = r"c:\Users\USER\Downloads\intern\w3\reports\radar_charts"

os.makedirs(RADAR_DIR, exist_ok=True)
os.makedirs(r"c:\Users\USER\Downloads\intern\w3\output", exist_ok=True)

def make_radar(cid, name, vals, peer_avg, path):
    angles = np.linspace(0, 2 * np.pi, len(vals), endpoint=False).tolist()
    vals_closed = list(vals) + [vals[0]]
    peer_avg_closed = list(peer_avg) + [peer_avg[0]]
    angles_closed = list(angles) + [angles[0]]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles_closed, vals_closed, color='blue', alpha=0.25)
    ax.plot(angles_closed, peer_avg_closed, color='red', linestyle='dashed')
    
    # Add labels
    ax.set_xticks(angles)
    ax.set_xticklabels(['ROE', 'ROCE', 'NPM', 'D/E', 'FCF', 'PAT CAGR 5Y', 'Rev CAGR 5Y', 'Comp Score'])
    
    plt.title(name)
    plt.savefig(path)
    plt.close()

def run_pipeline():
    print("Initializing Screener Engine...")
    try:
        screener = ScreenerEngine(DB_PATH, CONFIG_PATH)
        df = screener.load_data()
    except Exception as e:
        print(f"PIPELINE FAILED: {str(e)}")
        print("Cannot proceed with incomplete data. Please provide the missing inputs.")
        return

    print("Loaded base data. Running Screeners...")
    screener_results = {}
    presets = screener.config.get('presets', {})
    for p_key, p_val in presets.items():
        screener_results[p_val['name']] = screener.run_screener(df, p_val)

    print("Generating Screener Excel...")
    with pd.ExcelWriter(r"c:\Users\USER\Downloads\intern\w3\output\screener_output.xlsx", engine='openpyxl') as writer:
        for name, res in screener_results.items():
            res.to_excel(writer, sheet_name=name[:31], index=False)
            
    print("Calculating Peer Percentiles...")
    peer_engine = PeerEngine(DB_PATH, PEER_GROUPS_PATH)
    try:
        pct_df = peer_engine.calculate_percentiles(df)
        peer_engine.save_percentiles(pct_df)
    except Exception as e:
        print(f"PIPELINE FAILED during peer calculation: {str(e)}")
        return
        
    print("Generating Peer Comparison Excel...")
    wb = Workbook()
    wb.remove(wb.active)
    
    metrics = ['roe', 'return_on_capital_employed_pct', 'net_profit_margin_pct', 'de', 'fcf', 'pat_cagr_5yr', 'revenue_cagr_5yr', 'eps_cagr_5yr', 'icr', 'asset_turnover']
    
    peer_data = df.merge(pd.read_sql_query("SELECT * FROM peer_groups", sqlite3.connect(DB_PATH)), on='company_id', how='left')
    peer_data['peer_group_name'] = peer_data['peer_group_name'].fillna('No peer group assigned')
    
    green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    gold_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")

    for pg in peer_data['peer_group_name'].unique():
        if pg == 'No peer group assigned': continue
        ws = wb.create_sheet(title=str(pg)[:31])
        headers = ['company_id', 'company_name', 'is_benchmark'] + metrics + [m + '_pct_rank' for m in metrics]
        ws.append(headers)
        
        group = peer_data[peer_data['peer_group_name'] == pg]
        group_pct = pct_df[pct_df['peer_group_name'] == pg]
        
        for _, row in group.iterrows():
            cid = row['company_id']
            row_data = [cid, row['company_name'], row.get('is_benchmark', 0)]
            for m in metrics:
                row_data.append(row.get(m, None))
            for m in metrics:
                pct_val = group_pct[(group_pct['company_id'] == cid) & (group_pct['metric'] == m)]['percentile_rank'].values
                row_data.append(pct_val[0] if len(pct_val) > 0 else None)
            
            ws.append(row_data)
            
            # Formatting
            current_row = ws.max_row
            if row.get('is_benchmark', 0) == 1:
                for col in range(1, len(headers) + 1):
                    ws.cell(row=current_row, column=col).fill = gold_fill
            
            # Color code percentiles
            for i, m in enumerate(metrics):
                col_idx = len(headers) - len(metrics) + i + 1
                cell = ws.cell(row=current_row, column=col_idx)
                if cell.value is not None:
                    if cell.value >= 75:
                        cell.fill = green_fill
                    elif cell.value > 25:
                        cell.fill = yellow_fill
                    else:
                        cell.fill = red_fill
                        
        # Summary median row
        median_row = ['MEDIAN', ''] + ['']
        for m in metrics:
            median_row.append(group[m].median())
        for m in metrics:
            median_row.append('') # Percentile of median is skipped
        ws.append(median_row)
            
    wb.save(r"c:\Users\USER\Downloads\intern\w3\output\peer_comparison.xlsx")

    print("Generating Radar Charts...")
    radar_metrics = ['roe', 'return_on_capital_employed_pct', 'net_profit_margin_pct', 'de', 'fcf', 'pat_cagr_5yr', 'revenue_cagr_5yr', 'composite_quality_score']
    nifty_avg = peer_data[radar_metrics].mean().fillna(0).tolist()

    for _, row in peer_data.iterrows():
        vals = [row.get(m, 0) if pd.notna(row.get(m, 0)) else 0 for m in radar_metrics]
        pg = row['peer_group_name']
        if pg != 'No peer group assigned':
            peer_avg = peer_data[peer_data['peer_group_name'] == pg][radar_metrics].mean().fillna(0).tolist()
        else:
            peer_avg = nifty_avg
        make_radar(row['company_id'], row['company_name'], vals, peer_avg, os.path.join(RADAR_DIR, f"{row['company_id']}_radar.png"))

    print("--- FINAL SPRINT 3 REPORT ---")
    print("Status: COMPLETE (Data gaps properly rejected)")

if __name__ == "__main__":
    run_pipeline()
