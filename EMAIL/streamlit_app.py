"""Streamlit front-end for The Closer – Cold Email Writer & Send Bot.

This app bundles contact loading, email generation (with optional LLM rewrite),
preview & editing, sending/drafting, and logging into a single UI.
"""

import os
import sys
from pathlib import Path

# Ensure the-closer package is importable
sys.path.insert(0, str(Path(__file__).parent / "the-closer"))

import streamlit as st

from loader import load_contacts
from email_generator import render_template, enhance_with_llm
from email_sender import send_email
from logger import log_entry

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="The Closer – Email Outreach",
    page_icon="📧",
    layout="centered",
)

st.title("📧 The Closer – Cold Email Writer & Send Bot")
st.markdown(
    "Generate personalised outreach emails, preview & edit them, then send or draft."
)

# ---------------------------------------------------------------------------
# Configuration sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    dry_run = st.checkbox(
        "Dry run (simulate – no external calls)",
        value=os.getenv("DRY_RUN", "true").lower() == "true",
        help="When checked, no email is actually sent or drafted.",
    )

    use_llm = st.checkbox(
        "Use LLM rewrite (Groq)",
        value=os.getenv("USE_LLM", "false").lower() == "true",
        help="When checked, the email body will be rewritten via the LLM client.",
    )

    st.divider()
    st.markdown("**Contact source**")

    contact_source = st.radio(
        "Load contacts from:",
        options=["Default sample data", "Upload file"],
        index=0,
    )

    uploaded_file = None
    if contact_source == "Upload file":
        uploaded_file = st.file_uploader(
            "Upload contacts.json or contacts.csv",
            type=["json", "csv"],
        )

    st.divider()
    st.caption(
        "Set **SMTP_HOST**, **SMTP_USER**, **SMTP_PASSWORD** in `.env` "
        "for real sending.  The default dry‑run mode is safe."
    )

# ---------------------------------------------------------------------------
# Load contacts
# ---------------------------------------------------------------------------
contacts = []

if uploaded_file is not None:
    # Save the uploaded file temporarily and load it
    tmp_path = Path(__file__).parent / "_uploaded_contacts"
    tmp_path.write_bytes(uploaded_file.getbuffer())
    contacts = load_contacts(str(tmp_path))
    tmp_path.unlink(missing_ok=True)
else:
    # Try project-level contacts.json, then fallback to hardcoded sample data
    for candidate in [
        Path(__file__).parent / "contacts.json",
        Path(__file__).parent / "contacts.csv",
    ]:
        if candidate.exists():
            contacts = load_contacts(str(candidate))
            break
    if not contacts:
        contacts = load_contacts()  # fallback to hardcoded sample list

if not contacts:
    st.warning("No contacts found.  Please upload a contacts file.")
    st.stop()

# ---------------------------------------------------------------------------
# Contact selector
# ---------------------------------------------------------------------------
st.subheader("🎯 Select a Contact")


def contact_label(c):
    """Human-readable label for a contact."""
    name = c.get("recipient_name") or c.get("recipient_email", "?")
    company = c.get("company", "")
    role = c.get("role", "")
    parts = [name]
    if company:
        parts.append(f"@ {company}")
    if role:
        parts.append(f"– {role}")
    return " ".join(parts)


selected_idx = st.selectbox(
    "Choose a contact to generate an email for:",
    options=range(len(contacts)),
    format_func=lambda i: contact_label(contacts[i]),
)
contact = contacts[selected_idx]

# ---------------------------------------------------------------------------
# Generate email
# ---------------------------------------------------------------------------
st.subheader("✉️ Generated Email")

payload = render_template(contact)

if use_llm:
    with st.spinner("Rewriting body with LLM…"):
        payload = enhance_with_llm(payload)

st.markdown(f"**Subject:** {payload['subject']}")

edited_body = st.text_area(
    "Body (editable – changes are used when sending):",
    value=payload["body"],
    height=300,
)
payload["body"] = edited_body

# ---------------------------------------------------------------------------
# Action buttons
# ---------------------------------------------------------------------------
st.subheader("🚀 Action")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

send_clicked = col1.button("📤 Send", type="primary")
draft_clicked = col2.button("📝 Draft")
preview_clicked = col3.button("👁️ Preview")
skip_clicked = col4.button("⏭️ Skip")

# Preview in an expander (cleaner than a popup)
if preview_clicked:
    with st.expander("📬 Full Email Preview", expanded=True):
        st.markdown(f"**To:** {contact.get('recipient_email', 'N/A')}")
        st.markdown(f"**Subject:** {payload['subject']}")
        st.markdown("---")
        st.markdown(payload["body"])

if send_clicked:
    result = send_email(payload, mode="send", dry_run=dry_run)
    status = result.get("status", "error")
    detail = result.get("detail", "")
    log_entry(contact, payload, status, detail)
    if status == "sent":
        st.success(f"✅ Email sent successfully!  ({detail})")
    elif status == "draft_created":
        st.info(f"📝 Draft created.  ({detail})")
    else:
        st.error(f"❌ Failed to send: {detail}")

if draft_clicked:
    result = send_email(payload, mode="draft", dry_run=dry_run)
    status = result.get("status", "error")
    detail = result.get("detail", "")
    log_entry(contact, payload, status, detail)
    if status == "draft_created":
        st.info(f"📝 Draft created.  ({detail})")
    else:
        st.error(f"❌ Failed to create draft: {detail}")

if skip_clicked:
    log_entry(contact, payload, "skipped", "Skipped by user via Streamlit UI")
    st.success("⏭️ Contact skipped – nothing was sent.")

# ---------------------------------------------------------------------------
# Log viewer
# ---------------------------------------------------------------------------
st.divider()
st.subheader("📋 Outreach Log")

log_path = os.getenv("LOG_FILE", "outreach_log.csv")
if Path(log_path).exists():
    with open(log_path, encoding="utf-8") as f:
        log_content = f.read()
    st.text_area("Log content (read‑only):", value=log_content, height=150)
else:
    st.caption(
        "No log file found yet.  It will be created when you send, draft, or skip."
    )
