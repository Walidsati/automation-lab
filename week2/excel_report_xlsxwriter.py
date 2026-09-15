#!/usr/bin/env python3
"""Generate a formatted Excel report from sales.csv — using xlsxwriter."""

from pathlib import Path
import pandas as pd
import xlsxwriter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
INPUT = DATA_DIR / "sales.csv"
OUTPUT = DATA_DIR / "sales_report_xw.xlsx"


def build_formats(wb):
    return {
        "header": wb.add_format({
            "bold": True, "font_color": "white", "bg_color": "#4472C4",
            "align": "center", "valign": "vcenter",
            "border": 1, "border_color": "#BFBFBF",
        }),
        "text": wb.add_format({"border": 1, "border_color": "#BFBFBF"}),
        "int": wb.add_format({"num_format": "#,##0", "border": 1, "border_color": "#BFBFBF"}),
        "money": wb.add_format({"num_format": "$#,##0.00", "border": 1, "border_color": "#BFBFBF"}),
        "date": wb.add_format({"num_format": "yyyy-mm-dd", "border": 1, "border_color": "#BFBFBF"}),
        "total": wb.add_format({"bold": True, "bg_color": "#FFF2CC", "border": 1, "border_color": "#BFBFBF"}),
        "total_money": wb.add_format({
            "bold": True, "bg_color": "#FFF2CC", "num_format": "$#,##0.00",
            "border": 1, "border_color": "#BFBFBF",
        }),
        "best": wb.add_format({"bg_color": "#C6EFCE", "border": 1, "border_color": "#BFBFBF"}),
        "best_money": wb.add_format({
            "bg_color": "#C6EFCE", "num_format": "$#,##0.00",
            "border": 1, "border_color": "#BFBFBF",
        }),
    }


def write_table(ws, df, formats, money_cols=(), date_cols=(), start_row=0):
    for col_idx, col_name in enumerate(df.columns):
        ws.write(start_row, col_idx, col_name, formats["header"])
    for row_idx, (_, row) in enumerate(df.iterrows(), start=start_row + 1):
        for col_idx, col_name in enumerate(df.columns):
            value = row[col_name]
            if col_name in money_cols:
                fmt = formats["money"]
            elif col_name in date_cols:
                fmt = formats["date"]
            elif isinstance(value, int) and not isinstance(value, bool):
                fmt = formats["int"]
            else:
                fmt = formats["text"]
            ws.write(row_idx, col_idx, value, fmt)
    return start_row + 1 + len(df)


def generate_excel_report() -> Path:
    """Full Excel pipeline. Returns output path. Reusable."""
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

    wb = xlsxwriter.Workbook(OUTPUT)
    formats = build_formats(wb)

    # Raw Data
    ws1 = wb.add_worksheet("Raw Data")
    ws1.freeze_panes(1, 0)
    raw = df[["date", "region", "product", "units", "unit_price", "revenue"]]
    write_table(ws1, raw, formats, money_cols=["unit_price", "revenue"], date_cols=["date"])
    ws1.set_column(0, 0, 12)
    ws1.set_column(1, 1, 10)
    ws1.set_column(2, 2, 12)
    ws1.set_column(3, 3, 10)
    ws1.set_column(4, 5, 14)

    # By Region
    ws2 = wb.add_worksheet("By Region")
    next_row = write_table(ws2, by_region, formats, money_cols=["revenue"])
    ws2.write(next_row, 0, "TOTAL", formats["total"])
    ws2.write(next_row, 1, int(by_region["units"].sum()), formats["total"])
    ws2.write(next_row, 2, float(by_region["revenue"].sum()), formats["total_money"])
    ws2.set_column(0, 0, 12)
    ws2.set_column(1, 2, 14)

    # By Month
    ws3 = wb.add_worksheet("By Month")
    best_revenue = float(by_month["revenue"].max())
    for col_idx, col_name in enumerate(by_month.columns):
        ws3.write(0, col_idx, col_name, formats["header"])
    for row_idx, (_, row) in enumerate(by_month.iterrows(), start=1):
        is_best = abs(float(row["revenue"]) - best_revenue) < 0.001
        ws3.write(row_idx, 0, row["month"], formats["best"] if is_best else formats["text"])
        ws3.write(row_idx, 1, int(row["units"]), formats["best"] if is_best else formats["int"])
        ws3.write(row_idx, 2, float(row["revenue"]), formats["best_money"] if is_best else formats["money"])
    ws3.set_column(0, 0, 12)
    ws3.set_column(1, 2, 14)

    wb.close()
    return OUTPUT


def main():
    out = generate_excel_report()
    print(f"Excel saved: {out}")


if __name__ == "__main__":
    main()
