
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/processed")

# 1. Load datasets
orders = pd.read_csv(
    DATA_DIR / "delivered_orders.csv",
    parse_dates=["order_purchase_timestamp"],
)

customers = pd.read_csv(DATA_DIR / "customers.csv")
items = pd.read_csv(DATA_DIR / "order_items.csv")

print("Loaded datasets successfully.")


# 2. Attach the stable customer identifier
# Use the existing customer_unique_id if present.
# Otherwise, retrieve it from the customer table.

if "customer_unique_id" not in orders.columns:
    orders = orders.merge(
        customers[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

print("Customer identifiers ready.")
print(
    "Unique customers:",
    orders["customer_unique_id"].nunique()
)


print("Customer identifiers merged successfully.")

# 3. Calculate item value at order level
order_value = (
    items.groupby("order_id", as_index=False)
    .agg(order_value=("price", "sum"))
)

# One row per delivered order
orders = orders.merge(
    order_value,
    on="order_id",
    how="left",
    validate="one_to_one",
)

# 4. Check required fields
print("\nMissing values in analysis columns:")
print(
    orders[
        [
            "customer_unique_id",
            "order_purchase_timestamp",
            "order_value",
        ]
    ].isna().sum()
)

orders = orders.dropna(
    subset=[
        "customer_unique_id",
        "order_purchase_timestamp",
        "order_value",
    ]
).copy()

# 5. Define reference date
reference_date = (
    orders["order_purchase_timestamp"].max().normalize()
    + pd.Timedelta(days=1)
)

# 6. Calculate RFM metrics
rfm = (
    orders.groupby("customer_unique_id")
    .agg(
        last_purchase=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("order_value", "sum"),
    )
    .reset_index()
)

rfm["recency"] = (
    reference_date - rfm["last_purchase"]
).dt.days

# 7. Score customers from 1 to 5
# Higher R score = more recent purchase
rfm["R_score"] = pd.qcut(
    rfm["recency"].rank(method="first", ascending=False),
    5,
    labels=[1, 2, 3, 4, 5],
).astype(int)

rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5],
).astype(int)

rfm["M_score"] = pd.qcut(
    rfm["monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5],
).astype(int)

# 8. Create initial customer segments


def assign_segment(row):
    if row["frequency"] >= 2 and row["R_score"] >= 4:
        return "Recent Repeat Customers"

    elif row["frequency"] >= 2 and row["M_score"] >= 4:
        return "Repeat High-Value Customers"

    elif row["frequency"] >= 2:
        return "Other Repeat Customers"

    elif row["R_score"] >= 4 and row["M_score"] >= 4:
        return "Recent High-Value One-Time Customers"

    elif row["R_score"] <= 2:
        return "Lapsed One-Time Customers"

    elif row["M_score"] >= 4:
        return "High-Spend One-Time Customers"

    else:
        return "Other One-Time Customers"



rfm["segment"] = rfm.apply(assign_segment, axis=1)

# 9. Save customer-level results
rfm.to_csv(
    DATA_DIR / "rfm_customer_segments.csv",
    index=False,
)

# 10. Summarize customer segments
segment_summary = (
    rfm.groupby("segment")
    .agg(
        customers=("customer_unique_id", "nunique"),
        total_monetary=("monetary", "sum"),
        average_monetary=("monetary", "mean"),
        average_frequency=("frequency", "mean"),
    )
    .reset_index()
)

segment_summary["customer_percentage"] = (
    segment_summary["customers"] / len(rfm) * 100
).round(2)

segment_summary.to_csv(
    DATA_DIR / "rfm_segment_summary.csv",
    index=False,
)

print("\n========== RFM OVERVIEW ==========")
print("Reference date:", reference_date.date())
print("Customers analyzed:", len(rfm))

print("\n========== RFM SEGMENT SUMMARY ==========")
print(segment_summary.round(2).to_string(index=False))

print("\nRFM ANALYSIS COMPLETE")
print("Saved rfm_customer_segments.csv")
print("Saved rfm_segment_summary.csv")
