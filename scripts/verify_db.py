import sqlite3

conn = sqlite3.connect('data/nifty100.db')
print('companies count:', conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0])
print('PRAGMA foreign_key_check:', conn.execute('PRAGMA foreign_key_check').fetchall())

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('\nTables:')
for t in tables:
    count = conn.execute(f'SELECT COUNT(*) FROM {t[0]}').fetchone()[0]
    print(f'  {t[0]}: {count} rows')

missing = ['ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'WIPRO', 'ZOMATO', 'ZYDUSLIFE']
for t in ['profitandloss', 'balancesheet', 'cashflow', 'financial_ratios']:
    try:
        orphans = conn.execute(f'SELECT COUNT(*) FROM {t} WHERE company_id IN ({",".join("?" for _ in missing)})', missing).fetchone()[0]
        print(f'{t} orphans: {orphans}')
    except Exception as e:
        print(e)
conn.close()
