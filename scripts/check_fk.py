"""Find P&L company_ids that don't exist in companies table."""
import pandas as pd, os

DATA_DIR = 'data'

# Load companies
for f in os.listdir(DATA_DIR):
    if f.endswith('companies.xlsx'):
        companies_df = pd.read_excel(os.path.join(DATA_DIR, f), header=1)
        break

company_ids = set(companies_df['id'].str.strip().str.upper())
print(f"Companies: {len(company_ids)}")

# Check P&L
for f in os.listdir(DATA_DIR):
    if f.endswith('profitandloss.xlsx'):
        pl_df = pd.read_excel(os.path.join(DATA_DIR, f), header=1)
        break

pl_ids = set(pl_df['company_id'].str.strip().str.upper().unique())
orphans = pl_ids - company_ids
print(f"\nP&L company_ids NOT in companies ({len(orphans)}): {sorted(orphans)}")
print(f"P&L company_ids total unique: {len(pl_ids)}")
