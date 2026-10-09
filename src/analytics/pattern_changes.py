import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def generate_pattern_changes():
    ca_path = os.path.join(OUTPUT_DIR, 'capital_allocation.csv')
    if not os.path.exists(ca_path):
        print(f"capital_allocation.csv not found at {ca_path}")
        return

    df = pd.read_csv(ca_path)
    
    # We expect columns like company_id, year, pattern_label
    if 'year' not in df.columns or 'pattern_label' not in df.columns:
        print("Required columns missing in capital_allocation.csv")
        return
        
    df = df.sort_values(by=['company_id', 'year'])
    
    changes = []
    
    for cid, group in df.groupby('company_id'):
        for i in range(1, len(group)):
            prev_row = group.iloc[i-1]
            curr_row = group.iloc[i]
            
            # Identify YoY change. E.g. if previous year is 2022 and current is 2023
            # We don't fabricate missing years. If there's a gap, it's still the consecutive available year
            if curr_row['pattern_label'] != prev_row['pattern_label']:
                changes.append({
                    'company_id': cid,
                    'previous_year': prev_row['year'],
                    'current_year': curr_row['year'],
                    'previous_pattern': prev_row['pattern_label'],
                    'current_pattern': curr_row['pattern_label']
                })
                
    df_changes = pd.DataFrame(changes)
    
    out_path = os.path.join(OUTPUT_DIR, 'pattern_changes.csv')
    df_changes.to_csv(out_path, index=False)
    print(f"Pattern changes generated: {out_path} with {len(df_changes)} changes")

if __name__ == '__main__':
    generate_pattern_changes()
