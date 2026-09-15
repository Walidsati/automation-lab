#!/usr/bin/env python3
"""Week 2 project: run the full sales report pipeline end-to-end.

Steps:
  1. Generate Excel report
  2. Generate PDF report (with chart)
  3. Email the PDF with HTML body + attachment

Usage:
    python run_report.py
"""

import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---- Paths ----
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "data" / "run_report.log"


def setup_logging() -> logging.Logger:
    """Configure logging to both file and console, in UTC."""
    logger = logging.getLogger("run_report")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S UTC",
    )
    formatter.converter = time.gmtime

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def main() -> int:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Week 2 pipeline started")

    # Import here so import errors surface after logging is ready
    from excel_report_xlsxwriter import generate_excel_report
    from pdf_report import generate_pdf_report
    from email_report import send_report_email

    try:
        # Step 1: Excel
        t0 = time.time()
        logger.info("Step 1/3: generating Excel report")
        xlsx = generate_excel_report()
        logger.info(f"  Excel saved: {xlsx} ({time.time() - t0:.2f}s)")

        # Step 2: PDF
        t0 = time.time()
        logger.info("Step 2/3: generating PDF report")
        pdf = generate_pdf_report()
        logger.info(f"  PDF saved: {pdf} ({time.time() - t0:.2f}s)")

        # Step 3: Email
        t0 = time.time()
        logger.info("Step 3/3: sending email")
        send_report_email(pdf)
        logger.info(f"  Email sent ({time.time() - t0:.2f}s)")

        logger.info("Pipeline finished successfully")
        return 0

    except Exception:
        logger.exception("Pipeline failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

