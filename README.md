# TechFi Outreach Agent

This project reads leads from CSV or an optional Google Sheet, uses CrewAI for
qualification and personalization, builds the final outreach copy deterministically
in Python, and can optionally send email through Zoho SMTP.

## Lead source modes

CSV mode remains the default and safest mode.

- `LEAD_SOURCE_TYPE=csv` reads from `data/test_leads.csv` and writes to `data/outreach_output.csv`
- `LEAD_SOURCE_TYPE=google_sheet` reads from a Google Sheet worksheet and writes results to a Google Sheet output worksheet

## Lead statuses

- `New` = ready to process
- `Drafted` = generated but not sent
- `Sent` = already emailed
- `Error` = failed during send
- `Replied` = manual status after reply
- `Not Interested` = do not contact again

Only leads with `New` or a blank status are processed. Leads with any other status
are skipped to prevent duplicate outreach.

## Do-not-contact list

`data/do_not_contact.csv` stores email addresses that should never receive outreach.
The script checks this file before normal status processing, using case-insensitive
trimmed email matching. If the file is missing, the script treats the do-not-contact
list as empty and continues safely.

## Richer lead fields

- `lead_source` = where the lead came from, such as LinkedIn, Apollo, or Referral
- `country` = target country
- `lead_type` = Direct Client, Salesforce Consulting Agency, IT Services Agency, Recruiter, or Partner
- `pain_signal` = strongest reason for outreach, such as a Salesforce QA role, hiring signal, or client-delivery need
- `last_contacted_at` = optional manual tracking field

Example row:

```csv
first_name,last_name,email,company_name,title,website,linkedin_url,service_angle,lead_source,country,lead_type,pain_signal,notes,last_contacted_at,status
Harsh Veer,Nirwan,thetechfilabs@gmail.com,The Technology Fiction,Founder,https://www.thetechnologyfiction.com/,https://www.linkedin.com/company/thetechnologyfiction,Salesforce staff augmentation,Manual Test,India,Internal Test,Testing Salesforce staff augmentation outreach flow,Testing email trigger to my own Gmail account,,New
```

## Google Sheets setup

Google Sheets mode is optional. CSV mode remains the default.

Steps:

1. Create a Google Cloud project.
2. Enable the Google Sheets API.
3. Create service account credentials.
4. Download the service account JSON file.
5. Save it locally as `secrets/google_service_account.json`.
6. Share the Google Sheet with the service account email.
7. Set these environment variables:

```bash
LEAD_SOURCE_TYPE=google_sheet
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_WORKSHEET_NAME=Leads
GOOGLE_OUTPUT_WORKSHEET_NAME=Outreach Output
GOOGLE_SERVICE_ACCOUNT_FILE=secrets/google_service_account.json
MAX_LEADS_PER_RUN=1
```

Never commit the service account JSON file.
Keep `ENABLE_EMAIL_SEND=false` during testing.

Expected `Leads` worksheet columns:

```text
first_name
last_name
email
company_name
title
website
linkedin_url
service_angle
lead_source
country
lead_type
pain_signal
notes
last_contacted_at
status
```

The output worksheet includes all original columns plus:

```text
qualified
priority
personalization_hook
subject
email_body
follow_up_1
follow_up_2
status
error_message
skip_reason
```

## Testing

Keep `ENABLE_EMAIL_SEND=false` during testing so the script only creates drafts.

Run the local checks with:

```bash
./.venv/bin/python src/main.py
./.venv/bin/python -m pytest
```
