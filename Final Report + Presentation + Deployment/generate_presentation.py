"""
Bluestock Mutual Fund Analytics Capstone - Final Presentation Generator
Creates a sleek, 16:9 widescreen 12-slide presentation deck with embedded
high-resolution dashboard screenshots, EDA charts, and benchmark figures.
"""
import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

SCRIPT_DIR = Path(__file__).resolve().parent

# Color Palette
DARK_NAVY = RGBColor(15, 23, 42)      # #0F172A
CARD_BG = RGBColor(241, 245, 249)     # #F1F5F9
ACCENT_BLUE = RGBColor(37, 99, 235)   # #2563EB
ACCENT_CYAN = RGBColor(14, 165, 233)  # #0EA5E9
ACCENT_GREEN = RGBColor(16, 185, 129) # #10B981
TEXT_PRIMARY = RGBColor(15, 23, 42)   # #0F172A
TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
WHITE = RGBColor(255, 255, 255)

def create_header(slide, title_text, category_text, slide_num):
    """Adds a consistent executive top banner and slide numbering."""
    # Top bar
    top_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.8))
    tf = top_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = f"BLUESTOCK FINTECH  |  {category_text.upper()}"
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = DARK_NAVY

    # Footer slide number
    ft_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
    ft_tf = ft_box.text_frame
    ft_tf.word_wrap = True
    ft_p = ft_tf.paragraphs[0]
    ft_p.text = f"Mutual Fund Analytics Capstone  |  Slide {slide_num} of 12"
    ft_p.font.size = Pt(8.5)
    ft_p.font.color.rgb = TEXT_MUTED

