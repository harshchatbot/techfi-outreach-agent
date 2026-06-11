from pathlib import Path

import gspread
import pandas as pd
from gspread.exceptions import WorksheetNotFound


def get_google_sheet_client(service_account_file: str):
    credentials_path = Path(service_account_file)
    if not credentials_path.exists():
        raise FileNotFoundError(
            "Google service account file not found. Add it at "
            "secrets/google_service_account.json or set GOOGLE_SERVICE_ACCOUNT_FILE."
        )

    return gspread.service_account(filename=str(credentials_path))


def read_leads_from_sheet(
    sheet_id: str,
    worksheet_name: str,
    service_account_file: str,
) -> pd.DataFrame:
    client = get_google_sheet_client(service_account_file)
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)


def write_results_to_sheet(
    sheet_id: str,
    worksheet_name: str,
    results_df: pd.DataFrame,
    service_account_file: str,
) -> None:
    client = get_google_sheet_client(service_account_file)
    spreadsheet = client.open_by_key(sheet_id)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except WorksheetNotFound:
        row_count = max(len(results_df.index) + 1, 1)
        col_count = max(len(results_df.columns), 1)
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=row_count,
            cols=col_count,
        )

    worksheet.clear()

    values = [results_df.columns.tolist()]
    if not results_df.empty:
        values.extend(
            results_df.fillna("").astype(str).values.tolist()
        )

    worksheet.update("A1", values)
