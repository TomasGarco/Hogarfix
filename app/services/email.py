from app.utils import send_email as _send_email


def send_email(email: str, subject: str, body: str, html_body: str | None = None):
    """Send email using the configured backend (plain text and optional HTML)."""
    return _send_email(subject=subject, to_email=email, text_body=body, html_body=html_body)
