import os
import sqlite3
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'nifty100.db')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
SECTOR_DIR = os.path.join(REPORTS_DIR, 'sector')
PORTFOLIO_DIR = os.path.join(REPORTS_DIR, 'portfolio')

os.makedirs(SECTOR_DIR, exist_ok=True)
os.makedirs(PORTFOLIO_DIR, exist_ok=True)

UTILITIES_TICKERS = {'NTPC', 'POWERGRID', 'TATAPOWER', 'NHPC', 'ADANIGREEN', 'JSWENERGY'}

def get_latest_company_data():
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    WITH RankedRatios AS (
        SELECT r.*,
               ROW_NUMBER() OVER(PARTITION BY r.company_id ORDER BY r.year DESC) as rn
        FROM financial_ratios r
    )
    SELECT c.id as company_id, 
           c.company_name, 
           s.broad_sector, 
           s.sub_sector,
           curr.year as latest_year,
           curr.return_on_equity_pct as roe,
           curr.return_on_capital_employed_pct as roce,
           curr.debt_to_equity as de,
           curr.operating_profit_margin_pct as opm,
           curr.net_profit_margin_pct as npm,
           curr.free_cash_flow_cr as fcf,
           curr.composite_quality_score as composite_score,
           prev.return_on_equity_pct as prev_roe,
           prev.return_on_capital_employed_pct as prev_roce,
           prev.debt_to_equity as prev_de,
           prev.operating_profit_margin_pct as prev_opm,
           prev.net_profit_margin_pct as prev_npm,
           prev.free_cash_flow_cr as prev_fcf
    FROM companies c
    LEFT JOIN sectors s ON c.id = s.company_id
    LEFT JOIN RankedRatios curr ON c.id = curr.company_id AND curr.rn = 1
    LEFT JOIN RankedRatios prev ON c.id = prev.company_id AND prev.rn = 2
    ORDER BY c.id ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def generate_sector_reports(df):
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SectorTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )
    
    h2_style = ParagraphStyle(
        'SectorH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=1
    )
    
    cell_header = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    # Define the 11 sectors: 10 from broad_sector + Utilities partition
    # Build a dedicated sector assignment column
    df_sec = df.copy()
    
    # We create the 11 sectors mapping
    sector_groups = {}
    base_sectors = [s for s in df_sec['broad_sector'].dropna().unique() if s != 'Energy']
    for s in base_sectors:
        sector_groups[s] = df_sec[df_sec['broad_sector'] == s]
        
    # Split Energy into Oil & Gas / Energy and Utilities
    energy_df = df_sec[df_sec['broad_sector'] == 'Energy']
    utilities_df = energy_df[energy_df['company_id'].isin(UTILITIES_TICKERS)]
    pure_energy_df = energy_df[~energy_df['company_id'].isin(UTILITIES_TICKERS)]
    
    sector_groups['Energy'] = pure_energy_df
    sector_groups['Utilities'] = utilities_df
    
    print(f"Generating reports for {len(sector_groups)} sectors...")

    for sector_name, group in sector_groups.items():
        if group.empty:
            continue
            
        safe_name = sector_name.replace(' ', '_').replace('&', 'and')
        pdf_path = os.path.join(SECTOR_DIR, f"{safe_name}_Report.pdf")
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        elements = []
        
        # Header
        elements.append(Paragraph(f"Sector Intelligence Report: {sector_name}", title_style))
        elements.append(Paragraph(f"Nifty 100 Sectoral Analysis • Coverage: {len(group)} Companies", h2_style))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Sector Summary Median KPIs
        med_roe = group['roe'].median()
        med_roce = group['roce'].median()
        med_de = group['de'].median()
        med_opm = group['opm'].median()
        med_fcf = group['fcf'].median()
        med_score = group['composite_score'].median()
        
        # Best performer
        best_comp = group.sort_values('composite_score', ascending=False).iloc[0]
        
        summary_data = [
            [Paragraph("<b>Metric</b>", cell_header), Paragraph("<b>Sector Median</b>", cell_header), Paragraph("<b>Top Performer</b>", cell_header), Paragraph("<b>Leader Score</b>", cell_header)],
            [Paragraph("Return on Equity (ROE)", cell_style), Paragraph(f"{med_roe:.2f}%" if pd.notna(med_roe) else "N/A", cell_style), Paragraph(f"{best_comp['company_name']} ({best_comp['company_id']})", cell_style), Paragraph(f"{best_comp['composite_score']:.2f}", cell_style)],
            [Paragraph("ROCE", cell_style), Paragraph(f"{med_roce:.2f}%" if pd.notna(med_roce) else "N/A", cell_style), Paragraph("Sector Median D/E", cell_style), Paragraph(f"{med_de:.2f}" if pd.notna(med_de) else "N/A", cell_style)],
            [Paragraph("Operating Margin (OPM)", cell_style), Paragraph(f"{med_opm:.2f}%" if pd.notna(med_opm) else "N/A", cell_style), Paragraph("Sector Median FCF", cell_style), Paragraph(f"₹{med_fcf:,.0f} Cr" if pd.notna(med_fcf) else "N/A", cell_style)],
            [Paragraph("Quality Composite Score", cell_style), Paragraph(f"{med_score:.2f}" if pd.notna(med_score) else "N/A", cell_style), Paragraph("Total Tracked Entities", cell_style), Paragraph(str(len(group)), cell_style)]
        ]
        
        sum_table = Table(summary_data, colWidths=[130, 100, 190, 100])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.HexColor('#FFFFFF')]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(sum_table)
        elements.append(Spacer(1, 0.25 * inch))
        
        # Table of all companies in sector with 8 metrics
        elements.append(Paragraph("Constituent Companies Performance Matrix", h2_style))
        
        headers = ["Company", "Ticker", "ROE %", "ROCE %", "D/E", "OPM %", "FCF (Cr)", "Score"]
        table_rows = [[Paragraph(f"<b>{h}</b>", cell_header) for h in headers]]
        
        for _, r in group.sort_values('company_id').iterrows():
            c_name = r['company_name'][:20] + ('...' if len(str(r['company_name'])) > 20 else '')
            table_rows.append([
                Paragraph(c_name, ParagraphStyle('LeftCell', parent=cell_style, alignment=0)),
                Paragraph(str(r['company_id']), cell_style),
                Paragraph(f"{r['roe']:.1f}%" if pd.notna(r['roe']) else "N/A", cell_style),
                Paragraph(f"{r['roce']:.1f}%" if pd.notna(r['roce']) else "N/A", cell_style),
                Paragraph(f"{r['de']:.2f}" if pd.notna(r['de']) else "N/A", cell_style),
                Paragraph(f"{r['opm']:.1f}%" if pd.notna(r['opm']) else "N/A", cell_style),
                Paragraph(f"{r['fcf']:.0f}" if pd.notna(r['fcf']) else "N/A", cell_style),
                Paragraph(f"{r['composite_score']:.1f}" if pd.notna(r['composite_score']) else "N/A", cell_style)
            ])
            
        co_table = Table(table_rows, colWidths=[140, 60, 50, 50, 45, 55, 65, 55])
        co_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.HexColor('#FFFFFF')]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(co_table)
        
        doc.build(elements)
        print(f"Generated Sector Report: {pdf_path}")

