# CropConnect: Threat Model & Security Architecture (Layer 10)

## 1. Protected Assets & Criticality

| Asset | Description | Impact if Compromised |
|---|---|---|
| **Farmer PII** | Phone numbers, full names, village, district, land size | Severe (Privacy violation under India DPDP Act 2023, farmer trust loss) |
| **Farmer Credentials** | Email addresses, password hashes, auth tokens, session cookies | Critical (Unauthorized takeover of irrigation pumps & farm systems) |
| **Physical Pump Actuators** | High-voltage irrigation water pumps & field relays | Catastrophic (Flooding crops, equipment burnout, physical damage) |
| **Sensor Telemetry Data** | Time-series soil moisture, temperature, microclimate readings | Moderate (Competitor intelligence or corrupted crop planning) |
| **Third-Party API Keys** | Gemini AI key, Data.gov.in key, SMTP credentials, Sentry DSN | Severe (Financial draining via API quota exhaustion or data theft) |

---

## 2. Attack Surface & Entry Points
1. **Public Web Forms**: `/api/auth/signup`, `/api/auth/login`, `/api/auth/password-reset-request`, `/api/enquiries`.
2. **IoT Ingestion Endpoint**: `/api/telemetry/ingest` (unauthenticated cellular edge or device API key).
3. **Hardware Command Poll**: `/api/esp32/relay-command` (polled by physical ESP32 microcontrollers).
4. **File Upload Endpoint**: `/api/vision/detect`, `/crop-scan` (leaf image file ingestion for disease diagnosis).
5. **Authenticated REST Endpoints**: `/api/pumps/*`, `/api/sensors/*`, `/api/farm/*`, `/api/ai/*`.

---

## 3. OWASP Top 10 Threat Analysis & Mitigations

| Threat (OWASP Top 10) | Entry Point | Likelihood | Impact | Existing Mitigations in Code | Missing / Recommended Hardening |
|---|---|:---:|:---:|---|---|
| **A01: Broken Access Control (IDOR)** | `/api/pumps/{id}`, `/api/sensors/history` | High | Critical | Central `can(user, action, resource)` checks in `permissions.py`; database queries filter strictly by `user_id` / `organization_id`; cross-tenant requests return 404. | Automated test suite replaying permission matrices against all endpoints. |
| **A02: Cryptographic Failures** | Database persistence, session transport | Medium | High | PII encrypted using AES-256-GCM (`CROP_DATA_SECRET_KEY`); passwords hashed with PBKDF2; HTTPS enforced in transit; tokens signed with HMAC-SHA256. | KMS-managed automatic key rotation. |
| **A03: Injection (SQL / NoSQL / Command)** | Form inputs, telemetry payload, search bars | Medium | Critical | Parameterized queries with mysql-connector / bound variables; zero raw string concatenation; strict Pydantic input schemas. | Automated SQL injection scanner in CI. |
| **A04: Insecure Design** | Unbounded AI queries, brute force login | High | High | Dual sliding-window rate limiters on auth (5/15m) and AI endpoints; hard spending caps on paid LLM APIs. | Automated bot protection (Cloudflare Turnstile on public signup). |
| **A05: Security Misconfiguration** | HTTP headers, CORS, debug endpoints | Medium | High | Security headers middleware (`CSP`, `nosniff`, `DENY`, `strict-origin`); CORS restricted to exact Vercel origins; debug routes disabled in production. | Automated header scanner in CI. |
| **A06: Vulnerable Dependencies** | Python & npm dependencies | Medium | High | Dependabot automated alerts; CI environment validation check; lockfiles committed (`package-lock.json`, `requirements.lock.txt`). | Integration of `audit-ci` / `pip-audit` in GitHub Actions. |
| **A07: Identification & Auth Failures** | Login & password reset flows | High | Critical | SameSite HttpOnly cookies; double-submit CSRF token validation; 6-digit email verification codes expiring in 24h; password reset links expiring in 15m. | Optional WebAuthn / FIDO2 biometric authentication for mobile farmers. |
| **A08: Software & Data Integrity Failures** | Malicious file upload via `/crop-scan` | Medium | High | Image payload validated on server: binary magic bytes checked, file size capped at 10MB, strictly processed through PIL/OpenCV without shell execution. | ClamAV antivirus scanning container for uploads. |
| **A09: Security Logging & Monitoring Failures** | Silent errors or sensitive log leaking | Medium | Medium | Sentry integration with environment separation; structured logger; automatic redaction of password, token, and secret fields. | SIEM forwarding for suspicious login spikes. |
| **A10: Server-Side Request Forgery (SSRF)** | Mandi price queries, webhook callers | Low | High | External HTTP client (`http_client.py`) restricts destinations to strict allowlist (data.gov.in, open-meteo.com, googleapis.com); zero user-supplied hostnames fetched. | Outbound egress filtering at the network level. |

---

## 4. Data Protection & Privacy Verification (DPDP Compliance)
- [x] **Field-Level Encryption**: Sensitive PII columns (`name`, `phone`, `village`, `district`, `state`) are encrypted at rest with AES-256-GCM before writing to the database.
- [x] **Log Sanitization**: Request parameters and log handlers redact any keys matching `password`, `token`, `secret`, `authorization`.
- [x] **Right to Data Portability**: Users can download all stored personal telemetry and farm configuration in structured JSON via `GET /api/auth/export-data`.
- [x] **Right to Erasure**: Users can permanently anonymize personal records and delete their account via `POST /api/auth/delete-account`.
