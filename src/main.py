import csv
from pathlib import Path

import pandas as pd

from utils import read_leads, save_output

INPUT_FILE = "data/test_leads.csv"
OUTPUT_FILE = "data/outreach_output.csv"
DO_NOT_CONTACT_FILE = "data/do_not_contact.csv"

GENERATED_FIELDS = [
    "qualified",
    "priority",
    "personalization_hook",
    "subject",
    "email_body",
    "follow_up_1",
    "follow_up_2",
    "error_message",
    "skip_reason",
]


def _clean_value(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def normalize_email(email) -> str:
    return _clean_value(email).lower()


def should_process_status(status) -> bool:
    normalized_status = _clean_value(status).lower()
    return normalized_status in ("", "new")


def load_do_not_contact_emails(file_path: str) -> set[str]:
    path = Path(file_path)
    if not path.exists():
        return set()

    blocked_emails: set[str] = set()
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            normalized_email = normalize_email((row or {}).get("email"))
            if normalized_email:
                blocked_emails.add(normalized_email)

    return blocked_emails


def is_do_not_contact(email, blocked_emails: set[str]) -> bool:
    return normalize_email(email) in blocked_emails


def _prepare_output_row(lead: dict) -> dict:
    output_row = {
        key: "" if pd.isna(value) else value
        for key, value in lead.items()
    }

    for field in GENERATED_FIELDS:
        output_row.setdefault(field, "")

    return output_row


def process_leads(
    leads_df: pd.DataFrame,
    do_not_contact_emails: set[str],
    generate_outreach_fn,
    send_email_fn,
    email_send_enabled: bool,
) -> tuple[list[dict], dict]:
    results = []
    summary = {
        "processed": 0,
        "sent": 0,
        "drafted": 0,
        "skipped": 0,
        "errors": 0,
    }

    for _, row in leads_df.iterrows():
        lead = row.to_dict()
        output_row = _prepare_output_row(lead)
        email = _clean_value(lead.get("email"))
        status = _clean_value(lead.get("status"))

        if is_do_not_contact(email, do_not_contact_emails):
            print(f"Skipping {email} because email is in do-not-contact list")
            output_row["status"] = "Skipped"
            output_row["skip_reason"] = "Do not contact"
            summary["skipped"] += 1
            results.append(output_row)
            continue

        if not should_process_status(status):
            print(f"Skipping {email} because status is {status}")
            output_row["skip_reason"] = f"Status is {status}"
            summary["skipped"] += 1
            results.append(output_row)
            continue

        print(
            f"Generating outreach for: "
            f"{lead.get('first_name')} {lead.get('last_name')} - {lead.get('company_name')}"
        )

        result = generate_outreach_fn(lead)
        output_row.update(result)
        output_row["error_message"] = ""
        output_row["skip_reason"] = ""
        summary["processed"] += 1

        print("\nGenerated email body:")
        print(output_row.get("email_body", ""))

        if not email_send_enabled:
            output_row["status"] = "Drafted"
            summary["drafted"] += 1
        else:
            try:
                sent = send_email_fn(
                    to_email=output_row.get("email"),
                    subject=output_row.get("subject"),
                    body=output_row.get("email_body"),
                )

                if sent:
                    output_row["status"] = "Sent"
                    summary["sent"] += 1
                else:
                    output_row["status"] = "Error"
                    output_row["error_message"] = "send_email returned False"
                    summary["errors"] += 1
            except Exception as exc:
                output_row["status"] = "Error"
                output_row["error_message"] = str(exc)
                summary["errors"] += 1

        results.append(output_row)

    return results, summary


def main():
    from config import ENABLE_EMAIL_SEND
    from email_sender import send_email
    from outreach import generate_outreach_email

    # Safety: only process 1 test record.
    leads_df = read_leads(INPUT_FILE, limit=1)
    do_not_contact_emails = load_do_not_contact_emails(DO_NOT_CONTACT_FILE)

    results, summary = process_leads(
        leads_df=leads_df,
        do_not_contact_emails=do_not_contact_emails,
        generate_outreach_fn=generate_outreach_email,
        send_email_fn=send_email,
        email_send_enabled=ENABLE_EMAIL_SEND,
    )

    save_output(results, OUTPUT_FILE)

    print(f"\nDone. Outreach output saved to: {OUTPUT_FILE}")
    print(f"Processed: {summary['processed']}")
    print(f"Sent: {summary['sent']}")
    print(f"Drafted: {summary['drafted']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")


if __name__ == "__main__":
    main()
