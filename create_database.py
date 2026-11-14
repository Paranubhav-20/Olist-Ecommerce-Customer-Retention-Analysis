
from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "ecommerce.db"

# Load the processed CSV files into SQLite
tables = {
    "delivered_orders": "delivered_orders.csv",
    "customers": "customers.csv",
    "order_items": "order_items.csv",
    "payments": "payments.csv",
    "rfm_customer_segments": "rfm_customer_segments.csv",
}

with sqlite3.connect(DB_PATH) as conn:
    for table_name, filename in tables.items():
        file_path = DATA_DIR / filename

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
        )

        print(
            f"Loaded {table_name}: "
            f"{len(df):,} rows, {len(df.columns)} columns"
        )

    print("\nTables created successfully.")

    # Confirm the tables exist
    result = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """,
        conn,
    )

    print("\nDATABASE TABLES")
    print(result.to_string(index=False))

print(f"\nDatabase saved at: {DB_PATH.resolve()}")
