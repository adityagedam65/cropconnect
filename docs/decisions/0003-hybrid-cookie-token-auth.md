# 3. Hybrid Cookie & Bearer Token Authentication with CSRF Protection

## Context
CropConnect serves both browser-based users on web dashboards and programmatic API consumers/IoT setups. We needed strong protection against XSS and CSRF without breaking SPA usability.

## Decision
We implemented a **hybrid authentication model**:
1. For browsers: An `HttpOnly`, `SameSite=None` (or `Lax`), `Secure` auth cookie (`cropconnect_auth`) coupled with a double-submit CSRF cookie/header (`x-csrf-token`).
2. For mobile/hardware clients: An `Authorization: Bearer <token>` header signed with HMAC-SHA256 (`CROP_AUTH_TOKEN_SECRET`).
3. Cross-origin requests validate against `FRONTEND_ORIGINS` to block unauthorized origins.

## Alternatives Considered
- **Pure LocalStorage Bearer Token**: Rejected due to high vulnerability to XSS token theft.
- **Third-party Auth (Clerk / Auth0)**: Considered, but rejected to maintain self-contained infrastructure, avoid per-user SaaS subscription costs for Indian farmers, and permit offline SIM800L device key validation.

## Consequences
- **Positive**: Resilient against both CSRF and XSS; zero dependency on external authentication SaaS.
- **Negative**: Requires strict cookie configuration across cross-site staging and production domains.
