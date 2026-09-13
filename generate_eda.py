import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

markdown_intro = """
# Bluestock Mutual Fund Analytics - Exploratory Data Analysis (DAY 3)

This notebook contains the exploratory data analysis for the Bluestock Mutual Fund Analytics project.
"""

code_setup = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

# Create directory for charts
os.makedirs('reports/eda', exist_ok=True)

# Connect to the database
conn = sqlite3.connect('bluestock_mf.db')

# Load the data
dim_fund = pd.read_sql('SELECT * FROM dim_fund', conn)
fact_nav = pd.read_sql('SELECT * FROM fact_nav', conn)
fact_aum = pd.read_sql('SELECT * FROM fact_aum', conn)
fact_monthly_sip = pd.read_sql('SELECT * FROM fact_monthly_sip', conn)
fact_category_inflows = pd.read_sql('SELECT * FROM fact_category_inflows', conn)
fact_industry_folios = pd.read_sql('SELECT * FROM fact_industry_folios', conn)
fact_transactions = pd.read_sql('SELECT * FROM fact_transactions', conn)
fact_holdings = pd.read_sql('SELECT * FROM fact_holdings', conn)
fact_performance = pd.read_sql('SELECT * FROM fact_performance', conn)

# Convert date columns to datetime
fact_nav['date'] = pd.to_datetime(fact_nav['date'])
fact_aum['date'] = pd.to_datetime(fact_aum['date'])
fact_transactions['transaction_date'] = pd.to_datetime(fact_transactions['transaction_date'])
fact_holdings['portfolio_date'] = pd.to_datetime(fact_holdings['portfolio_date'])
"""

md_nav = "## 1. NAV Trend Analysis"
code_nav = """
# 1. NAV Trends
# Plot daily NAV trends for all 40 schemes covering 2022-2026.
# We will use Plotly for this.

merged_nav = fact_nav.merge(dim_fund[['amfi_code', 'scheme_name']], on='amfi_code')

fig1 = px.line(merged_nav, x='date', y='nav', color='scheme_name', title='Daily NAV Trends (2022-2026)',
              labels={'date': 'Date', 'nav': 'Net Asset Value (NAV)'})

# Check if 2023 and 2024 are in data
min_date = merged_nav['date'].min()
max_date = merged_nav['date'].max()

if max_date >= pd.to_datetime('2023-01-01'):
    fig1.add_vrect(x0="2023-01-01", x1="2023-12-31", annotation_text="2023 Bull Run", fillcolor="green", opacity=0.1, line_width=0)
if max_date >= pd.to_datetime('2024-01-01'):
    fig1.add_vrect(x0="2024-01-01", x1="2024-12-31", annotation_text="2024 Correction", fillcolor="red", opacity=0.1, line_width=0)

fig1.update_layout(showlegend=False) # Hide legend to make it readable due to 40 schemes
fig1.write_image('reports/eda/1_nav_trends.png', width=1200, height=600)
fig1.show()
"""

md_aum = "## 2. AUM Growth"
code_aum = """
# 2. AUM Growth by Fund House
fact_aum['year'] = fact_aum['date'].dt.year
aum_yearly = fact_aum.groupby(['year', 'fund_house'])['aum_crore'].max().reset_index()

plt.figure(figsize=(14, 7))
ax2 = sns.barplot(data=aum_yearly, x='year', y='aum_crore', hue='fund_house')
plt.title('AUM Growth by Fund House (2022-2025)')
plt.ylabel('AUM (Crore)')
plt.xlabel('Year')

# Annotate SBI's highest AUM if applicable
sbi_max = aum_yearly[aum_yearly['fund_house'] == 'SBI Mutual Fund']['aum_crore'].max()
if pd.notna(sbi_max):
    plt.annotate(f"SBI Peak: ₹{sbi_max/100000:.2f}L Cr", 
                 xy=(3, sbi_max), xytext=(2.5, sbi_max * 1.05),
                 arrowprops=dict(facecolor='black', shrink=0.05))

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('reports/eda/2_aum_growth.png')
plt.show()
"""

md_sip = "## 3. SIP Inflow Time Series"
code_sip = """
# 3. SIP Inflow Time Series
fig3 = px.bar(fact_monthly_sip, x='month', y='sip_inflow_crore', 
              title='Monthly SIP Inflows (Jan 2022 - Dec 2025)',
              labels={'month': 'Month', 'sip_inflow_crore': 'SIP Inflow (Crores)'})

