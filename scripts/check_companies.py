"""Check companies source for NULL face_value rows."""
import pandas as pd
import os

DATA_DIR = 'data'
for f in os.listdir(DATA_DIR):
    if f.endswith('companies.xlsx'):
        src = os.path.join(DATA_DIR, f)
        break

df = pd.read_excel(src, header=1)
print(f"Total rows: {len(df)}")
print(f"NULL face_value rows: {df['face_value'].isna().sum()}")
print(df[df['face_value'].isna()][['id','company_name','face_value']])
print()
print("All face_value values:")
print(df[['id','face_value']].head(20))
