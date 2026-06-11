import streamlit as st
from loader import load_contacts
from email_generator import generate_email

st.set_page_config(page_title="The Closer – Email Draft Generator", layout="centered")

st.title("📧 The Closer – Personalized Email Drafts")

# Load contacts (user can provide path)
contact_path = st.text_input("Path to contacts file (JSON/CSV)", value="")
contacts = load_contacts(contact_path)

if not contacts:
    st.warning("No contacts found – using the built‑in sample list.")

# Create selector
contact_options = [
    f"{c.get('recipient_name', '?')} – {c['recipient_email']}" for c in contacts
]
selected_index = st.selectbox(
    "Choose a contact",
    options=range(len(contact_options)),
    format_func=lambda i: contact_options[i],
)
selected_contact = contacts[selected_index]

# Generate email
payload = generate_email(selected_contact)

st.subheader("Subject")
st.write(payload["subject"])

st.subheader("Body")
st.text_area("Email body", value=payload["body"], height=300)

if st.button("Send via SMTP (demo)"):
    st.info(
        "SMTP integration not configured – implement with `smtplib` or a service like SendGrid."
    )
