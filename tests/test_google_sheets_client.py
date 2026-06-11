from pathlib import Path

import pytest

import google_sheets_client


def test_google_service_account_file_missing_raises_clear_error(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError) as exc_info:
        google_sheets_client.get_google_sheet_client(str(missing_file))

    assert (
        str(exc_info.value)
        == "Google service account file not found. Add it at secrets/google_service_account.json or set GOOGLE_SERVICE_ACCOUNT_FILE."
    )
