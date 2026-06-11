# email_sender.py
"""Email Sender Module
Handles three modes:
- ``draft``: Return a Gmail draft placeholder.
- ``smtp``: Send via ``smtplib``.
- ``noop``: No action when explicitly selected.
The function also respects ``DRY_RUN`` from ``.env`` and returns a safe draft result without external calls.
"""

import os
import smtplib
from email.message import EmailMessage
from typing import Any, Dict

from dotenv import load_dotenv
load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"


def _send_smtp(payload: Any) -> Dict[str, Any]:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender_name = os.getenv("SENDER_NAME", "")

    if not host or not user or not password:
        return {
            "status": "error",
            "detail": "SMTP configuration missing. Check SMTP_HOST, SMTP_USER, SMTP_PASSWORD.",
        }

    msg = EmailMessage()
    msg["Subject"] = payload["subject"]
    msg["From"] = f"{sender_name} <{user}>" if sender_name else user
    msg["To"] = payload["recipient_email"]
    msg.set_content(payload["body"])

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return {"status": "sent", "detail": "SMTP send successful"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _create_gmail_draft(payload: Any) -> Dict[str, Any]:
    # Placeholder – real implementation would use Google API client.
    return {"status": "draft_created", "detail": "Gmail draft placeholder"}


def send_email(payload: Any, mode: str = "draft", dry_run: bool = DRY_RUN) -> Dict[str, Any]:
    """Send or draft an email based on the selected mode.

    Parameters
    ----------
    payload: dict
        Must contain ``subject``, ``body``, ``recipient_email``.
    mode: str
        ``draft``, ``smtp`` or ``send``.
    dry_run: bool, optional
        If ``True`` the function returns a draft result without contacting external services.
    """
    if dry_run:
        return {"status": "draft_created", "detail": "Dry-run mode – no external call made"}

    normalized_mode = mode.lower()
    if normalized_mode in {"smtp", "send"}:
        return _send_smtp(payload)
    if normalized_mode == "draft":
        return _create_gmail_draft(payload)
    if normalized_mode == "noop":
        return {"status": "noop", "detail": "No action performed"}

    return {"status": "error", "detail": f"Unknown email mode: {mode}"}
