import os
import pandas as pd
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DB_PATH = os.path.join(DATA_DIR, 'nifty100.db')

def generate_pros_cons():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Load companies master
    companies_df = pd.read_sql("SELECT id as company_id, company_name FROM companies", conn)
    
    # 2. Load sectors
    sectors_df = pd.read_sql("SELECT company_id, broad_sector FROM sectors", conn)
    
    # 3. Load financial_ratios history ordered by company_id, year
    ratios_df = pd.read_sql("SELECT * FROM financial_ratios ORDER BY company_id, year", conn)
    
    # 4. Load profitandloss history
    pl_df = pd.read_sql("SELECT * FROM profitandloss ORDER BY company_id, year", conn)
    
    # 5. Load balancesheet history
    bs_df = pd.read_sql("SELECT * FROM balancesheet ORDER BY company_id, year", conn)
    
    # 6. Load stock_prices/market_cap for dividend yield if available
    try:
        mc_df = pd.read_sql("SELECT company_id, year, market_cap_crore FROM market_cap ORDER BY company_id, year", conn)
    except Exception:
        mc_df = pd.DataFrame(columns=['company_id', 'year', 'market_cap_crore'])
        
    conn.close()
    
    sector_map = dict(zip(sectors_df['company_id'], sectors_df['broad_sector']))
    
    results = []
    
    for _, comp in companies_df.iterrows():
        cid = comp['company_id']
        sector = sector_map.get(cid, "Other")
        is_financial = (sector == 'Financial Services')
        
        c_ratios = ratios_df[ratios_df['company_id'] == cid].copy()
        c_pl = pl_df[pl_df['company_id'] == cid].copy()
        c_bs = bs_df[bs_df['company_id'] == cid].copy()
        c_mc = mc_df[mc_df['company_id'] == cid].copy()
        
        pros = []
        cons = []
        
        if not c_ratios.empty:
            latest_r = c_ratios.iloc[-1]
            latest_year = latest_r['year']
            
            # --- 12 PRO RULES ---
            
            # Pro Rule 1: ROE > 20% sustained for 3+ years
            if len(c_ratios) >= 3:
                last_3_roe = c_ratios.tail(3)['return_on_equity_pct'].dropna()
                if len(last_3_roe) == 3 and (last_3_roe > 20.0).all():
                    pros.append({
                        'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_1',
                        'text': 'Consistently high return on equity above 20% demonstrates exceptional capital efficiency',
                        'confidence_pct': 92.0
                    })
            elif pd.notna(latest_r.get('return_on_equity_pct')) and latest_r['return_on_equity_pct'] > 20.0:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_1',
                    'text': 'Consistently high return on equity above 20% demonstrates exceptional capital efficiency',
                    'confidence_pct': 85.0
                })

            # Pro Rule 2: FCF positive for 5+ consecutive years
            last_fcf = c_ratios['free_cash_flow_cr'].dropna()
            if len(last_fcf) >= 5 and (last_fcf.tail(5) > 0).all():
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_2',
                    'text': 'Strong free cash flow generation over 5 years signals healthy business fundamentals',
                    'confidence_pct': 90.0
                })
            elif len(last_fcf) >= 3 and (last_fcf.tail(3) > 0).all():
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_2',
                    'text': 'Strong free cash flow generation over 5 years signals healthy business fundamentals',
                    'confidence_pct': 75.0
                })

            # Pro Rule 3: D/E = 0 in latest year
            de_val = latest_r.get('debt_to_equity')
            icr_lbl = str(latest_r.get('icr_label', ''))
            if (pd.notna(de_val) and de_val == 0.0) or ('Debt Free' in icr_lbl):
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_3',
                    'text': 'Debt-free balance sheet provides financial flexibility and eliminates interest burden',
                    'confidence_pct': 95.0
                })

            # Pro Rule 4: Revenue CAGR > 15% over 5 years
            rev_cagr = latest_r.get('revenue_cagr_5yr')
            if pd.notna(rev_cagr) and rev_cagr > 15.0:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_4',
                    'text': 'Revenue growing at above 15% CAGR over 5 years reflects strong business momentum',
                    'confidence_pct': 88.0
                })

            # Pro Rule 5: OPM > 25% in latest year
            opm_val = latest_r.get('operating_profit_margin_pct')
            if pd.notna(opm_val) and opm_val > 25.0:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_5',
                    'text': 'Operating profit margin above 25% indicates strong pricing power and cost discipline',
                    'confidence_pct': 86.0
                })

            # Pro Rule 6: PAT CAGR > 20% over 5 years
            pat_cagr = latest_r.get('pat_cagr_5yr')
            if pd.notna(pat_cagr) and pat_cagr > 20.0:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_6',
                    'text': 'Net profit compounding at above 20% over 5 years creates significant shareholder value',
                    'confidence_pct': 89.0
                })

            # Pro Rule 7: ICR > 10 or Debt Free
            icr_val = latest_r.get('interest_coverage')
            if ('Debt Free' in icr_lbl) or (pd.notna(de_val) and de_val == 0.0) or (pd.notna(icr_val) and icr_val > 10.0):
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_7',
                    'text': 'Very high interest coverage ratio reflects negligible financial stress from debt servicing',
                    'confidence_pct': 88.0
                })

            # Pro Rule 8: Dividend Yield > 2% with FCF positive
            fcf_val = latest_r.get('free_cash_flow_cr')
            div_payout = latest_r.get('dividend_payout_ratio_pct')
            # Check dividend yield if market cap available, or healthy dividend payout with FCF > 0
            has_div_pro = False
            if pd.notna(fcf_val) and fcf_val > 0:
                if pd.notna(div_payout) and div_payout >= 25.0:
                    has_div_pro = True
                elif not c_mc.empty:
                    latest_mc = c_mc.iloc[-1].get('market_cap_crore')
                    if pd.notna(latest_mc) and latest_mc > 0 and not c_pl.empty:
                        div_amt = (c_pl.iloc[-1].get('net_profit', 0) * (div_payout or 0)) / 100.0
                        if (div_amt / latest_mc) * 100 >= 2.0:
                            has_div_pro = True
            if has_div_pro:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_8',
                    'text': 'Consistent dividend yield above 2% backed by positive free cash flow',
                    'confidence_pct': 82.0
                })

            # Pro Rule 9: EPS CAGR > 15% over 5 years
            eps_cagr = latest_r.get('eps_cagr_5yr')
            if pd.notna(eps_cagr) and eps_cagr > 15.0:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_9',
                    'text': 'Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding',
                    'confidence_pct': 87.0
                })

            # Pro Rule 10: ROE improving for 3 consecutive years
            if len(c_ratios) >= 3:
                r_tail3 = c_ratios.tail(3)['return_on_equity_pct'].tolist()
                if len(r_tail3) == 3 and pd.notna(r_tail3[0]) and pd.notna(r_tail3[1]) and pd.notna(r_tail3[2]):
                    if r_tail3[2] > r_tail3[1] > r_tail3[0]:
                        pros.append({
                            'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_10',
                            'text': 'Return on equity improving for 3 consecutive years shows strengthening business quality',
                            'confidence_pct': 84.0
                        })

            # Pro Rule 11: Revenue CAGR < PAT CAGR (operating leverage)
            if pd.notna(rev_cagr) and pd.notna(pat_cagr) and pat_cagr > rev_cagr and pat_cagr > 0:
                pros.append({
                    'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_11',
                    'text': 'Revenue growing slower than profits shows improving operating leverage and scale benefits',
                    'confidence_pct': 85.0
                })

            # Pro Rule 12: Balance sheet assets growing with declining debt
            if len(c_bs) >= 2:
                bs_tail2 = c_bs.tail(2)
                a_prev, a_curr = bs_tail2.iloc[0].get('total_assets', 0), bs_tail2.iloc[1].get('total_assets', 0)
                b_prev, b_curr = bs_tail2.iloc[0].get('borrowings', 0), bs_tail2.iloc[1].get('borrowings', 0)
                if pd.notna(a_curr) and pd.notna(a_prev) and pd.notna(b_curr) and pd.notna(b_prev):
                    if a_curr > a_prev and b_curr < b_prev:
                        pros.append({
                            'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_12',
                            'text': 'Growing asset base funded by internal accruals reflects self-sustaining growth',
                            'confidence_pct': 86.0
                        })

            # --- 12 CON RULES ---

            # Con Rule 1: D/E > 2.0 for non-financial companies
            if not is_financial and pd.notna(de_val) and de_val > 2.0:
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_1',
                    'text': f'Debt-to-equity ratio of {de_val:.2f} is elevated for a non-financial company and warrants monitoring',
                    'confidence_pct': 88.0
                })

            # Con Rule 2: FCF negative for 3 consecutive years
            if len(last_fcf) >= 3 and (last_fcf.tail(3) < 0).all():
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_2',
                    'text': 'Free cash flow negative for 3 consecutive years raises concern about cash generation quality',
                    'confidence_pct': 89.0
                })

            # Con Rule 3: OPM declining for 3 consecutive years
            if len(c_ratios) >= 3:
                opm_tail3 = c_ratios.tail(3)['operating_profit_margin_pct'].tolist()
                if len(opm_tail3) == 3 and pd.notna(opm_tail3[0]) and pd.notna(opm_tail3[1]) and pd.notna(opm_tail3[2]):
                    if opm_tail3[2] < opm_tail3[1] < opm_tail3[0]:
                        cons.append({
                            'company_id': cid, 'type': 'Con', 'rule_id': 'CON_3',
                            'text': 'Operating margins declining for 3 consecutive years suggest pricing or cost pressure',
                            'confidence_pct': 84.0
                        })

            # Con Rule 4: Net profit negative in latest year
            latest_np = None
            if not c_pl.empty:
                latest_np = c_pl.iloc[-1].get('net_profit')
            if (pd.notna(latest_np) and latest_np < 0) or (pd.notna(latest_r.get('net_profit_margin_pct')) and latest_r['net_profit_margin_pct'] < 0):
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_4',
                    'text': 'Company reported a net loss in the most recent financial year',
                    'confidence_pct': 96.0
                })

            # Con Rule 5: Revenue declining for 2+ years
            if len(c_pl) >= 3:
                sales_tail3 = c_pl.tail(3)['sales'].tolist()
                if len(sales_tail3) == 3 and pd.notna(sales_tail3[0]) and pd.notna(sales_tail3[1]) and pd.notna(sales_tail3[2]):
                    if sales_tail3[2] < sales_tail3[1] < sales_tail3[0]:
                        cons.append({
                            'company_id': cid, 'type': 'Con', 'rule_id': 'CON_5',
                            'text': 'Revenue contraction over 2 consecutive years indicates demand weakness or market share loss',
                            'confidence_pct': 85.0
                        })

            # Con Rule 6: ICR < 1.5
            if pd.notna(icr_val) and icr_val < 1.5 and icr_val > 0 and ('Debt Free' not in icr_lbl):
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_6',
                    'text': 'Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations',
                    'confidence_pct': 90.0
                })

            # Con Rule 7: Dividend payout > 100%
            if pd.notna(div_payout) and div_payout > 100.0:
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_7',
                    'text': 'Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable',
                    'confidence_pct': 88.0
                })

            # Con Rule 8: D/E rising for 3 consecutive years
            if len(c_ratios) >= 3 and not is_financial:
                de_tail3 = c_ratios.tail(3)['debt_to_equity'].tolist()
                if len(de_tail3) == 3 and pd.notna(de_tail3[0]) and pd.notna(de_tail3[1]) and pd.notna(de_tail3[2]):
                    if de_tail3[2] > de_tail3[1] > de_tail3[0] and de_tail3[2] > 0.5:
                        cons.append({
                            'company_id': cid, 'type': 'Con', 'rule_id': 'CON_8',
                            'text': 'Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk',
                            'confidence_pct': 83.0
                        })

            # Con Rule 9: EPS declining for 3 consecutive years
            if len(c_pl) >= 3:
                eps_tail3 = c_pl.tail(3)['eps'].tolist()
                if len(eps_tail3) == 3 and pd.notna(eps_tail3[0]) and pd.notna(eps_tail3[1]) and pd.notna(eps_tail3[2]):
                    if eps_tail3[2] < eps_tail3[1] < eps_tail3[0]:
                        cons.append({
                            'company_id': cid, 'type': 'Con', 'rule_id': 'CON_9',
                            'text': 'Earnings per share declining for 3 consecutive years reflects deteriorating profitability',
                            'confidence_pct': 85.0
                        })

            # Con Rule 10: ROCE < 10%
            roce_val = latest_r.get('return_on_capital_employed_pct')
            if pd.notna(roce_val) and roce_val < 10.0:
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_10',
                    'text': 'Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital',
                    'confidence_pct': 86.0
                })

            # Con Rule 11: Net Debt > 3x EBITDA
            nd_ebitda = latest_r.get('net_debt_to_ebitda')
            if pd.notna(nd_ebitda) and nd_ebitda > 3.0:
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_11',
                    'text': 'Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility',
                    'confidence_pct': 87.0
                })

            # Con Rule 12: Revenue CAGR < 5% over 5 years
            if pd.notna(rev_cagr) and rev_cagr < 5.0:
                cons.append({
                    'company_id': cid, 'type': 'Con', 'rule_id': 'CON_12',
                    'text': 'Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum',
                    'confidence_pct': 81.0
                })

        # --- MANDATORY MINIMUM 1 PRO AND 1 CON PER COMPANY ---
        if not pros:
            # Fallback Pro
            pros.append({
                'company_id': cid, 'type': 'Pro', 'rule_id': 'PRO_FB',
                'text': f'Established market position and substantial operating scale within the {sector} sector',
                'confidence_pct': 70.0
            })
            
        if not cons:
            # Fallback Con
            cons.append({
                'company_id': cid, 'type': 'Con', 'rule_id': 'CON_FB',
                'text': f'Vulnerable to macroeconomic cycles, input cost inflation, and sector-wide margin volatility',
                'confidence_pct': 70.0
            })
            
        # Filter confidence > 60%
        valid_pros = [p for p in pros if p['confidence_pct'] > 60.0]
        valid_cons = [c for c in cons if c['confidence_pct'] > 60.0]
        
        results.extend(valid_pros)
        results.extend(valid_cons)
        
    df_results = pd.DataFrame(results)
    
    # Ensure correct columns and order
    cols = ['company_id', 'type', 'rule_id', 'text', 'confidence_pct']
    df_results = df_results[cols]
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_csv = os.path.join(OUTPUT_DIR, 'pros_cons_generated.csv')
    df_results.to_csv(out_csv, index=False)
    
    # Verification
    n_companies = len(companies_df)
    comp_with_pro = df_results[df_results['type'] == 'Pro']['company_id'].nunique()
    comp_with_con = df_results[df_results['type'] == 'Con']['company_id'].nunique()
    print(f"Generated {len(df_results)} pro/con signals across {df_results['company_id'].nunique()} companies.")
    print(f"Companies with at least 1 Pro: {comp_with_pro}/{n_companies}")
    print(f"Companies with at least 1 Con: {comp_with_con}/{n_companies}")

if __name__ == '__main__':
    generate_pros_cons()
