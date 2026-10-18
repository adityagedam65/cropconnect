# Alert Runbook: High Application Error Rate / 5xx Spike (Layer 14c)

## What this alert means
Sentry or uptime monitors detected more than 10 unhandled 5xx exceptions within a 5-minute window.

## How to check impact
1. Open Sentry Dashboard → `Issues` view.
2. Group by `Unhandled` and examine the top spike.
3. Check the affected endpoint and number of affected users.

## Likely Causes
1. A recent code deployment introduced an unhandled edge-case bug.
2. Downstream API failure (e.g. Gemini AI or Data.gov.in returning 502/504 that is unhandled).
3. Secret key rotation error or missing environment variable in production.

## Step-by-Step Fixes
1. If the error spike correlates with a recent release (< 30 minutes ago), immediately trigger a rollback via [rollback.md](file:///docs/runbooks/rollback.md).
2. If caused by downstream AI API rate limiting or outage:
   - Verify fallback logic is active (CropConnect should return heuristic agronomy advice when Gemini is unavailable).
3. If caused by malformed input:
   - Add temporary input rejection at the boundary or deploy an urgent patch.
4. Verify error rate returns to zero on Sentry.

## When to Escalate
If the issue affects financial records, user auth across all tenants, or pump hardware commands, escalate to Lead Engineer and declare SEV-1.
