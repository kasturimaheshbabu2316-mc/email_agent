# logger.py
"""Simple CSV logger for The Closer.

Each call to :func:`log_entry` appends a row to ``outreach_log.csv`` located in the
project root. The log contains a timestamp, contact information, the generated
subject and body, the operation status (sent, draft_created, dry_run, skipped,
error), and an optional error message.

The implementation is deliberately lightweight and avoids external
dependencies – only the Python standard library is used. It respects the
environment variable ``LOG_FILE`` if set; otherwise it defaults to
``outreach_log.csv`` in the current working directory.
"""

import csv
import os
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

DEFAULT_LOG_PATH = "outreach_log.csv"


def _ensure_log_file(path: str) -> None:
    """Create the CSV file with a header if it does not yet exist.

    The header columns are:
    ``timestamp,recipient_name,recipient_email,company,role,subject,body,status,error``
    """
    if not os.path.exists(path):
        with open(path, mode="w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow([
                "timestamp",
                "recipient_name",
                "recipient_email",
                "company",
                "role",
                "subject",
                "body",
                "status",
                "error",
            ])


def log_entry(
    contact: Mapping[str, Any],
    payload: Mapping[str, Any],
    status: str,
    error: Optional[str] = None,
    log_path: Optional[str] = None,
) -> None:
    """Append a single log entry.

    Parameters
    ----------
    contact: dict
        The original contact record (usually returned by ``loader.load_contacts``).
    payload: dict
        The email payload containing ``subject`` and ``body``.
    status: str
        One of ``sent``, ``draft_created``, ``dry_run``, ``skipped`` or ``error``.
    error: str, optional
        Human‑readable error message when ``status`` is ``error``.
    log_path: str, optional
        Override the destination CSV file. If omitted, the ``LOG_FILE`` env var is
        consulted, falling back to ``outreach_log.csv``.
    """
    path = log_path or os.getenv("LOG_FILE", DEFAULT_LOG_PATH)
    _ensure_log_file(path)

    timestamp = datetime.utcnow().isoformat() + "Z"
    row = [
        timestamp,
        contact.get("recipient_name", ""),
        contact.get("recipient_email", ""),
        contact.get("company", ""),
        contact.get("role", ""),
        payload.get("subject", ""),
        payload.get("body", "").replace("\n", " "),  # one‑line for CSV
        status,
        error or "",
    ]

    with open(path, mode="a", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(row)
