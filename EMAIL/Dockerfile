# Dockerfile for The Closer
# Build a lightweight container that runs the application in dry‑run mode by default.
# Adjust environment variables via --env-file or -e flags when running.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

ENV PYTHONUNBUFFERED=1

# Default command runs the CLI entry point
CMD ["python", "the-closer/main.py"]