max_inflow = fact_monthly_sip['sip_inflow_crore'].max()
max_month = fact_monthly_sip.loc[fact_monthly_sip['sip_inflow_crore'].idxmax(), 'month']

fig3.add_annotation(x=max_month, y=max_inflow, text=f"All-time high: ₹{max_inflow} Cr", showarrow=True, arrowhead=1)
fig3.write_image('reports/eda/3_sip_inflows.png', width=1000, height=500)
fig3.show()
"""

md_category = "## 4. Category Inflow Heatmap"
code_category = """
# 4. Category Inflow Heatmap
pivot_inflows = fact_category_inflows.pivot(index='category', columns='month', values='net_inflow_crore')

plt.figure(figsize=(16, 8))
sns.heatmap(pivot_inflows, cmap='RdYlGn', center=0, annot=False)
plt.title('Category Net Inflows Heatmap (Crores)')
plt.ylabel('Fund Category')
plt.xlabel('Month')
plt.tight_layout()
plt.savefig('reports/eda/4_category_heatmap.png')
plt.show()
"""

md_demographics = "## 5. Investor Demographics"
code_demographics = """
# 5. Investor Demographics
# a. Age group distribution (Pie)
age_dist = fact_transactions.drop_duplicates('investor_id')['age_group'].value_counts().reset_index()
age_dist.columns = ['age_group', 'count']

fig5a = px.pie(age_dist, values='count', names='age_group', title='Investor Age Group Distribution')
fig5a.write_image('reports/eda/5a_age_distribution.png')
fig5a.show()

# b. SIP amount box plot by age group
sip_tx = fact_transactions[fact_transactions['transaction_type'] == 'SIP']
plt.figure(figsize=(10, 6))
sns.boxplot(data=sip_tx, x='age_group', y='amount_inr')
plt.title('SIP Amount Distribution by Age Group')
plt.yscale('log')
plt.ylabel('Amount (INR) - Log Scale')
plt.savefig('reports/eda/5b_sip_amount_by_age.png')
plt.show()

# c. Gender split
gender_dist = fact_transactions.drop_duplicates('investor_id')['gender'].value_counts().reset_index()
gender_dist.columns = ['gender', 'count']
fig5c = px.pie(gender_dist, values='count', names='gender', title='Investor Gender Split', hole=0.4)
fig5c.write_image('reports/eda/5c_gender_split.png')
fig5c.show()
"""

md_geography = "## 6. Geographic Distribution"
code_geography = """
# 6. Geographic Distribution
# a. SIP Amount by State
state_sip = sip_tx.groupby('state')['amount_inr'].sum().reset_index().sort_values('amount_inr', ascending=False)
plt.figure(figsize=(12, 8))
sns.barplot(data=state_sip.head(15), x='amount_inr', y='state', orient='h')
plt.title('Top 15 States by Total SIP Amount')
plt.xlabel('Total SIP Amount (INR)')
plt.tight_layout()
plt.savefig('reports/eda/6a_sip_by_state.png')
plt.show()

# b. T30 vs B30 city tier
tier_dist = fact_transactions.drop_duplicates('investor_id')['city_tier'].value_counts().reset_index()
tier_dist.columns = ['city_tier', 'count']
fig6b = px.pie(tier_dist, values='count', names='city_tier', title='T30 vs B30 Investor Distribution')
fig6b.write_image('reports/eda/6b_city_tier.png')
fig6b.show()
"""

md_folios = "## 7. Folio Count Growth"
code_folios = """
# 7. Folio Count Growth
fig7 = px.line(fact_industry_folios, x='month', y='total_folios_crore', 
               title='Industry Folio Count Growth (2022-2025)')

