import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'nifty100.db')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'tearsheets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
TEMP_DIR = os.path.join(BASE_DIR, 'scratch', 'charts')

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_tearsheets():
    conn = sqlite3.connect(DB_PATH)
    
    comp_df = pd.read_sql("SELECT * FROM companies", conn)
    pl_df = pd.read_sql("SELECT * FROM profitandloss", conn)
    bs_df = pd.read_sql("SELECT * FROM balancesheet", conn)
    cf_df = pd.read_sql("SELECT * FROM cashflow", conn)
    ratio_df = pd.read_sql("SELECT * FROM financial_ratios", conn)
    
    # Try to load pros and cons from output if exists, else empty
    pc_path = os.path.join(OUTPUT_DIR, 'pros_cons_generated.csv')
    if os.path.exists(pc_path):
        pc_df = pd.read_csv(pc_path)
    else:
        pc_df = pd.DataFrame(columns=['company_id', 'type', 'text'])

    ca_path = os.path.join(OUTPUT_DIR, 'capital_allocation.csv')
    if os.path.exists(ca_path):
        ca_df = pd.read_csv(ca_path)
    else:
        ca_df = pd.DataFrame(columns=['company_id', 'pattern_label'])
        
    conn.close()

    skipped = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    h2_style = styles['Heading2']
    normal_style = styles['Normal']

    for _, row in comp_df.iterrows():
        cid = row['id']
        cname = row['company_name']
        
        c_pl = pl_df[pl_df['company_id'] == cid].sort_values('year')
        c_ratio = ratio_df[ratio_df['company_id'] == cid].sort_values('year')
        c_bs = bs_df[bs_df['company_id'] == cid].sort_values('year')
        c_cf = cf_df[cf_df['company_id'] == cid].sort_values('year')
        
        if c_pl.empty or c_ratio.empty:
            skipped.append({'company_id': cid, 'reason': 'Missing P&L or Ratio Data'})
            continue
            
        pdf_path = os.path.join(REPORTS_DIR, f"{cid}_Tearsheet.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []
        
        # Page 1: Header
        elements.append(Paragraph(f"{cname} ({cid})", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # 6 KPI Tiles (latest year)
        latest_ratio = c_ratio.iloc[-1]
        kpi_data = [
            ["ROE", f"{latest_ratio.get('return_on_equity_pct', 0):.2f}%", "ROCE", f"{latest_ratio.get('return_on_capital_employed_pct', 0):.2f}%"],
            ["D/E", f"{latest_ratio.get('debt_to_equity', 0):.2f}", "OPM", f"{latest_ratio.get('operating_profit_margin_pct', 0):.2f}%"],
            ["FCF", f"{latest_ratio.get('free_cash_flow_cr', 0):.0f} Cr", "Net Profit Margin", f"{latest_ratio.get('net_profit_margin_pct', 0):.2f}%"]
        ]
        
        t = Table(kpi_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.beige),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Trends (Revenue, Net Profit, ROE, ROCE)
        elements.append(Paragraph("Performance Trends", h2_style))
        
        # Generate chart
        fig, axs = plt.subplots(2, 2, figsize=(8, 6))
        
        if not c_pl.empty:
            axs[0,0].bar(c_pl['year'], c_pl['sales'], color='blue')
            axs[0,0].set_title('Revenue')
            axs[0,1].bar(c_pl['year'], c_pl['net_profit'], color='green')
            axs[0,1].set_title('Net Profit')
            
        if not c_ratio.empty:
            axs[1,0].plot(c_ratio['year'], c_ratio['return_on_equity_pct'], marker='o', color='red')
            axs[1,0].set_title('ROE %')
            axs[1,1].plot(c_ratio['year'], c_ratio['return_on_capital_employed_pct'], marker='o', color='purple')
            axs[1,1].set_title('ROCE %')
            
        plt.tight_layout()
        chart_path1 = os.path.join(TEMP_DIR, f"{cid}_page1.png")
        plt.savefig(chart_path1)
        plt.close(fig)
        
        elements.append(Image(chart_path1, width=6*inch, height=4.5*inch))
        
        elements.append(PageBreak())
        
        # Page 2: Balance Sheet Composition
        elements.append(Paragraph("Balance Sheet & Cash Flows", h2_style))
        
        fig2, axs2 = plt.subplots(1, 2, figsize=(8, 4))
        if not c_bs.empty:
            latest_bs = c_bs.iloc[-1]
            labels = ['Equity', 'Borrowings', 'Other Liab']
            sizes = [max(latest_bs.get('equity_capital',0)+latest_bs.get('reserves',0), 0), 
                     max(latest_bs.get('borrowings',0), 0), 
                     max(latest_bs.get('other_liabilities',0), 0)]
            if sum(sizes) > 0:
                axs2[0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            axs2[0].set_title('BS Composition')
            
        if not c_cf.empty:
            latest_cf = c_cf.iloc[-1]
            labels = ['CFO', 'CFI', 'CFF']
            vals = [latest_cf.get('operating_activity',0), latest_cf.get('investing_activity',0), latest_cf.get('financing_activity',0)]
            axs2[1].bar(labels, vals, color=['green', 'red', 'blue'])
            axs2[1].set_title('Cash Flows (Cr)')
            
        plt.tight_layout()
        chart_path2 = os.path.join(TEMP_DIR, f"{cid}_page2.png")
        plt.savefig(chart_path2)
        plt.close(fig2)
        
        elements.append(Image(chart_path2, width=6*inch, height=3*inch))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Pros and Cons
        elements.append(Paragraph("Pros & Cons", h2_style))
        c_pc = pc_df[pc_df['company_id'] == cid]
        pros = c_pc[c_pc['type'] == 'Pro']['text'].tolist()
        cons = c_pc[c_pc['type'] == 'Con']['text'].tolist()
        
        if pros:
            elements.append(Paragraph("<b>Pros:</b> " + ", ".join(pros), normal_style))
        if cons:
            elements.append(Paragraph("<b>Cons:</b> " + ", ".join(cons), normal_style))
            
        elements.append(Spacer(1, 0.2 * inch))
        
        # Capital Allocation Badge
        c_ca = ca_df[ca_df['company_id'] == cid]
        if not c_ca.empty:
            badge = c_ca.iloc[-1].get('pattern_label', 'Unknown')
            elements.append(Paragraph(f"<b>Capital Allocation Badge:</b> {badge}", normal_style))
            
        try:
            doc.build(elements)
        except Exception as e:
            skipped.append({'company_id': cid, 'reason': f"PDF Build Error: {str(e)}"})
            
    df_skipped = pd.DataFrame(skipped)
    df_skipped.to_csv(os.path.join(OUTPUT_DIR, 'skipped_tearsheets.csv'), index=False)
    print("Tearsheets Generation Complete.")
    
if __name__ == '__main__':
    generate_tearsheets()
