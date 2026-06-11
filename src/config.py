import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")
ENABLE_EMAIL_SEND = os.getenv("ENABLE_EMAIL_SEND", "false").lower() == "true"

LEAD_SOURCE_TYPE = os.getenv("LEAD_SOURCE_TYPE", "csv").strip().lower() or "csv"
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "").strip()
GOOGLE_SHEET_WORKSHEET_NAME = os.getenv(
    "GOOGLE_SHEET_WORKSHEET_NAME",
    "Leads",
).strip() or "Leads"
GOOGLE_OUTPUT_WORKSHEET_NAME = os.getenv(
    "GOOGLE_OUTPUT_WORKSHEET_NAME",
    "Outreach Output",
).strip() or "Outreach Output"
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "secrets/google_service_account.json",
).strip() or "secrets/google_service_account.json"
MAX_LEADS_PER_RUN = int(os.getenv("MAX_LEADS_PER_RUN", "1"))


def validate_config() -> None:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file.")

    if LEAD_SOURCE_TYPE not in {"csv", "google_sheet"}:
        raise ValueError("LEAD_SOURCE_TYPE must be either 'csv' or 'google_sheet'.")

    if LEAD_SOURCE_TYPE == "google_sheet" and not GOOGLE_SHEET_ID:
        raise ValueError(
            "GOOGLE_SHEET_ID is required when LEAD_SOURCE_TYPE=google_sheet."
        )

    if MAX_LEADS_PER_RUN < 1:
        raise ValueError("MAX_LEADS_PER_RUN must be at least 1.")


validate_config()
