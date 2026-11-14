
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")

required_files = [
    "olist_orders_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
]

print("Checking Olist dataset files...\n")

missing_files = []

for filename in required_files:
    filepath = DATA_DIR / filename

    if filepath.exists():
        print(f"FOUND: {filename}")
    else:
        print(f"MISSING: {filename}")
        missing_files.append(filename)

if missing_files:
    print("\nPlease check the filenames and folder location.")
else:
    print("\nAll four files are available!")

    datasets = {
        "Orders": pd.read_csv(DATA_DIR / "olist_orders_dataset.csv"),
        "Customers": pd.read_csv(DATA_DIR / "olist_customers_dataset.csv"),
        "Order Items": pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv"),
        "Payments": pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv"),
    }

    print("\nDATASET SIZES")

    for name, df in datasets.items():
        print(f"{name}: {df.shape[0]:,} rows, {df.shape[1]} columns")

    print("\nSAMPLE ORDER RECORDS")
    print(datasets["Orders"].head().to_string(index=False))

    print("\nORDER COLUMN NAMES")
    print(datasets["Orders"].columns.tolist())
