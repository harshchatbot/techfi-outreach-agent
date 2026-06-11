import smtplib
from email.message import EmailMessage

from config import ENABLE_EMAIL_SEND, SENDER_APP_PASSWORD, SENDER_EMAIL


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
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        smtp.send_message(message)

    print(f"Email sent to: {to_email}")
    return True