import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_ratios, get_companies, get_sectors, get_market_cap, get_valuation,
    get_pl, get_bs, get_cf, get_prosandcons, get_peers, get_documents,
    get_capital_allocation_data, get_connection
)
from src.dashboard.utils.theme import get_terminal_chart_layout

def render_screen_home():
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 01 • Executive Macro Surveillance
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Portfolio Pulse & Universe Overview
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Institutional macro surveillance across 92 constituent equities of the Nifty 100 Index.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_filt, col_info = st.columns([1, 3])
    with col_filt:
        selected_year = st.selectbox(
            "Reporting Financial Year",
            options=[2024, 2023, 2022, 2021, 2020, 2019],
            index=0,
            key="home_year_select",
            help="Filters ratio distributions and market valuation data."
        )

    with col_info:
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; align-items: center; justify-content: flex-end; height: 100%; padding-top: 1.2rem;">
            <span class="terminal-badge badge-neutral">UNIVERSE: NIFTY 100</span>
            <span class="terminal-badge badge-discount">AUDITED FY{selected_year}</span>
            <span class="terminal-badge badge-neutral">SOURCE: BSE / NSE</span>
        </div>
        """, unsafe_allow_html=True)

    df_ratios = get_ratios(year=selected_year)
    df_comp = get_companies()
    df_sectors = get_sectors()
    df_mc = get_market_cap(year=selected_year)
    df_val = get_valuation()

    if df_ratios.empty:
        st.warning(f"No financial ratio records found for FY{selected_year}.")
    else:
        avg_roe = df_ratios['return_on_equity_pct'].mean() if 'return_on_equity_pct' in df_ratios.columns else 0
        med_de = df_ratios['debt_to_equity'].median() if 'debt_to_equity' in df_ratios.columns else 0
        med_rev_cagr = df_ratios['revenue_cagr_5yr'].median() if 'revenue_cagr_5yr' in df_ratios.columns else 0
        debt_free_count = (df_ratios['debt_to_equity'] == 0).sum() if 'debt_to_equity' in df_ratios.columns else 0
        total_companies = len(df_ratios['company_id'].unique())
        med_pe = df_mc['pe_ratio'].median() if not df_mc.empty and 'pe_ratio' in df_mc.columns else 0

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Average ROE", f"{avg_roe:.1f}%")
        m2.metric("Median P/E", f"{med_pe:.1f}x")
        m3.metric("Median D/E", f"{med_de:.2f}x")
        m4.metric("Debt-Free Equities", f"{debt_free_count}")
        m5.metric("Median Rev 5Y CAGR", f"{med_rev_cagr:.1f}%")
        m6.metric("Active Universe", f"{total_companies} / 92")

        st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
        c_left, c_right = st.columns([3, 2])

        with c_left:
            st.markdown('<div class="terminal-card-title">📈 Macro Multi-Year KPI Trajectories (FY19–FY24)</div>', unsafe_allow_html=True)
            trend_records = []
            for yr in [2019, 2020, 2021, 2022, 2023, 2024]:
                r_yr = get_ratios(year=yr)
                if not r_yr.empty:
                    trend_records.append({
                        "Year": str(yr),
                        "Median ROE (%)": r_yr['return_on_equity_pct'].median(),
                        "Median OPM (%)": r_yr['operating_profit_margin_pct'].median(),
                        "Median D/E (x10)": r_yr['debt_to_equity'].median() * 10
                    })
            
            if trend_records:
                df_trend = pd.DataFrame(trend_records)
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=df_trend['Year'], y=df_trend['Median ROE (%)'],
                    mode='lines+markers', name='Median ROE (%)',
                    line=dict(color='#0ea5e9', width=3),
                    marker=dict(size=7, color='#0ea5e9')
                ))
                fig_trend.add_trace(go.Scatter(
                    x=df_trend['Year'], y=df_trend['Median OPM (%)'],
                    mode='lines+markers', name='Median OPM (%)',
                    line=dict(color='#10b981', width=2.5),
                    marker=dict(size=6, color='#10b981')
                ))
                fig_trend.add_trace(go.Scatter(
                    x=df_trend['Year'], y=df_trend['Median D/E (x10)'],
                    mode='lines+markers', name='Median D/E (x10)',
                    line=dict(color='#f59e0b', width=2, dash='dot'),
                    marker=dict(size=5, color='#f59e0b')
                ))
                layout = get_terminal_chart_layout()
                layout.update(
                    title=dict(text="<b>Constituent Median Profitability & Leverage</b>", font=dict(color='#f8fafc', size=13)),
                    height=340,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_trend.update_layout(layout)
                st.plotly_chart(fig_trend, use_container_width=True)

        with c_right:
            st.markdown('<div class="terminal-card-title">🌐 Sector Distribution & Index Breadth</div>', unsafe_allow_html=True)
            if not df_sectors.empty:
                sec_counts = df_sectors['broad_sector'].value_counts().reset_index()
                sec_counts.columns = ['Sector', 'Count']
                
                fig_pie = px.pie(
                    sec_counts, names='Sector', values='Count', hole=0.55,
                    color_discrete_sequence=['#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b']
                )
                fig_pie.update_traces(
                    textposition='inside', textinfo='percent',
                    hovertemplate="<b>%{label}</b><br>Equities: %{value}<br>Weight: %{percent}<extra></extra>"
                )
                layout_pie = get_terminal_chart_layout()
                layout_pie.update(
                    title=dict(text="<b>Companies by Broad Sector</b>", font=dict(color='#f8fafc', size=13)),
                    height=340, showlegend=True,
                    legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10))
                )
                fig_pie.update_layout(layout_pie)
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        t1, t2 = st.columns([1, 1])

        with t1:
            st.markdown('<div class="terminal-card-title">🏆 Top 5 ROE Compounders (FY{})</div>'.format(selected_year), unsafe_allow_html=True)
            merged_roe = df_ratios.merge(df_comp[['id', 'company_name']], left_on='company_id', right_on='id', how='left')
            merged_roe = merged_roe.merge(df_sectors[['company_id', 'broad_sector']], on='company_id', how='left')
            
            top_roe = merged_roe.sort_values('return_on_equity_pct', ascending=False).head(5)[
                ['company_name', 'company_id', 'broad_sector', 'return_on_equity_pct', 'operating_profit_margin_pct', 'debt_to_equity']
            ]
            top_roe.columns = ['Company', 'Ticker', 'Sector', 'ROE (%)', 'OPM (%)', 'D/E']
            top_roe['ROE (%)'] = top_roe['ROE (%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            top_roe['OPM (%)'] = top_roe['OPM (%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            top_roe['D/E'] = top_roe['D/E'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            st.dataframe(top_roe, use_container_width=True, hide_index=True)

        with t2:
            st.markdown('<div class="terminal-card-title">🏷️ Valuation Signals (Epic 06 Valuation Engine)</div>', unsafe_allow_html=True)
            if not df_val.empty and 'flag' in df_val.columns:
                discount_n = len(df_val[df_val['flag'] == 'Discount'])
                caution_n = len(df_val[df_val['flag'] == 'Caution'])
                fair_n = len(df_val[df_val['flag'] == 'Fair'])
                
                st.markdown(f"""
                <div style="display: flex; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <div style="flex: 1; padding: 0.6rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; text-align: center;">
                        <div style="font-size: 0.68rem; color: #94a3b8; font-weight: 600;">DISCOUNT SIGNALS</div>
                        <div style="font-size: 1.3rem; color: #34d399; font-weight: 700; font-family: 'JetBrains Mono';">{discount_n}</div>
                    </div>
                    <div style="flex: 1; padding: 0.6rem; background: rgba(148, 163, 184, 0.1); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 6px; text-align: center;">
                        <div style="font-size: 0.68rem; color: #94a3b8; font-weight: 600;">FAIR VALUED</div>
                        <div style="font-size: 1.3rem; color: #f8fafc; font-weight: 700; font-family: 'JetBrains Mono';">{fair_n}</div>
                    </div>
                    <div style="flex: 1; padding: 0.6rem; background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 6px; text-align: center;">
                        <div style="font-size: 0.68rem; color: #94a3b8; font-weight: 600;">CAUTION / OVERVALUED</div>
                        <div style="font-size: 1.3rem; color: #fb7185; font-weight: 700; font-family: 'JetBrains Mono';">{caution_n}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                sample_val = df_val[['company_name', 'company_id', 'sector', 'P/E', 'flag']].head(5)
                sample_val.columns = ['Company', 'Ticker', 'Sector', 'P/E Multiple', 'Valuation Signal']
                st.dataframe(sample_val, use_container_width=True, hide_index=True)
            else:
                st.info("Run `python src/analytics/valuation.py` to refresh valuation flags.")

