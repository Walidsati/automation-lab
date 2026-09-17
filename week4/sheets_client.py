#!/usr/bin/env python3
"""Reusable Google Sheets client with OAuth2 flow.

Usage:
    from sheets_client import get_sheets_service

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId="...", range="A1:C10"
    ).execute()
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ---- Paths ----
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
CLIENT_SECRET_FILE = ROOT / "client_secret.json"
TOKEN_FILE = ROOT / "token.json"

# Scopes — read + write Sheets, and Drive access for creating files
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def get_credentials() -> Credentials:
    """Get valid credentials, running OAuth flow if needed."""

    creds = None

    # Reuse existing token if present
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # If no valid token, run the flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("No valid token found — opening browser for authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save for next time
        TOKEN_FILE.write_text(creds.to_json())
        print(f"Token saved to {TOKEN_FILE}")

    return creds


def get_sheets_service():
    """Return an authenticated Sheets API service object."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


if __name__ == "__main__":
    # Quick test — list your first 5 spreadsheets
    service = get_sheets_service()
    print("Sheets service ready.")
