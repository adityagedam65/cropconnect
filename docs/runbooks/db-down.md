# Alert Runbook: Database Unreachable / Pool Degraded (Layer 14c)

## What this alert means
The `/api/health` check returned `status: "degraded"` and `db: "error"`, meaning FastAPI cannot acquire a connection from the database pool.

## How to check impact
1. Hit `/api/health` directly:
   ```bash
   curl -i https://cropconnect01-production.up.railway.app/api/health
   ```
2. Check Sentry for `OperationalError` or `ConnectionRefusedError`.

## Likely Causes
1. MySQL container on Railway crashed or ran Out-Of-Memory (OOM).
2. Database connection pool exhausted due to unclosed database cursors.
3. Network blip between Railway API service and MySQL service.
4. Database credentials or host environment variables modified.

## Step-by-Step Fixes
1. Open Railway Dashboard → `MySQL Service`.
2. Check RAM and CPU metrics. If RAM is at 100%, the process was likely killed by OOM.
3. Check Service Logs for `mysqld: Out of memory` or `Too many connections`.
4. If MySQL is stopped: click **Restart**.
5. If pool is exhausted: restart the `cropconnect-backend` service to reset connection pool handles.
6. Verify `/api/health` returns HTTP 200 with `{"status":"ok","db":"ok"}`.

## When to Escalate
If MySQL refuses to start or data corruption is reported in the logs, escalate to Lead Infrastructure Engineer immediately and prepare point-in-time restore per [backups.md](file:///docs/runbooks/backups.md).