def render_screen_profile():
    df_comp = get_companies()
    if df_comp.empty:
        st.error("No company records available in database.")
        return

    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 02 • Single Company Fundamental Audit
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Company Fundamental Intelligence
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            10-year historical KPI trajectories, balance sheet health, and financial statement audit.
        </div>
    </div>
    """, unsafe_allow_html=True)

    comp_options = df_comp.apply(lambda x: f"{x['company_name']} ({x['id']})", axis=1).tolist()
    default_idx = 0
    for i, opt in enumerate(comp_options):
        if "(TCS)" in opt:
            default_idx = i
            break

    selected_option = st.selectbox(
        "Search Equity by Name or Ticker",
        options=comp_options,
        index=default_idx,
        key="profile_comp_select",
        help="Select an equity to load full 10-year financial models."
    )

    ticker = selected_option.split("(")[-1].replace(")", "").strip()
    comp_row = df_comp[df_comp['id'] == ticker]
    if comp_row.empty:
        st.warning("Selected security record not found.")
        return

    comp_info = comp_row.iloc[0]
    df_sec = get_sectors()
    sec_row = df_sec[df_sec['company_id'] == ticker]
    sector = sec_row.iloc[0]['broad_sector'] if not sec_row.empty else "N/A"
    sub_sector = sec_row.iloc[0]['sub_sector'] if not sec_row.empty else "N/A"

    st.markdown(f"""
    <div class="terminal-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem; font-weight: 800; color: #f8fafc; font-family: 'Inter';">{comp_info['company_name']}</span>
                    <span class="terminal-badge badge-neutral">{ticker}</span>
                    <span class="terminal-badge badge-discount">{sector}</span>
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.35rem;">
                    Sub-Sector: <b style="color: #cbd5e1;">{sub_sector}</b> | 
                    Face Value: <b style="color: #cbd5e1;">₹{comp_info.get('face_value', 'N/A')}</b> | 
                    Book Value: <b style="color: #cbd5e1;">₹{comp_info.get('book_value', 'N/A')}</b>
                </div>
            </div>
            <div>
                <a href="{comp_info.get('website', '#')}" target="_blank" style="text-decoration: none;">
                    <span class="terminal-badge badge-neutral" style="cursor: pointer;">Corporate Website ↗</span>
                </a>
                <a href="{comp_info.get('nse_profile', '#')}" target="_blank" style="text-decoration: none; margin-left: 0.5rem;">
                    <span class="terminal-badge badge-neutral" style="cursor: pointer;">NSE Exchange ↗</span>
                </a>
            </div>
        </div>
        <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin-top: 0.85rem; padding-top: 0.85rem; border-top: 1px solid #1e2e4a;">
            {comp_info.get('about_company', 'No description available for this constituent equity.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_rat = get_ratios(ticker=ticker)
    if not df_rat.empty:
        df_rat_sorted = df_rat.sort_values('year', ascending=False)
        latest_rat = df_rat_sorted.iloc[0]
        
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        roe = latest_rat.get('return_on_equity_pct', pd.NA)
        roce = latest_rat.get('return_on_capital_employed_pct', pd.NA)
        npm = latest_rat.get('net_profit_margin_pct', pd.NA)
        de = latest_rat.get('debt_to_equity', pd.NA)
        rev_cagr = latest_rat.get('revenue_cagr_5yr', pd.NA)
        fcf = latest_rat.get('free_cash_flow_cr', pd.NA)
        
        k1.metric("ROE (%)", f"{roe:.2f}%" if pd.notna(roe) else "N/A", delta="Quality" if pd.notna(roe) and roe > 15 else None)
        k2.metric("ROCE (%)", f"{roce:.2f}%" if pd.notna(roce) else "N/A")
        k3.metric("Net Margin (%)", f"{npm:.2f}%" if pd.notna(npm) else "N/A")
        k4.metric("Debt-to-Equity", f"{de:.2f}x" if pd.notna(de) else "N/A")
        k5.metric("Rev 5Y CAGR", f"{rev_cagr:.2f}%" if pd.notna(rev_cagr) else "N/A")
        k6.metric("Free Cash Flow", f"₹{fcf:,.0f} Cr" if pd.notna(fcf) else "N/A")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    c_pl, c_roe = st.columns([1, 1])

    with c_pl:
        st.markdown('<div class="terminal-card-title">📊 10-Year Revenue & Net Profit Trajectory (Cr)</div>', unsafe_allow_html=True)
        df_pl = get_pl(ticker=ticker)
        if not df_pl.empty:
            df_pl_sorted = df_pl.sort_values('year')
            fig_pl = go.Figure()
            fig_pl.add_trace(go.Bar(
                x=df_pl_sorted['year'], y=df_pl_sorted['sales'], 
                name='Revenue (Sales)', marker_color='#0ea5e9',
                hovertemplate="Year: %{x}<br>Revenue: ₹%{y:,.0f} Cr<extra></extra>"
            ))
            fig_pl.add_trace(go.Bar(
                x=df_pl_sorted['year'], y=df_pl_sorted['net_profit'], 
                name='Net Profit (PAT)', marker_color='#10b981',
                hovertemplate="Year: %{x}<br>Net Profit: ₹%{y:,.0f} Cr<extra></extra>"
            ))
            layout_pl = get_terminal_chart_layout()
            layout_pl.update(
                barmode='group', height=320, yaxis_title="Amount (₹ Crore)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_pl.update_layout(layout_pl)
            st.plotly_chart(fig_pl, use_container_width=True)

    with c_roe:
        st.markdown('<div class="terminal-card-title">📈 10-Year ROE vs. ROCE Capital Efficiency (%)</div>', unsafe_allow_html=True)
        if not df_rat.empty:
            df_rat_asc = df_rat.sort_values('year')
            fig_roe = go.Figure()
            if 'return_on_equity_pct' in df_rat_asc.columns:
                fig_roe.add_trace(go.Scatter(
                    x=df_rat_asc['year'], y=df_rat_asc['return_on_equity_pct'], 
                    mode='lines+markers', name='ROE (%)',
                    line=dict(color='#0ea5e9', width=2.5),
                    marker=dict(size=6, color='#0ea5e9'),
                    hovertemplate="Year: %{x}<br>ROE: %{y:.2f}%<extra></extra>"
                ))
            if 'return_on_capital_employed_pct' in df_rat_asc.columns:
                fig_roe.add_trace(go.Scatter(
                    x=df_rat_asc['year'], y=df_rat_asc['return_on_capital_employed_pct'], 
                    mode='lines+markers', name='ROCE (%)',
                    line=dict(color='#8b5cf6', width=2.5),
                    marker=dict(size=6, color='#8b5cf6'),
                    hovertemplate="Year: %{x}<br>ROCE: %{y:.2f}%<extra></extra>"
                ))
            layout_roe = get_terminal_chart_layout()
            layout_roe.update(
                height=320, yaxis_title="Percentage (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_roe.update_layout(layout_roe)
            st.plotly_chart(fig_roe, use_container_width=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    c_bs, c_pc = st.columns([1, 1])

    with c_bs:
        st.markdown('<div class="terminal-card-title">🏛️ Capital Structure & Balance Sheet Composition (Cr)</div>', unsafe_allow_html=True)
        df_bs = get_bs(ticker=ticker)
        if not df_bs.empty:
            df_bs_sorted = df_bs.sort_values('year')
            fig_bs = go.Figure()
            fig_bs.add_trace(go.Bar(
                x=df_bs_sorted['year'], y=df_bs_sorted.get('reserves', 0), 
                name='Reserves & Surplus', marker_color='#0ea5e9'
            ))
            fig_bs.add_trace(go.Bar(
                x=df_bs_sorted['year'], y=df_bs_sorted.get('equity_capital', 0), 
                name='Equity Capital', marker_color='#10b981'
            ))
            fig_bs.add_trace(go.Bar(
                x=df_bs_sorted['year'], y=df_bs_sorted.get('borrowings', 0), 
                name='Borrowings (Debt)', marker_color='#f43f5e'
            ))
            layout_bs = get_terminal_chart_layout()
            layout_bs.update(
                barmode='stack', height=300, yaxis_title="Amount (₹ Crore)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_bs.update_layout(layout_bs)
            st.plotly_chart(fig_bs, use_container_width=True)

    with c_pc:
        st.markdown('<div class="terminal-card-title">⚖️ Algorithmic Pros & Cons Assessment</div>', unsafe_allow_html=True)
        df_pc = get_prosandcons(ticker=ticker)
        pros = df_pc['pros'].dropna().tolist() if not df_pc.empty and 'pros' in df_pc.columns else []
        cons = df_pc['cons'].dropna().tolist() if not df_pc.empty and 'cons' in df_pc.columns else []
        
        st.markdown("""
        <div style="background-color: #0f172a; border: 1px solid #1e2e4a; border-radius: 8px; padding: 1rem; min-height: 280px;">
        """, unsafe_allow_html=True)
        
        st.markdown("<b style='color: #34d399; font-size: 0.85rem;'>STRENGTHS / PROS</b>", unsafe_allow_html=True)
        if pros:
            for p in pros[:4]:
                st.markdown(f"<div style='font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.35rem;'>🟢 {p}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 0.8rem; color: #94a3b8;'>No distinct pros flagged.</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
        st.markdown("<b style='color: #fb7185; font-size: 0.85rem;'>RISKS / CONS</b>", unsafe_allow_html=True)
        if cons:
            for c in cons[:4]:
                st.markdown(f"<div style='font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.35rem;'>🔴 {c}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 0.8rem; color: #94a3b8;'>No distinct risks flagged.</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="terminal-card-title">📑 Comprehensive Financial Statements Audit</div>', unsafe_allow_html=True)
    tab_pl, tab_bs, tab_cf = st.tabs(["Profit & Loss Statement", "Balance Sheet", "Cash Flow Statement"])

    with tab_pl:
        if not df_pl.empty:
            display_pl = df_pl[['year', 'sales', 'expenses', 'operating_profit', 'opm_percentage', 'interest', 'depreciation', 'profit_before_tax', 'net_profit', 'eps']].sort_values('year', ascending=False)
            display_pl.columns = ['Year', 'Sales (Cr)', 'Expenses (Cr)', 'Operating Profit (Cr)', 'OPM (%)', 'Interest (Cr)', 'Depreciation (Cr)', 'PBT (Cr)', 'Net Profit (Cr)', 'EPS (₹)']
            st.dataframe(display_pl, use_container_width=True, hide_index=True)

    with tab_bs:
        df_bs_full = get_bs(ticker=ticker)
        if not df_bs_full.empty:
            display_bs = df_bs_full[['year', 'equity_capital', 'reserves', 'borrowings', 'other_liabilities', 'total_liabilities', 'fixed_assets', 'investments', 'other_asset', 'total_assets']].sort_values('year', ascending=False)
            display_bs.columns = ['Year', 'Equity Cap (Cr)', 'Reserves (Cr)', 'Borrowings (Cr)', 'Other Liab (Cr)', 'Total Liab (Cr)', 'Fixed Assets (Cr)', 'Investments (Cr)', 'Other Assets (Cr)', 'Total Assets (Cr)']
            st.dataframe(display_bs, use_container_width=True, hide_index=True)

    with tab_cf:
        df_cf_full = get_cf(ticker=ticker)
        if not df_cf_full.empty:
            display_cf = df_cf_full[['year', 'operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow']].sort_values('year', ascending=False)
            display_cf.columns = ['Year', 'Operating CF (Cr)', 'Investing CF (Cr)', 'Financing CF (Cr)', 'Net Cash Flow (Cr)']
            st.dataframe(display_cf, use_container_width=True, hide_index=True)

def render_screen_screener():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 03 • Quantitative Strategy Engine
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Multi-Metric Quantitative Screener
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Institutional strategy presets and 10 dynamic financial filter thresholds across Nifty 100 constituents.
        </div>
    </div>
    """, unsafe_allow_html=True)

    defaults = {
        'roe_min': 0.0, 'de_max': 5.0, 'fcf_min': -50000.0, 'rev_cagr_min': -20.0,
        'pat_cagr_min': -20.0, 'opm_min': -20.0, 'pe_max': 200.0, 'pb_max': 50.0,
        'div_min': 0.0, 'icr_min': -10.0
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    def apply_preset(preset_name):
        for k, v in defaults.items():
            st.session_state[k] = v
        if preset_name == 'Quality':
            st.session_state.roe_min = 15.0
            st.session_state.de_max = 1.0
            st.session_state.fcf_min = 0.0
            st.session_state.rev_cagr_min = 10.0
        elif preset_name == 'Value':
            st.session_state.pe_max = 25.0
            st.session_state.pb_max = 3.5
            st.session_state.de_max = 1.5
            st.session_state.div_min = 1.0
        elif preset_name == 'Growth':
            st.session_state.pat_cagr_min = 15.0
            st.session_state.rev_cagr_min = 12.0
            st.session_state.roe_min = 12.0
        elif preset_name == 'Dividend':
            st.session_state.div_min = 1.5
            st.session_state.fcf_min = 0.0
        elif preset_name == 'Debt-Free':
            st.session_state.de_max = 0.0
            st.session_state.roe_min = 10.0
        elif preset_name == 'Turnaround':
            st.session_state.rev_cagr_min = 10.0
            st.session_state.fcf_min = 0.0

    st.sidebar.markdown('<div class="terminal-card-title">⚡ STRATEGY PRESETS</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.sidebar.columns(2)
    with p_col1:
        if st.button("🌟 Quality", key="btn_quality", use_container_width=True):
            apply_preset('Quality')
        if st.button("🚀 Growth", key="btn_growth", use_container_width=True):
            apply_preset('Growth')
        if st.button("🛡️ Debt-Free", key="btn_debtfree", use_container_width=True):
            apply_preset('Debt-Free')
    with p_col2:
        if st.button("💎 Value", key="btn_value", use_container_width=True):
            apply_preset('Value')
        if st.button("💰 Dividend", key="btn_dividend", use_container_width=True):
            apply_preset('Dividend')
        if st.button("🔄 Turnaround", key="btn_turnaround", use_container_width=True):
            apply_preset('Turnaround')

    if st.sidebar.button("↺ Reset All Filters", key="btn_reset_scr", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v

    st.sidebar.markdown('<div style="margin-top: 1rem;" class="terminal-card-title">⚙️ CUSTOM SLIDERS</div>', unsafe_allow_html=True)
    st.sidebar.slider("Minimum ROE (%)", -50.0, 100.0, key='roe_min', step=1.0)
    st.sidebar.slider("Maximum D/E Ratio", 0.0, 10.0, key='de_max', step=0.1)
    st.sidebar.slider("Minimum FCF (Cr)", -50000.0, 50000.0, key='fcf_min', step=1000.0)
    st.sidebar.slider("Min Rev 5Y CAGR (%)", -30.0, 100.0, key='rev_cagr_min', step=1.0)
    st.sidebar.slider("Min PAT 5Y CAGR (%)", -30.0, 100.0, key='pat_cagr_min', step=1.0)
    st.sidebar.slider("Min Operating Margin (%)", -30.0, 100.0, key='opm_min', step=1.0)
    st.sidebar.slider("Maximum P/E Multiple", 0.0, 300.0, key='pe_max', step=5.0)
    st.sidebar.slider("Maximum P/B Ratio", 0.0, 50.0, key='pb_max', step=1.0)
    st.sidebar.slider("Minimum Div Yield (%)", 0.0, 10.0, key='div_min', step=0.2)
    st.sidebar.slider("Min Interest Coverage (ICR)", -20.0, 100.0, key='icr_min', step=2.0)

    df_rat = get_ratios(year=2024)
    if df_rat.empty:
        df_rat = get_ratios(year=2023)
    df_comp = get_companies()
    df_sec = get_sectors()
    df_mc = get_market_cap(year=2024)

    df = df_rat.merge(df_comp[['id', 'company_name']], left_on='company_id', right_on='id', how='left')
    df = df.merge(df_sec[['company_id', 'broad_sector', 'sub_sector']], on='company_id', how='left')
    if not df_mc.empty:
        df = df.merge(df_mc[['company_id', 'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 'market_cap_crore']], on='company_id', how='left')
    else:
        df['pe_ratio'] = pd.NA
        df['pb_ratio'] = pd.NA
        df['dividend_yield_pct'] = pd.NA
        df['market_cap_crore'] = 0

    mask = (
        (df['return_on_equity_pct'].fillna(-999) >= st.session_state.roe_min) &
        (df['debt_to_equity'].fillna(999) <= st.session_state.de_max) &
        (df['free_cash_flow_cr'].fillna(-999999) >= st.session_state.fcf_min) &
        (df['revenue_cagr_5yr'].fillna(-999) >= st.session_state.rev_cagr_min) &
        (df['pat_cagr_5yr'].fillna(-999) >= st.session_state.pat_cagr_min) &
        (df['operating_profit_margin_pct'].fillna(-999) >= st.session_state.opm_min) &
        (df['pe_ratio'].fillna(9999) <= st.session_state.pe_max) &
        (df['pb_ratio'].fillna(9999) <= st.session_state.pb_max) &
        (df['dividend_yield_pct'].fillna(-999) >= st.session_state.div_min) &
        (df['interest_coverage'].fillna(-999) >= st.session_state.icr_min)
    )
    filtered = df[mask].copy()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Screened Equities", f"{len(filtered)} / {len(df)}", delta=f"{(len(filtered)/max(len(df),1)*100):.1f}% of Universe")
    s2.metric("Cohort Avg ROE", f"{filtered['return_on_equity_pct'].mean():.1f}%" if not filtered.empty else "—")
    s3.metric("Cohort Median P/E", f"{filtered['pe_ratio'].median():.1f}x" if not filtered.empty else "—")
    s4.metric("Cohort Median D/E", f"{filtered['debt_to_equity'].median():.2f}x" if not filtered.empty else "—")

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    display_cols = [
        'company_id', 'company_name', 'broad_sector', 'return_on_equity_pct', 
        'debt_to_equity', 'free_cash_flow_cr', 'revenue_cagr_5yr', 'operating_profit_margin_pct',
        'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 'interest_coverage'
    ]
    out_cols = [c for c in display_cols if c in filtered.columns]
    display_df = filtered[out_cols].copy()
    display_df.rename(columns={
        'company_id': 'Ticker', 'company_name': 'Company Name', 'broad_sector': 'Sector',
        'return_on_equity_pct': 'ROE (%)', 'debt_to_equity': 'D/E (x)', 'free_cash_flow_cr': 'FCF (Cr)',
        'revenue_cagr_5yr': 'Rev 5Y CAGR (%)', 'operating_profit_margin_pct': 'OPM (%)',
        'pe_ratio': 'P/E', 'pb_ratio': 'P/B', 'dividend_yield_pct': 'Div Yield (%)',
        'interest_coverage': 'ICR'
    }, inplace=True)

    if not display_df.empty:
        for col in ['ROE (%)', 'Rev 5Y CAGR (%)', 'OPM (%)', 'Div Yield (%)']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
        for col in ['D/E (x)', 'P/E', 'P/B', 'ICR']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        if 'FCF (Cr)' in display_df.columns:
            display_df['FCF (Cr)'] = display_df['FCF (Cr)'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    col_exp, _ = st.columns([1, 4])
    with col_exp:
        csv_data = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Cohort (CSV)",
            data=csv_data,
            file_name="nifty100_screened_equities.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_download_screener_csv"
        )

def render_screen_peers():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 04 • Cohort Benchmarking
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Peer Group Benchmarking & Percentile Radars
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Cross-sectional competitive positioning against peer medians across 10 capital efficiency and growth metrics.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_peers = get_peers()
    if df_peers.empty:
        st.error("No peer percentile records available in database.")
        return
    df_comp = get_companies()

    groups = sorted([g for g in df_peers['peer_group'].dropna().unique() if g != 'No peer group assigned'])
    col_grp, col_cmp = st.columns([1, 1])
    with col_grp:
        selected_group = st.selectbox(
            "Select Industry Peer Cohort",
            options=groups,
            index=groups.index("IT Services") if "IT Services" in groups else 0,
            key="peers_grp_select"
        )

    group_data = df_peers[df_peers['peer_group'] == selected_group]
    group_companies = group_data['company_id'].unique().tolist()
    comp_map = dict(zip(df_comp['id'], df_comp['company_name']))
    cmp_display_options = [f"{comp_map.get(cid, cid)} ({cid})" for cid in group_companies]

    with col_cmp:
        selected_comp_str = st.selectbox(
            "Select Company for Radar Analysis",
            options=cmp_display_options,
            index=0 if cmp_display_options else 0,
            key="peers_cmp_select"
        )

    selected_ticker = selected_comp_str.split("(")[-1].replace(")", "").strip() if selected_comp_str else group_companies[0]

    METRIC_LABELS = {
        'roe': 'Return on Equity (ROE)',
        'return_on_capital_employed_pct': 'ROCE',
        'net_profit_margin_pct': 'Net Margin (NPM)',
        'de': 'Debt/Equity (Health)',
        'fcf': 'Free Cash Flow (FCF)',
        'pat_cagr_5yr': 'PAT 5Y CAGR',
        'revenue_cagr_5yr': 'Rev 5Y CAGR',
        'eps_cagr_5yr': 'EPS 5Y CAGR',
        'icr': 'Interest Coverage (ICR)',
        'asset_turnover': 'Asset Turnover'
    }

    comp_metrics = group_data[group_data['company_id'] == selected_ticker].copy()
    c_radar, c_summary = st.columns([3, 2])

    with c_radar:
        st.markdown(f'<div class="terminal-card-title">🎯 Percentile Radar: {comp_map.get(selected_ticker, selected_ticker)} vs. Cohort Median</div>', unsafe_allow_html=True)
        if not comp_metrics.empty:
            categories = [METRIC_LABELS.get(m, m) for m in comp_metrics['metric']]
            comp_percentiles = comp_metrics['percentile_rank'].tolist()
            categories_closed = categories + [categories[0]]
            comp_percentiles_closed = comp_percentiles + [comp_percentiles[0]]
            median_percentiles_closed = [50] * len(categories_closed)
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=median_percentiles_closed, theta=categories_closed,
                mode='lines', name='Cohort Median (50th Pct)',
                line=dict(color='#64748b', width=1.5, dash='dash'), hoverinfo='none'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=comp_percentiles_closed, theta=categories_closed,
                fill='toself', fillcolor='rgba(14, 165, 233, 0.22)',
                name=f"{selected_ticker} Percentile",
                line=dict(color='#0ea5e9', width=2.5),
                marker=dict(size=6, color='#38bdf8'),
                hovertemplate="Metric: %{theta}<br>Percentile Rank: %{r:.1f}th<extra></extra>"
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100], tickfont=dict(color='#64748b', size=9), gridcolor='#1e2e4a', linecolor='#1e2e4a'),
                    angularaxis=dict(tickfont=dict(color='#cbd5e1', size=10, family='Inter'), gridcolor='#1e2e4a', linecolor='#1e2e4a'),
                    bgcolor='rgba(15, 23, 42, 0.4)'
                ),
                paper_bgcolor='rgba(0,0,0,0)', height=380,
                margin=dict(l=60, r=60, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color='#cbd5e1', size=11))
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    with c_summary:
        st.markdown('<div class="terminal-card-title">📋 Competitive Positioning Audit</div>', unsafe_allow_html=True)
        if not comp_metrics.empty:
            comp_metrics['Metric Name'] = comp_metrics['metric'].map(METRIC_LABELS)
            def get_rank_badge(pct):
                if pct >= 75: return "🟢 Top Quartile (Leader)"
                elif pct >= 50: return "🔵 Above Median"
                elif pct >= 25: return "🟡 Below Median"
                else: return "🔴 Bottom Quartile"
            comp_metrics['Quartile'] = comp_metrics['percentile_rank'].apply(get_rank_badge)
            summary_view = comp_metrics[['Metric Name', 'value', 'percentile_rank', 'Quartile']].copy()
            summary_view.columns = ['Metric', 'Reported Value', 'Percentile Rank', 'Standing']
            summary_view['Reported Value'] = summary_view['Reported Value'].apply(lambda x: f"{x:,.2f}")
            summary_view['Percentile Rank'] = summary_view['Percentile Rank'].apply(lambda x: f"{x:.1f}th")
            st.dataframe(summary_view, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="terminal-card-title">👥 Full Cohort Cross-Sectional Comparison ({selected_group})</div>', unsafe_allow_html=True)
    pivot_df = group_data.pivot(index='company_id', columns='metric', values='value').reset_index()
    pivot_df['Company Name'] = pivot_df['company_id'].map(comp_map)
    cols = ['company_id', 'Company Name'] + [m for m in METRIC_LABELS.keys() if m in pivot_df.columns]
    pivot_display = pivot_df[cols].copy()
    pivot_display.rename(columns={'company_id': 'Ticker'}, inplace=True)
    pivot_display.rename(columns=METRIC_LABELS, inplace=True)
    for col in pivot_display.columns:
        if col not in ['Ticker', 'Company Name']:
            pivot_display[col] = pivot_display[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "—")
    st.dataframe(pivot_display, use_container_width=True, hide_index=True)

def render_screen_trends():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 05 • Longitudinal Trajectory
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Multi-Metric Historical Trend Analytics
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Longitudinal financial trajectory analysis, multi-metric overlay, and year-over-year volatility tracking.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_comp = get_companies()
    if df_comp.empty:
        st.error("No companies data available.")
        return

    comp_options = df_comp.apply(lambda x: f"{x['company_name']} ({x['id']})", axis=1).tolist()
    default_idx = 0
    for i, opt in enumerate(comp_options):
        if "(RELIANCE)" in opt:
            default_idx = i
            break

    col_c, col_m = st.columns([1, 2])
    with col_c:
        selected_option = st.selectbox(
            "Select Constituent Equity",
            options=comp_options,
            index=default_idx,
            key="trends_comp_select"
        )

    ticker = selected_option.split("(")[-1].replace(")", "").strip()
    df_rat = get_ratios(ticker=ticker)
    if df_rat.empty:
        st.warning("No ratio history found for selected equity.")
        return

    df_rat = df_rat.sort_values('year')
    METRIC_DICT = {
        'return_on_equity_pct': 'ROE (%)',
        'return_on_capital_employed_pct': 'ROCE (%)',
        'net_profit_margin_pct': 'Net Margin (%)',
        'operating_profit_margin_pct': 'Operating Margin (%)',
        'debt_to_equity': 'Debt-to-Equity (x)',
        'revenue_cagr_5yr': 'Revenue 5Y CAGR (%)',
        'pat_cagr_5yr': 'PAT 5Y CAGR (%)',
        'free_cash_flow_cr': 'Free Cash Flow (Cr)',
        'asset_turnover': 'Asset Turnover (x)',
        'interest_coverage': 'Interest Coverage (ICR)'
    }
    available_metrics = [k for k in METRIC_DICT.keys() if k in df_rat.columns]

    with col_m:
        selected_metrics = st.multiselect(
            "Select up to 4 Metrics to Overlay",
            options=available_metrics,
            default=['return_on_equity_pct', 'net_profit_margin_pct', 'operating_profit_margin_pct'],
            format_func=lambda x: METRIC_DICT.get(x, x),
            max_selections=4,
            key="trends_metrics_select"
        )

    if not selected_metrics:
        st.info("Select at least one metric from the dropdown above to display the chart.")
    else:
        TRACE_COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6']
        fig = go.Figure()
        for i, m in enumerate(selected_metrics):
            metric_name = METRIC_DICT.get(m, m)
            color = TRACE_COLORS[i % len(TRACE_COLORS)]
            yoy = df_rat[m].pct_change() * 100
            hover_texts = []
            for val, y_change in zip(df_rat[m], yoy):
                change_str = f" (YoY: {y_change:+.1f}%)" if pd.notna(y_change) else ""
                hover_texts.append(f"{val:,.2f}{change_str}")
                
            fig.add_trace(go.Scatter(
                x=df_rat['year'], y=df_rat[m], mode='lines+markers', name=metric_name,
                line=dict(color=color, width=2.5), marker=dict(size=7, color=color),
                text=hover_texts, hovertemplate="Year: %{x}<br>" + metric_name + ": %{text}<extra></extra>"
            ))
            
        layout = get_terminal_chart_layout()
        layout.update(
            title=dict(text=f"<b>Historical Trajectory — {selected_option.split('(')[0].strip()}</b>", font=dict(color='#f8fafc', size=14)),
            height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="terminal-card-title">📅 Historical Audit Records & Year-over-Year Trajectory</div>', unsafe_allow_html=True)
    table_cols = ['year'] + selected_metrics
    sub_df = df_rat[table_cols].sort_values('year', ascending=False).copy()
    sub_df.rename(columns={'year': 'Year'}, inplace=True)
    sub_df.rename(columns=METRIC_DICT, inplace=True)
    for col in sub_df.columns:
        if col != 'Year':
            sub_df[col] = sub_df[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "—")
    st.dataframe(sub_df, use_container_width=True, hide_index=True)

def render_screen_sectors():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 06 • Sector Allocation
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Sector Intelligence & Comparative Aggregates
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Cross-sector capital distribution, median margin benchmarks, and revenue-to-profitability bubble surveillance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_sec = get_sectors()
    sectors_list = ["All Sectors"] + sorted(df_sec['broad_sector'].dropna().unique().tolist())
    selected_sector = st.selectbox("Filter by Broad Economic Sector", options=sectors_list, index=0, key="sec_filter_select")

    conn = get_connection()
    query = """
    SELECT c.company_name, c.id as company_id, s.broad_sector, s.sub_sector, 
           r.return_on_equity_pct, r.operating_profit_margin_pct,
           p.sales as sales_cr, p.net_profit as net_profit_cr,
           m.market_cap_crore, m.pe_ratio
    FROM companies c
    JOIN sectors s ON c.id = s.company_id
    LEFT JOIN (
        SELECT company_id, return_on_equity_pct, operating_profit_margin_pct,
               ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY year DESC) as rn
        FROM financial_ratios
    ) r ON c.id = r.company_id AND r.rn = 1
    LEFT JOIN (
        SELECT company_id, sales, net_profit,
               ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY year DESC) as rn
        FROM profitandloss
    ) p ON c.id = p.company_id AND p.rn = 1
    LEFT JOIN (
        SELECT company_id, market_cap_crore, pe_ratio,
               ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY year DESC) as rn
        FROM market_cap
    ) m ON c.id = m.company_id AND m.rn = 1
    """
    df = pd.read_sql(query, conn)
    df_filtered = df[df['broad_sector'] == selected_sector].copy() if selected_sector != "All Sectors" else df.copy()

    s1, s2, s3, s4 = st.columns(4)
    total_sec_mcap = df_filtered['market_cap_crore'].sum()
    s1.metric("Constituent Equities", f"{len(df_filtered)} Companies")
    s2.metric("Combined Market Cap", f"₹{total_sec_mcap:,.0f} Cr" if total_sec_mcap > 0 else "—")
    s3.metric("Median Sector ROE", f"{df_filtered['return_on_equity_pct'].median():.1f}%" if not df_filtered.empty else "—")
    s4.metric("Median Sector OPM", f"{df_filtered['operating_profit_margin_pct'].median():.1f}%" if not df_filtered.empty else "—")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    c_bubble, c_bar = st.columns([3, 2])

    with c_bubble:
        st.markdown('<div class="terminal-card-title">🫧 Revenue vs. Return on Equity (Bubble Size = Market Cap)</div>', unsafe_allow_html=True)
        bubble_data = df_filtered.copy()
        bubble_data['market_cap_crore'] = bubble_data['market_cap_crore'].fillna(1000).abs()
        bubble_data['sales_cr'] = bubble_data['sales_cr'].fillna(0)
        bubble_data['return_on_equity_pct'] = bubble_data['return_on_equity_pct'].fillna(0)
        
        fig_bubble = px.scatter(
            bubble_data, x="sales_cr", y="return_on_equity_pct", size="market_cap_crore",
            color="sub_sector" if selected_sector != "All Sectors" else "broad_sector",
            hover_name="company_name", size_max=45,
            labels={"sales_cr": "Annual Revenue (₹ Crore)", "return_on_equity_pct": "Return on Equity (%)"}
        )
        layout_bubble = get_terminal_chart_layout()
        layout_bubble.update(height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)))
        fig_bubble.update_layout(layout_bubble)
        st.plotly_chart(fig_bubble, use_container_width=True)

    with c_bar:
        st.markdown('<div class="terminal-card-title">📊 Sector Market Capitalization Weights</div>', unsafe_allow_html=True)
        sec_agg = df.groupby('broad_sector').agg(
            total_mcap=('market_cap_crore', 'sum'),
            company_count=('company_id', 'count')
        ).reset_index().sort_values('total_mcap', ascending=True)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=sec_agg['broad_sector'], x=sec_agg['total_mcap'], orientation='h',
            marker=dict(color=sec_agg['total_mcap'], colorscale=[[0, '#0284c7'], [1, '#38bdf8']], line=dict(color='#0ea5e9', width=1)),
            hovertemplate="Sector: %{y}<br>Market Cap: ₹%{x:,.0f} Cr<extra></extra>"
        ))
        layout_bar = get_terminal_chart_layout()
        layout_bar.update(height=380, xaxis_title="Market Cap (₹ Crore)", margin=dict(l=100, r=20, t=20, b=40))
        fig_bar.update_layout(layout_bar)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="terminal-card-title">📑 Sector Aggregates & Benchmark Medians</div>', unsafe_allow_html=True)
    sec_summary_table = df.groupby('broad_sector').agg(
        Equities=('company_id', 'count'),
        Total_Market_Cap=('market_cap_crore', 'sum'),
        Total_Revenue=('sales_cr', 'sum'),
        Median_ROE=('return_on_equity_pct', 'median'),
        Median_OPM=('operating_profit_margin_pct', 'median'),
        Median_PE=('pe_ratio', 'median')
    ).reset_index().sort_values('Total_Market_Cap', ascending=False)
    sec_summary_table.columns = ['Broad Sector', 'Constituent Count', 'Total Market Cap (Cr)', 'Total Revenue (Cr)', 'Median ROE (%)', 'Median OPM (%)', 'Median P/E']
    sec_summary_table['Total Market Cap (Cr)'] = sec_summary_table['Total Market Cap (Cr)'].apply(lambda x: f"₹{x:,.0f}")
    sec_summary_table['Total Revenue (Cr)'] = sec_summary_table['Total Revenue (Cr)'].apply(lambda x: f"₹{x:,.0f}")
    sec_summary_table['Median ROE (%)'] = sec_summary_table['Median ROE (%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
    sec_summary_table['Median OPM (%)'] = sec_summary_table['Median OPM (%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
    sec_summary_table['Median P/E'] = sec_summary_table['Median P/E'].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "—")
    st.dataframe(sec_summary_table, use_container_width=True, hide_index=True)

def render_screen_capital():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 07 • Capital Deployment
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Capital Allocation Architecture & Strategy Treemap
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Algorithmic cash deployment classification based on Operating, Investing, and Financing cash flows.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = get_capital_allocation_data()
    if df.empty:
        st.error("Capital allocation analytical data (`output/capital_allocation.csv`) not found.")
        return

    counts = df['pattern_label'].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Shareholder Returns (+, -, -)", f"{counts.get('Shareholder Returns', 0)} Equities")
    c2.metric("Reinvestor (+, -, -)", f"{counts.get('Reinvestor', 0)} Equities")
    c3.metric("Growth Debt-Funded (-, -, +)", f"{counts.get('Growth Funded by Debt', 0)} Equities")
    c4.metric("Mixed / Transition (+, -, +)", f"{counts.get('Mixed', 0)} Equities")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="terminal-card-title">🗺️ Capital Allocation Treemap (Size = Market Capitalization)</div>', unsafe_allow_html=True)

    COLOR_MAP = {
        'Shareholder Returns': '#10b981', 'Reinvestor': '#0ea5e9', 'Mixed': '#8b5cf6',
        'Growth Funded by Debt': '#f59e0b', 'Liquidating Assets': '#ec4899',
        'Distress Signal': '#f43f5e', 'Pre-Revenue': '#64748b', 'Unclassified': '#475569'
    }
    df = df.copy()
    df['company_name'] = df['company_name'].fillna(df['company_id']).astype(str).str.replace('\n', ' ').str.strip()
    df['broad_sector'] = df['broad_sector'].fillna('General').astype(str).str.replace('\n', ' ').str.strip()
    df['pattern_label'] = df['pattern_label'].fillna('Unclassified').astype(str).str.replace('\n', ' ').str.strip()
    df['Root'] = 'Nifty 100 Universe'
    df['company_display'] = df['company_name'] + " (" + df['company_id'].astype(str) + ")"
    df_tree = df.dropna(subset=['Root', 'pattern_label', 'broad_sector', 'company_display', 'market_cap_crore'])
    df_tree = df_tree[df_tree['market_cap_crore'] > 0]

    try:
        fig_treemap = px.treemap(
            df_tree, path=['Root', 'pattern_label', 'broad_sector', 'company_display'],
            values='market_cap_crore', color='pattern_label', color_discrete_map=COLOR_MAP
        )
        fig_treemap.update_traces(
            textinfo="label+value", hovertemplate="<b>%{label}</b><br>Market Cap: ₹%{value:,.0f} Cr<extra></extra>",
            marker=dict(line=dict(color='#080d1a', width=1.5))
        )
        layout_tree = get_terminal_chart_layout()
        layout_tree.update(height=480, margin=dict(l=10, r=10, t=10, b=10))
        fig_treemap.update_layout(layout_tree)
        st.plotly_chart(fig_treemap, use_container_width=True)
    except Exception as e:
        fig_bar = px.bar(
            df.groupby('pattern_label')['market_cap_crore'].sum().reset_index(),
            x='pattern_label', y='market_cap_crore', color='pattern_label',
            color_discrete_map=COLOR_MAP
        )
        fig_bar.update_layout(get_terminal_chart_layout())
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="terminal-card-title">📋 Constituent Capital Deployment Classification Audit</div>', unsafe_allow_html=True)
    table_cols = ['company_id', 'company_name', 'broad_sector', 'cfo_sign', 'cfi_sign', 'cff_sign', 'pattern_label', 'market_cap_crore']
    available_cols = [c for c in table_cols if c in df.columns]
    display_table = df[available_cols].copy().sort_values('market_cap_crore', ascending=False)
    display_table.rename(columns={
        'company_id': 'Ticker', 'company_name': 'Company Name', 'broad_sector': 'Sector',
        'cfo_sign': 'CFO (Operating)', 'cfi_sign': 'CFI (Investing)', 'cff_sign': 'CFF (Financing)',
        'pattern_label': 'Capital Strategy', 'market_cap_crore': 'Market Cap (Cr)'
    }, inplace=True)
    if 'Market Cap (Cr)' in display_table.columns:
        display_table['Market Cap (Cr)'] = display_table['Market Cap (Cr)'].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(display_table, use_container_width=True, hide_index=True)

def render_screen_reports():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #0ea5e9; letter-spacing: 0.1em; text-transform: uppercase;">
            Screen 08 • Statutory Filings
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">
            Annual Reports & Regulatory Filings Hub
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Searchable access to 1,404 verified BSE exchange corporate filings and statutory disclosures across Nifty 100 companies.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_docs = get_documents()
    if df_docs.empty:
        st.error("No statutory filing records available.")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Indexed Statutory Filings", f"{len(df_docs):,} Documents")
    m2.metric("Audited Listed Companies", f"{df_docs['company_id'].nunique()} Equities")
    m3.metric("Latest Available Cycle", f"FY{df_docs['year'].max()}")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    col_search, col_yr = st.columns([3, 1])

    with col_search:
        search_query = st.text_input(
            "Search by Company Name or NSE Ticker",
            placeholder="e.g. Tata Consultancy Services, TCS, Reliance, HDFC...",
            key="rep_search_input"
        )
    years_list = ["All Years"] + sorted([str(y) for y in df_docs['year'].dropna().unique()], reverse=True)
    with col_yr:
        selected_year = st.selectbox("Filing Year", options=years_list, index=0, key="rep_year_select")

    filtered_docs = df_docs.copy()
    if search_query:
        q = search_query.strip().lower()
        filtered_docs = filtered_docs[
            filtered_docs['company_name'].str.lower().str.contains(q) |
            filtered_docs['company_id'].str.lower().str.contains(q)
        ]
    if selected_year != "All Years":
        filtered_docs = filtered_docs[filtered_docs['year'].astype(str) == selected_year]

    st.markdown(f'<div class="terminal-card-title">📄 Verified Exchange Filings ({len(filtered_docs)} Matching Records)</div>', unsafe_allow_html=True)
    display_df = filtered_docs[['company_name', 'company_id', 'year', 'annual_report']].copy()
    display_df.rename(columns={
        'company_name': 'Company Name', 'company_id': 'Ticker', 'year': 'Fiscal Year',
        'annual_report': 'BSE Exchange Document Link'
    }, inplace=True)

    st.dataframe(
        display_df,
        column_config={
            "BSE Exchange Document Link": st.column_config.LinkColumn(
                "Filing Source",
                help="Click to open the verified BSE India statutory filing PDF",
                display_text="Open BSE Filing ↗"
            )
        },
        use_container_width=True,
        hide_index=True
    )
