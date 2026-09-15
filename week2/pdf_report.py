#!/usr/bin/env python3
"""Generate a PDF sales report using reportlab + matplotlib."""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
)

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
INPUT = DATA_DIR / "sales.csv"
CHART_PATH = DATA_DIR / "sales_by_region.png"
OUTPUT = DATA_DIR / "sales_report.pdf"

BRAND_BLUE = colors.HexColor("#4472C4")
LIGHT_GRAY = colors.HexColor("#F2F2F2")
DARK_GRAY = colors.HexColor("#595959")
YELLOW = colors.HexColor("#FFF2CC")


def make_region_chart(df, out_path):
    by_region = df.groupby("region")["revenue"].sum().sort_values().round(2)
    fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
    bars = ax.barh(by_region.index, by_region.values, color="#4472C4")
    ax.set_xlabel("Revenue ($)")
    ax.set_title("Revenue by Region", fontsize=12, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    for bar, val in zip(bars, by_region.values):
        ax.text(val + 100, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def build_pdf(df, by_region, by_month, chart_path, out_path):
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Sales Report", author="Automation Lab",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"],
        textColor=BRAND_BLUE, fontSize=22, spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        textColor=DARK_GRAY, fontSize=11, spaceAfter=18,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        textColor=BRAND_BLUE, spaceBefore=14, spaceAfter=8,
    )

    story = []
    from datetime import datetime, timezone
    story.append(Paragraph("Sales Report", title_style))
    story.append(Paragraph(
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        subtitle_style,
    ))

    total_revenue = df["revenue"].sum()
    total_units = df["units"].sum()
    best_region = by_region.iloc[0]["region"]

    summary_table = Table(
        [["Total revenue", f"${total_revenue:,.2f}"],
         ["Total units", f"{total_units:,}"],
         ["Best region", best_region],
         ["Records", f"{len(df):,}"]],
        colWidths=[5 * cm, 5 * cm],
    )
    summary_table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK_GRAY),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.gray),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)

    story.append(Paragraph("Revenue by Region", h2_style))
    story.append(Image(str(chart_path), width=16 * cm, height=8 * cm))

    story.append(Paragraph("Region Breakdown", h2_style))
    region_data = [["Region", "Units", "Revenue"]]
    for _, row in by_region.iterrows():
        region_data.append([
            row["region"],
            f"{int(row['units']):,}",
            f"${row['revenue']:,.2f}",
        ])
    region_data.append([
        "TOTAL",
        f"{int(by_region['units'].sum()):,}",
        f"${by_region['revenue'].sum():,.2f}",
    ])
    region_table = Table(region_data, colWidths=[6 * cm, 4 * cm, 6 * cm], hAlign="LEFT")
    region_table.setStyle(_table_style_with_total(len(region_data)))
    story.append(region_table)

    story.append(Paragraph("Month Breakdown", h2_style))
    month_data = [["Month", "Units", "Revenue"]]
    for _, row in by_month.iterrows():
        month_data.append([
            row["month"],
            f"{int(row['units']):,}",
            f"${row['revenue']:,.2f}",
        ])
    month_table = Table(month_data, colWidths=[6 * cm, 4 * cm, 6 * cm], hAlign="LEFT")
    month_table.setStyle(_table_style_with_total(-1))
    story.append(month_table)

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)


def _table_style_with_total(num_rows):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, num_rows - 1), (-1, num_rows - 1), YELLOW),
        ("FONT", (0, num_rows - 1), (-1, num_rows - 1), "Helvetica-Bold", 9),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.gray),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK_GRAY)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"Sales Report — Page {canvas.getPageNumber()}")
    canvas.restoreState()


def generate_pdf_report() -> Path:
    """Full PDF pipeline. Returns output path. Reusable."""
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    df["month"] = df["date"].dt.strftime("%Y-%m")

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

    make_region_chart(df, CHART_PATH)
    build_pdf(df, by_region, by_month, CHART_PATH, OUTPUT)
    return OUTPUT


def main():
    out = generate_pdf_report()
    print(f"PDF saved: {out}")


if __name__ == "__main__":
    main()
