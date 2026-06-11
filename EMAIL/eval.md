# Evaluation Document for **The Closer**

---

## Overview
The `eval.md` file defines the verification and validation strategy for each development phase of **The Closer**. It is meant to be used by developers and reviewers to ensure that the implementation meets functional, non‑functional, and safety requirements before moving to the next phase.

## Phase‑Wise Evaluation Checklist

| Phase | Success Criteria | Test Type | Example Test / Metric |
|-------|------------------|-----------|-----------------------|
| **0 – Bootstrap** | All dependencies installed, virtual environment activated, `.env.example` present. | Manual / Automation script | `pip install -r requirements.txt` exits with code 0; `python -c "import dotenv"` succeeds. |
| **1 – Loader** | Contacts are loaded correctly from JSON/CSV, schema validated, fallback list used when file missing. | Unit tests | `test_loader_loads_json`, `test_loader_fallback_to_dummy`, `test_loader_invalid_schema_raises`. |
| **2 – Email Generator** | Template renders without errors, placeholders replaced, output respects UTF‑8. | Unit tests + snapshot test | Render sample payload and compare against stored snapshot; ensure no `UndefinedError`. |
| **3 – Preview & Confirmation** | Email preview displays correctly in terminal, user can approve/reject. | Integration test (mock stdin) | Simulate user input `y` and verify that `send_email` is called. |
| **4 – Sender** | Emails are sent only when `DRY_RUN=False`; SMTP errors are caught and logged; proper TLS/STARTTLS handling. | Functional test + mock SMTP server | Use `smtplib.SMTP` mock to assert `sendmail` called with correct arguments only in non‑dry mode. |
| **5 – Logger** | `outreach_log.csv` is created with headers, each row contains required columns, no CSV injection. | Unit test + security check | Write a log entry with a dangerous payload (`=SUM(A1:A2)`) and verify it is escaped. |
| **6 – Optional LLM Integration** *(if enabled)* | LLM API called with correct prompt, response parsed, fallback on quota errors. | Mock API test | Simulate HTTP 429 and verify deterministic fallback generator runs. |
| **7 – UI Extension** *(future)* | Web UI loads, responsive layout works on desktop & mobile, form validation passes. | End‑to‑end Selenium test | Submit form with valid data, check email preview appears. |
| **8 – Production Deployment** | Docker image builds, environment variables are not leaked, health‑check endpoint returns 200. | CI pipeline test | `docker build . && docker run -e DRY_RUN=1 image` exits cleanly. |

## General Evaluation Procedure
1. **Run Unit Tests** – Execute `pytest -q` in the project root. All tests must pass.
2. **Run Integration Tests** – Run the `test_integration.py` script which performs a full end‑to‑end dry‑run of the workflow.
3. **Static Analysis** – Use `ruff`/`flake8` for linting and `mypy` for type checking.
4. **Security Review** – Verify that no secrets are printed in logs and `.env*` is ignored.
5. **Performance Check** – Ensure loading >10 000 contacts completes within 5 seconds (benchmark script provided).
6. **User Acceptance** – Demo the preview and send flow to a stakeholder; collect sign‑off.

## Acceptance Checklist (to be filled by reviewer)
- [ ] All unit and integration tests pass.
- [ ] Linter reports 0 errors.
- [ ] No hard‑coded credentials in source files.
- [ ] Documentation (`README.md`, `architecture.md`, `edge-case.md`, `eval.md`) is up‑to‑date.
- [ ] Deployment script (`docker-compose.yml` if present) builds without errors.
- [ ] Stakeholder approved the demo.

---

*This document should be version‑controlled alongside the source code and updated whenever a new phase or feature is added.*
