import importlib
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


def _fake_result_from_lead(lead: dict) -> dict:
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


def _load_config_module(monkeypatch, **env_vars):
    for key in [
        "OPENAI_API_KEY",
        "SENDER_EMAIL",
        "SENDER_APP_PASSWORD",
        "ENABLE_EMAIL_SEND",
        "LEAD_SOURCE_TYPE",
        "GOOGLE_SHEET_ID",
        "GOOGLE_SHEET_WORKSHEET_NAME",
        "GOOGLE_OUTPUT_WORKSHEET_NAME",
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "MAX_LEADS_PER_RUN",
    ]:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LEAD_SOURCE_TYPE", "csv")
    monkeypatch.setenv("GOOGLE_SHEET_ID", "")
    monkeypatch.setenv("GOOGLE_SHEET_WORKSHEET_NAME", "Leads")
    monkeypatch.setenv("GOOGLE_OUTPUT_WORKSHEET_NAME", "Outreach Output")
    monkeypatch.setenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "secrets/google_service_account.json",
    )
    monkeypatch.setenv("MAX_LEADS_PER_RUN", "1")
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    sys.modules.pop("config", None)
    return importlib.import_module("config")


def test_config_defaults_to_csv(monkeypatch):
    config = _load_config_module(monkeypatch)

    assert config.LEAD_SOURCE_TYPE == "csv"
    assert config.MAX_LEADS_PER_RUN == 1


def test_config_requires_google_sheet_id_in_google_sheet_mode(monkeypatch):
    try:
        _load_config_module(monkeypatch, LEAD_SOURCE_TYPE="google_sheet")
    except ValueError as exc:
        assert str(exc) == "GOOGLE_SHEET_ID is required when LEAD_SOURCE_TYPE=google_sheet."
    else:
        raise AssertionError("Expected ValueError for missing GOOGLE_SHEET_ID")


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
        return _fake_result_from_lead(lead)

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
        return _fake_result_from_lead(lead)

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
    dummy_config.LEAD_SOURCE_TYPE = "csv"
    dummy_config.GOOGLE_SHEET_ID = ""
    dummy_config.GOOGLE_SHEET_WORKSHEET_NAME = "Leads"
    dummy_config.GOOGLE_OUTPUT_WORKSHEET_NAME = "Outreach Output"
    dummy_config.GOOGLE_SERVICE_ACCOUNT_FILE = "secrets/google_service_account.json"
    dummy_config.MAX_LEADS_PER_RUN = 1
    monkeypatch.setitem(sys.modules, "config", dummy_config)

    dummy_email_sender = ModuleType("email_sender")

    def _send_email(**_kwargs):
        raise AssertionError("send_email should not be called when disabled")

    dummy_email_sender.send_email = _send_email
    monkeypatch.setitem(sys.modules, "email_sender", dummy_email_sender)

    dummy_outreach = ModuleType("outreach")
    dummy_outreach.generate_outreach_email = _fake_result_from_lead
    monkeypatch.setitem(sys.modules, "outreach", dummy_outreach)

    main.main()

    output_text = output_file.read_text(encoding="utf-8")
    assert "Drafted" in output_text
    assert "Manual Test" in output_text
    assert "Salesforce Consulting Agency" in output_text


def test_csv_mode_uses_csv_reader_and_writer(monkeypatch):
    leads_df = pd.DataFrame([_sample_lead(status="New")])
    calls = {"read": 0, "save": 0, "generate": 0}

    monkeypatch.setattr(
        main,
        "read_leads",
        lambda input_file, limit=None: (
            calls.__setitem__("read", calls["read"] + 1) or leads_df
            if input_file == main.INPUT_FILE and limit == 1
            else (_ for _ in ()).throw(AssertionError("Unexpected CSV read args"))
        ),
    )

    def _save_output(results, output_file):
        calls["save"] += 1
        assert output_file == main.OUTPUT_FILE
        assert results[0]["status"] == "Drafted"

    monkeypatch.setattr(main, "save_output", _save_output)
    monkeypatch.setattr(main, "load_do_not_contact_emails", lambda _path: set())

    dummy_config = ModuleType("config")
    dummy_config.ENABLE_EMAIL_SEND = False
    dummy_config.LEAD_SOURCE_TYPE = "csv"
    dummy_config.GOOGLE_SHEET_ID = ""
    dummy_config.GOOGLE_SHEET_WORKSHEET_NAME = "Leads"
    dummy_config.GOOGLE_OUTPUT_WORKSHEET_NAME = "Outreach Output"
    dummy_config.GOOGLE_SERVICE_ACCOUNT_FILE = "secrets/google_service_account.json"
    dummy_config.MAX_LEADS_PER_RUN = 1
    monkeypatch.setitem(sys.modules, "config", dummy_config)

    dummy_email_sender = ModuleType("email_sender")
    dummy_email_sender.send_email = lambda **_kwargs: (_ for _ in ()).throw(
        AssertionError("send_email should not be called when disabled")
    )
    monkeypatch.setitem(sys.modules, "email_sender", dummy_email_sender)

    dummy_outreach = ModuleType("outreach")

    def _generate(lead):
        calls["generate"] += 1
        return _fake_result_from_lead(lead)

    dummy_outreach.generate_outreach_email = _generate
    monkeypatch.setitem(sys.modules, "outreach", dummy_outreach)

    main.main()

    assert calls == {"read": 1, "save": 1, "generate": 1}


