import pandas as pd
from pathlib import Path
import sys


# ============================================================
# 1. PROJECT PATHS
# ============================================================

# Project root:
# retail-ecommerce-analytics/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset folder
DATASET_DIR = PROJECT_ROOT / "dataset"

# Output folder
OUTPUT_DIR = PROJECT_ROOT / "data"

# Input files
ORDERS_FILE = DATASET_DIR / "orders.csv"
PRODUCTS_FILE = DATASET_DIR / "products.csv"
PRIOR_FILE = DATASET_DIR / "order_products__prior.csv"
TRAIN_FILE = DATASET_DIR / "order_products__train.csv"

# Output file
OUTPUT_FILE = OUTPUT_DIR / "prepared_transactions.csv"


# ============================================================
# 2. CHECK FILES
# ============================================================

print("=" * 60)
print("RETAIL & E-COMMERCE ANALYTICS")
print("DATA PREPROCESSING")
print("=" * 60)

print("\nProject root:")
print(PROJECT_ROOT)

print("\nDataset directory:")
print(DATASET_DIR)

print("\nChecking required files...\n")

required_files = [
    ORDERS_FILE,
    PRODUCTS_FILE,
    PRIOR_FILE,
    TRAIN_FILE
]

for file in required_files:
    print(f"{file.name:<30}", end="")

    if file.exists():
        print("FOUND")
    else:
        print("NOT FOUND")
        print("\nERROR: Required file is missing:")
        print(file)
        sys.exit(1)


# ============================================================
# 3. CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\nOutput directory:")
print(OUTPUT_DIR)


# ============================================================
# 4. LOAD ORDERS
# ============================================================

print("\n" + "=" * 60)
print("STEP 1: Loading orders.csv")
print("=" * 60)

orders = pd.read_csv(
    ORDERS_FILE,
    usecols=[
        "order_id",
        "order_dow",
        "order_hour_of_day"
    ]
)

print(f"Orders loaded: {len(orders):,}")


# ============================================================
# 5. LOAD PRODUCTS
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: Loading products.csv")
print("=" * 60)

products = pd.read_csv(
    PRODUCTS_FILE,
    usecols=[
        "product_id",
        "product_name"
    ]
)

print(f"Products loaded: {len(products):,}")


# ============================================================
# 6. CREATE PRODUCT LOOKUP
# ============================================================

product_lookup = products.set_index(
    "product_id"
)["product_name"]


# ============================================================
# 7. PROCESS TRANSACTION FILE
# ============================================================

def process_transactions(input_file, output_file, write_header=False):

    print("\n" + "=" * 60)
    print(f"PROCESSING: {input_file.name}")
    print("=" * 60)

    # Read large CSV in chunks
    chunk_size = 100_000

    total_rows = 0
    chunk_number = 0

    # Read CSV chunk by chunk
    for chunk in pd.read_csv(
        input_file,
        chunksize=chunk_size
    ):

        chunk_number += 1

        print(
            f"Processing chunk {chunk_number} "
            f"({len(chunk):,} rows)..."
        )

        # ----------------------------------------------------
        # Merge with orders
        # ----------------------------------------------------

        chunk = chunk.merge(
            orders,
            on="order_id",
            how="left"
        )

        # ----------------------------------------------------
        # Add product name
        # ----------------------------------------------------

        chunk["product_name"] = chunk["product_id"].map(
            product_lookup
        )

        # ----------------------------------------------------
        # Each row represents one purchased product
        # ----------------------------------------------------

        chunk["quantity"] = 1

        # ----------------------------------------------------
        # Create simulated event timestamp
        # ----------------------------------------------------

        #
        # Instacart does not provide an exact transaction
        # timestamp.
        #
        # It provides:
        #
        # order_dow
        # order_hour_of_day
        #
        # We use these to create a simulated timestamp.
        #

        base_date = pd.Timestamp("2026-09-21")

        chunk["event_time"] = (
            base_date
            + pd.to_timedelta(
                chunk["order_dow"],
                unit="D"
            )
            + pd.to_timedelta(
                chunk["order_hour_of_day"],
                unit="h"
            )
            + pd.to_timedelta(
                chunk["order_id"] % 60,
                unit="s"
            )
        )

        # ----------------------------------------------------
        # Select required columns
        # ----------------------------------------------------

        result = chunk[
            [
                "event_time",
                "order_id",
                "product_id",
                "product_name",
                "quantity"
            ]
        ]

        # ----------------------------------------------------
        # Write to output CSV
        # ----------------------------------------------------

        result.to_csv(
            output_file,
            mode="w" if write_header and chunk_number == 1 else "a",
            header=write_header and chunk_number == 1,
            index=False
        )

        total_rows += len(result)

        print(
            f"Total processed so far: "
            f"{total_rows:,}"
        )

    print(f"\nFinished {input_file.name}")
    print(f"Rows processed: {total_rows:,}")

    return total_rows


# ============================================================
# 8. DELETE OLD OUTPUT FILE
# ============================================================

if OUTPUT_FILE.exists():

    print("\nExisting output file found.")

    print("Deleting old prepared_transactions.csv...")

    OUTPUT_FILE.unlink()


# ============================================================
# 9. PROCESS PRIOR DATA
# ============================================================

prior_rows = process_transactions(
    PRIOR_FILE,
    OUTPUT_FILE,
    write_header=True
)


# ============================================================
# 10. PROCESS TRAIN DATA
# ============================================================

train_rows = process_transactions(
    TRAIN_FILE,
    OUTPUT_FILE,
    write_header=False
)


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

total_rows = prior_rows + train_rows

print("\n")
print("=" * 60)
print("PREPROCESSING COMPLETE")
print("=" * 60)

print(f"Prior transactions : {prior_rows:,}")
print(f"Train transactions : {train_rows:,}")
print(f"Total transactions : {total_rows:,}")

print("\nOutput file:")

print(OUTPUT_FILE)

print("\nFile exists:", OUTPUT_FILE.exists())

if OUTPUT_FILE.exists():

    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)

    print(
        f"Output file size: "
        f"{file_size_mb:.2f} MB"
    )

print("\n" + "=" * 60)
print("NEXT STEP")
print("=" * 60)

print(
    "The prepared transaction data is now ready "
    "to be streamed into Kafka."
)