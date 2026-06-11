import sys
from types import ModuleType

import pandas as pd

import main


def _sample_lead(status="New", email="lead@example.com") -> dict:
    return {
        "first_name": "Ava",
        "last_name": "Stone",
        "email": email,
        "company_name": "Acme Labs",
        "title": "Founder",
        "website": "https://example.com",
        "linkedin_url": "https://linkedin.com/company/example",
        "service_angle": "Salesforce staff augmentation",
        "lead_source": "Manual Test",
        "country": "India",
        "lead_type": "Salesforce Consulting Agency",
        "pain_signal": "Posted a Salesforce QA automation role",
        "notes": "Testing",
        "last_contacted_at": "",
        "status": status,
    }


def test_should_process_status_cases():
    assert main.should_process_status("")
    assert main.should_process_status(float("nan"))
    assert main.should_process_status("New")
    assert main.should_process_status("  new  ")
    assert not main.should_process_status("Sent")
    assert not main.should_process_status("Drafted")
    assert not main.should_process_status("Error")
    assert not main.should_process_status("Replied")
    assert not main.should_process_status("Not Interested")
    assert not main.should_process_status("Custom")


def test_load_do_not_contact_missing_file_returns_empty_set(tmp_path):
    missing_file = tmp_path / "missing.csv"

    assert main.load_do_not_contact_emails(str(missing_file)) == set()


def test_load_do_not_contact_normalizes_emails(tmp_path):
    dnc_file = tmp_path / "do_not_contact.csv"
    dnc_file.write_text(
        "email,reason,added_date\n"
        "  BLOCKED@example.com  ,Opted out,2026-06-12\n"
        "Second@Example.com,Manual block,2026-06-12\n",
        encoding="utf-8",
    )

    blocked = main.load_do_not_contact_emails(str(dnc_file))

    assert blocked == {"blocked@example.com", "second@example.com"}


def test_process_leads_skips_do_not_contact_before_generation():
    leads_df = pd.DataFrame([_sample_lead(email=" BLOCKED@example.com ")])
    calls = {"generate": 0, "send": 0}

    def fake_generate(_lead):
        calls["generate"] += 1
        raise AssertionError("generate_outreach_email should not be called")

    def fake_send(**_kwargs):
        calls["send"] += 1
        raise AssertionError("send_email should not be called")

    results, summary = main.process_leads(
        leads_df=leads_df,
        do_not_contact_emails={"blocked@example.com"},
        generate_outreach_fn=fake_generate,
        send_email_fn=fake_send,
        email_send_enabled=False,
    )

    assert calls == {"generate": 0, "send": 0}
    assert results[0]["status"] == "Skipped"
    assert results[0]["skip_reason"] == "Do not contact"
    assert results[0]["error_message"] == ""
    assert summary["processed"] == 0
    assert summary["skipped"] == 1


def test_process_leads_new_lead_drafts_when_sending_disabled():
    leads_df = pd.DataFrame([_sample_lead(status="New")])
    calls = {"generate": 0, "send": 0}

    def fake_generate(lead):
        calls["generate"] += 1
        return {
            "email": lead["email"],
            "company_name": lead["company_name"],
            "title": lead["title"],
            "service_angle": lead["service_angle"],
            "qualified": "Yes",
            "priority": "High",
            "personalization_hook": "Noticed Acme Labs supports Salesforce delivery.",
            "subject": "Salesforce Delivery Support",
            "email_body": "P.S. If this is not relevant, feel free to reply \"not interested\" and I won't follow up.",
            "follow_up_1": "Follow up 1",
            "follow_up_2": "Follow up 2",
            "status": "Drafted",
        }

    def fake_send(**_kwargs):
        calls["send"] += 1
        return True

    results, summary = main.process_leads(
        leads_df=leads_df,
        do_not_contact_emails=set(),
        generate_outreach_fn=fake_generate,
        send_email_fn=fake_send,
        email_send_enabled=False,
    )

    assert calls == {"generate": 1, "send": 0}
    assert results[0]["status"] == "Drafted"
    assert "P.S. If this is not relevant" in results[0]["email_body"]
    assert results[0]["lead_source"] == "Manual Test"
    assert results[0]["country"] == "India"
    assert results[0]["lead_type"] == "Salesforce Consulting Agency"
    assert results[0]["pain_signal"] == "Posted a Salesforce QA automation role"
    assert results[0]["last_contacted_at"] == ""
    assert results[0]["skip_reason"] == ""
    assert summary["drafted"] == 1
    assert summary["processed"] == 1