def get_trend_arrow(curr, prev, higher_is_better=True):
    if pd.isna(curr) or pd.isna(prev):
        return ("→", "Flat / N/A", colors.HexColor('#64748B'))
    if prev == 0:
        pct_change = 0.0
    else:
        pct_change = ((curr - prev) / abs(prev)) * 100.0
        
    if abs(pct_change) <= 2.0:
        return ("→", f"{pct_change:+.1f}% (Flat)", colors.HexColor('#475569'))
    elif pct_change > 2.0:
        if higher_is_better:
            return ("↑", f"{pct_change:+.1f}% (Improved)", colors.HexColor('#16A34A'))
        else:
            return ("↑", f"{pct_change:+.1f}% (Higher Risk)", colors.HexColor('#DC2626'))
    else:
        if higher_is_better:
            return ("↓", f"{pct_change:+.1f}% (Declined)", colors.HexColor('#DC2626'))
        else:
            return ("↓", f"{pct_change:+.1f}% (Deleveraging)", colors.HexColor('#16A34A'))

def generate_portfolio_summary(df):
    pdf_path = os.path.join(PORTFOLIO_DIR, "portfolio_summary.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'PortTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )
    sub_style = ParagraphStyle(
        'PortSub',
        parent=styles['Heading3'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=0
    )
    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        alignment=1
    )
    card_val = ParagraphStyle(
        'CardVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )
    card_trend = ParagraphStyle(
        'CardTrend',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=1
    )
    
    elements = []
    
    df_sorted = df.sort_values('company_id').reset_index(drop=True)
    total_cos = len(df_sorted)
    
    for idx, r in df_sorted.iterrows():
        cid = r['company_id']
        cname = r['company_name']
        sector = r.get('broad_sector', 'Unclassified')
        latest_yr = r.get('latest_year', 'FY24')
        
        # Header
        elements.append(Paragraph(f"{cname} ({cid})", title_style))
        elements.append(Paragraph(f"Sector: {sector}  •  Reporting Year: {latest_yr}  •  Portfolio Rank #{idx+1} of {total_cos}", sub_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Compute arrows
        roe_arrow, roe_txt, roe_color = get_trend_arrow(r['roe'], r['prev_roe'], higher_is_better=True)
        roce_arrow, roce_txt, roce_color = get_trend_arrow(r['roce'], r['prev_roce'], higher_is_better=True)
        de_arrow, de_txt, de_color = get_trend_arrow(r['de'], r['prev_de'], higher_is_better=False)
        opm_arrow, opm_txt, opm_color = get_trend_arrow(r['opm'], r['prev_opm'], higher_is_better=True)
        fcf_arrow, fcf_txt, fcf_color = get_trend_arrow(r['fcf'], r['prev_fcf'], higher_is_better=True)
        npm_arrow, npm_txt, npm_color = get_trend_arrow(r['npm'], r['prev_npm'], higher_is_better=True)
        
        # Top 6 KPI Tiles in 2 rows of 3
        tile1 = [
            Paragraph("Return on Equity (ROE)", card_title),
            Paragraph(f"{r['roe']:.2f}%" if pd.notna(r['roe']) else "N/A", card_val),
            Paragraph(f"<font color='{roe_color.hexval()}'><b>{roe_arrow} {roe_txt}</b></font>", card_trend)
        ]
        tile2 = [
            Paragraph("Return on Capital (ROCE)", card_title),
            Paragraph(f"{r['roce']:.2f}%" if pd.notna(r['roce']) else "N/A", card_val),
            Paragraph(f"<font color='{roce_color.hexval()}'><b>{roce_arrow} {roce_txt}</b></font>", card_trend)
        ]
        tile3 = [
            Paragraph("Debt to Equity (D/E)", card_title),
            Paragraph(f"{r['de']:.2f}" if pd.notna(r['de']) else "N/A", card_val),
            Paragraph(f"<font color='{de_color.hexval()}'><b>{de_arrow} {de_txt}</b></font>", card_trend)
        ]
        tile4 = [
            Paragraph("Operating Margin (OPM)", card_title),
            Paragraph(f"{r['opm']:.2f}%" if pd.notna(r['opm']) else "N/A", card_val),
            Paragraph(f"<font color='{opm_color.hexval()}'><b>{opm_arrow} {opm_txt}</b></font>", card_trend)
        ]
        tile5 = [
            Paragraph("Free Cash Flow (FCF)", card_title),
            Paragraph(f"₹{r['fcf']:,.0f} Cr" if pd.notna(r['fcf']) else "N/A", card_val),
            Paragraph(f"<font color='{fcf_color.hexval()}'><b>{fcf_arrow} {fcf_txt}</b></font>", card_trend)
        ]
        tile6 = [
            Paragraph("Net Profit Margin (NPM)", card_title),
            Paragraph(f"{r['npm']:.2f}%" if pd.notna(r['npm']) else "N/A", card_val),
            Paragraph(f"<font color='{npm_color.hexval()}'><b>{npm_arrow} {npm_txt}</b></font>", card_trend)
        ]
        
        grid_data = [
            [tile1, tile2, tile3],
            [tile4, tile5, tile6]
        ]
        
        grid_table = Table(grid_data, colWidths=[170, 170, 170], rowHeights=[95, 95])
        grid_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(grid_table)
        elements.append(Spacer(1, 0.4 * inch))
        
        # Summary & Benchmark Note
        score_val = f"{r['composite_score']:.2f}" if pd.notna(r['composite_score']) else "N/A"
        summary_table_data = [
            [Paragraph("<b>Intelligence Metric</b>", card_title), Paragraph("<b>Value</b>", card_title), Paragraph("<b>Evaluation</b>", card_title)],
            [Paragraph("Composite Quality Score", card_trend), Paragraph(score_val, card_trend), Paragraph("Top Quartile" if pd.notna(r['composite_score']) and r['composite_score'] >= 70 else "Core Portfolio", card_trend)],
            [Paragraph("Cash Flow Trend", card_trend), Paragraph(f"{fcf_arrow} {fcf_txt}", card_trend), Paragraph("Self-funded Growth" if pd.notna(r['fcf']) and r['fcf'] > 0 else "External Financing", card_trend)],
            [Paragraph("Balance Sheet Leverage", card_trend), Paragraph(f"{de_arrow} {de_txt}", card_trend), Paragraph("Conservative" if pd.notna(r['de']) and r['de'] < 0.5 else "Monitored", card_trend)]
        ]
        
        s_tbl = Table(summary_table_data, colWidths=[180, 160, 170])
        s_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.HexColor('#FFFFFF')]),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(s_tbl)
        
        # Footer text
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"<i>Nifty 100 Portfolio Intelligence Platform • Generated for BlueStock Fintech • Page {idx+1} of {total_cos}</i>", sub_style))
        
        if idx < total_cos - 1:
            elements.append(PageBreak())
            
    doc.build(elements)
    print(f"Generated 92-page Portfolio Summary PDF: {pdf_path}")

def generate_batch_reports():
    print("Loading latest financial metrics for batch reports...")
    df = get_latest_company_data()
    print(f"Loaded {len(df)} companies.")
    generate_sector_reports(df)
    generate_portfolio_summary(df)
    print("Batch Reports Generation Complete.")

if __name__ == '__main__':
    generate_batch_reports()