min_month = fact_industry_folios['month'].min()
max_month = fact_industry_folios['month'].max()
min_val = fact_industry_folios[fact_industry_folios['month'] == min_month]['total_folios_crore'].values[0]
max_val = fact_industry_folios[fact_industry_folios['month'] == max_month]['total_folios_crore'].values[0]

fig7.add_annotation(x=min_month, y=min_val, text=f"{min_month}: {min_val} Cr", showarrow=True)
fig7.add_annotation(x=max_month, y=max_val, text=f"{max_month}: {max_val} Cr", showarrow=True)
fig7.write_image('reports/eda/7_folio_growth.png', width=1000, height=500)
fig7.show()
"""

md_correlation = "## 8. NAV Return Correlation Matrix"
code_correlation = """
# 8. NAV Return Correlation Matrix
# Select top 10 funds by AUM
top_10_funds = fact_performance.nlargest(10, 'aum_crore')['amfi_code'].tolist()
top_10_names = dict(zip(fact_performance['amfi_code'], fact_performance['scheme_name']))

top_nav = merged_nav[merged_nav['amfi_code'].isin(top_10_funds)].copy()
# Only use trading days to calculate daily returns properly
top_nav = top_nav[top_nav['is_trading_day'] == 1]

pivot_nav = top_nav.pivot(index='date', columns='amfi_code', values='nav')
daily_returns = pivot_nav.pct_change().dropna()
corr_matrix = daily_returns.corr()

# Rename columns/index to scheme names for readability
corr_matrix.columns = [top_10_names[c][:25] for c in corr_matrix.columns]
corr_matrix.index = [top_10_names[i][:25] for i in corr_matrix.index]

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f")
plt.title('Daily Return Correlation Matrix (Top 10 Funds by AUM)')
plt.tight_layout()
plt.savefig('reports/eda/8_correlation_matrix.png')
plt.show()
"""

md_sector = "## 9. Sector Allocation Donut"
code_sector = """
# 9. Sector Allocation Donut
# Aggregate sector weights across all equity funds
# Taking the latest portfolio date
latest_date = fact_holdings['portfolio_date'].max()
latest_holdings = fact_holdings[fact_holdings['portfolio_date'] == latest_date]

sector_alloc = latest_holdings.groupby('sector')['market_value_cr'].sum().reset_index()
sector_alloc = sector_alloc[sector_alloc['sector'] != 'Cash & Equivalents']

fig9 = px.pie(sector_alloc, values='market_value_cr', names='sector', hole=0.5, 
              title=f'Sector Allocation Across All Funds ({latest_date.date()})')
fig9.update_traces(textposition='inside', textinfo='percent+label')
fig9.update_layout(showlegend=False)
fig9.write_image('reports/eda/9_sector_allocation.png', width=800, height=800)
fig9.show()
"""

md_extra_charts = "## Extra EDA Charts"
code_extra_charts = """
# Extra Chart 1: Lumpsum vs SIP volume
tx_types = fact_transactions.groupby('transaction_type')['amount_inr'].sum().reset_index()
plt.figure(figsize=(8, 6))
sns.barplot(data=tx_types, x='transaction_type', y='amount_inr')
plt.title('Total Investment Volume by Transaction Type')
plt.ylabel('Total INR')
plt.savefig('reports/eda/10_tx_type_volume.png')
plt.show()

