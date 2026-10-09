"""Check for duplicate (company_id, year) in P&L and BS."""
import pandas as pd, os

DATA_DIR = 'data'

for fname, hdr in [('profitandloss.xlsx',1),('balancesheet.xlsx',1),('cashflow.xlsx',1)]:
    for f in os.listdir(DATA_DIR):
        if f.endswith(fname):
            df = pd.read_excel(os.path.join(DATA_DIR,f), header=hdr)
            # normalise year just to check raw
            dups = df[df.duplicated(subset=['company_id','year'], keep=False)]
            print(f"{fname}: {len(df)} rows, {len(dups)} dup rows")
            if len(dups) > 0:
                print(dups[['company_id','year']].head(10))
            break