def test_process_leads_sent_status_skips_without_generation():
    leads_df = pd.DataFrame([_sample_lead(status="Sent")])
    calls = {"generate": 0, "send": 0}

    def fake_generate(_lead):
        calls["generate"] += 1
        raise AssertionError("generate_outreach_email should not be called")

    def fake_send(**_kwargs):
        calls["send"] += 1
        raise AssertionError("send_email should not be called")

    results, summary = main.process_leads(
        leads_df=leads_df,
        do_not_contact_emails=set(),
        generate_outreach_fn=fake_generate,
        send_email_fn=fake_send,
        email_send_enabled=True,
    )

    assert calls == {"generate": 0, "send": 0}
    assert results[0]["status"] == "Sent"
    assert results[0]["skip_reason"] == "Status is Sent"
    assert summary["processed"] == 0
    assert summary["skipped"] == 1


def test_process_leads_send_failure_marks_error():
    leads_df = pd.DataFrame([_sample_lead(status="New")])

    def fake_generate(lead):
        return {
            "email": lead["email"],
            "company_name": lead["company_name"],
            "title": lead["title"],
            "service_angle": lead["service_angle"],
            "qualified": "Yes",
            "priority": "High",
            "personalization_hook": "Noticed Acme Labs supports Salesforce delivery.",
            "subject": "Salesforce Delivery Support",
            "email_body": "Body",
            "follow_up_1": "Follow up 1",
            "follow_up_2": "Follow up 2",
            "status": "Drafted",
        }

    def fake_send(**_kwargs):
        raise RuntimeError("SMTP failed")

    results, summary = main.process_leads(
        leads_df=leads_df,
        do_not_contact_emails=set(),
        generate_outreach_fn=fake_generate,
        send_email_fn=fake_send,
        email_send_enabled=True,
    )

    assert results[0]["status"] == "Error"
    assert results[0]["error_message"] == "SMTP failed"
    assert summary["errors"] == 1


def test_main_reads_missing_do_not_contact_file_without_crashing(monkeypatch, tmp_path):
    input_file = tmp_path / "leads.csv"
    output_file = tmp_path / "output.csv"
    input_file.write_text(
        "first_name,last_name,email,company_name,title,website,linkedin_url,service_angle,lead_source,country,lead_type,pain_signal,notes,last_contacted_at,status\n"
        "Ava,Stone,lead@example.com,Acme Labs,Founder,https://example.com,https://linkedin.com/company/example,Salesforce staff augmentation,Manual Test,India,Salesforce Consulting Agency,Posted a Salesforce QA automation role,Testing,,New\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(main, "INPUT_FILE", str(input_file))
    monkeypatch.setattr(main, "OUTPUT_FILE", str(output_file))
    monkeypatch.setattr(main, "DO_NOT_CONTACT_FILE", str(tmp_path / "missing.csv"))

    dummy_config = ModuleType("config")
    dummy_config.ENABLE_EMAIL_SEND = False
    monkeypatch.setitem(sys.modules, "config", dummy_config)

    dummy_email_sender = ModuleType("email_sender")

    def _send_email(**_kwargs):
        raise AssertionError("send_email should not be called when disabled")

    dummy_email_sender.send_email = _send_email
    monkeypatch.setitem(sys.modules, "email_sender", dummy_email_sender)

    dummy_outreach = ModuleType("outreach")

    def _generate_outreach_email(lead):
        return {
            "email": lead["email"],
            "company_name": lead["company_name"],
            "title": lead["title"],
            "service_angle": lead["service_angle"],
            "qualified": "Yes",
            "priority": "High",
            "personalization_hook": "Noticed Acme Labs supports Salesforce delivery.",
            "subject": "Salesforce Delivery Support",
            "email_body": "Body",
            "follow_up_1": "Follow up 1",
            "follow_up_2": "Follow up 2",
            "status": "Drafted",
        }

    dummy_outreach.generate_outreach_email = _generate_outreach_email
    monkeypatch.setitem(sys.modules, "outreach", dummy_outreach)

    main.main()

    output_text = output_file.read_text(encoding="utf-8")
    assert "Drafted" in output_text
    assert "Manual Test" in output_text
    assert "Salesforce Consulting Agency" in output_text