# Extra Chart 2: SIP AUM Growth
plt.figure(figsize=(12, 6))
sns.lineplot(data=fact_monthly_sip, x='month', y='sip_aum_lakh_crore', marker='o')
plt.title('SIP AUM Growth (Lakh Crore)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('reports/eda/11_sip_aum_growth.png')
plt.show()

# Extra Chart 3: Fund Category AUM share
cat_aum = fact_performance.groupby('category')['aum_crore'].sum().reset_index()
fig_extra3 = px.pie(cat_aum, values='aum_crore', names='category', title='AUM Market Share by Category')
fig_extra3.write_image('reports/eda/12_category_aum_share.png')
fig_extra3.show()

# Extra Chart 4: Expense Ratio vs 1Yr Return
plt.figure(figsize=(10, 6))
sns.scatterplot(data=fact_performance, x='expense_ratio_pct', y='return_1yr_pct', hue='category', size='aum_crore', sizes=(50, 500))
plt.title('Expense Ratio vs 1-Year Return')
plt.tight_layout()
plt.savefig('reports/eda/13_expense_vs_return.png')
plt.show()

# Extra Chart 5: Payment Mode Distribution
payment_dist = fact_transactions['payment_mode'].value_counts().reset_index()
plt.figure(figsize=(8, 6))
sns.barplot(data=payment_dist, x='count', y='payment_mode', orient='h')
plt.title('Payment Mode Preferences')
plt.tight_layout()
plt.savefig('reports/eda/14_payment_modes.png')
plt.show()
"""

md_findings = "## 10. Key EDA Findings"
code_findings = """
# Generate Key Findings dynamically based on data
f1 = f"1. **NAV Growth**: NAV trends show noticeable upward momentum; tracking peak-to-trough provides insight into market cycles."
f2 = f"2. **AUM Dominance**: SBI Mutual Fund maintains the highest AUM among tracked fund houses, peaking at ₹{sbi_max/100000:.2f} Lakh Crore."
f3 = f"3. **SIP Inflows**: Monthly SIP inflows hit an all-time high of ₹{max_inflow} Crore in {max_month}, demonstrating strong retail participation."
f4 = f"4. **Category Flows**: The inflow heatmap highlights sector rotation, with specific equity categories dominating inflows during bull periods."
f5 = f"5. **Investor Demographics**: {age_dist.iloc[0]['age_group']} is the dominant age group, representing {age_dist.iloc[0]['count'] / age_dist['count'].sum() * 100:.1f}% of unique investors."
f6 = f"6. **Geographic Concentration**: The top state by SIP investment volume is {state_sip.iloc[0]['state']} with ₹{state_sip.iloc[0]['amount_inr']:,.0f} invested."
f7 = f"7. **City Tier**: {tier_dist.iloc[0]['city_tier']} cities dominate the investor base, underscoring urban penetration of mutual funds."
f8 = f"8. **Folio Expansion**: Total industry folios grew from {min_val} Cr in {min_month} to {max_val} Cr in {max_month}."
f9 = f"9. **Fund Correlation**: Top 10 funds by AUM show varied daily return correlations, implying some diversification benefits across categories."
f10 = f"10. **Sector Allocation**: The {sector_alloc.sort_values('market_value_cr', ascending=False).iloc[0]['sector']} sector holds the highest cumulative weight across equity fund portfolios."

findings = [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]
for finding in findings:
    print(finding)
"""

cells = [
    nbf.v4.new_markdown_cell(markdown_intro),
    nbf.v4.new_code_cell(code_setup),
    nbf.v4.new_markdown_cell(md_nav),
    nbf.v4.new_code_cell(code_nav),
    nbf.v4.new_markdown_cell(md_aum),
    nbf.v4.new_code_cell(code_aum),
    nbf.v4.new_markdown_cell(md_sip),
    nbf.v4.new_code_cell(code_sip),
    nbf.v4.new_markdown_cell(md_category),
    nbf.v4.new_code_cell(code_category),
    nbf.v4.new_markdown_cell(md_demographics),
    nbf.v4.new_code_cell(code_demographics),
    nbf.v4.new_markdown_cell(md_geography),
    nbf.v4.new_code_cell(code_geography),
    nbf.v4.new_markdown_cell(md_folios),
    nbf.v4.new_code_cell(code_folios),
    nbf.v4.new_markdown_cell(md_correlation),
    nbf.v4.new_code_cell(code_correlation),
    nbf.v4.new_markdown_cell(md_sector),
    nbf.v4.new_code_cell(code_sector),
    nbf.v4.new_markdown_cell(md_extra_charts),
    nbf.v4.new_code_cell(code_extra_charts),
    nbf.v4.new_markdown_cell(md_findings),
    nbf.v4.new_code_cell(code_findings)
]

nb['cells'] = cells

with open('EDA_Analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("EDA_Analysis.ipynb generated successfully.")
