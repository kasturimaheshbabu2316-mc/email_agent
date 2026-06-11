# loader.py
"""Contact Loader Module
Loads contact records from JSON, CSV, or fallback hard‑coded list.
"""
import json
import csv
import os
from typing import List, Dict

# Define required fields
REQUIRED_FIELDS = [
    "recipient_email",
    "company",
    "role",
    "candidate_name",
    "candidate_background",
]

def _validate_contact(record: Dict) -> bool:
    """Return True if record contains all required fields."""
    return all(record.get(field) for field in REQUIRED_FIELDS)

def load_contacts(path: str = "") -> List[Dict]:
    """Load contacts from a given path.
    - If path ends with .json → parse JSON list.
    - If path ends with .csv → parse CSV rows.
    - If path is empty or loading fails → return a hard‑coded sample list.
    """
    contacts: List[Dict] = []
    if path and os.path.isfile(path):
        try:
            if path.lower().endswith('.json'):
                with open(path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        contacts = loaded
                    else:
                        print(f"[loader] Expected a JSON list in {path}, but got {type(loaded).__name__}.")
                        contacts = []
            elif path.lower().endswith('.csv'):
                with open(path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    contacts = [row for row in reader]
        except Exception as e:
            print(f"[loader] Failed to read {path}: {e}")
            contacts = []
    # Fallback hard‑coded sample if nothing loaded
    if not contacts:
        contacts = [
            {
                "recipient_name": "Priya Sharma",
                "recipient_email": "priya@example.com",
                "company": "Acme AI",
                "role": "Backend Engineering Intern",
                "job_url": "https://example.com/job",
                "personalization_note": "Company recently launched an AI workflow automation product",
                "candidate_name": "Your Name",
                "candidate_background": "Python developer interested in automation and AI agents",
                "portfolio_url": "https://github.com/yourname",
            },
            {
                "recipient_name": "Alex Johnson",
                "recipient_email": "alex@example.com",
                "company": "BetaTech",
                "role": "Data Engineer",
                "job_url": "https://example.com/job2",
                "personalization_note": "BetaTech open‑source data pipeline project",
                "candidate_name": "Your Name",
                "candidate_background": "Data pipelines and ETL automation",
                "portfolio_url": "https://github.com/yourname",
            },
        ]
    # Filter out invalid contacts
    valid_contacts = [c for c in contacts if _validate_contact(c)]
    if len(valid_contacts) < len(contacts):
        print(f"[loader] Skipped {len(contacts) - len(valid_contacts)} invalid contact(s).")
    return valid_contacts
