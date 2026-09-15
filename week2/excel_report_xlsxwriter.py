#!/usr/bin/env python3
"""Generate a formatted Excel report from sales.csv — using xlsxwriter."""

from pathlib import Path
import pandas as pd
import xlsxwriter

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT = SCRIPT_DIR / "data" / "sales.csv"
OUTPUT = SCRIPT_DIR / "data" / "sales_report_xw.xlsx"


def build_formats(wb):
    """Create all reusable formats once."""
    return {
        "header": wb.add_format({
            "bold": True, "font_color": "white", "bg_color": "#4472C4",
            "align": "center", "valign": "vcenter", "border": 1, "border_color": "#BFBFBF",
        }),
        "text": wb.add_format({
            "border": 1, "border_color": "#BFBFBF", "valign": "vcenter",
        }),
        "int": wb.add_format({
            "num_format": "#,##0", "border": 1, "border_color": "#BFBFBF",
        }),
        "money": wb.add_format({
            "num_format": "$#,##0.00", "border": 1, "border_color": "#BFBFBF",
        }),
        "date": wb.add_format({
            "num_format": "yyyy-mm-dd", "border": 1, "border_color": "#BFBFBF",
        }),
        "total": wb.add_format({
            "bold": True, "bg_color": "#FFF2CC",
            "border": 1, "border_color": "#BFBFBF",
        }),
        "total_money": wb.add_format({
            "bold": True, "bg_color": "#FFF2CC", "num_format": "$#,##0.00",
            "border": 1, "border_color": "#BFBFBF",
        }),
        "best": wb.add_format({
            "bg_color": "#C6EFCE", "border": 1, "border_color": "#BFBFBF",
        }),
        "best_money": wb.add_format({
            "bg_color": "#C6EFCE", "num_format": "$#,##0.00",
            "border": 1, "border_color": "#BFBFBF",
        }),
    }


def write_table(ws, df, formats, money_cols=(), date_cols=(), start_row=0):
    """Write DataFrame to worksheet with styled header + typed cells."""
    # Header
    for col_idx, col_name in enumerate(df.columns):
        ws.write(start_row, col_idx, col_name, formats["header"])

    # Data
    for row_idx, (_, row) in enumerate(df.iterrows(), start=start_row + 1):
        for col_idx, col_name in enumerate(df.columns):
            value = row[col_name]
            if col_name in money_cols:
                fmt = formats["money"]
            elif col_name in date_cols:
                fmt = formats["date"]
            elif isinstance(value, (int,)) and not isinstance(value, bool):
                fmt = formats["int"]
            else:
                fmt = formats["text"]
            ws.write(row_idx, col_idx, value, fmt)

    return start_row + 1 + len(df)   # first empty row after table


def main():
    # Load + prep
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

    by_region = (
        df.groupby("region")
        .agg(units=("units", "sum"), revenue=("revenue", "sum"))
        .round(2)
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
    by_month = (
        df.groupby("month")
        .agg(units=("units", "sum"), revenue=("revenue", "sum"))
        .round(2)
        .reset_index()
    )

    # Workbook
    wb = xlsxwriter.Workbook(OUTPUT)
    formats = build_formats(wb)

    # ---- Sheet 1: Raw Data ----
    ws1 = wb.add_worksheet("Raw Data")
    ws1.freeze_panes(1, 0)  # freeze header row
    raw = df[["date", "region", "product", "units", "unit_price", "revenue"]]
    write_table(ws1, raw, formats, money_cols=["unit_price", "revenue"], date_cols=["date"])
    ws1.set_column(0, 0, 12)   # date
    ws1.set_column(1, 1, 10)   # region
    ws1.set_column(2, 2, 12)   # product
    ws1.set_column(3, 3, 10)   # units
    ws1.set_column(4, 5, 14)   # unit_price, revenue

    # ---- Sheet 2: By Region ----
    ws2 = wb.add_worksheet("By Region")
    next_row = write_table(ws2, by_region, formats, money_cols=["revenue"])

    # Total row
    ws2.write(next_row, 0, "TOTAL", formats["total"])
    ws2.write(next_row, 1, int(by_region["units"].sum()), formats["total"])
    ws2.write(next_row, 2, float(by_region["revenue"].sum()), formats["total_money"])

    ws2.set_column(0, 0, 12)
    ws2.set_column(1, 2, 14)

    # ---- Sheet 3: By Month ----
    ws3 = wb.add_worksheet("By Month")
    best_revenue = float(by_month["revenue"].max())

    # Header
    for col_idx, col_name in enumerate(by_month.columns):
        ws3.write(0, col_idx, col_name, formats["header"])

    # Rows with conditional "best" format
    for row_idx, (_, row) in enumerate(by_month.iterrows(), start=1):
        is_best = abs(float(row["revenue"]) - best_revenue) < 0.001
        month_fmt = formats["best"] if is_best else formats["text"]
        units_fmt = formats["best"] if is_best else formats["int"]
        money_fmt = formats["best_money"] if is_best else formats["money"]
        ws3.write(row_idx, 0, row["month"], month_fmt)
        ws3.write(row_idx, 1, int(row["units"]), units_fmt)
        ws3.write(row_idx, 2, float(row["revenue"]), money_fmt)

    ws3.set_column(0, 0, 12)
    ws3.set_column(1, 2, 14)

    wb.close()
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
