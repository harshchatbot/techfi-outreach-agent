# TechFi Outreach Agent

## Lead statuses

- `New` = ready to process
- `Drafted` = generated but not sent
- `Sent` = already emailed
- `Error` = failed during send
- `Replied` = manual status after reply
- `Not Interested` = do not contact again

Only leads with `New` or a blank status are processed. Leads with any other status
are skipped to prevent duplicate outreach.
