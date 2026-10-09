"""Day 1 verification: check DB tables, constraints, row counts."""
import sqlite3

conn = sqlite3.connect('data/nifty100.db')

# All tables
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print('=== TABLES ===')
for (name,) in tables:
    cnt = conn.execute(f'SELECT COUNT(*) FROM [{name}]').fetchone()[0]
    print(f'  {name}: {cnt} rows')

print()

# Schema check - PK/FK for each table
print('=== CONSTRAINTS ===')
for (name,) in tables:
    pks = [r for r in conn.execute(f'PRAGMA table_info([{name}])').fetchall() if r[5] > 0]
    fks = conn.execute(f'PRAGMA foreign_key_list([{name}])').fetchall()
    print(f'  {name}: PKs={[p[1] for p in pks]}, FKs={len(fks)}')

# financial_ratios check
count_orig = 1161
count_new = conn.execute('SELECT COUNT(*) FROM financial_ratios').fetchone()[0]
print()
print('=== financial_ratios PRESERVATION ===')
print(f'  Backup (original)   : {count_orig}')
print(f'  New DB              : {count_new}')
print(f'  Difference          : {count_new - count_orig}')
print(f'  Status              : {"OK" if count_new == count_orig else "MISMATCH"}')

conn.close()
