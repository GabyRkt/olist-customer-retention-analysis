import os
import kagglehub
import pandas as pd
import pandas_gbq
from pathlib import Path

# Configuration 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/gcp-key.json"

PROJECT_ID = "portfolio-olist-496116"
DATASET_ID = "olist_raw"

# Tables to load (filename → BigQuery table name) 
TABLES = {
    "olist_customers_dataset.csv":           "customers",
    "olist_orders_dataset.csv":              "orders",
    "olist_order_items_dataset.csv":         "order_items",
    "olist_order_payments_dataset.csv":      "order_payments",
    "olist_order_reviews_dataset.csv":       "order_reviews",
    "olist_products_dataset.csv":            "products",
    "olist_sellers_dataset.csv":             "sellers",
    "olist_geolocation_dataset.csv":         "geolocation",
    "product_category_name_translation.csv": "product_category_translation",
}

def clean_column_names(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.replace(r'[^a-z0-9_]', '', regex=True)
    )
    return df

def load_table(df, table_name):
    table_ref = f"{DATASET_ID}.{table_name}"
    try:
        pandas_gbq.to_gbq(
            df,
            destination_table=table_ref,
            project_id=PROJECT_ID,
            if_exists="replace",
            progress_bar=True,
        )
        print(f"  Success: {len(df):,} rows loaded into {table_name}")
    except Exception as e:
        print(f"  Error on {table_name}: {e}")

# Download dataset from Kaggle
print("Downloading Olist dataset from Kaggle...")
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
print(f"Downloaded to: {path}\n")

# Load & push each table 
for filename, table_name in TABLES.items():
    filepath = Path(path) / filename

    if not filepath.exists():
        print(f"  WARNING: {filename} not found, skipping.")
        continue

    print(f"Loading {filename}...")
    df = pd.read_csv(filepath, low_memory=False)
    df = clean_column_names(df)
    print(f"  Columns: {list(df.columns)}")
    load_table(df, table_name)

print("\nAll tables loaded successfully.")