#!/usr/bin/env python3
"""
Read the next 'pending' row from the content-queue Google Sheet and, optionally,
write a status update back to it.

Requires a Google service account JSON (path via GOOGLE_SERVICE_ACCOUNT_JSON env
var or --creds) with edit access to the target sheet, and the gspread package
(`pip install gspread google-auth`).

Sheet columns expected (header row): title, style, key, tempo_bpm, duration_hours,
status, video_id, scheduled_date

Usage:
    python read_sheet.py --sheet-id <SHEET_ID> --next-pending
    python read_sheet.py --sheet-id <SHEET_ID> --set-status 3 done --video-id abc123
"""
import argparse
import json
import os

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client(creds_path: str):
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def next_pending_row(sheet):
    records = sheet.get_all_records()  # list of dicts keyed by header row
    for i, row in enumerate(records, start=2):  # row 1 is header
        if row.get("status", "").strip().lower() == "pending":
            row["_row_number"] = i
            return row
    return None


def set_status(sheet, row_number: int, status: str, video_id: str | None = None):
    header = sheet.row_values(1)
    status_col = header.index("status") + 1
    sheet.update_cell(row_number, status_col, status)
    if video_id and "video_id" in header:
        video_col = header.index("video_id") + 1
        sheet.update_cell(row_number, video_col, video_id)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sheet-id", required=True)
    p.add_argument("--worksheet", default="Sheet1")
    p.add_argument("--creds", default=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
    p.add_argument("--next-pending", action="store_true")
    p.add_argument("--set-status", nargs=2, metavar=("ROW_NUMBER", "STATUS"))
    p.add_argument("--video-id", default=None)
    args = p.parse_args()

    client = get_client(args.creds)
    sheet = client.open_by_key(args.sheet_id).worksheet(args.worksheet)

    if args.next_pending:
        row = next_pending_row(sheet)
        print(json.dumps(row) if row else "null")
    elif args.set_status:
        row_number, status = args.set_status
        set_status(sheet, int(row_number), status, args.video_id)
        print(f"Updated row {row_number} -> status={status}")


if __name__ == "__main__":
    main()
