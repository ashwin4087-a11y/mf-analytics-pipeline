import pytest
import pandas as pd
import numpy as np
import os
import sqlite3
import yaml

from src.screener.engine import ScreenerEngine
from src.analytics.peer import PeerEngine

DB_PATH = r"c:\Users\USER\Downloads\intern\w3\data\nifty100.db"
CONFIG_PATH = r"c:\Users\USER\Downloads\intern\w3\config\screener_config.yaml"

@pytest.fixture
def engine():
    return ScreenerEngine(DB_PATH, CONFIG_PATH)

@pytest.fixture
def df(engine):
    return engine.load_data()

def test_screener_presets_conditions(engine, df):
    presets = engine.config.get('presets', {})
    assert len(presets) == 6, "Must have exactly 6 presets"
    
    for p_key, p_val in presets.items():
        res = engine.run_screener(df, p_val)
        
        # Verify conditions are satisfied
        if 'roe_min' in p_val:
            assert all(res['roe'] >= p_val['roe_min'])
        if 'fcf_min' in p_val:
            assert all(res['fcf'] >= p_val['fcf_min'])
        if 'revenue_cagr_5yr_min' in p_val:
            assert all(res['revenue_cagr_5yr'] >= p_val['revenue_cagr_5yr_min'])
        if 'de_max' in p_val:
            # Financials are exempt
            for _, row in res.iterrows():
                assert row['de'] <= p_val['de_max'] or row['broad_sector'] == 'Financials'
        if 'pe_max' in p_val:
            assert all(res['pe'] <= p_val['pe_max'])
        if 'pb_max' in p_val:
            assert all(res['pb'] <= p_val['pb_max'])
        if 'dividend_yield_min' in p_val:
            assert all(res['dividend_yield'] >= p_val['dividend_yield_min'])
        if 'dividend_payout_max' in p_val:
            assert all(res['dividend_payout'] <= p_val['dividend_payout_max'])
        if 'revenue_cagr_3yr_min' in p_val:
            assert all(res['revenue_cagr_3yr'] >= p_val['revenue_cagr_3yr_min'])
        if 'pat_cagr_5yr_min' in p_val:
            assert all(res['pat_cagr_5yr'] >= p_val['pat_cagr_5yr_min'])
        if 'revenue_min' in p_val:
            assert all(res['revenue'] >= p_val['revenue_min'])
        if 'fcf_positive_latest' in p_val and p_val['fcf_positive_latest']:
            assert all(res['fcf'] > 0)
        if 'de_declining' in p_val and p_val['de_declining']:
            assert all(res['de_declining'] == True)
            
def test_composite_score(df):
    assert 'composite_quality_score' in df.columns
    scores = df['composite_quality_score'].dropna()
    assert len(scores) > 0
    assert all(scores >= 0) and all(scores <= 100), "Scores must be 0-100"
    
def test_peer_engine_percentiles():
    peer_engine = PeerEngine(DB_PATH, r"c:\Users\USER\Downloads\intern\w3\data\peer_groups.xlsx")
    screener = ScreenerEngine(DB_PATH, CONFIG_PATH)
    df = screener.load_data()
    
    pct_df = peer_engine.calculate_percentiles(df)
    
    # Verify exactly 10 metrics
    metrics = pct_df['metric'].unique()
    assert len(metrics) == 10
    
    # Test D/E inverse ranking logic specifically
    # Find a group with D/E values
    de_df = pct_df[pct_df['metric'] == 'de']
    if len(de_df) > 0:
        group_name = de_df['peer_group_name'].iloc[0]
        group_de = de_df[de_df['peer_group_name'] == group_name].copy()
        
        # Get raw values
        raw_vals = df[df['company_id'].isin(group_de['company_id'])]
        merged = group_de.merge(raw_vals[['company_id', 'de']], on='company_id')
        
        if len(merged.dropna(subset=['de'])) >= 2:
            # Sort by raw D/E ascending (lowest D/E should have highest percentile)
            merged = merged.sort_values('de')
            # The first row (lowest DE) should have a percentile rank >= the last row (highest DE)
            assert merged.iloc[0]['percentile_rank'] >= merged.iloc[-1]['percentile_rank'], "D/E inverse ranking failed"
