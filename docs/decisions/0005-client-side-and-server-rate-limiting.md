# 5. Dual-Layer Rate Limiting and LLM Cost Protection

## Context
CropConnect exposes public API endpoints (signup, login, enquiries) and expensive AI operations (Gemini crop diagnosis, OCR, Mandi price lookups). Without rate limiting, the platform is vulnerable to brute-force credential stuffing, API spam, and runaway LLM billing.

## Decision
We implemented a sliding-window rate limiter:
- Strictest on Auth: 5 attempts per 15 min per IP for signup/password reset.
- AI Operations: Per-user sliding-window limits returning `HTTP 429` with `Retry-After` header.
- Public Endpoints: 5 requests per 5 minutes for enquiries.
- Client-Side Handling: React frontend intercepts 429 responses and displays user-friendly countdown cooldowns.

## Alternatives Considered
- **Unbounded Access**: Rejected due to high risk of API credit exhaustion.
- **External API Gateway (Cloudflare WAF Rate Limiting)**: Retained as edge protection, but application-level rate limiting is enforced on the server as the ultimate source of truth.

## Consequences
- **Positive**: Hard spending cap protection, elimination of brute-force attacks, predictable monthly operational costs.
- **Negative**: High-frequency legitimate users must wait for window resets during heavy testing.
