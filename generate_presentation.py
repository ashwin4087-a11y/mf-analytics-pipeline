from pptx import Presentation
from pptx.util import Inches, Pt
from pathlib import Path

def create_presentation():
    prs = Presentation()
    
    # Define slide layouts
    title_slide_layout = prs.slide_layouts[0]
    bullet_slide_layout = prs.slide_layouts[1]
    blank_slide_layout = prs.slide_layouts[5]

    # Slide 1: Title
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Bluestock Mutual Fund Analytics"
    subtitle.text = "Capstone Project Final Presentation\nAnalytics Team\nSeptember 2026"

    # Slide 2: Problem & Objective
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    title_shape.text = "Problem & Objective"
    tf = body_shape.text_frame
    tf.text = "Problem Statement: Fragmented, raw mutual fund data lacks actionable insights."
    p = tf.add_paragraph()
    p.text = "Objectives:"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Build an automated ETL pipeline"
    p.level = 2
    p = tf.add_paragraph()
    p.text = "Calculate performance (Sharpe, Alpha) & risk (VaR) metrics"
    p.level = 2
    p = tf.add_paragraph()
    p.text = "Why it matters: Empowers data-driven investment decisions rather than emotion-based trading."
    p.level = 1

    # Slide 3: Data Sources
    slide = prs.slides.add_slide(bullet_slide_layout)
    title_shape = slide.shapes.title
    body_shape = slide.shapes.placeholders[1]
    title_shape.text = "Data Sources"
    tf = body_shape.text_frame
    tf.text = "10 Datasets Integrated:"
    tf.add_paragraph().text = "1. Scheme Master & NAV (Daily tracking)"
    tf.add_paragraph().text = "2. Benchmark Indices (NIFTY 50, NIFTY 100)"
    tf.add_paragraph().text = "3. AUM & SIP Inflows"
    tf.add_paragraph().text = "4. Investor Demographics & Transactions"
    tf.add_paragraph().text = "Data Coverage: Highly granular daily data covering multiple market cycles, enabling deep quantitative analysis."

    # Slide 4: Architecture / ETL
    slide = prs.slides.add_slide(bullet_slide_layout)
    title_shape = slide.shapes.title
    body_shape = slide.shapes.placeholders[1]
    title_shape.text = "Architecture & ETL Pipeline"
    tf = body_shape.text_frame
    tf.text = "Data Flow:"
    tf.add_paragraph().text = "Raw CSVs -> Pandas Cleaning -> SQLite Database -> Jupyter/Python Analytics -> Power BI"
    tf.add_paragraph().text = "Key Transformations:"
    p = tf.add_paragraph()
    p.text = "Date standardization"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "NAV forward-filling (excluding weekends for return calcs)"
    p.level = 1
    p = tf.add_paragraph()
    p.text = "Star Schema creation (Fact & Dim tables)"
    p.level = 1

    # Slide 5: EDA Highlights I
    slide = prs.slides.add_slide(blank_slide_layout)
    title_shape = slide.shapes.title
    title_shape.text = "EDA Highlights I: Demographics"
    img_path = Path('reports/eda/06_age_distribution.png')
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(1), Inches(1.5), width=Inches(4.5))
    txBox = slide.shapes.add_textbox(Inches(5.8), Inches(2), Inches(3.5), Inches(3))
    tf = txBox.text_frame
    tf.text = "Insight:"
    tf.add_paragraph().text = "- '26-35' age group dominates (40.7%)"
    tf.add_paragraph().text = "- Mutual fund adoption is heavily driven by younger, working-age adults."

    # Slide 6: EDA Highlights II
    slide = prs.slides.add_slide(blank_slide_layout)
    title_shape = slide.shapes.title
    title_shape.text = "EDA Highlights II: Risk vs Return"
    img_path = Path('reports/eda/18_risk_return_scatter.png')
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(1), Inches(1.5), width=Inches(4.5))
    txBox = slide.shapes.add_textbox(Inches(5.8), Inches(2), Inches(3.5), Inches(3))
    tf = txBox.text_frame
    tf.text = "Insight:"
    tf.add_paragraph().text = "- Classic risk-reward trade-off is visible."
    tf.add_paragraph().text = "- Some funds achieve higher returns without proportionally higher standard deviation (better Sharpe)."

    # Slide 7: Performance Metrics I
    slide = prs.slides.add_slide(bullet_slide_layout)
    title_shape = slide.shapes.title
    body_shape = slide.shapes.placeholders[1]
    title_shape.text = "Performance Metrics I"
    tf = body_shape.text_frame
    tf.text = "Return & Risk Evaluated:"
    tf.add_paragraph().text = "- CAGR computed for 1, 3, and 5-year horizons."
    tf.add_paragraph().text = "- Sharpe Ratio calculated against a 6.5% Risk-Free Rate."
    tf.add_paragraph().text = "- Sortino Ratio utilized to specifically isolate downside volatility."
    tf.add_paragraph().text = "- Finding: High absolute returns do not always correlate with high risk-adjusted returns."

    # Slide 8: Performance Metrics II
    slide = prs.slides.add_slide(blank_slide_layout)
    title_shape = slide.shapes.title
    title_shape.text = "Performance Metrics II"
    img_path = Path('benchmark_comparison_chart.png')
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(0.5), Inches(1.5), width=Inches(5))
    txBox = slide.shapes.add_textbox(Inches(5.8), Inches(2), Inches(3.5), Inches(3))
    tf = txBox.text_frame
    tf.text = "Alpha & Benchmarking:"
    tf.add_paragraph().text = "- Top 5 Scorecard funds successfully beat NIFTY 100."
    tf.add_paragraph().text = "- Maximum drawdown metrics identified funds vulnerable to severe market corrections."

    # Slide 9: Dashboard I
    slide = prs.slides.add_slide(bullet_slide_layout)
    title_shape = slide.shapes.title
    body_shape = slide.shapes.placeholders[1]
    title_shape.text = "Power BI Dashboard (Overview & Performance)"
    tf = body_shape.text_frame
    tf.text = "Pages 1 & 2:"
    tf.add_paragraph().text = "Overview Page: High-level KPI aggregations including Total AUM, overall SIP inflows, and top-line investor counts."
    tf.add_paragraph().text = "Fund Performance Page: Drill-down into specific scheme CAGRs, Sharpe ratios, and our custom composite Scorecard."
    tf.add_paragraph().text = "[Note: Dashboard deployed via bluestock_mf.pbix]"

    # Slide 10: Dashboard II
    slide = prs.slides.add_slide(bullet_slide_layout)
    title_shape = slide.shapes.title
    body_shape = slide.shapes.placeholders[1]
    title_shape.text = "Power BI Dashboard (NAV & Trends)"
    tf = body_shape.text_frame
    tf.text = "Pages 3 & 4:"
    tf.add_paragraph().text = "NAV Details Page: Interactive time-series visualisations allowing dynamic date slicing of historical NAV trends."
    tf.add_paragraph().text = "SIP & Market Trends Page: Visual heatmaps of category inflows and cohort behavioral analytics."
    tf.add_paragraph().text = "All pages include cross-filtering and dynamic slicers for intuitive exploration."

    # Slide 11: Key Findings & Recommendations
    slide = prs.slides.add_slide(bullet_slide_layout)
    title_shape = slide.shapes.title
    body_shape = slide.shapes.placeholders[1]
    title_shape.text = "Key Findings & Recommendations"
    tf = body_shape.text_frame
    tf.text = "Key Findings:"
    tf.add_paragraph().text = "Top funds exhibit significant sector concentration (High HHI)."
    tf.add_paragraph().text = "SIP continuity analysis reveals critical 'at-risk' investors with >35 day gaps."
    tf.add_paragraph().text = "Recommendations:"
    tf.add_paragraph().text = "Investors: Rely on the risk-adjusted Scorecard rather than chasing 1-year yield."
    tf.add_paragraph().text = "Business: Trigger automated retention campaigns for at-risk SIP cohorts."

    # Slide 12: Thank You
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Thank You"
    subtitle.text = "Questions & Discussion"

    prs.save('Bluestock_MF_Presentation.pptx')
    print("Successfully generated Bluestock_MF_Presentation.pptx")

if __name__ == '__main__':
    create_presentation()
