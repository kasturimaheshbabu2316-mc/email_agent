import os
from jinja2 import Template
from typing import Any, Dict, TypedDict

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

# Deterministic template matching problem.md requirements (no redundant Subject header)
TEMPLATE_STR = """Hi {{ recipient_name }},

I noticed {{ company }} is hiring for {{ role }}. {{ personalization_note }}

I'm {{ candidate_name }}, and I've been working on {{ candidate_background }}.

Would you be open to a quick chat or looking at my profile?

Best,
{{ candidate_name }}
{{ portfolio_url }}"""

def render_template(contact: Dict[str, Any]) -> EmailPayload:
    """Renders a base email using the contact details and a Jinja template."""
    # 1. Generate the standard subject line
    subject_line = f"Quick note on the {contact['role']} role"
    
    # 2. Render the template text for the message body
    template = Template(TEMPLATE_STR)
    body = template.render(
        recipient_name=contact.get('recipient_name', ''),
        company=contact['company'],
        role=contact['role'],
        personalization_note=contact.get('personalization_note', ''),
        candidate_name=contact['candidate_name'],
        candidate_background=contact['candidate_background'],
        portfolio_url=contact.get('portfolio_url', ''),
    )
    
    return {"subject": subject_line, "body": body.strip()}

def _rewrite_body_with_llm(body: str) -> str:
    try:
        from llm_client import rewrite_body
        return rewrite_body(body)
    except ImportError:
        return body + "\n\n(Polished by fallback LLM)"


def enhance_with_llm(payload: EmailPayload) -> EmailPayload:
    """Polishes the rendered email text using an LLM if USE_LLM=true."""
    use_llm = os.getenv('USE_LLM', 'false').lower() == 'true'
    if not use_llm:
        return payload

    try:
        new_body = _rewrite_body_with_llm(payload['body'])
        return {"subject": payload['subject'], "body": new_body}
    except Exception:
        return payload