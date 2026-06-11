import html
import smtplib
from email.message import EmailMessage

from config import ENABLE_EMAIL_SEND, SENDER_APP_PASSWORD, SENDER_EMAIL


SMTP_HOST = "smtp.zoho.in"
SMTP_PORT = 465
TECHFI_LABS_URL = "https://techfilabs.com/"


def convert_plain_text_to_html(body: str) -> str:
    escaped_body = html.escape(body)

    # Hyperlink only the first occurrence of TechFi Labs
    escaped_body = escaped_body.replace(
        "TechFi Labs",
        f'<a href="{TECHFI_LABS_URL}">TechFi Labs</a>',
        1,
    )

    # Preserve line breaks in email
    html_body = escaped_body.replace("\n", "<br>")

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #111827;">
        {html_body}
      </body>
    </html>
    """


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not ENABLE_EMAIL_SEND:
        print("Email sending is disabled. Set ENABLE_EMAIL_SEND=true in .env to send.")
        return False

    if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
        raise ValueError("SENDER_EMAIL or SENDER_APP_PASSWORD is missing in .env.")

    message = EmailMessage()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    # Plain text fallback
    message.set_content(body)

    # HTML version with TechFi Labs hyperlink
    html_body = convert_plain_text_to_html(body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        smtp.send_message(message)

    print(f"Email sent to: {to_email}")
    return True