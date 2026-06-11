# Edge Cases Documentation for **The Closer**

---

## 1. General Edge‑Case Categories

| Category | Description | Typical Symptom | Mitigation |
|----------|-------------|----------------|------------|
| **Missing Configuration** | Required environment variables or `.env` entries are absent. | Script aborts with `KeyError` or `FileNotFoundError`. | Validate config at startup, provide clear error messages, fall back to safe defaults where possible. |
| **Empty / Malformed Input Data** | `contacts.json` or CSV is empty, malformed JSON, missing required fields, duplicate IDs. | Loader returns `[]` or raises `json.JSONDecodeError`. | Schema validation (pydantic), graceful exit with helpful message, optional fallback dummy contacts for demo. |
| **Invalid Email Addresses** | `email` field does not conform to RFC‑5322 (missing `@`, illegal characters). | SMTP rejects mail, or `email.utils.parseaddr` returns empty address. | Validate using `email_validator` or a regex; flag and skip problematic contacts. |
| **SMTP Connectivity Issues** | Network down, wrong host/port, TLS handshake failure, authentication error. | `smtplib.SMTPException` / timeout. | Retry logic with exponential back‑off, fallback to dry‑run mode, log detailed error. |
| **Template Rendering Errors** | Jinja2 template contains undefined variables or syntax errors. | `TemplateError` at generation time. | Early template validation, unit tests for each placeholder, default safe values. |
| **Large Contact Lists** | >10 000 contacts – memory or rate‑limit problems. | Slow execution, possible Out‑of‑Memory. | Stream processing (generator), batch sending, pagination, progress indicator. |
| **Unicode / Encoding Problems** | Names or content contain non‑ASCII characters. | Garbled output, UnicodeEncodeError when writing files or sending mail. | Use UTF‑8 everywhere, explicit encoding in file handling, `email.header.Header` for subject. |
| **Dry‑Run / Draft Mode Mismatch** | `DRY_RUN` flag not respected, emails actually sent during demo. | Unexpected real traffic. | Centralised guard in `email_sender.send_email` that checks the flag before any network call. |
| **Logging Failures** | `outreach_log.csv` cannot be opened (permission, disk full). | No audit trail, possible crash. | Open file with `a` mode, create with headers if missing, fallback to console logging. |
| **File‑Permission Errors** | Project directory is read‑only or user lacks write access. | All write operations fail. | Detect `PermissionError` early, provide instruction to adjust folder permissions. |

## 2. Phase‑Specific Edge Cases

### Phase 0 – Bootstrap
- **Dependency Installation Failure** – `pip install -r requirements.txt` exits with non‑zero code.
  - *Mitigation*: Pin versions, use a virtual environment, provide a `requirements.txt` hash for verification.

### Phase 1 – Loader
- **CSV delimiter mismatch** (comma vs semicolon). 
  - *Mitigation*: Detect delimiter automatically with `csv.Sniffer`.
- **Missing `name` field** – fallback to `email` as display name.

### Phase 2 – Email Generator
- **Missing placeholder** (`{{ first_name }}` not present in payload). 
  - *Mitigation*: Provide default empty string in the Jinja2 environment.

### Phase 3 – Preview & Confirmation
- **Terminal width overflow** – long email body wraps incorrectly.
  - *Mitigation*: Use `rich` `Panel` with auto‑wrap, truncate long lines for preview.

### Phase 4 – Sender
- **TLS/STARTTLS mismatch** – server expects STARTTLS but we start TLS directly.
  - *Mitigation*: Detect server capabilities with `ehlo()` and choose appropriate method.

### Phase 5 – Logger
- **CSV injection** – a field starts with `=`, `+`, `-`, or `@`.
  - *Mitigation*: Escape leading characters (`'=` → `'\='`).

### Phase 6 – Optional LLM Integration
- **LLM API quota exceeded** – returns HTTP 429.
  - *Mitigation*: Switch to deterministic fallback generator, log warning.

### Phase 7 – UI Extension (future)
- **Browser compatibility** – CSS grid not supported on older browsers.
  - *Mitigation*: Provide graceful fallback layout.

### Phase 8 – Production Deployment
- **Environment variable leakage** – `.env` accidentally committed.
  - *Mitigation*: Add `.env*` to `.gitignore`, enforce pre‑commit hook.

## 3. Validation Checklist
- [ ] All required env vars present (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `DRY_RUN`).
- [ ] Loader successfully parses at least one contact.
- [ ] Template renders without `UndefinedError`.
- [ ] Preview displays correctly in terminal.
- [ ] `send_email` respects `DRY_RUN` flag.
- [ ] Logging creates `outreach_log.csv` with correct headers.
- [ ] Errors are captured and logged, not uncaught exceptions.
- [ ] Unicode characters survive round‑trip (load → generate → send → log).

---

*Prepared to guide testing and hardening of each development phase.*
