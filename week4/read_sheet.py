#!/usr/bin/env python3
"""Read data from a Google Sheet and print it."""

import os
from pathlib import Path

from dotenv import load_dotenv

from sheets_client import get_sheets_service

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SHEET_ID = os.environ["TEST_SHEET_ID"]


def main():
    service = get_sheets_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="A1:C5",
    ).execute()

    rows = result.get("values", [])
    print(f"Fetched {len(rows)} rows\n")

    for i, row in enumerate(rows):
        print(f"Row {i}: {row}")


if __name__ == "__main__":
    main()
