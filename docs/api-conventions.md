# CropConnect: API Conventions & Standards (Layer 5)

## 1. URL & Naming Conventions
- All backend routes are prefixed with `/api/` (except root `/` and health checks `/health`, `/health/live`).
- Resource naming uses lowercase plural nouns: `/api/pumps`, `/api/sensors`, `/api/enquiries`.
- Action endpoints use RESTful HTTP verbs where possible:
  - `GET /api/pumps` — List pumps
  - `POST /api/pumps` — Create pump
  - `GET /api/pumps/{id}` — Get single pump
  - `PUT /api/pumps/{id}` — Replace pump
  - `PATCH /api/pumps/{id}` — Partial update pump
  - `DELETE /api/pumps/{id}` — Delete pump
- Specific sub-actions use kebab-case verbs: `/api/pumps/{id}/toggle-mode`, `/api/auth/password-reset-request`.

---

## 2. Standard Unified Error Format
Every API error response follows a single predictable schema:

```json
{
  "ok": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested sensor channel could not be found.",
    "details": [],
    "requestId": "a8f3b9c1"
  }
}
```

### Standard Error Codes:
- `VALIDATION_ERROR` (422 / 400): Malformed input payload or boundary validation failure.
- `UNAUTHENTICATED` (401): Missing, expired, or invalid session cookie / auth token.
- `PERMISSION_DENIED` (403): User lacks permission for the requested action under RBAC.
- `RESOURCE_NOT_FOUND` (404): Resource ID does not exist or belongs to another tenant.
- `RATE_LIMIT_EXCEEDED` (429): Request limit reached; includes `Retry-After` header.
- `INTERNAL_SERVER_ERROR` (500): Unhandled exception; stack trace sent to Sentry, sanitized message to user.
- `SERVICE_UNAVAILABLE` (503): Database or downstream upstream dependency unreachable.

---

## 3. Boundary Input Validation (Pydantic)
- **Zero Raw Requests**: Every input payload is declared as a Pydantic model (`models.py`) with strict field constraints (`min_length`, `max_length`, regex patterns, bounds).
- **Sanitization**: Strings are automatically stripped, emails normalized to lowercase, and unsupported fields rejected (`extra = "forbid"`).

---

## 4. Standardized Pagination
List endpoints with potential unbounded growth (telemetry history, audit events, chat history) implement cursor or limit-offset pagination:

```json
{
  "ok": true,
  "data": [...],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "totalCount": 240,
    "hasMore": true,
    "nextCursor": "eyJsYXN0X2lkIjogNTB9"
  }
}
```

---

## 5. Auth & Tenant Context Resolution
FastAPI dependency injection resolves the authenticated identity and organizational context in every protected handler:

```python
from services.deps import get_current_user

@router.get("/api/sensors/history")
def get_sensor_history(
    current_user: tuple[int, str] = Depends(get_current_user),
    limit: int = 50,
):
    user_id, email = current_user
    # Handler uses user_id / org_id to strictly scope database queries
    return get_tenant_sensor_readings(user_id, limit=limit)
```

---

## 6. HTTP Status Codes Matrix

| Code | Usage Scenario |
|---|---|
| **200 OK** | Successful read, update, or action execution |
| **201 Created** | Successful creation of a resource (e.g. signup, new device) |
| **400 Bad Request** | Malformed parameters, missing CSRF token, or invalid business state |
| **401 Unauthorized** | Missing or expired credentials |
| **403 Forbidden** | Authenticated, but lacking RBAC permission or invalid origin |
| **404 Not Found** | Resource does not exist or belongs to another organization |
| **422 Unprocessable** | Pydantic schema validation error |
| **429 Too Many Requests** | Rate limit window exceeded; returns `Retry-After` header |
| **500 Internal Error** | Unexpected crash logged to Sentry |
| **503 Unavailable** | Database pool degraded or downstream API offline |
