# app.py
"""Streamlit UI for The Closer email generator.
This app loads contacts, lets the user pick a contact, renders the email
using the deterministic template (templates/email_template.txt) and
optionally enhances the body with the LLM (if USE_LLM=true).
"""

import os
import streamlit as st
from pathlib import Path

# Local imports (relative to project root)
from loader import load_contacts
from email_generator import generate_email, enhance_with_llm

st.set_page_config(page_title="The Closer", layout="centered")

st.title("🚀 The Closer – Email Draft Generator")

# Load contacts – allow optional path via input or env var
default_path = os.getenv("CONTACTS_PATH", "")
path_input = st.text_input("Path to contacts file (JSON or CSV)", value=default_path)

contacts = load_contacts(path_input)
if not contacts:
    st.warning("No contacts found – using built‑in sample contacts.")
    contacts = load_contacts("")

# Show a selector for contacts
options = [f"{c.get('recipient_name', 'Unnamed')} – {c.get('company', '')}" for c in contacts]
selected_idx = st.selectbox("Select a contact", range(len(options)), format_func=lambda i: options[i])
contact = contacts[selected_idx]

# Generate deterministic email
payload = generate_email(contact)

# Optional LLM enhancement
if st.checkbox("Enhance body with LLM (requires API key and USE_LLM=true)"):
    payload = enhance_with_llm(payload)

st.subheader("Subject")
st.code(payload["subject"], language="text")

st.subheader("Body")
st.code(payload["body"], language="markdown")

if st.button("Copy to clipboard"):
    st.markdown(
        f"<script>navigator.clipboard.writeText(`Subject: {payload['subject']}\n\n{payload['body']}`)</script>",
        unsafe_allow_html=True,
    )
    st.success("Copied to clipboard!")
