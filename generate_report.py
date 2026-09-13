from fpdf import FPDF
from pathlib import Path

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Bluestock Mutual Fund Analytics Capstone - Final Report', 0, 1, 'R')
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(4)

def create_report():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Cover Page
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 24)
    pdf.set_text_color(0, 51, 102)
    pdf.ln(50)
    pdf.cell(0, 10, 'Bluestock Mutual Fund Analytics', 0, 1, 'C')
    pdf.set_font('helvetica', '', 16)
    pdf.cell(0, 10, 'Capstone Project Final Report', 0, 1, 'C')
    pdf.ln(30)
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, 'Prepared By: Analytics Team', 0, 1, 'C')
    pdf.cell(0, 10, 'Date: September 2026', 0, 1, 'C')
    
    # 2. Executive Summary
    pdf.add_page()
    pdf.chapter_title('Executive Summary')
    pdf.chapter_body(
        "This project delivers a comprehensive end-to-end data pipeline and analytics solution for the Bluestock Mutual Fund portfolio. "
        "We successfully ingested, cleaned, and integrated 10 disparate raw CSV datasets into a highly optimized SQLite Star Schema database. "
        "Leveraging this foundation, we conducted extensive Exploratory Data Analysis (EDA) across 40 mutual fund schemes, covering AUM growth, NAV trends, "
        "and investor demographics. Furthermore, we calculated advanced performance and risk metrics (Sharpe, Sortino, Alpha, Beta, VaR, CVaR) and benchmarked "
        "funds against NIFTY 50 and NIFTY 100 indices. Finally, we developed a composite Fund Scorecard and a cohort-based behavioral model to guide "
        "business decisions."
    )
    
    # 3. Problem Statement & Objectives
    pdf.chapter_title('Problem Statement & Objectives')
    pdf.chapter_body(
        "Objective: To transform fragmented mutual fund data into actionable financial intelligence.\n\n"
        "Key Deliverables Achieved:\n"
        "- Automated ETL Pipeline for accurate data ingestion and cleansing.\n"
        "- Relational Database Design (Star Schema) enabling robust querying.\n"
        "- Extensive EDA identifying key market and demographic trends.\n"
        "- Advanced Risk & Performance Analytics including VaR, Drawdowns, and Benchmarking.\n"
        "- A unified Fund Scorecard to objectively rank 40 funds.\n"
    )

    # 4. Data Sources & 5. ETL Pipeline
    pdf.add_page()
    pdf.chapter_title('Data Sources & ETL Pipeline Design')
    pdf.chapter_body(
        "Data Sources:\n"
        "The project integrated 10 core datasets containing historical NAVs, Benchmark Indices, Fund Master details, SIP flows, AUM records, and investor transactions. "
        "The coverage spanned over multiple years with high-frequency daily NAV trading data.\n\n"
        "ETL Pipeline Design:\n"
        "1. Extraction: Raw CSV files were read using Pandas.\n"
        "2. Transformation: Handled missing values, standardized date formats, calculated forward-filled NAVs (while explicitly flagging non-trading days to preserve return distribution accuracy), and normalized category texts.\n"
        "3. Loading: Data was pushed into a structured SQLite database (`bluestock_mf.db`)."
    )

    # 6. Database Design
    pdf.chapter_title('Database Design (Star Schema)')
    pdf.chapter_body(
        "The database was architected using a Star Schema optimized for analytics:\n"
        "- Fact Tables: `fact_nav` (64,320 rows), `fact_performance`, `fact_transactions` (32,778 rows), `fact_benchmark_indices`, `fact_sip_inflows`, `fact_aum`, `fact_holdings`.\n"
        "- Dimension Tables: `dim_fund` (40 schemes), `dim_investor`.\n"
        "This centralized architecture allowed seamless joins for computing complex metrics like the rolling Sharpe ratio and Alpha."
    )

    # 7. Exploratory Data Analysis
    pdf.add_page()
    pdf.chapter_title('Exploratory Data Analysis (EDA)')
    pdf.chapter_body(
        "We generated 25 distinct visualizations analyzing fund metrics and demographic trends. Key findings include:\n"
        "- SBI Mutual Fund consistently holds the highest AUM.\n"
        "- The '26-35' age group represents 40.7% of all unique investors, dominating the demographic spread.\n"
        "- T30 cities account for 66.7% of investors, confirming a strong urban penetration.\n"
        "- High correlation (>0.8) exists amongst the Top 10 equity funds, suggesting limited diversification benefits.\n"
    )
    
    # Embed some key EDA charts
    eda_dir = Path('reports/eda')
    if eda_dir.exists():
        charts = ['01_nav_trends_all_funds.png', '06_age_distribution.png', '18_risk_return_scatter.png', '20_drawdown_vs_alpha.png']
        for chart in charts:
            img_path = eda_dir / chart
            if img_path.exists():
                pdf.add_page()
                pdf.chapter_title(f'EDA Visualization: {chart.replace(".png", "")}')
                pdf.image(str(img_path), x=15, w=180)

    # 8. Performance Analytics
    pdf.add_page()
    pdf.chapter_title('Performance Analytics')
    pdf.chapter_body(
        "To evaluate true fund quality, we computed the following across all 40 funds:\n"
        "- Daily Returns & CAGR (1yr, 3yr, 5yr).\n"
        "- Sharpe Ratio & Sortino Ratio: Calculated using an annualized Risk-Free rate of 6.5%.\n"
        "- Alpha and Beta: Computed via OLS Regression against the NIFTY 100 benchmark.\n"
        "- Maximum Drawdown: Extracted the worst peak-to-trough decline dynamically.\n"
        "- Fund Scorecard: A composite 0-100 score prioritizing Risk-Adjusted Returns (Sharpe 25%, Alpha 20%) over raw returns."
    )
    
    # Embed Benchmark Chart
    bench_chart = Path('benchmark_comparison_chart.png')
    if bench_chart.exists():
        pdf.add_page()
        pdf.chapter_title('Top 5 Funds vs Benchmarks (NIFTY 50 & 100)')
        pdf.image(str(bench_chart), x=15, w=180)
        pdf.chapter_body("Tracking error calculations revealed that the top active funds successfully outperformed the passive indices over the 3-year horizon.")

    # 9. Advanced Analytics
    pdf.add_page()
    pdf.chapter_title('Advanced Analytics & Risk Metrics')
    pdf.chapter_body(
        "Beyond standard metrics, we performed deep behavioral and risk modeling:\n"
        "- Historical VaR (95%) and CVaR identified the funds with the most severe 'fat tail' risk during market corrections.\n"
        "- 90-Day Rolling Sharpe highlighted that risk-adjusted performance is highly time-dependent.\n"
        "- Investor Cohort Analysis mapped early vs late investor groups, proving earlier cohorts have significantly higher lifetime invested capital.\n"
        "- SIP Continuity Analysis tracked investors with 6+ SIPs, flagging accounts with >35 days average gap as 'at-risk' of attrition.\n"
        "- Sector HHI quantified portfolio concentration, showing high density in the Banking & Financial Services sectors."
    )

    # Embed Rolling Sharpe Chart
    sharpe_chart = Path('rolling_sharpe_chart.png')
    if sharpe_chart.exists():
        pdf.image(str(sharpe_chart), x=15, w=180)

    # 10. Dashboard
    pdf.add_page()
    pdf.chapter_title('Power BI Dashboard')
    pdf.chapter_body(
        "The Interactive Power BI Dashboard comprises 4 comprehensive pages:\n"
        "1. Overview: High-level KPI aggregations.\n"
        "2. Fund Performance: Deep-dive into specific fund returns and scorecard ranks.\n"
        "3. NAV Details: Historical time-series exploration.\n"
        "4. SIP & Market Trends: Heatmaps and behavioral analytics.\n\n"
        "[Note: Final dashboard deployment screenshots are maintained directly within the Power BI Service workspace.]"
    )

    # 11. Findings & 12. Recommendations
    pdf.add_page()
    pdf.chapter_title('Key Findings & Recommendations')
    pdf.chapter_body(
        "Key Findings:\n"
        "1. The highest rated funds on our composite scorecard successfully generated positive Alpha against NIFTY 100.\n"
        "2. Significant concentration risk (High HHI) exists in top funds.\n"
        "3. Younger demographics (26-35) prefer SIPs, while higher-income bands execute large lumpsums.\n\n"
        "Recommendations:\n"
        "- Investors: Utilize the generated Scorecard to select funds based on risk-adjusted returns rather than just 1-year trailing absolute returns.\n"
        "- Fund Managers: Monitor HHI metrics to ensure portfolios do not inadvertently become closet index trackers heavily overweight in Banking.\n"
        "- Business/Product Teams: Target the 'at-risk' SIP investors (gap > 35 days) with automated retention campaigns."
    )

    # 13. Limitations & 14. Conclusion
    pdf.chapter_title('Limitations & Conclusion')
    pdf.chapter_body(
        "Limitations:\n"
        "- Alpha and Beta were computed strictly against NIFTY 100 for all funds, which is a broad market comparison rather than category-specific.\n"
        "- The 6.5% Risk-Free Rate is held constant historically, while in reality, repo rates fluctuated.\n"
        "- Historical data limits the 5-year CAGR computation for newer funds.\n\n"
        "Conclusion:\n"
        "This capstone successfully demonstrates a production-grade analytics pipeline. By transforming raw CSV data into a unified relational database, and layering on Python-based quantitative modeling, we generated deep insights that bridge the gap between raw data and actionable financial intelligence."
    )

    pdf.output('Final_Report.pdf')
    print("Successfully generated Final_Report.pdf")

if __name__ == '__main__':
    create_report()
