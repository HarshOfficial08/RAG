"""Outbound email via SMTP (e.g. Gmail + an App Password). See
docs/plan/06-auth.md for the auth flows this supports (password reset).
"""

import smtplib
from email.message import EmailMessage

from app.config import settings


class MailerNotConfiguredError(Exception):
    """Raised when SMTP credentials aren't set — see .env.example."""


def send_email(to: str, subject: str, body: str) -> None:
    if not settings.smtp_user or not settings.smtp_pass:
        raise MailerNotConfiguredError("SMTP_USER/SMTP_PASS are not configured in .env")

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_pass)
        smtp.send_message(message)
