#!/usr/bin/env python3
"""Email the sales report PDF with an inline HTML summary."""

import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ---- Paths ----
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
INPUT = DATA_DIR / "sales.csv"
PDF_PATH = DATA_DIR / "sales_report.pdf"

# ---- Load secrets from .env ----
load_dotenv(ROOT / ".env")

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


def build_summary_html(df):
    """Return an HTML string summarizing the sales data."""
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)

    total_revenue = df["revenue"].sum()
    total_units = df["units"].sum()
    best_region_row = (
        df.groupby("region")["revenue"].sum().sort_values(ascending=False).index[0]
    )

    # By region table rows
    by_region = (
        df.groupby("region")
        .agg(units=("units", "sum"), revenue=("revenue", "sum"))
        .round(2)
        .sort_values("revenue", ascending=False)
        .reset_index()
    )

    region_rows = "\n".join(
        f"<tr>"
        f"<td style='padding:6px 12px;border-bottom:1px solid #eee;'>{r['region']}</td>"
        f"<td style='padding:6px 12px;border-bottom:1px solid #eee;text-align:right;'>{int(r['units']):,}</td>"
        f"<td style='padding:6px 12px;border-bottom:1px solid #eee;text-align:right;'>${r['revenue']:,.2f}</td>"
        f"</tr>"
        for _, r in by_region.iterrows()
    )

    html = f"""
    <html>
      <body style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#222;">
        <h2 style="color:#4472C4;margin-bottom:4px;">Sales Report</h2>
        <p style="color:#666;margin-top:0;">
          Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>

        <table style="border-collapse:collapse;background:#f2f2f2;padding:12px;border-radius:6px;">
          <tr>
            <td style="padding:6px 18px 6px 6px;color:#555;">Total revenue</td>
            <td style="padding:6px 6px;font-weight:600;">${total_revenue:,.2f}</td>
          </tr>
          <tr>
            <td style="padding:6px 18px 6px 6px;color:#555;">Total units</td>
            <td style="padding:6px 6px;font-weight:600;">{total_units:,}</td>
          </tr>
          <tr>
            <td style="padding:6px 18px 6px 6px;color:#555;">Best region</td>
            <td style="padding:6px 6px;font-weight:600;">{best_region_row}</td>
          </tr>
        </table>

        <h3 style="color:#4472C4;margin-top:24px;">Revenue by Region</h3>
        <table style="border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="background:#4472C4;color:white;">
              <th style="padding:8px 12px;text-align:left;">Region</th>
              <th style="padding:8px 12px;text-align:right;">Units</th>
              <th style="padding:8px 12px;text-align:right;">Revenue</th>
            </tr>
          </thead>
          <tbody>
            {region_rows}
          </tbody>
        </table>

        <p style="margin-top:24px;color:#666;font-size:13px;">
          Full report with charts is attached as a PDF.
        </p>
      </body>
    </html>
    """
    return html


def build_plain_text(df):
    """Simple plaintext fallback for email clients that don't render HTML."""
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    total_revenue = df["revenue"].sum()
    total_units = df["units"].sum()
    return (
        f"Sales Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Total revenue: ${total_revenue:,.2f}\n"
        f"Total units: {total_units:,}\n\n"
        f"Full report attached as PDF.\n"
    )


def main():
    # Read data for the summary
    df = pd.read_csv(INPUT)

    # Build the message
    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"Sales Report — {datetime.now().strftime('%Y-%m-%d')}"

    # Plain text first, then HTML alternative
    msg.set_content(build_plain_text(df))
    msg.add_alternative(build_summary_html(df), subtype="html")

    # Attach the PDF
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}. Run pdf_report.py first.")
    pdf_bytes = PDF_PATH.read_bytes()
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=PDF_PATH.name,
    )

    # Send
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.starttls(context=context)
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    print(f"Email sent to {EMAIL_TO}")
    print(f"Attachment: {PDF_PATH.name} ({len(pdf_bytes) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

