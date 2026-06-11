from outreach import generate_outreach_email
from utils import read_leads, save_output
from email_sender import send_email

INPUT_FILE = "data/test_leads.csv"
OUTPUT_FILE = "data/outreach_output.csv"


def main():
    # Safety: only process 1 test record.
    leads_df = read_leads(INPUT_FILE, limit=1)

    results = []

    for _, row in leads_df.iterrows():
        lead = row.to_dict()

        print(
            f"Generating outreach for: "
            f"{lead.get('first_name')} {lead.get('last_name')} - {lead.get('company_name')}"
        )

        result = generate_outreach_email(lead)

        print("\nGenerated email body:")
        print(result.get("email_body", ""))

        sent = send_email(
            to_email=result.get("email"),
            subject=result.get("subject"),
            body=result.get("email_body"),
        )

        result["status"] = "Sent" if sent else "Drafted"

        results.append(result)

    save_output(results, OUTPUT_FILE)

    print(f"\nDone. Outreach output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
