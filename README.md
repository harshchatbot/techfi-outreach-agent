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

## Testing

Keep `ENABLE_EMAIL_SEND=false` during testing so the script only creates drafts.

Run the local checks with:

```bash
./.venv/bin/python src/main.py
./.venv/bin/python -m pytest
```
