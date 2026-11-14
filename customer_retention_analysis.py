
from pathlib import Path
import pandas as pd

# Load the prepared dataset
DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/processed")

orders = pd.read_csv(
    DATA_DIR / "delivered_orders.csv",
    parse_dates=["order_purchase_timestamp"],
)

print("========== CUSTOMER RETENTION ANALYSIS ==========")

# 1. Count delivered orders per unique customer
customer_orders = (
    orders.groupby("customer_unique_id")
    .agg(
        total_orders=("order_id", "nunique"),
        first_purchase=("order_purchase_timestamp", "min"),
        last_purchase=("order_purchase_timestamp", "max"),
    )
    .reset_index()
)

# 2. Classify customers by purchase frequency
customer_orders["customer_type"] = customer_orders[
    "total_orders"
].apply(
    lambda count: "Repeat Customer"
    if count >= 2
    else "One-Time Customer"
)

# 3. Calculate baseline metrics
total_customers = customer_orders["customer_unique_id"].nunique()
total_orders = orders["order_id"].nunique()

repeat_customers = (
    customer_orders["total_orders"] >= 2
).sum()

one_time_customers = (
    customer_orders["total_orders"] == 1
).sum()

repeat_customer_rate = (
    repeat_customers / total_customers * 100
    if total_customers else 0
)

orders_from_repeat_customers = customer_orders.loc[
    customer_orders["total_orders"] >= 2,
    "total_orders"
].sum()

repeat_order_share = (
    orders_from_repeat_customers / total_orders * 100
    if total_orders else 0
)

# 4. Display results
print(f"\nTotal delivered orders: {total_orders:,}")
print(f"Unique purchasing customers: {total_customers:,}")
print(f"Repeat customers: {repeat_customers:,}")
print(f"One-time customers: {one_time_customers:,}")
print(f"Repeat customer rate: {repeat_customer_rate:.2f}%")
print(
    "Orders from repeat customers:",
    f"{orders_from_repeat_customers:,}",
)
print(f"Repeat-customer order share: {repeat_order_share:.2f}%")

# 5. Customer frequency distribution
print("\n========== PURCHASE FREQUENCY ==========")

frequency = (
    customer_orders["total_orders"]
    .value_counts()
    .sort_index()
)

print(frequency.head(10).to_string())

# 6. Save customer-level analysis
customer_orders.to_csv(
    OUTPUT_DIR / "customer_purchase_summary.csv",
    index=False,
)

# Save key metrics for documentation
metrics = pd.DataFrame({
    "metric": [
        "total_delivered_orders",
        "unique_customers",
        "repeat_customers",
        "one_time_customers",
        "repeat_customer_rate_pct",
        "orders_from_repeat_customers",
        "repeat_customer_order_share_pct",
    ],
    "value": [
        total_orders,
        total_customers,
        int(repeat_customers),
        int(one_time_customers),
        round(repeat_customer_rate, 2),
        int(orders_from_repeat_customers),
        round(repeat_order_share, 2),
    ],
})

metrics.to_csv(
    OUTPUT_DIR / "customer_retention_metrics.csv",
    index=False,
)

print("\nSaved customer_purchase_summary.csv")
print("Saved customer_retention_metrics.csv")
print("\nANALYSIS COMPLETE")
