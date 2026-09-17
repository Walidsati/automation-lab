#!/usr/bin/env python3
"""Read data from a Google Sheet, compute a summary, write it back."""

import os
from pathlib import Path

from dotenv import load_dotenv

from sheets_client import get_sheets_service

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SHEET_ID = os.environ["TEST_SHEET_ID"]


def main():
    service = get_sheets_service()
    sheets = service.spreadsheets()

    # ---- 1. Read the data ----
    result = sheets.values().get(
        spreadsheetId=SHEET_ID,
        range="A1:C5",
    ).execute()
    rows = result.get("values", [])

    # ---- 2. Compute total ----
    data_rows = rows[1:]  # skip header
    amounts = [int(row[1]) for row in data_rows]
    total = sum(amounts)
    count = len(amounts)
    average = round(total / count, 2) if count else 0

    print(f"Total:   {total}")
    print(f"Count:   {count}")
    print(f"Average: {average}")

    # ---- 3. Write the summary back to E1:F3 ----
    summary = [
        ["Total", total],
        ["Count", count],
        ["Average", average],
    ]
    sheets.values().update(
        spreadsheetId=SHEET_ID,
        range="E1",
        valueInputOption="USER_ENTERED",
        body={"values": summary},
    ).execute()

    print(f"\nSummary written to E1:F3 in the sheet.")


if __name__ == "__main__":
    main()
