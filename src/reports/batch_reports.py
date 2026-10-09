import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
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

def generate_batch_reports():
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT s.broad_sector, s.company_id, c.company_name, 
           r.return_on_equity_pct as roe, r.debt_to_equity as de, r.free_cash_flow_cr as fcf,
           r.composite_quality_score
    FROM sectors s
    JOIN companies c ON s.company_id = c.id
    JOIN financial_ratios r ON s.company_id = r.company_id
    WHERE r.year = (SELECT MAX(year) FROM financial_ratios)
    """
    df = pd.read_sql(query, conn)
    conn.close()

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    h2_style = styles['Heading2']
    
    # 1. Sector Reports
    for sector, group in df.groupby('broad_sector'):
        safe_sector = str(sector).replace('/', '_').replace('\\', '_')
        pdf_path = os.path.join(SECTOR_DIR, f"{safe_sector}_Report.pdf")
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []
        
        elements.append(Paragraph(f"Sector Report: {sector}", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary
        elements.append(Paragraph(f"Total Companies: {len(group)}", h2_style))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Table of companies
        data = [["Company", "Ticker", "ROE %", "D/E", "Composite Score"]]
        for _, row in group.iterrows():
            data.append([
                row['company_name'],
                row['company_id'],
                f"{row['roe']:.2f}" if pd.notna(row['roe']) else "N/A",
                f"{row['de']:.2f}" if pd.notna(row['de']) else "N/A",
                f"{row.get('composite_quality_score', 0):.2f}"
            ])
            
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        elements.append(t)
        doc.build(elements)

    # 2. Portfolio Report
    pdf_path = os.path.join(PORTFOLIO_DIR, "portfolio_summary.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    
    elements.append(Paragraph("Portfolio Summary Report", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    elements.append(Paragraph(f"Total Companies in Portfolio: {len(df)}", h2_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Sector Breakdown
    sector_counts = df['broad_sector'].value_counts().reset_index()
    sector_counts.columns = ['Sector', 'Count']
    
    data = [["Sector", "Company Count"]]
    for _, row in sector_counts.iterrows():
        data.append([row['Sector'], str(row['Count'])])
        
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    print("Batch Reports Generation Complete.")

if __name__ == '__main__':
    generate_batch_reports()
