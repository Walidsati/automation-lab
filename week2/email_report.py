#!/usr/bin/env python3
"""Email the sales report PDF with an inline HTML summary (Jinja2)."""

import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
INPUT = DATA_DIR / "sales.csv"
PDF_PATH = DATA_DIR / "sales_report.pdf"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

load_dotenv(ROOT / ".env")


def _get_secrets():
    return (
        os.environ["GMAIL_USER"],
        os.environ["GMAIL_APP_PASSWORD"],
        os.environ["EMAIL_TO"],
    )


def build_summary_html(df) -> str:
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    total_revenue = float(df["revenue"].sum())
    total_units = int(df["units"].sum())

    by_region = (
        df.groupby("region")
        .agg(units=("units", "sum"), revenue=("revenue", "sum"))
        .round(2)
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
    by_month = (
        df.groupby(df["date"].dt.strftime("%Y-%m"))
        .agg(units=("units", "sum"), revenue=("revenue", "sum"))
        .round(2)
        .reset_index()
        .rename(columns={"date": "month"})
    )
    best_region = by_region.iloc[0]["region"]

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    template = env.get_template("email.html")

    return template.render(
        title="Sales Report",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        total_revenue=total_revenue,
        total_units=total_units,
        best_region=best_region,
        regions=by_region.to_dict("records"),
        months=by_month.to_dict("records"),
    )


def build_plain_text(df) -> str:
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    total_revenue = float(df["revenue"].sum())
    total_units = int(df["units"].sum())
    return (
        f"Sales Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Total revenue: ${total_revenue:,.2f}\n"
        f"Total units: {total_units:,}\n\n"
        f"Full report attached as PDF.\n"
    )


def send_report_email(pdf_path: Path = None) -> None:
    """Send the report email. Uses given PDF path or default. Reusable."""
    pdf_path = pdf_path or PDF_PATH
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}. Run pdf_report.py first.")

    gmail_user, gmail_password, email_to = _get_secrets()

    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"])

    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = email_to
    msg["Subject"] = f"Sales Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    msg.set_content(build_plain_text(df))
    msg.add_alternative(build_summary_html(df), subtype="html")

    pdf_bytes = pdf_path.read_bytes()
    msg.add_attachment(
        pdf_bytes, maintype="application", subtype="pdf", filename=pdf_path.name,
    )

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.starttls(context=context)
        smtp.login(gmail_user, gmail_password)
        smtp.send_message(msg)

    print(f"Email sent to {email_to}")
    print(f"Attachment: {pdf_path.name} ({len(pdf_bytes) / 1024:.1f} KB)")


def main():
    send_report_email()


if __name__ == "__main__":
    main()
