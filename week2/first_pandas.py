#!/usr/bin/env python3
"""First look at pandas for automation."""

from pathlib import Path
import pandas as pd

# Location-independent paths
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "data" / "sales.csv"

# Load
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")

# Peek
print("\nFirst 3 rows:")
print(df.head(3))

# Add a computed column: revenue
df["revenue"] = df["units"] * df["unit_price"]
print("\nFirst 3 rows with revenue:")
print(df.head(3)[["date", "region", "product", "units", "unit_price", "revenue"]])

# Quick stats
print(f"\nTotal revenue: ${df['revenue'].sum():,.2f}")
print(f"Total units: {df['units'].sum():,}")

# Group by region
print("\nRevenue by region:")
print(df.groupby("region")["revenue"].sum().sort_values(ascending=False))

# Group by product
print("\nRevenue by product:")
print(df.groupby("product")["revenue"].sum().sort_values(ascending=False))
