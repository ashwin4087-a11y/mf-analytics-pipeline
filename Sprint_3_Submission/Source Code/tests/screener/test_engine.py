import pytest
import pandas as pd
import numpy as np
import yaml
import os
from src.screener.engine import ScreenerEngine

@pytest.fixture
def sample_config(tmp_path):
    config = {
        'presets': {
            'test_preset': {
                'roe_min': 15.0,
                'de_max': 1.0,
                'icr_min': 5.0
            }
        }
    }
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return str(config_file)

@pytest.fixture
def mock_df():
    return pd.DataFrame({
        'company_id': [1, 2, 3, 4],
        'company_name': ['A', 'B', 'Bank', 'C'],
        'roe': [20.0, 10.0, 15.0, np.nan],
        'de': [0.5, 2.0, 5.0, 0.8],
        'broad_sector': ['IT', 'FMCG', 'Financials', 'Auto'],
        'icr': [10.0, 2.0, np.nan, np.nan],
        'icr_label': ['', '', '', 'Debt Free'],
        'composite_quality_score': [0.0, 0.0, 0.0, 0.0]
    })

def test_config_loading(sample_config):
    engine = ScreenerEngine(":memory:", sample_config)
    assert 'test_preset' in engine.config['presets']

def test_de_financials_exclusion(mock_df, sample_config):
    engine = ScreenerEngine(":memory:", sample_config)
    filters = {'de_max': 1.0}
    result = engine.run_screener(mock_df, filters)
    
    # Company 1 (de=0.5 < 1) passes
    # Company 2 (de=2.0 > 1) fails
    # Company 3 (de=5.0) is Financials, so passes
    assert 1 in result['company_id'].values
    assert 2 not in result['company_id'].values
    assert 3 in result['company_id'].values

def test_icr_debt_free(mock_df, sample_config):
    engine = ScreenerEngine(":memory:", sample_config)
    # Apply the DB level rule explicitly if we mock DF before load_data
    mock_df.loc[mock_df['icr_label'] == 'Debt Free', 'icr'] = np.inf
    
    filters = {'icr_min': 5.0}
    result = engine.run_screener(mock_df, filters)
    
    # Company 1 (icr=10) passes
    # Company 4 (Debt Free -> inf) passes
    assert 1 in result['company_id'].values
    assert 4 in result['company_id'].values

def test_missing_values_handled(mock_df, sample_config):
    engine = ScreenerEngine(":memory:", sample_config)
    filters = {'roe_min': 15.0}
    result = engine.run_screener(mock_df, filters)
    
    # Company 4 has NaN ROE, should be excluded, not crash
    assert 4 not in result['company_id'].values
    assert 1 in result['company_id'].values
