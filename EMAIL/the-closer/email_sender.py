# email_sender.py
"""Email Sender Module
Implements three operational modes:
- ``draft``: Create a Gmail draft via API (placeholder implementation).
- ``smtp``: Send the email through an SMTP server.
- ``noop``: No‑operation / dry‑run mode.

All modes respect the ``DRY_RUN`` flag from the ``.env`` file. In dry‑run the function returns a
``draft_created`` status without contacting any external service (Phase 4 requirement).
A small retry wrapper (max 2 attempts) is applied to the SMTP pathway to tolerate transient network
issues.
"""

import os
import smtplib
import time
from email.message import EmailMessage
from typing import Any
from collections.abc import Mapping


from dotenv import load_dotenv

# Load environment variables early so that DRY_RUN and other settings are available.
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration flags
# ---------------------------------------------------------------------------
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _send_smtp(payload: Mapping[str, str]) -> dict[str, Any]:
    """Send an email via SMTP with a simple retry mechanism.

    Parameters
    ----------
    payload: dict
        Must contain ``subject``, ``body`` and ``recipient_email``.

    Returns
    -------
    dict
        ``{"status": "sent", "detail": "..."}`` on success or ``{"status": "error", "detail": "..."}`` on failure.
    """
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

    attempts = 0
    max_attempts = 2
    while attempts < max_attempts:
        try:
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(user, password)
                server.send_message(msg)
            return {"status": "sent", "detail": "SMTP send successful"}
        except Exception as e:
            attempts += 1
            if attempts >= max_attempts:
                return {"status": "error", "detail": str(e)}
            time.sleep(1)

    return {"status": "error", "detail": "Unexpected control flow – SMTP send failed"}


def _create_gmail_draft(payload: Mapping[str, str]) -> dict[str, Any]:
    """Create a Gmail draft.

    This placeholder returns a successful result without calling the Google API. In a full
    implementation you would use the Google API client with OAuth credentials.
    """
    return {"status": "draft_created", "detail": "Gmail draft placeholder"}


def send_email(payload: Mapping[str, str], mode: str = "draft", dry_run: bool = DRY_RUN) -> dict[str, Any]:
    """Send or draft an email based on the selected mode.

    Parameters
    ----------
    payload: dict
        Must contain ``subject``, ``body`` and ``recipient_email``.
    mode: str, optional
        ``draft``, ``smtp`` or ``send``.
    dry_run: bool, optional
        If ``True`` the function short‑circuits and returns a ``draft_created`` status without
        contacting external services.
    """
    if dry_run:
        return {"status": "draft_created", "detail": "Dry‑run mode – no external call made"}

    normalized_mode = mode.lower()
    if normalized_mode in {"smtp", "send"}:
        return _send_smtp(payload)
    if normalized_mode == "draft":
        return _create_gmail_draft(payload)
    if normalized_mode == "noop":
        return {"status": "noop", "detail": "No action performed"}

    return {"status": "error", "detail": f"Unknown email mode: {mode}"}
