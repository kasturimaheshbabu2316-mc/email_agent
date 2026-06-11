import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def log_entry(
    contact: Dict[str, Any], payload: Dict[str, str], status: str, detail: str
) -> None:
    """Append a single outreach event to a CSV log file.

    Parameters
    ----------
    contact: dict
        The contact information (should contain at least ``recipient_email``).
    payload: dict
        Email payload with ``subject`` and ``body`` keys.
    status: str
        One of ``sent``, ``draft_created``, ``skipped`` or ``error``.
    detail: str
        Human‑readable detail or error message.
    """
    log_path = os.getenv("LOG_FILE", "outreach_log.csv")
    log_file = Path(log_path)
    # Ensure parent directory exists
    if log_file.parent and not log_file.parent.exists():
        log_file.parent.mkdir(parents=True, exist_ok=True)
    # Write header if file does not exist yet
    write_header = not log_file.is_file()
    with log_file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(
                [
                    "timestamp",
                    "recipient_email",
                    "subject",
                    "status",
                    "detail",
                ]
            )
        writer.writerow(
            [
                datetime.utcnow().isoformat(),
                contact.get("recipient_email", ""),
                payload.get("subject", ""),
                status,
                detail,
            ]
        )
