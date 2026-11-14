
from pathlib import Path
import pandas as pd

# Project folders
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load original data
orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")

print("STEP 1: INITIAL DATA QUALITY")

datasets = {
    "orders": orders,
    "customers": customers,
    "items": items,
    "payments": payments,
}

for name, df in datasets.items():
    print(f"\n{name.upper()}")
    print("Duplicate rows:", df.duplicated().sum())
    print("Missing values by column:")
    print(df.isnull().sum()[lambda x: x > 0])

# Convert order date columns
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column], errors="coerce"
    )

print("\nSTEP 2: DATE VALIDATION")
print(orders[date_columns].dtypes)

# Check for invalid date sequences
invalid_dates = orders[
    (orders["order_delivered_customer_date"].notna())
    & (
        orders["order_delivered_customer_date"]
        < orders["order_purchase_timestamp"]
    )
]

print(
    "\nOrders delivered before purchase timestamp:",
    len(invalid_dates),
)

# Prepare the delivered-order dataset
delivered_orders = orders[
    orders["order_status"] == "delivered"
].copy()

# Attach the stable customer identifier
delivered_orders = delivered_orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id",
    how="left",
    validate="many_to_one",
)

# Keep records with valid purchase dates and customer IDs
analysis_orders = delivered_orders.dropna(
    subset=["order_purchase_timestamp", "customer_unique_id"]
).copy()

# Add purchase month for cohort analysis
analysis_orders["purchase_month"] = (
    analysis_orders["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)

# Save processed datasets
analysis_orders.to_csv(
    PROCESSED_DIR / "delivered_orders.csv",
    index=False,
)

customers.to_csv(
    PROCESSED_DIR / "customers.csv",
    index=False,
)

items.to_csv(
    PROCESSED_DIR / "order_items.csv",
    index=False,
)

payments.to_csv(
    PROCESSED_DIR / "payments.csv",
    index=False,
)

print("\nSTEP 3: ANALYSIS DATASET")
print("Delivered orders:", len(delivered_orders))
print("Valid analysis orders:", len(analysis_orders))
print(
    "Unique customers:",
    analysis_orders["customer_unique_id"].nunique(),
)
print(
    "Unique orders:",
    analysis_orders["order_id"].nunique(),
)

print("\nSTEP 4: FILES SAVED")
for file in PROCESSED_DIR.glob("*.csv"):
    print(file)

print("\nDATA PREPARATION COMPLETE")
