# Bluestock Mutual Fund Analytics

## Project Overview
The Bluestock Mutual Fund Analytics Capstone is a comprehensive, end-to-end data pipeline and analytics solution. It transforms fragmented, raw mutual fund data into a highly structured database, upon which extensive quantitative analysis, risk modelling, and interactive dashboards are built.

## Objectives
1. Design and deploy an automated ETL pipeline.
2. Build an optimized SQLite Star Schema database.
3. Conduct deep Exploratory Data Analysis (EDA) on mutual fund market trends.
4. Calculate rigorous performance and risk metrics (Sharpe, Alpha, VaR).
5. Build an interactive Power BI dashboard for intuitive data exploration.

## Dataset Description
The project integrates 10 core datasets containing historical financial and demographic data:
- **Fund Master**: Static details of the 40 analyzed schemes.
- **NAV Historical**: Daily Net Asset Value (NAV) spanning multiple years.
- **Benchmark Indices**: NIFTY 50 and NIFTY 100 daily closing values.
- **AUM**: Monthly Assets Under Management per fund.
- **SIP Inflows**: Monthly systemic investment plan volumes.
- **Category Returns**: Broad mutual fund category performance metrics.
- **Folio Data**: Count of investor accounts (folios).
- **Transactions**: Investor-level transaction logs (SIP vs Lumpsum).
- **Holdings**: Sectoral and equity allocations per fund.
- **Investors**: Demographic data (age, gender, income, city tier).

## Project Architecture
1. **Extraction**: Raw CSVs are ingested via Python (`pandas`).
2. **Transformation**: Missing values are imputed, NAV dates are standardized, and data is structured into Fact and Dimension models.
3. **Loading**: Data is persisted into `bluestock_mf.db`.
4. **Analytics**: Jupyter notebooks calculate advanced metrics and export results.
5. **Visualization**: Power BI connects to the structured outputs for interactive reporting.

## Repository Structure
```
bluestock_mf_capstone/
├── data/                  # Raw and processed datasets
├── dashboard/             # Power BI dashboard (.pbix)
├── notebooks/             # Jupyter notebooks for EDA and Analytics
├── scripts/               # Python ETL and modeling scripts
├── sql/                   # SQL schemas and queries
├── reports/               # Final PDF report and PPTX presentation
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

## Installation
Ensure you have Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/bluestock/mutual-fund-analytics.git
cd mutual-fund-analytics

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Pipeline
A master execution script is provided to document and run the pipeline:
```bash
python run_pipeline.py
```
*Note: The pipeline guards against overwriting the compiled SQLite database if it already exists to save computation time.*

## Data Cleaning
Handled via `clean_and_load.py`. Non-trading days in the NAV dataset were meticulously handled by forward-filling prices but flagging them to avoid artificial 0% returns during volatility calculations.

## EDA
Located in `run_eda.py` and `EDA_Analysis.ipynb`. Analyzes demographic spreads, AUM dominance, and sector allocations using `matplotlib` and `seaborn`.

## Performance Analytics
Calculates 1/3/5-year CAGR, Sharpe Ratios (6.5% Rf), Sortino Ratios, Alpha, Beta, and Maximum Drawdown. A composite 0-100 Scorecard ranks all 40 funds.

## Advanced Analytics
Located in `Advanced_Analytics.ipynb`. Features:
- Historical VaR (95%) & CVaR
- 90-Day Rolling Sharpe Ratio
- Investor Cohort Behavioral Analysis
- SIP Continuity Modeling
- Sector Herfindahl-Hirschman Index (HHI)

## Dashboard
The interactive Power BI dashboard is located at `dashboard/bluestock_mf.pbix`. 
To view it, open the file using **Power BI Desktop**. It features 4 pages: Overview, Fund Performance, NAV Details, and SIP & Market Trends, complete with dynamic slicers.

## Key Findings
1. Top funds exhibit significant sector concentration risk (High HHI in Banking).
2. The `26-35` age demographic dominates mutual fund adoption.
3. Earlier investor cohorts have significantly higher lifetime invested capital.
4. Top active funds successfully generated positive Alpha against the NIFTY 100 over a 3-year horizon.

## Deliverables
- ETL pipeline (`clean_and_load.py`)
- SQLite schema/database (`schema.sql`)
- EDA notebook & charts (`reports/eda/`)
- Performance analytics (`Performance_Analytics.ipynb`, `fund_scorecard.csv`)
- Advanced analytics (`Advanced_Analytics.ipynb`, `recommender.py`)
- Power BI dashboard (`dashboard/bluestock_mf.pbix`)
- Final report (`Final_Report.pdf`)
- Presentation (`Bluestock_MF_Presentation.pptx`)

## Limitations
- Alpha and Beta are computed strictly against the broad NIFTY 100 index, rather than category-specific benchmarks.
- The 6.5% Risk-Free Rate is assumed constant historically.
- Limited multi-decade historical data restricts 5-year CAGR computation for newer funds.

## Team
- Rajesh
- Ashwin Perumal SR
- Aditya Gupta