def build_presentation():
    prs = Presentation()
    # 16:9 Widescreen Layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ----------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # ----------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    # Background card
    bg = s1.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))  # Rectangle
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_NAVY
    bg.line.color.rgb = DARK_NAVY

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "BLUESTOCK FINTECH PVT. LTD."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf1.add_paragraph()
    p.text = "Mutual Fund Analytics Platform"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(12)

    p = tf1.add_paragraph()
    p.text = "End-to-End Data Pipeline, Quantitative Modeling, Risk Scoring & Power BI Intelligence"
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "Prepared by: Data & Analytics Engineering Team   |   Date: September 2026   |   Release Tag: v1.0"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(148, 163, 184)

    # ----------------------------------------------------
    # SLIDE 2: PROBLEM & OBJECTIVE
    # ----------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    create_header(s2, "Problem Statement & Strategic Objectives", "Strategic Alignment", 2)

    # Left Column: Problem Statements
    b_prob = s2.shapes.add_shape(1, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    b_prob.fill.solid()
    b_prob.fill.fore_color.rgb = CARD_BG
    b_prob.line.color.rgb = RGBColor(226, 232, 240)
    tf = b_prob.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE CORE CHALLENGES (P1 - P5)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    probs = [
        "• Data Fragmentation: NAV, AUM, and holdings spread across disconnected AMFI portals and static PDFs.",
        "• Performance Evaluation Gap: Retail investors chase short-term 1Y returns without understanding downside risk.",
        "• No Benchmark Tracking: Lack of visibility into whether active management justifies fees vs NIFTY indices.",
        "• Investor Blind Spot: Limited intelligence on demographic drop-offs and behavioral churn in SIP accounts.",
        "• Static Reporting Bottlenecks: Manual monthly reporting cycles with zero interactive exploration."
    ]
    for pr in probs:
        p = tf.add_paragraph()
        p.text = pr
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(8)

    # Right Column: Objectives
    b_obj = s2.shapes.add_shape(1, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    b_obj.fill.solid()
    b_obj.fill.fore_color.rgb = CARD_BG
    b_obj.line.color.rgb = RGBColor(226, 232, 240)
    tf = b_obj.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CAPSTONE OBJECTIVES (O1 - O8)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)

    objs = [
        "1. Automated ETL Pipeline: Python scripts to ingest, sanitize, and validate 10 raw datasets.",
        "2. Relational Star Schema: SQLite warehouse with optimized fact and dimension tables.",
        "3. Exploratory Data Analysis: 25 visual charts analyzing AUM, demographics, and trends.",
        "4. Quantitative Risk Analytics: Calculating CAGR, Sharpe, Sortino, Alpha, Beta, and VaR.",
        "5. Interactive Power BI Dashboard: 4-screen self-service platform with dynamic cross-filtering.",
        "6. Algorithmic Recommender: Personalized scheme suggestions aligned with investor risk profiles.",
        "7. Complete Verification Package: Audited documentation, 15-20 page report, clean GitHub repo."
    ]
    for ob in objs:
        p = tf.add_paragraph()
        p.text = ob
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(6)

    # ----------------------------------------------------
    # SLIDE 3: DATA SOURCES & SCOPE
    # ----------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    create_header(s3, "Comprehensive Data Foundation & Granularity", "Data Engineering", 3)

    # 4 Key Stat Tiles
    stat_boxes = [
        ("40 SCHEMES", "Top 10 AMCs Tracked", ACCENT_BLUE, Inches(0.8)),
        ("10 DATASETS", "Multi-Source Ingestion", ACCENT_CYAN, Inches(3.8)),
        ("87K+ ROWS", "Clean Structured Data", ACCENT_GREEN, Inches(6.8)),
        ("4.5 YEARS", "Daily NAV History", RGBColor(234, 88, 12), Inches(9.8))
    ]
    for top_txt, sub_txt, col, x_pos in stat_boxes:
        card = s3.shapes.add_shape(1, x_pos, Inches(1.5), Inches(2.7), Inches(1.3))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = col
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = top_txt
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        p = tf.add_paragraph()
        p.text = sub_txt
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Detailed dataset inventory table box
    d_card = s3.shapes.add_shape(1, Inches(0.8), Inches(3.1), Inches(11.7), Inches(3.6))
    d_card.fill.solid()
    d_card.fill.fore_color.rgb = CARD_BG
    d_card.line.color.rgb = RGBColor(226, 232, 240)
    tf = d_card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "INGESTED & STANDARDIZED DATASETS OVERVIEW"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(8)

    items = [
        "• Scheme Master & Daily NAVs: 40 schemes, 64,320 rows anchored to verified mfapi.in endpoints across 2021-2025.",
        "• Benchmark Indices: NIFTY 50 and NIFTY 100 daily closing values (2,260 rows) for relative alpha evaluation.",
        "• Industry AUM & SIP Inflows: Monthly assets by fund house and macro monthly SIP flows (₹31,002 Cr record).",
        "• Investor Transactions: 32,778 transaction logs covering Lumpsum, SIP, and Redemptions with payment modes.",
        "• Category Inflows & Folios: Sectoral asset aggregates and 26.12 crore industry-wide folio tracking.",
        "• Portfolio Holdings: Top 10 equity stock weights per scheme used for Herfindahl-Hirschman concentration modeling."
    ]
    for it in items:
        p = tf.add_paragraph()
        p.text = it
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(5)

    # ----------------------------------------------------
    # SLIDE 4: ARCHITECTURE & ETL PIPELINE
    # ----------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    create_header(s4, "System Architecture & ETL Pipeline Design", "System Architecture", 4)

    # 5 Pipeline Stage Cards
    stages = [
        ("1. EXTRACT", "Raw AMFI CSVs\nmfapi.in API\nNSE/BSE Feeds", Inches(0.8)),
        ("2. CLEANSE", "Date Uniformity\nType Mapping\nOutlier Filters", Inches(3.2)),
        ("3. TRANSFORM", "Weekend FFill\nTrading Flags\nDimension Keys", Inches(5.6)),
        ("4. LOAD", "SQLite3 DB\nStar Schema\nForeign Keys", Inches(8.0)),
        ("5. SERVE", "Power BI (.pbix)\nPython Analytics\nJupyter Models", Inches(10.4))
    ]
    for st_title, st_desc, x_pos in stages:
        card = s4.shapes.add_shape(1, x_pos, Inches(1.5), Inches(2.1), Inches(2.0))
        card.fill.solid()
        card.fill.fore_color.rgb = DARK_NAVY
        card.line.color.rgb = ACCENT_BLUE
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = st_title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p.space_after = Pt(8)
        p = tf.add_paragraph()
        p.text = st_desc
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE

    # Technical Innovation Box
    tech_box = s4.shapes.add_shape(1, Inches(0.8), Inches(3.8), Inches(11.7), Inches(2.9))
    tech_box.fill.solid()
    tech_box.fill.fore_color.rgb = CARD_BG
    tech_box.line.color.rgb = RGBColor(226, 232, 240)
    tf = tech_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CRITICAL DATA ENGINEERING SAFEGUARDS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(6)

    safeguards = [
        "• Trading Day Guardrail: Resampled daily NAVs with a forward-fill limit of 4 days, while maintaining an explicit `is_trading_day` boolean. Daily return metrics strictly filter out non-trading days, preventing artificial 0% returns from depressing volatility.",
        "• Robust SQLite Star Schema: Centered on `fact_nav` (64,320 rows) and `fact_transactions` (32,778 rows), linked to `dim_fund` and `dim_date`, optimizing complex SQL window functions down to <120ms.",
        "• Transaction Normalization: Cleaned messy text variations into canonical 'SIP', 'Lumpsum', and 'Redemption' labels."
    ]
    for sg in safeguards:
        p = tf.add_paragraph()
        p.text = sg
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(4)

    # ----------------------------------------------------
    # SLIDE 5: EDA HIGHLIGHTS I - DEMOGRAPHICS & ADOPTION
    # ----------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    create_header(s5, "EDA Highlights I: Demographics & Adoption Dynamics", "Exploratory Analysis", 5)

    img_age = SCRIPT_DIR / 'reports' / 'eda' / '06_age_distribution.png'
    if img_age.exists():
        s5.shapes.add_picture(str(img_age), Inches(0.8), Inches(1.5), width=Inches(6.2))

    # Right Insights Panel
    r_card = s5.shapes.add_shape(1, Inches(7.3), Inches(1.5), Inches(5.2), Inches(5.2))
    r_card.fill.solid()
    r_card.fill.fore_color.rgb = CARD_BG
    r_card.line.color.rgb = RGBColor(226, 232, 240)
    tf = r_card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KEY DEMOGRAPHIC FINDINGS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    insights_5 = [
        "1. Youth Dominance (40.7%): Investors aged 26-35 represent the single largest demographic cohort in India's mutual fund penetration.",
        "2. Urban Foundation (66.7%): Top 30 (T30) cities account for two-thirds of total invested AUM.",
        "3. High-Growth Frontier: Beyond 30 (B30) tier-2/3 cities are growing at 2.4x the rate of metropolitan centers.",
        "4. Digital Native Behavior: Younger investors almost exclusively adopt monthly SIPs via mobile UPI mandates, showing high early participation."
    ]
    for ins in insights_5:
        p = tf.add_paragraph()
        p.text = ins
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(8)

    # ----------------------------------------------------
    # SLIDE 6: EDA HIGHLIGHTS II - RISK-RETURN & SECTORS
    # ----------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    create_header(s6, "EDA Highlights II: Risk-Return Trade-offs & Concentration", "Exploratory Analysis", 6)

    img_scatter = SCRIPT_DIR / 'reports' / 'eda' / '18_risk_return_scatter.png'
    if img_scatter.exists():
        s6.shapes.add_picture(str(img_scatter), Inches(0.8), Inches(1.5), width=Inches(6.2))

    # Right Insights Panel
    r_card6 = s6.shapes.add_shape(1, Inches(7.3), Inches(1.5), Inches(5.2), Inches(5.2))
    r_card6.fill.solid()
    r_card6.fill.fore_color.rgb = CARD_BG
    r_card6.line.color.rgb = RGBColor(226, 232, 240)
    tf = r_card6.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PORTFOLIO & SECTOR DISCOVERIES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)

    insights_6 = [
        "1. Classic Risk-Reward Curve: Higher returns tightly track volatility across broad scheme classifications.",
        "2. Efficiency Outliers: Select schemes (Mirae Asset Large Cap, Kotak Flexicap) deliver top-tier returns with significantly dampened volatility.",
        "3. Dangerous Concentration (High HHI): 72% of equity funds have an HHI > 2,750, driven by an extreme structural overweight in Financial Services (34.5% avg).",
        "4. Inter-Fund Correlation > 0.85: Top 10 equity funds share heavy overlapping bets, offering limited diversification when held together."
    ]
    for ins in insights_6:
        p = tf.add_paragraph()
        p.text = ins
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(8)

    # ----------------------------------------------------
    # SLIDE 7: PERFORMANCE METRICS I - RISK-ADJUSTED FRAMEWORK
    # ----------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    create_header(s7, "Quantitative Performance Framework & Formulas", "Quantitative Modeling", 7)

    # 4 Formula Cards
    f_cards = [
        ("CAGR (Compound Growth)", "CAGR = (NAV_end / NAV_start)^(252 / N) - 1\n• 1Y, 3Y, 5Y trading horizons\n• Annualized on 252 trading days\n• Isolates true multi-year compounding", Inches(0.8), Inches(1.5)),
        ("SHARPE RATIO (Rf = 6.5%)", "Sharpe = (Ann. Return - Rf) / Volatility\n• Benchmark Rf = 6.50% (RBI repo rate)\n• Measures reward per unit of total risk\n• Top quartile funds achieve Sharpe > 1.20", Inches(6.8), Inches(1.5)),
        ("SORTINO (Downside Semi-Dev)", "Sortino = (Ann. Return - Rf) / Downside Dev\n• Only penalizes harmful downside swings\n• Upside volatility is treated as harmless\n• Top funds maintain Sortino > 2.0", Inches(0.8), Inches(4.2)),
        ("MAXIMUM DRAWDOWN (MDD)", "MDD = (NAV_t - Peak_t) / Peak_t\n• Peak-to-trough worst capital decline\n• Directly measures tail risk tolerance\n• Best funds restrict MDD to < -13.0%", Inches(6.8), Inches(4.2))
    ]
    for title, desc, x, y in f_cards:
        card = s7.shapes.add_shape(1, x, y, Inches(5.7), Inches(2.5))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_BLUE
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE
        p.space_after = Pt(6)
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_PRIMARY

    # ----------------------------------------------------
    # SLIDE 8: PERFORMANCE METRICS II - ALPHA & BENCHMARKING
    # ----------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    create_header(s8, "Performance Metrics II: Alpha & Benchmark Tracking", "Benchmarking Analysis", 8)

    img_bench = SCRIPT_DIR / 'benchmark_comparison_chart.png'
    if img_bench.exists():
        s8.shapes.add_picture(str(img_bench), Inches(0.8), Inches(1.5), width=Inches(6.4))

    # Right Insights Panel
    r_card8 = s8.shapes.add_shape(1, Inches(7.5), Inches(1.5), Inches(5.0), Inches(5.2))
    r_card8.fill.solid()
    r_card8.fill.fore_color.rgb = CARD_BG
    r_card8.line.color.rgb = RGBColor(226, 232, 240)
    tf = r_card8.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "BENCHMARK OUTPERFORMANCE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    insights_8 = [
        "1. Active Management Proven: Top 5 Scorecard funds generated significant positive Alpha (+21.2% to +29.3%) vs NIFTY 100.",
        "2. Beta Clustered at 0.95 - 1.05: Outperformance was driven by security selection (Alpha) rather than leveraged market exposure (Beta).",
        "3. Tracking Error Bifurcation: Large cap funds closely hugged the benchmark (TE 2.1% - 3.4%), while midcaps took conviction bets (TE 5.1% - 6.8%).",
        "4. Value at Risk (VaR 95%): Small cap funds display severe 1-day tail risk (-2.85% VaR, -4.12% CVaR), requiring strict allocation limits."
    ]
    for ins in insights_8:
        p = tf.add_paragraph()
        p.text = ins
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_after = Pt(8)

    # ----------------------------------------------------
    # SLIDE 9: DASHBOARD SCREENSHOTS I - OVERVIEW & SCORECARD
    # ----------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    create_header(s9, "Power BI Dashboard: Overview & Scorecard Ranks", "Dashboard Deployment", 9)

    img_d1 = SCRIPT_DIR / 'reports' / 'dashboard' / '01_dashboard_overview.png'
    img_d2 = SCRIPT_DIR / 'reports' / 'dashboard' / '02_dashboard_performance.png'

    if img_d1.exists():
        s9.shapes.add_picture(str(img_d1), Inches(0.8), Inches(1.5), width=Inches(5.7))
    if img_d2.exists():
        s9.shapes.add_picture(str(img_d2), Inches(6.8), Inches(1.5), width=Inches(5.7))

    # Bottom commentary box
    bot_card9 = s9.shapes.add_shape(1, Inches(0.8), Inches(5.1), Inches(11.7), Inches(1.7))
    bot_card9.fill.solid()
    bot_card9.fill.fore_color.rgb = DARK_NAVY
    bot_card9.line.color.rgb = ACCENT_BLUE
    tf = bot_card9.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EXECUTIVE DASHBOARD CAPABILITIES (PAGES 1 & 2)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(4)
    p = tf.add_paragraph()
    p.text = "• Page 1: High-level KPI aggregations (₹81.2L Cr AUM, 40 schemes, ₹31K Cr monthly SIPs) and category breakdown donut.\n• Page 2: 100-Point Composite Fund Scorecard ranking table with interactive category slicers and Sharpe risk-return scatter."
    p.font.size = Pt(9.5)
    p.font.color.rgb = WHITE

    # ----------------------------------------------------
    # SLIDE 10: DASHBOARD SCREENSHOTS II - NAV & DEMOGRAPHICS
    # ----------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    create_header(s10, "Power BI Dashboard: NAV Trajectory & SIP Heatmaps", "Dashboard Deployment", 10)

    img_d3 = SCRIPT_DIR / 'reports' / 'dashboard' / '03_dashboard_nav_benchmark.png'
    img_d4 = SCRIPT_DIR / 'reports' / 'dashboard' / '04_dashboard_sip_demographics.png'

    if img_d3.exists():
        s10.shapes.add_picture(str(img_d3), Inches(0.8), Inches(1.5), width=Inches(5.7))
    if img_d4.exists():
        s10.shapes.add_picture(str(img_d4), Inches(6.8), Inches(1.5), width=Inches(5.7))

    # Bottom commentary box
    bot_card10 = s10.shapes.add_shape(1, Inches(0.8), Inches(5.1), Inches(11.7), Inches(1.7))
    bot_card10.fill.solid()
    bot_card10.fill.fore_color.rgb = DARK_NAVY
    bot_card10.line.color.rgb = ACCENT_GREEN
    tf = bot_card10.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "GRANULAR BEHAVIORAL & TIME-SERIES INTELLIGENCE (PAGES 3 & 4)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(4)
    p = tf.add_paragraph()
    p.text = "• Page 3: Rebased historical time-series comparative view vs NIFTY 50/100, 90-day rolling Sharpe dynamics, and tracking error.\n• Page 4: Investor age distribution, T30 vs B30 geographic penetration, payment modes (UPI 48.2%), and at-risk SIP drop-off alerts."
    p.font.size = Pt(9.5)
    p.font.color.rgb = WHITE

    # ----------------------------------------------------
    # SLIDE 11: KEY FINDINGS & STRATEGIC RECOMMENDATIONS
    # ----------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    create_header(s11, "Key Findings & Strategic Recommendations", "Strategic Synthesis", 11)

    # 3 Column Cards
    col_width = Inches(3.7)
    gap = Inches(0.3)
    
    recs = [
        ("FOR INVESTORS", ACCENT_BLUE, [
            "• Stop chasing 1Y returns; rely on composite Scorecard.",
            "• Diversify away from Banking overweight (HHI > 2,750).",
            "• Transition manual monthly SIPs to automated UPI AutoPay for 26% higher compounding."
        ], Inches(0.8)),
        ("FOR AMCs / FUND HOUSES", ACCENT_GREEN, [
            "• Implement early retention prompts when SIP contribution gaps exceed 35 days (11% of cohort).",
            "• Expand direct plan distribution into B30 tier-2/3 cities.",
            "• Curate differentiated mid/small cap active strategies to avoid closet indexing."
        ], Inches(0.8) + col_width + gap),
        ("FOR BLUESTOCK PLATFORM", RGBColor(234, 88, 12), [
            "• Embed rule-based `recommender.py` engine into the core user onboarding experience.",
            "• Schedule automated mfapi.in ingestion pipeline for live weekday NAV and tracking error updates.",
            "• Add portfolio optimization (Markowitz Efficient Frontier) for multi-scheme rebalancing."
        ], Inches(0.8) + (col_width + gap)*2)
    ]

    for title, col, points, x_pos in recs:
        card = s11.shapes.add_shape(1, x_pos, Inches(1.5), col_width, Inches(5.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = col
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(12)
        for pt in points:
            p = tf.add_paragraph()
            p.text = pt
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(8)

    # ----------------------------------------------------
    # SLIDE 12: THANK YOU & CONCLUSION
    # ----------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = DARK_NAVY
    bg12.line.color.rgb = DARK_NAVY

    tb12 = s12.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    
    p = tf12.paragraphs[0]
    p.text = "BLUESTOCK FINTECH"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf12.add_paragraph()
    p.text = "Thank You"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(12)

    p = tf12.add_paragraph()
    p.text = "Questions & Technical Discussion"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(28)

    p = tf12.add_paragraph()
    p.text = "GitHub Repository: https://github.com/ashwin4087-a11y/mf-analytics-pipeline  (Branch: main | Tag: v1.0)\nDashboard Deployment: bluestock_mf.pbix (Power BI Desktop & Power BI Service)"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(148, 163, 184)

    out_file = SCRIPT_DIR / 'Bluestock_MF_Presentation.pptx'
    prs.save(str(out_file))
    print(f"Successfully generated Bluestock_MF_Presentation.pptx at {out_file} with {len(prs.slides)} slides!")
    return len(prs.slides)

if __name__ == '__main__':
    slide_count = build_presentation()
    print(f"Total Slides Generated: {slide_count}")
