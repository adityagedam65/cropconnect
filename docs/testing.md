# CropConnect: Testing Strategy & Standards (Layer 8)

## 1. The Three-Level Testing Pyramid

CropConnect enforces three automated testing tiers across the repository:

```
          / \
         /   \     E2E Tests (Playwright) — 5 Critical User Flows
        /     \    -------------------------------------------------
       /       \   Integration Tests — API Endpoints + Real Test DB
      /         \  -------------------------------------------------
     /           \ Unit Tests — Business Logic & Domain Services (/services)
```

### Level 1: Unit Tests
- **Scope**: Individual algorithms and domain helpers in `/services`, `/lib`, and `security_crypto.py`.
- **Target Coverage**: 75–85% on critical business logic (encryption, sensor threshold calculations, rate limit counters, permission resolution).
- **Tooling**: Python `unittest` / `pytest` for backend; `vitest` for frontend.
- **Execution**: Instant (< 5 seconds total).

### Level 2: Integration Tests
- **Scope**: FastAPI route handlers interacting with the relational database and middleware stack.
- **Database Rule**: Run against a real test database container (MySQL/Docker in CI), never in-memory mock dictionaries that mask constraint violations.
- **Scenarios Covered**:
  - Unauthenticated requests receive `401 Unauthorized`.
  - Missing permissions receive `403 Forbidden`.
  - Cross-tenant ID tampering returns `404 Not Found` (never leaking tenant data).
  - Malformed payload yields standard `422/400 Validation Error`.

### Level 3: End-to-End (E2E) Browser Tests
- **Tooling**: Playwright (`cropconnect-frontend/playwright.config.js`).
- **5 Critical Non-Negotiable User Flows**:
  1. **Farmer Authentication**: Signup → Email verification prompt → Login → Session persistence.
  2. **Dashboard Cockpit**: Sensor cards render live readings; threshold warnings trigger correctly.
  3. **Pump Remote Control**: Toggle pump relay on/off; command queue updates; status reflects immediately.
  4. **AI Disease Scan**: Leaf image upload → diagnosis cards appear with treatment remedies.
  5. **Mandi Market Explorer**: Commodity price filter → mandi table populates with expected modal rates.

---

## 2. Mocking Boundaries: What is Mocked vs Never Mocked

| Component | Policy | Rationale |
|---|:---:|---|
| **Our Relational Database** | 🚫 **NEVER MOCKED** | Mocking the database hides foreign key failures, index mismatches, type casting bugs, and transaction leaks. |
| **Our Auth & Permissions** | 🚫 **NEVER MOCKED** | Authentication cookies, token hashing, and `can()` checks must execute real logic in tests. |
| **Google Gemini API** | ✅ **MOCKED** | External LLMs are non-deterministic, cost money per call, and introduce network flakes in CI. |
| **Data.gov.in Mandi API** | ✅ **MOCKED** | Government API experiences downtime; test fixtures simulate realistic price responses. |
| **Open-Meteo Weather API**| ✅ **MOCKED** | External forecast service; simulated in tests with structured weather JSON fixtures. |
| **Twilio / WhatsApp API** | ✅ **MOCKED** | SMS/WhatsApp sending is stubbed in test environments to prevent unwanted carrier fees. |

---

## 3. Golden Rules of Testing (Appendix A)
1. **Never let an agent edit a test to pass**: If a test reveals a bug, the bug MUST be fixed in application code, never by relaxing test assertions.
2. **Every skip requires an explanation**: Any `.skip`, `xit`, or `@pytest.mark.skip` without an attached issue ticket is rejected by CI.
3. **Verify failure first**: When writing regression tests for bugs, prove that the test fails against the current code before applying the fix.
4. **CI Blocks Merge on Any Failure**: No pull request can merge to `main` unless 100% of the test suite passes green in GitHub Actions.
