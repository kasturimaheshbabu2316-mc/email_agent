import os
from jinja2 import Template
from typing import Any, Dict, TypedDict
from pathlib import Path


class Contact(TypedDict):
    recipient_name: str
    recipient_email: str
    company: str
    role: str
    job_url: str
    personalization_note: str
    candidate_name: str
    candidate_background: str
    portfolio_url: str


class EmailPayload(TypedDict):
    subject: str
    body: str


# Deterministic template matching problem.md requirements (body only, subject handled separately)
TEMPLATE_PATH = Path(__file__).parent / "templates" / "email_template.txt"
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    TEMPLATE_STR = f.read()


def generate_email(contact: Dict[str, Any]) -> EmailPayload:
    """Generate a deterministic email payload for a given contact.

    The subject line is constructed from the contact's role, and the body
    is rendered from a Jinja2 template that excludes any subject header.
    This matches the Phase2 specification in the implementation plan.
    """
    subject_line = f"Quick note on the {contact['role']} role"
    template = Template(TEMPLATE_STR)
    body = template.render(
        recipient_name=contact.get("recipient_name", ""),
        company=contact["company"],
        role=contact["role"],
        personalization_note=contact.get("personalization_note", ""),
        candidate_name=contact["candidate_name"],
        candidate_background=contact["candidate_background"],
        portfolio_url=contact.get("portfolio_url", ""),
    )
    return {"subject": subject_line, "body": body.strip()}


# Backwards‑compatible alias (optional)
def render_template(contact: Dict[str, Any]) -> EmailPayload:
    """Legacy wrapper for existing imports; forwards to ``generate_email``."""
    return generate_email(contact)


def enhance_with_llm(payload: EmailPayload) -> EmailPayload:
    """Placeholder for Groq LLM enhancement. Returns payload unchanged if not configured.
    The actual implementation lives in llm_client.py and is called only when USE_LLM=true.
    """
    use_llm = os.getenv("USE_LLM", "false").lower() == "true"
    if not use_llm:
        return payload
    try:
        from llm_client import rewrite_body

        new_body = rewrite_body(payload["body"])
        return {"subject": payload["subject"], "body": new_body}
    except Exception:
        # In case of failure, fallback to original payload
        return payload
