# Runbook: Production Deployment & Readiness (Layer 9c)

## 1. Production Readiness Checklist

Before triggering your initial or major production release:
- [ ] **Custom Domains & HTTPS**:
  - Frontend: `https://cropconnect01.vercel.app` (or custom apex domain) with auto-renewing Let's Encrypt SSL.
  - Backend: `https://cropconnect01-production.up.railway.app` with managed TLS.
- [ ] **Security Headers Configured**:
  - `Content-Security-Policy`: Restricts scripts and frame-ancestors.
  - `X-Content-Type-Options: nosniff`.
  - `X-Frame-Options: DENY`.
  - `Referrer-Policy: strict-origin-when-cross-origin`.
- [ ] **Graceful Shutdown**:
  - Backend lifespan handles SIGTERM: stops accepting new requests, drains in-flight DB queries, cancels WhatsApp scheduler tasks cleanly.
- [ ] **Database Migration Pipeline**:
  - `migrate_db.py` executes automatically before Uvicorn starts in Railway.
  - Deploy halts immediately if any migration fails.
- [ ] **Uptime & Health Checks**:
  - Railway healthcheck pointing to `/api/health` with a 30-second timeout.
  - UptimeRobot monitor checking `/api/health` every 5 minutes with keyword verification (`ok`).

---

## 2. Step-by-Step Initial Deployment Instructions

### Step 1: Provision Railway Infrastructure
1. Log into Railway and create a new Project: `CropConnect-Production`.
2. Add a **MySQL** Database service:
   - Copy connection credentials (`MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`).
3. Add a **GitHub Repo** Web Service pointing to `cropconnect-backend`:
   - Set Root Directory: `/cropconnect-backend`.
   - Build Command: automatic via `nixpacks.toml` / `requirements.txt`.
   - Start Command: `python migrate_db.py && uvicorn app:app --host 0.0.0.0 --port $PORT`.

### Step 2: Configure Environment Variables in Railway
Run the production configuration script or set variables in Railway Dashboard:
```bash
# Generate high-entropy secrets
DATA_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
AUTH_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
ESP32_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

railway variables set CROP_DATA_SECRET_KEY="$DATA_SECRET"
railway variables set CROP_AUTH_TOKEN_SECRET="$AUTH_SECRET"
railway variables set ESP32_API_KEY="$ESP32_KEY"
railway variables set ALLOW_GLOBAL_ESP32_API_KEY="false"
railway variables set AUTH_COOKIE_SECURE="true"
railway variables set AUTH_COOKIE_SAMESITE="none"
railway variables set TRUST_PROXY_HEADERS="true"
railway variables set FRONTEND_ORIGINS="https://cropconnect01.vercel.app"
railway variables set SENTRY_DSN="<your-backend-sentry-dsn>"
railway variables set GEMINI_API_KEY="<your-gemini-key>"
railway variables set DATA_GOV_API_KEY="<your-datagov-key>"
```

### Step 3: Provision Frontend on Vercel
1. Import GitHub repository into Vercel.
2. Set Root Directory: `cropconnect-frontend`.
3. Framework Preset: `Vite`.
4. Configure Vercel Environment Variables:
   - `VITE_BACKEND_URL`: `https://cropconnect01-production.up.railway.app`
   - `VITE_SENTRY_DSN`: `<your-frontend-sentry-dsn>`
   - `VITE_PUBLIC_TRANSLATION_ENABLED`: `true`
5. Click **Deploy**.

### Step 4: Verification
1. Ping backend health check:
   ```bash
   curl -i https://cropconnect01-production.up.railway.app/api/health
   # Must return HTTP 200 with {"status":"ok","db":"ok"}
   ```
2. Ping liveness probe:
   ```bash
   curl -i https://cropconnect01-production.up.railway.app/api/health/live
   # Must return HTTP 200 with {"status":"ok","live":true}
   ```
3. Load the frontend URL in a desktop browser and on a mobile phone (375px width).
4. Run an end-to-end signup, verify dashboard loading, and trigger a test pump toggle.
