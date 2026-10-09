"""Diagnose FK violations in financial_ratios — find which company_ids are orphaned."""
import sqlite3

conn = sqlite3.connect('data/nifty100.db')
conn.execute("PRAGMA foreign_keys = ON")

violations = conn.execute("PRAGMA foreign_key_check").fetchall()
print(f"Total FK violations: {len(violations)}")

# Get all distinct orphaned company_ids
orphan_rows = conn.execute("""
    SELECT DISTINCT fr.company_id, COUNT(*) as cnt
    FROM financial_ratios fr
    LEFT JOIN companies c ON fr.company_id = c.id
    WHERE c.id IS NULL
    GROUP BY fr.company_id
""").fetchall()

print(f"\nOrphaned company_ids in financial_ratios ({len(orphan_rows)}):")
for row in orphan_rows:
    print(f"  {row[0]}: {row[1]} rows")

# Check if these are in the financial_ratios.xlsx source
print("\nCompanies in DB:")
companies = conn.execute("SELECT id FROM companies").fetchall()
print(f"  Count: {len(companies)}")

conn.close()
