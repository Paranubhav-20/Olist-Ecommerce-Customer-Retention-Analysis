
from pathlib import Path
import pandas as pd

# 1. Load the datasets
DATA_DIR = Path("data/raw")

orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")

datasets = {
    "Orders": orders,
    "Customers": customers,
    "Order Items": items,
    "Payments": payments
}

# 2. Dataset overview
print("\n========== DATASET OVERVIEW ==========")

for name, df in datasets.items():
    print(f"\n{name}")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Duplicate full rows:", df.duplicated().sum())

# 3. Missing-value analysis
print("\n========== MISSING VALUES ==========")

for name, df in datasets.items():
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print(f"\n{name}")
    if missing.empty:
        print("No missing values found.")
    else:
        print(missing.to_string())

# 4. Data types
print("\n========== DATA TYPES: ORDERS ==========")
print(orders.dtypes)

# 5. Order status distribution
print("\n========== ORDER STATUS ==========")
print(orders["order_status"].value_counts(dropna=False))

# 6. Key relationship checks
print("\n========== RELATIONSHIP CHECKS ==========")

print(
    "Unique order IDs in orders:",
    orders["order_id"].nunique()
)

print(
    "Unique customer IDs in customer table:",
    customers["customer_id"].nunique()
)

print(
    "Unique customer IDs in orders:",
    orders["customer_id"].nunique()
)

print(
    "Orders without a matching customer record:",
    (~orders["customer_id"].isin(customers["customer_id"])).sum()
)

print(
    "Order items without a matching order:",
    (~items["order_id"].isin(orders["order_id"])).sum()
)

print(
    "Payments without a matching order:",
    (~payments["order_id"].isin(orders["order_id"])).sum()
)

# 7. Check customer identity
print("\n========== CUSTOMER IDENTITY ==========")

print(
    "Customer records:",
    len(customers)
)

print(
    "Unique customer_unique_id values:",
    customers["customer_unique_id"].nunique()
)

print(
    "Orders with missing customer IDs:",
    orders["customer_id"].isnull().sum()
)

print("\n========== QUALITY CHECK COMPLETE ==========")
