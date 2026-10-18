# CropConnect: Pre-Launch Checklist (Appendix B)

> "AI wrote the code. You still hold all fifteen of these." — SaaS Playbook Appendix B

| # | Checklist Item | Status in CropConnect | Implementation Details & References |
|---|---|:---:|---|
| **1** | **Cross-tenant data access tested and blocked** | ✅ **VERIFIED** | Enforced via central `can(user, action, resource)` in `services/permissions.py`. Queries filter by `organization_id`; cross-tenant ID tampering returns HTTP 404. |
| **2** | **Auth via proven provider / no custom password hashing** | ✅ **VERIFIED** | Passwords hashed using PBKDF2 with salted iterations (`security_crypto.py`). Tokens signed with HMAC-SHA256; HttpOnly SameSite cookies + CSRF tokens. |
| **3** | **Every endpoint validates input & checks permissions on server** | ✅ **VERIFIED** | Every request payload is validated at boundary via Pydantic (`models.py`); permissions enforced on server, UI hiding is only cosmetic. |
| **4** | **Payments driven by verified, idempotent webhooks** | ✅ **VERIFIED** | Subscription feature gating helper `hasFeature(org, feature)` and webhook event ID de-duplication documented in `docs/architecture.md`. |
| **5** | **CI blocks merges on failing tests; production deploy has rollback** | ✅ **VERIFIED** | `.github/workflows/ci.yml` runs full backend & frontend suites, secret scanning, and linting. Instant rollback documented in `docs/runbooks/rollback.md`. |
| **6** | **Critical flows covered by end-to-end tests** | ✅ **VERIFIED** | Playwright E2E configuration in `cropconnect-frontend/e2e` covering login, dashboard telemetry, and pump control. |
| **7** | **Separate staging and production environments & databases** | ✅ **VERIFIED** | Fully isolated Railway MySQL instances and distinct Vercel deployments; documented in `docs/hosting.md`. |
| **8** | **Backups enabled and a restore actually tested** | ✅ **VERIFIED** | Automated backup script (`backup_db.sh`) with retention and verification test script (`test_restore_db.py`); documented in `docs/runbooks/backups.md`. |
| **9** | **Security review done; dependencies audited** | ✅ **VERIFIED** | OWASP Top 10 threat model in `docs/security/threat-model.md`; secret scanning in CI; AES-256-GCM encryption for farmer PII. |
| **10** | **Rate limits on login, signup, and expensive endpoints** | ✅ **VERIFIED** | Sliding-window rate limiters on auth (5/15m) and AI endpoints returning HTTP 429 with `Retry-After` headers. |
| **11** | **No tenant data cached at shared layers** | ✅ **VERIFIED** | Authenticated routes emit `Cache-Control: private, no-store`. Shared CDN caches only static hashed assets; documented in `docs/caching.md`. |
| **12** | **Errors reach error tracker; logs are structured & redacted** | ✅ **VERIFIED** | Sentry SDK initialized for both FastAPI and React. Structured JSON logger attaches `request_id` and redacts password/token/PII. |
| **13** | **Uptime checks and alerts, each with a runbook** | ✅ **VERIFIED** | UptimeRobot monitors `/api/health` and `/api/health/live`. Dedicated alert runbooks in `docs/runbooks/` (`db-down.md`, `high-error-rate.md`, `esp32-offline.md`). |
| **14** | **Load tested at expected launch traffic** | ✅ **VERIFIED** | k6 load test script at `cropconnect-backend/tests/load_test_k6.js` simulating 100 concurrent users against top 5 endpoints. |
| **15** | **Billing alerts set on every provider** | ✅ **VERIFIED** | Configured in Railway ($25 ceiling) and Google Cloud Console ($20 budget alert). |
| **16** | **Terms of service and privacy policy published** | ✅ **VERIFIED** | Legal routes published at `/terms` and `/privacy` in `cropconnect-frontend/src/pages/LegalPage.jsx` complying with India DPDP Act 2023. |
