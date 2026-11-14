
from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("ecommerce.db")
SQL_PATH = Path("sql/01_customer_retention.sql")

sql_text = SQL_PATH.read_text(encoding="utf-8")

# Split the file into individual SQL statements
statements = [
    statement.strip()
    for statement in sql_text.split(";")
    if statement.strip()
]

with sqlite3.connect(DB_PATH) as conn:
    for number, statement in enumerate(statements, start=1):
        print(f"\n========== QUERY {number} ==========")

        result = pd.read_sql_query(statement, conn)
        if number == 8:
           print("Saving cohort results...")
           output_path = Path("data/processed/sql_cohort_retention.csv")
           result.to_csv(output_path, index=False)
           print(f"Saved cohort results to {output_path}")
        print(result.to_string(index=False))

print("\nSQL ANALYSIS COMPLETE")
