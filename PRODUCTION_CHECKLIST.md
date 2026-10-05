# CropConnect Production Checklist

## Code quality (all automated — no manual steps needed)

- [x] sharp added to devDependencies; generate-icons script registered in package.json
- [x] Sentry replayIntegration added; replaysOnErrorSampleRate warning resolved
- [x] docker-compose.yml documented as local-dev-only with danger warning block
- [x] .env.docker.example created with all required vars listed
- [x] DashboardContext fully decoupled — DashboardPageContent reads context directly, no ctx prop-drilling
- [x] CI generates PWA icons on clean environments before build
- [x] CI validates environment config before backend tests run

## Secrets

- [ ] CROP_DATA_SECRET_KEY is a fresh randomly generated 32+ character string
- [ ] CROP_AUTH_TOKEN_SECRET is a fresh randomly generated 32+ character string
- [ ] ESP32_API_KEY rotated from any development value
- [ ] ALLOW_GLOBAL_ESP32_API_KEY=false confirmed in production env
- [ ] Run: grep -r "replace-with" . — result must be empty

## Security

- [ ] AUTH_COOKIE_SECURE=true in production env
- [ ] AUTH_COOKIE_SAMESITE=none and backend is behind HTTPS
- [ ] FRONTEND_ORIGINS contains only the production Vercel URL — no localhost

## Infrastructure

- [ ] TRUST_PROXY_HEADERS=true set in Railway environment
- [ ] GET /health endpoint responds 200 with {"status":"ok","db":"ok"}
- [ ] UptimeRobot or Betterstack monitor pointed at /health, alerting via email
- [ ] MySQL automated backup tested: backup created, restore verified

## Observability

- [ ] SENTRY_DSN configured in Railway env
- [ ] Sentry alert rule: email on every new issue
- [ ] Sentry alert rule: notify on error spike (>10 errors in 5 minutes)

## Final checks

- [ ] Load the production URL and complete a full login → dashboard → pump toggle flow
- [ ] Confirm sensor data appears or empty state renders correctly
- [ ] Check browser console — zero errors on load

## Setting up Sentry alerts

### Backend alerts (Python / FastAPI)
SENTRY_DSN is already read in cropconnect-backend/app.py.
Set it in Railway: Project → Service → Variables → SENTRY_DSN

### Frontend alerts (React)
VITE_SENTRY_DSN is read in cropconnect-frontend/src/index.jsx.
Set it in Vercel: Project → Settings → Environment Variables → VITE_SENTRY_DSN
Use the same DSN value as the backend, or create a separate Sentry project
for the frontend for cleaner separation.

### Creating alert rules in Sentry
1. Go to your Sentry project → Alerts → Create Alert Rule

Rule 1 — New issue notification:
  - Name: New issue
  - Condition: A new issue is created
  - Action: Send an email to <your email>
  - Save rule

Rule 2 — Error spike:
  - Name: Error spike
  - Condition: Number of events in an issue is more than 10 in 5 minutes
  - Action: Send an email to <your email>
  - Save rule

Rule 3 (optional) — Notify on first occurrence of a new error in production:
  - Name: Production new error
  - Filter: Environment = production
  - Condition: A new issue is created
  - Action: Send a Slack notification (if Slack is connected) AND an email
  - Save rule

### Verifying Sentry is working
After setting both DSN values and redeploying:
1. Backend: curl -X POST https://cropconnect01-production.up.railway.app/api/enquiries
   with an invalid payload. Check Sentry for a validation error event.
2. Frontend: open the browser console on the production URL and run:
   throw new Error("Sentry test from browser")
   Check Sentry → Issues for the event within 30 seconds.

## Setting up uptime monitoring (UptimeRobot — free)

Step-by-step:
1. Create a free account at https://uptimerobot.com
2. Dashboard → Add New Monitor
3. Monitor Type: HTTP(S)
4. Friendly Name: CropConnect API
5. URL: https://cropconnect01-production.up.railway.app/api/health
6. Monitoring Interval: every 5 minutes
7. Under "Alert Contacts" → add your email address
8. Expand "Advanced Settings" → enable "Keyword exists" → keyword value: ok
   This validates the DB is responding, not just that HTTP returns 200.
9. Click "Create Monitor"

A healthy response from /api/health looks like:
  {"status":"ok","db":"ok"}

A degraded response (DB unreachable) looks like:
  {"status":"degraded","db":"error"}  (HTTP 503)

You will receive an email within 5 minutes if the backend goes down.
Add a second monitor for the frontend:
  URL: https://cropconnect01.vercel.app
  Keyword: CropConnect
  This catches Vercel deploy failures independently of the backend.

## Hardening pass completed in code

- [x] AI router has per-user sliding-window rate limiting with Retry-After responses
- [x] Startup environment guard validates required secrets and database variables
- [x] Backup script has timestamped retention and restore test script
- [x] PWA icon generation script and generated PNG icons are present
- [x] Backend and frontend Sentry initialization are wired
- [x] Dashboard sections are lazy-loaded through page modules
- [x] Mobile dashboard sidebar drawer is available under 768px
- [x] Dashboard colors use CSS custom properties
- [x] Market panel has a Data.gov empty state
- [x] Rate-limit, sensor-threshold, and pump-control tests are added
- [x] Health endpoint reports database latency, version, and environment
