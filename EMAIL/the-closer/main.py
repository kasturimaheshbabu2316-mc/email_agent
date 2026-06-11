# main.py
"""Entry point for The Closer application.
It orchestrates loading contacts, generating emails, previewing, obtaining user confirmation,
sending/drafting emails, and logging results. Opt‑out handling is built‑in.
"""

import os
from rich import print as rprint
from loader import load_contacts
from email_generator import render_template, enhance_with_llm
from email_sender import send_email
from logger import log_entry
from preview import preview_email, prompt_confirmation


def main():
    # Load contacts (default path)
    contacts = load_contacts()
    if not contacts:
        rprint("[red]No valid contacts found. Exiting.[/red]")
        return

    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    use_llm = os.getenv('USE_LLM', 'false').lower() == 'true'

    # ---------------------------------------------------
    # Opt‑out handling – skip contacts listed in opt_out.txt
    # ---------------------------------------------------
    opt_out_path = os.path.join(os.path.dirname(__file__), "..", "opt_out.txt")
    opt_out_emails = set()
    if os.path.isfile(opt_out_path):
        with open(opt_out_path, "r", encoding="utf-8") as f:
            opt_out_emails = {line.strip().lower() for line in f if line.strip()}

    for contact in contacts:
        # Skip if email is on the opt‑out list
        if contact.get("recipient_email", "").lower() in opt_out_emails:
            rprint(f"[yellow]Skipping {contact.get('recipient_email')} (opt‑out)" )
            log_entry(contact, {}, "opt_out")
            continue

        payload = render_template(contact)
        # Optional LLM enhancement
        if use_llm:
            payload = enhance_with_llm(payload)

        preview_email(payload['subject'], payload['body'])
        choice = prompt_confirmation()
        if choice == "skip":
            status = "skipped"
            log_entry(contact, payload, status)
            continue
        mode = "draft" if choice == "draft" else "send"
        result = send_email(payload, mode, dry_run)
        status = result.get('status', 'error')
        log_entry(contact, payload, status, result.get('detail'))

if __name__ == "__main__":
    main()
