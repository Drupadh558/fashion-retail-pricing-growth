import os
import sqlite3
import pandas as pd
import numpy as np

# 1. Load raw dataset
RAW_PATH = os.path.join("data", "myntra_dataset_ByScraping.csv")
df = pd.read_csv(RAW_PATH)

print(f"Loaded raw rows: {len(df)}")

# 2. Standardize column names cleanly
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Map columns dynamically based on standard schema
col_map = {}
for c in df.columns:
    if "brand" in c:
        col_map[c] = "brand"
    elif "pant" in c or "product" in c or "name" in c or "desc" in c:
        col_map[c] = "product_name"
    elif "price" in c and "mrp" not in c and "original" not in c:
        col_map[c] = "selling_price"
    elif "mrp" in c or "original" in c:
        col_map[c] = "mrp"
    elif "discount" in c:
        col_map[c] = "discount"
    elif "rating" in c and "count" not in c and "number" not in c:
        col_map[c] = "rating"
    elif "number" in c or "count" in c:
        col_map[c] = "rating_count"

df = df.rename(columns=col_map)

# 3. Data Cleaning (Remove duplicates & fix scraping outliers)
df = df.drop_duplicates().copy()
df["brand"] = df["brand"].astype(str).str.strip().str.title()
df["product_name"] = df["product_name"].astype(str).str.strip()

for col in ["selling_price", "mrp", "discount", "rating", "rating_count"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["brand", "selling_price", "mrp"])
df = df[(df["selling_price"] > 0) & (df["mrp"] >= df["selling_price"])]

# Fix discount anomalies (e.g., 17.8 scraping glitch) and recalculate accurately
df["discount_pct"] = np.round(((df["mrp"] - df["selling_price"]) / df["mrp"]) * 100, 1)
df["rating"] = df["rating"].fillna(0).clip(0, 5)
df["rating_count"] = df["rating_count"].fillna(0).astype(int)

# 4. Feature Engineering for Business Functions
# Price Tier (Category Management)
df["price_tier"] = pd.cut(
    df["selling_price"],
    bins=[0, 799, 1799, 100000],
    labels=["Budget (<800)", "Mid-Range (800-1799)", "Premium (1800+)"]
)

# Discount Bucket (Demand & Pricing Management)
df["discount_band"] = pd.cut(
    df["discount_pct"],
    bins=[-1, 20, 40, 60, 100],
    labels=["0-20% (Low)", "20-40% (Moderate)", "40-60% (Sweet Spot)", "60%+ (Deep Discount)"]
)

# Demand & Revenue Proxy (Data Analytics)
df["estimated_revenue_proxy"] = df["selling_price"] * df["rating_count"]

# Ad-Monetization Opportunity Flag (Ads & Brand Growth)
low_traffic_cutoff = df["rating_count"].quantile(0.35)
df["ad_pitch_target"] = np.where(
    (df["rating"] >= 4.2) & (df["rating_count"] <= max(low_traffic_cutoff, 25)) & (df["rating_count"] > 0),
    "High Potential (Pitch Ads)",
    "Standard"
)

# 5. Save cleaned CSV and SQLite Database
CLEAN_CSV = os.path.join("data", "cleaned_retail_data.csv")
DB_PATH = os.path.join("data", "retail_analytics.db")

df.to_csv(CLEAN_CSV, index=False)

conn = sqlite3.connect(DB_PATH)
df.to_sql("products", conn, if_exists="replace", index=False)
conn.close()

print(f"Cleaned rows saved: {len(df)}")
print(f"Saved CSV to {CLEAN_CSV} and SQLite DB to {DB_PATH}")