
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/processed")

# Load delivered orders
orders = pd.read_csv(
    DATA_DIR / "delivered_orders.csv",
    parse_dates=["order_purchase_timestamp"],
)

# Remove rows without the information needed for cohort analysis
orders = orders.dropna(
    subset=["customer_unique_id", "order_purchase_timestamp"]
).copy()

# Assign each order to a calendar month
orders["order_month"] = (
    orders["order_purchase_timestamp"].dt.to_period("M")
)

# Find each customer's first delivered purchase month
first_purchase = (
    orders.groupby("customer_unique_id")["order_month"]
    .min()
    .rename("cohort_month")
)

orders = orders.join(
    first_purchase,
    on="customer_unique_id",
)

# Calculate months elapsed since the customer's first purchase
orders["cohort_index"] = (
    (orders["order_month"].dt.year - orders["cohort_month"].dt.year)
    * 12
    + orders["order_month"].dt.month
    - orders["cohort_month"].dt.month
)

# Count each customer only once per cohort and activity month
cohort_data = (
    orders.groupby(
        ["cohort_month", "cohort_index"]
    )["customer_unique_id"]
    .nunique()
    .reset_index(name="active_customers")
)

# Build the cohort count matrix
cohort_counts = cohort_data.pivot(
    index="cohort_month",
    columns="cohort_index",
    values="active_customers",
)

# Cohort size is the number of customers in month 0
cohort_sizes = cohort_counts[0]

# Convert counts into retention percentages
cohort_retention = cohort_counts.div(
    cohort_sizes,
    axis=0,
) * 100

# Format the output for readability
cohort_counts.index = cohort_counts.index.astype(str)
cohort_retention.index = cohort_retention.index.astype(str)

cohort_counts.columns = [
    f"Month_{int(column)}"
    for column in cohort_counts.columns
]

cohort_retention.columns = [
    f"Month_{int(column)}"
    for column in cohort_retention.columns
]

# Save results
cohort_counts.to_csv(DATA_DIR / "cohort_customer_counts.csv")
cohort_retention.to_csv(DATA_DIR / "cohort_retention.csv")

print("\n========== COHORT SIZES ==========")
print(cohort_counts.head(12).to_string())

print("\n========== COHORT RETENTION (%) ==========")
print(cohort_retention.head(12).round(2).to_string())

print("\nSaved cohort_customer_counts.csv")
print("Saved cohort_retention.csv")
print("\nCOHORT ANALYSIS COMPLETE")



import matplotlib.pyplot as plt
import seaborn as sns

# Reload the saved retention matrix
retention = pd.read_csv(
    DATA_DIR / "cohort_retention.csv",
    index_col=0,
)

# Ensure all month columns from Month_0 through Month_20 exist
month_columns = [f"Month_{i}" for i in range(21)]
retention = retention.reindex(columns=month_columns)

# Create a heatmap
plt.figure(figsize=(18, 10))

sns.heatmap(
    retention,
    annot=True,
    fmt=".1f",
    cmap="YlGnBu",
    vmin=0,
    vmax=5,
    linewidths=0.3,
    mask=retention.isna(),
    cbar_kws={"label": "Customer retention (%)"},
)

plt.title("Olist Customer Cohort Retention (Scale: 0-5%)")
plt.xlabel("Months Since First Delivered Purchase")
plt.ylabel("First Purchase Cohort")
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()

# Save chart in the project root
plt.savefig(
    "cohort_retention_heatmap.png",
    dpi=200,
    bbox_inches="tight",
)

plt.show()

print("Saved cohort_retention_heatmap.png")


# VALIDATION: check cohort calculations

print("\n========== COHORT VALIDATION ==========")

# Month 0 should equal the number of customers in each cohort
month_zero = cohort_counts["Month_0"]

print("Cohort sizes:")
print(month_zero.to_string())

# Month 0 retention should be 100%
print("\nMonth 0 retention:")
print(cohort_retention["Month_0"].to_string())

# Verify that every cohort starts at 100%
assert (cohort_retention["Month_0"] == 100).all()

print("\nValidation passed: Month 0 retention is 100%.")

# Check for missing calendar months in the dataset
print(
    "\nPurchase date range:",
    orders["order_purchase_timestamp"].min(),
    "to",
    orders["order_purchase_timestamp"].max(),
)

print("\nCohort validation complete.")
