# The Closer – Cold Email Writer & Send Bot

## Overview
A lightweight, modular Python application that generates, previews, and safely sends personalized cold outreach emails.

## Quick Start
```bash
# Clone / copy repository
# (already in place)

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# edit .env with your credentials

# Run demo (dry‑run by default)
python main.py
```

## Project Structure
```
the-closer/
├── main.py                 # Orchestrates the workflow
├── loader.py                # Loads contacts from JSON/CSV
├── email_generator.py       # Renders email templates (with optional LLM)
├── email_sender.py          # Sends or drafts emails
├── logger.py                # CSV logger & console summary
├── llm_client.py            # Groq LLM wrapper (optional)
├── ui.py                    # Optional Streamlit front‑end
├── contacts.json            # Sample input data
├── outreach_log.csv         # Log file (generated at runtime)
├── .env.example            # Environment variable template
├── requirements.txt         # Dependencies
└── README.md                # This file
```
```

## Production Deployment

### Dockerfile
```dockerfile
# Dockerfile for The Closer
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
```

### Building and Running
```bash
# Build the image
docker build -t the-closer .

# Run the container (dry‑run by default)
docker run --env-file .env -it the-closer
```

Refer to the `README.md` for usage details.

