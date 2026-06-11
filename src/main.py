import pandas as pd

from config import ENABLE_EMAIL_SEND
from outreach import generate_outreach_email
from utils import read_leads, save_output
from email_sender import send_email

INPUT_FILE = "data/test_leads.csv"
OUTPUT_FILE = "data/outreach_output.csv"

GENERATED_FIELDS = [
    "qualified",
    "priority",
    "personalization_hook",
    "subject",
    "email_body",
    "follow_up_1",
    "follow_up_2",
    "error_message",
]


def _clean_value(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def should_process_status(status) -> bool:
    normalized_status = _clean_value(status).lower()
    return normalized_status in ("", "new")


def _prepare_output_row(lead: dict) -> dict:
    output_row = {
        key: "" if pd.isna(value) else value
        for key, value in lead.items()
    }

    for field in GENERATED_FIELDS:
        output_row.setdefault(field, "")

    return output_row


def main():
    # Safety: only process 1 test record.
    leads_df = read_leads(INPUT_FILE, limit=1)

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
        status = _clean_value(lead.get("status"))

        if not should_process_status(status):
            email = _clean_value(lead.get("email"))
            print(f"Skipping {email} because status is {status}")
            summary["skipped"] += 1
            results.append(output_row)
            continue

        print(
            f"Generating outreach for: "
            f"{lead.get('first_name')} {lead.get('last_name')} - {lead.get('company_name')}"
        )

        result = generate_outreach_email(lead)
        output_row.update(result)
        output_row["error_message"] = ""
        summary["processed"] += 1

        print("\nGenerated email body:")
        print(output_row.get("email_body", ""))

        if not ENABLE_EMAIL_SEND:
            output_row["status"] = "Drafted"
            summary["drafted"] += 1
        else:
            try:
                sent = send_email(
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

    save_output(results, OUTPUT_FILE)

    print(f"\nDone. Outreach output saved to: {OUTPUT_FILE}")
    print(f"Processed: {summary['processed']}")
    print(f"Sent: {summary['sent']}")
    print(f"Drafted: {summary['drafted']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")


if __name__ == "__main__":
    main()