def test_max_leads_per_run_one_is_passed_to_csv_reader(monkeypatch):
    calls = {"limit": None}

    def _read_leads(_input_file, limit=None):
        calls["limit"] = limit
        return pd.DataFrame([_sample_lead(email="lead1@example.com")])

    monkeypatch.setattr(main, "read_leads", _read_leads)

    leads_df = main._load_leads(
        lead_source_type="csv",
        max_leads_per_run=1,
        google_sheet_id="",
        google_sheet_worksheet_name="Leads",
        google_service_account_file="secrets/google_service_account.json",
    )

    assert calls["limit"] == 1
    assert len(leads_df) == 1


def test_max_leads_per_run_five_limits_google_sheet_rows(monkeypatch):
    leads_df = pd.DataFrame(
        [_sample_lead(email=f"lead{i}@example.com") for i in range(6)]
    )

    dummy_google_client = ModuleType("google_sheets_client")
    dummy_google_client.read_leads_from_sheet = (
        lambda sheet_id, worksheet_name, service_account_file: leads_df
    )
    monkeypatch.setitem(sys.modules, "google_sheets_client", dummy_google_client)

    limited_df = main._load_leads(
        lead_source_type="google_sheet",
        max_leads_per_run=5,
        google_sheet_id="sheet-123",
        google_sheet_worksheet_name="Leads",
        google_service_account_file="secrets/google_service_account.json",
    )

    assert len(limited_df) == 5


def test_google_sheet_mode_uses_sheet_reader_and_writer(monkeypatch):
    leads_df = pd.DataFrame([_sample_lead(status="New")])
    calls = {"read": 0, "write": 0, "generate": 0}

    dummy_config = ModuleType("config")
    dummy_config.ENABLE_EMAIL_SEND = False
    dummy_config.LEAD_SOURCE_TYPE = "google_sheet"
    dummy_config.GOOGLE_SHEET_ID = "sheet-123"
    dummy_config.GOOGLE_SHEET_WORKSHEET_NAME = "Leads"
    dummy_config.GOOGLE_OUTPUT_WORKSHEET_NAME = "Outreach Output"
    dummy_config.GOOGLE_SERVICE_ACCOUNT_FILE = "secrets/google_service_account.json"
    dummy_config.MAX_LEADS_PER_RUN = 1
    monkeypatch.setitem(sys.modules, "config", dummy_config)

    dummy_email_sender = ModuleType("email_sender")
    dummy_email_sender.send_email = lambda **_kwargs: (_ for _ in ()).throw(
        AssertionError("send_email should not be called when disabled")
    )
    monkeypatch.setitem(sys.modules, "email_sender", dummy_email_sender)

    dummy_outreach = ModuleType("outreach")

    def _generate(lead):
        calls["generate"] += 1
        return _fake_result_from_lead(lead)

    dummy_outreach.generate_outreach_email = _generate
    monkeypatch.setitem(sys.modules, "outreach", dummy_outreach)

    dummy_google_client = ModuleType("google_sheets_client")

    def _read(sheet_id, worksheet_name, service_account_file):
        calls["read"] += 1
        assert sheet_id == "sheet-123"
        assert worksheet_name == "Leads"
        assert service_account_file == "secrets/google_service_account.json"
        return leads_df

    def _write(sheet_id, worksheet_name, results_df, service_account_file):
        calls["write"] += 1
        assert sheet_id == "sheet-123"
        assert worksheet_name == "Outreach Output"
        assert service_account_file == "secrets/google_service_account.json"
        assert isinstance(results_df, pd.DataFrame)
        assert results_df.iloc[0]["status"] == "Drafted"

    dummy_google_client.read_leads_from_sheet = _read
    dummy_google_client.write_results_to_sheet = _write
    monkeypatch.setitem(sys.modules, "google_sheets_client", dummy_google_client)

    main.main()

    assert calls == {"read": 1, "write": 1, "generate": 1}
