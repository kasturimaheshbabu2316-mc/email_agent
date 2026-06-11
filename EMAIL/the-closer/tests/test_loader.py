import json, csv, os, tempfile
import sys
import pytest

# Add the project root to sys.path for import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from loader import load_contacts

def write_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def write_csv(rows, path):
    if not rows:
        return
    fieldnames = rows[0].keys()
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def test_load_contacts_json(tmp_path):
    contacts = [
        {
            "recipient_name": "John Doe",
            "recipient_email": "john@example.com",
            "company": "Acme",
            "role": "Engineer",
            "candidate_name": "Your Name",
            "candidate_background": "Python dev",
            "portfolio_url": "https://github.com/yourname"
        },
        {
            "recipient_name": "Bad Contact",
            "recipient_email": "",
            "company": "Acme",
            "role": "Engineer",
            "candidate_name": "Your Name",
            "candidate_background": "Python dev",
            "portfolio_url": "https://github.com/yourname"
        }
    ]
    json_path = tmp_path / "contacts.json"
    write_json(contacts, str(json_path))
    loaded = load_contacts(str(json_path))
    assert len(loaded) == 1  # invalid entry filtered out
    assert loaded[0]["recipient_email"] == "john@example.com"

def test_load_contacts_csv(tmp_path):
    contacts = [
        {
            "recipient_name": "Jane",
            "recipient_email": "jane@example.com",
            "company": "Beta",
            "role": "Analyst",
            "candidate_name": "Your Name",
            "candidate_background": "Data analyst",
            "portfolio_url": "https://github.com/yourname"
        }
    ]
    csv_path = tmp_path / "contacts.csv"
    write_csv(contacts, str(csv_path))
    loaded = load_contacts(str(csv_path))
    assert len(loaded) == 1
    assert loaded[0]["recipient_email"] == "jane@example.com"

def test_load_contacts_fallback(tmp_path):
    # Pass an empty path to trigger fallback hard‑coded list
    loaded = load_contacts("")
    assert isinstance(loaded, list)
    assert len(loaded) >= 1
    # Verify required keys exist
    required = ["recipient_email", "company", "role", "candidate_name", "candidate_background"]
    for key in required:
        assert key in loaded[0]
