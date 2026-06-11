import os
import streamlit as st

from loader import load_contacts
from email_generator import render_template, enhance_with_llm
from email_sender import send_email
from logger import log_entry

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"

st.set_page_config(page_title="The Closer – Email Outreach", layout="centered")
st.title("🧊 The Closer – Email Outreach UI")

# ---------------------------------------------------------------------------
# Load contacts
# ---------------------------------------------------------------------------
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
contacts_path = os.path.join(project_root, "contacts.json")
if os.path.exists(contacts_path):
    contacts = load_contacts(contacts_path)
else:
    contacts = load_contacts(os.path.join(project_root, "contacts.csv"))

if not contacts:
    st.warning("No contacts available – check `contacts.json` or `contacts.csv` in the project root.")
    st.stop()


# Build a selector using a readable label for each contact
def contact_label(c):
    name = c.get("recipient_name") or c.get("recipient_email")
    company = c.get("company", "")
    role = c.get("role", "")
    return f"{name} – {role} @ {company}" if name else "Unnamed contact"


selected_index = st.selectbox(
    "Choose a contact",
    options=range(len(contacts)),
    format_func=lambda i: contact_label(contacts[i]),
)
contact = contacts[selected_index]

# ---------------------------------------------------------------------------
# Generate payload (optionally enhanced by LLM)
# ---------------------------------------------------------------------------
payload = render_template(contact)
if USE_LLM:
    if st.checkbox("Enable LLM rewrite (Groq)", value=False):
        payload = enhance_with_llm(payload)

st.subheader("📧 Generated Email")
st.markdown(f"**Subject:** {payload['subject']}")
# FIX: Capturing edited text area content back into the payload object dictionary
payload["body"] = st.text_area("Body", value=payload["body"], height=250)

# ---------------------------------------------------------------------------
# Action selection
# ---------------------------------------------------------------------------
mode = st.radio(
    "What to do with this email?", options=["draft", "send", "skip"], index=0
)

if st.button("Execute"):
    if mode == "skip":
        status = "skipped"
        # FIX: Matches structured logger.py schema mappings (Contact dataclass, EmailPayload dict, status string)
        log_entry(contact, payload, status, "Skipped by user via Streamlit UI")
        st.success("Contact skipped – nothing was sent.")
    else:
        # FIX: The positional/keyword arguments now align correctly with standard sender structures
        result = send_email(payload, mode)
        status = result.get("status", "error")
        log_entry(contact, payload, status, result.get("detail"))
        if status == "sent":
            st.success("✉️ Email successfully sent via SMTP.")
        elif status == "draft_created":
            st.info("✏️ Draft created (dry-run or Gmail draft placeholder).")
        else:
            st.error(f"❗️ Failed: {result.get('detail', 'unknown error')}")

st.caption("Logs are written to `outreach_log.csv` in the project root.")
