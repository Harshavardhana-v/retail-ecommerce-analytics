import pandas as pd
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input files
top20_file = PROJECT_ROOT / "mapreduce" / "top20_ids.txt"
products_file = PROJECT_ROOT / "dataset" / "products.csv"

# Output
output_file = PROJECT_ROOT / "data" / "top20_products.csv"

# Read Top 20 MapReduce result
top20 = pd.read_csv(
    top20_file,
    sep=r"\s+",
    header=None,
    names=["product_id", "units_sold"]
)

# Read product information
products = pd.read_csv(
    products_file,
    usecols=["product_id", "product_name"]
)

# Convert IDs to same type
top20["product_id"] = top20["product_id"].astype(int)
products["product_id"] = products["product_id"].astype(int)

# Join product IDs with product names
result = top20.merge(
    products,
    on="product_id",
    how="left"
)

# Arrange columns
result = result[
    ["product_id", "product_name", "units_sold"]
]

# Save
result.to_csv(
    output_file,
    index=False
)

print("\nTop 20 Products:")
print(result.to_string(index=False))

print(f"\nSaved to: {output_file}")