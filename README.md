# TechFi Outreach Agent

This project reads leads from CSV, uses CrewAI for qualification and personalization,
builds the final outreach copy deterministically in Python, and can optionally send
email through Zoho SMTP.

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

## Testing

Keep `ENABLE_EMAIL_SEND=false` during testing so the script only creates drafts.

Run the local checks with:

```bash
./.venv/bin/python src/main.py
./.venv/bin/python -m pytest
```
