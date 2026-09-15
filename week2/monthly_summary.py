#!/usr/bin/env python3
"""Monthly revenue by region — summary CSV."""

from pathlib import Path
import pandas as pd
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT = SCRIPT_DIR / "data" / "sales.csv"
OUTPUT = SCRIPT_DIR / "data" / "monthly_by_region.csv"

def main():
    # 1. Load
    df = pd.read_csv(INPUT)
    # 2. Date parsing
    df["date"] = pd.to_datetime(df["date"])
    # 3. Revenue
    df["revenue"] = df["units"] * df["unit_price"]
    # 4. Month
    df["month"] = df["date"].dt.strftime("%Y-%m")
    # 5. Group by month + region
    grouped = df.groupby(["month", "region"])["revenue"].sum()
    # 6. Pivot
    pivoted = grouped.unstack(fill_value=0).round(2)
    # 7. Print
    print(pivoted.round(2).to_string(float_format=lambda x: f"{x:,.2f}"))

    # 8. Save
    pivoted.to_csv(OUTPUT, float_format="%.2f")
    print(f"\nSaved to {OUTPUT}")
if __name__ == "__main__":
    main()
