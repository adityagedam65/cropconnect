# Runbook: Incident Response & Post-Mortem Process (Layer 14d)

## 1. Incident Severity Levels

- **SEV-1 (Critical)**: Production down, database unreachable, or telemetry ingestion halted globally. On-call responds within 15 minutes.
- **SEV-2 (High)**: A core feature (e.g. pump control or AI crop scan) is degraded for multiple farmers, but telemetry continues. Response within 1 hour.
- **SEV-3 (Medium)**: Cosmetic issue, isolated mandi price fetch error, or minor latency degradation. Response during business hours.

---

## 2. Incident Lifecycle & Workflow

```
[ALERT FIRED] ──> [TRIAGE & DECLARE SEV] ──> [MITIGATE / ROLLBACK] ──> [COMMUNICATE] ──> [POST-MORTEM]
```

### Step 1: Triage & Declaration
1. Verify the alert on Railway and Sentry dashboards.
2. Designate an Incident Commander (IC) in the response channel.
3. Post initial declaration:
   > *"Declaring SEV-1: /api/health responding 503. Investigating database connectivity on Railway. IC: @engineer."*

### Step 2: Customer Communication
For user-impacting outages (> 10 minutes), update status banner or broadcast notice:
> *"We are currently investigating an issue preventing real-time telemetry updates. Field ESP32 units will store telemetry locally and re-transmit once service is restored. No data is lost."*

### Step 3: Mitigation First, Root Cause Second
Always prefer fast rollback or service restart over live debugging in production:
- Follow [rollback.md](file:///docs/runbooks/rollback.md) if caused by a recent deploy.
- Follow [db-down.md](file:///docs/runbooks/db-down.md) if caused by connection pool exhaustion.

---

## 3. Post-Incident Review (PIR) Template

```markdown
# Incident Post-Mortem: [Brief Title]
**Date**: YYYY-MM-DD  
**Severity**: SEV-1 / SEV-2  
**Duration**: XX minutes  
**Incident Commander**: @name  

### 1. Summary
[2-3 sentences explaining what broke, the user impact, and how it was resolved.]

### 2. Timeline (UTC)
- HH:MM — Alert fired: [Alert Name]
- HH:MM — Engineer acknowledged alert; declared SEV-1
- HH:MM — Mitigation identified (e.g. rolled back commit abc1234)
- HH:MM — Deployment completed; /api/health green
- HH:MM — Incident resolved

### 3. Root Cause
[Technical explanation of the failure mode. Why did our safeguards fail to catch it?]

### 4. What Went Well vs What Went Poorly
- Well: Automated alert fired within 2 minutes; rollback succeeded in 45 seconds.
- Poorly: Missing integration test for multi-threaded connection pooling.

### 5. Action Items
- [ ] Action item 1: Add regression test covering this failure mode (Owner: @dev, Due: YYYY-MM-DD)
- [ ] Action item 2: Adjust alert threshold (Owner: @dev, Due: YYYY-MM-DD)
```
