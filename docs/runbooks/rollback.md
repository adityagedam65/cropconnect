# Runbook: Production & Staging Deployment Rollback (Layer 7c)

## 1. When to Initiate an Immediate Rollback
Initiate an immediate rollback if any of the following occur within 15 minutes of a deployment:
- HTTP 5xx error rate spikes above 1% on Sentry.
- The `/api/health` endpoint responds with `503 Service Unavailable` or `db: "error"`.
- Authentication failures prevent existing farmers from logging in.
- ESP32 telemetry ingestion drops to 0 packets/min across the fleet.

---

## 2. Fast Backend Rollback (Railway)

### Option A: Railway Instant Rollback via Web Console (Fastest: < 30 seconds)
1. Open the [Railway Dashboard](https://railway.app).
2. Navigate to: `CropConnect Project` → `Backend Service` → `Deployments` tab.
3. Locate the previous healthy deployment (marked with a green checkmark).
4. Click the three dots (`...`) next to the deployment → select **Redeploy**.
5. Railway spins up the previous container image immediately without rebuilding from git.
6. Check deployment logs and verify `/api/health` responds with `200 OK`.

### Option B: Railway Rollback via CLI
```bash
# List previous deployment IDs
railway deployment list

# Redeploy previous stable deployment
railway deployment redeploy <DEPLOYMENT_ID>
```

---

## 3. Fast Frontend Rollback (Vercel)

### Option A: Vercel Instant Rollback via Dashboard (< 10 seconds)
1. Open the [Vercel Dashboard](https://vercel.com).
2. Navigate to: `CropConnect Project` → `Deployments`.
3. Locate the previous successful production deployment.
4. Click the three dots (`...`) → click **Promote to Production** (or **Instant Rollback**).
5. Vercel routes traffic immediately to the previous immutable edge build.
6. Verify by loading `https://cropconnect01.vercel.app` in an incognito window.

### Option B: Vercel Rollback via CLI
```bash
# Promote prior stable deployment URL to production alias
vercel rollback
```

---

## 4. Handling Database Migration Rollbacks

> [!CAUTION]
> If the bad deployment applied backward-incompatible schema migrations, rolling back the application code alone may cause SQL errors.

1. **Verify Database State**:
   Inspect the migration log table in MySQL:
   ```sql
   SELECT * FROM schema_migrations ORDER BY applied_at DESC LIMIT 5;
   ```
2. **Backward-Compatible Migration Principle**:
   All CropConnect migrations adhere to the expand-and-contract pattern:
   - Additive changes (new columns, indexes) are non-breaking when rolling back code.
   - Destructive changes (dropping columns) are never executed in the same release as code changes.
3. **If Schema Must Be Reverted**:
   Execute the pre-deploy backup snapshot using the backup runbook:
   ```bash
   python cropconnect-backend/scripts/test_restore_db.py /backups/cropconnect_pre_deploy.sql.gz
   ```

---

## 5. Post-Rollback Checklist
- [ ] Verify `/api/health` and `/api/health/live` return 200 OK.
- [ ] Confirm Sentry issue stream stabilizes to baseline.
- [ ] Post incident notification in the team channel detailing the rollback reason and commit hash.
- [ ] Lock `main` branch until the root-cause bug reproduces in a local test.
