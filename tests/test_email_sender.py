from email_sender import convert_plain_text_to_html, send_email
import email_sender


def test_convert_plain_text_to_html_hyperlinks_first_techfi_labs_occurrence():
    body = "I run TechFi Labs, a Salesforce-focused delivery partner from India."

    html_body = convert_plain_text_to_html(body)

    assert '<a href="https://techfilabs.com/">TechFi Labs</a>' in html_body


def test_convert_plain_text_to_html_preserves_line_breaks():
    body = "Line one\nLine two\nLine three"

    html_body = convert_plain_text_to_html(body)

    assert "Line one<br>Line two<br>Line three" in html_body


def test_convert_plain_text_to_html_escapes_unsafe_html():
    body = '<script>alert("x")</script>\nTechFi Labs'

    html_body = convert_plain_text_to_html(body)

    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html_body
    assert "<script>" not in html_body


def test_convert_plain_text_to_html_links_only_first_occurrence():
    body = "TechFi Labs helps teams. TechFi Labs also supports delivery."

    html_body = convert_plain_text_to_html(body)

    assert html_body.count('<a href="https://techfilabs.com/">TechFi Labs</a>') == 1
    assert "TechFi Labs also supports delivery." in html_body


def test_send_email_does_not_send_when_disabled(monkeypatch):
    calls = {"smtp": 0}

    class DummySMTP:
        def __init__(self, *_args, **_kwargs):
            calls["smtp"] += 1

    monkeypatch.setattr(email_sender, "ENABLE_EMAIL_SEND", False)
    monkeypatch.setattr(email_sender.smtplib, "SMTP_SSL", DummySMTP)

    result = send_email(
        to_email="lead@example.com",
        subject="Test",
        body="I run TechFi Labs, a Salesforce-focused delivery partner from India.",
    )

    assert result is False
    assert calls["smtp"] == 0


def test_send_email_adds_html_alternative_without_real_smtp(monkeypatch):
    captured = {}

    class DummySMTP:
        def __init__(self, host, port):
            captured["host"] = host
            captured["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def login(self, email, password):
            captured["login"] = (email, password)

        def send_message(self, message):
            captured["message"] = message

    monkeypatch.setattr(email_sender, "ENABLE_EMAIL_SEND", True)
    monkeypatch.setattr(email_sender, "SENDER_EMAIL", "sender@example.com")
    monkeypatch.setattr(email_sender, "SENDER_APP_PASSWORD", "app-password")
    monkeypatch.setattr(email_sender.smtplib, "SMTP_SSL", DummySMTP)

    result = send_email(
        to_email="lead@example.com",
        subject="Test",
        body="I run TechFi Labs, a Salesforce-focused delivery partner from India.",
    )

    assert result is True
    assert captured["host"] == email_sender.SMTP_HOST
    assert captured["port"] == email_sender.SMTP_PORT
    assert captured["login"] == ("sender@example.com", "app-password")

    message = captured["message"]
    assert message.get_body(preferencelist=("plain",)).get_content().strip() == (
        "I run TechFi Labs, a Salesforce-focused delivery partner from India."
    )

    html_part = message.get_body(preferencelist=("html",))
    assert html_part is not None
    assert '<a href="https://techfilabs.com/">TechFi Labs</a>' in html_part.get_content()
