# CropConnect: Monitoring, Metrics & Alerting Plan (Layer 14)

## 1. Uptime Checks & Synthetic Health Probes

| Probe Name | Target URL | Expected Response | Check Frequency | Alert Provider | Runbook Link |
|---|---|:---:|:---:|---|:---:|
| **API Deep Health Check** | `/api/health` | HTTP 200 `{"status":"ok","db":"ok"}` | Every 5 minutes | UptimeRobot / Sentry | [db-down.md](file:///docs/runbooks/db-down.md) |
| **API Liveness Probe** | `/api/health/live` | HTTP 200 `{"status":"ok","live":true}` | Every 30 seconds | Railway Load Balancer | [high-error-rate.md](file:///docs/runbooks/high-error-rate.md) |
| **Frontend Web App** | `https://cropconnect01.vercel.app` | HTTP 200 (Keyword: `CropConnect`) | Every 5 minutes | UptimeRobot | [incident.md](file:///docs/runbooks/incident.md) |
| **Hardware Command Ingest**| `/api/esp32/relay-command` | HTTP 200 / 401 | Every 5 minutes | UptimeRobot | [esp32-offline.md](file:///docs/runbooks/esp32-offline.md) |

---

## 2. Key Technical & Business Metrics

### Technical Metrics (SLIs & SLOs)
- **API Availability**: Target: 99.9% uptime.
- **p95 Latency**: Target: < 300ms across all endpoints (< 50ms on telemetry ingestion).
- **HTTP 5xx Error Rate**: Target: < 0.1% of total requests.
- **Database Connection Pool Saturation**: Alert if active pool > 80% capacity for > 3 minutes.
- **Background Worker Latency**: Alert if scheduled WhatsApp notifications queue lag > 15 minutes.

### Business & Operational Metrics
- Daily active farmer sessions.
- Real-time ESP32 active fleet count (devices reporting within the last 15 minutes).
- Daily pump irrigation actuation volume (total runtime minutes).
- Daily crop disease scans processed.

---

## 3. Actionable Alert Rules & Severity Levels

> [!NOTE]
> Following the rule of "Keep alerts to only things that need a human to act", informational warnings are logged to Sentry dashboards without triggering paging notifications.

| Alert Trigger | Threshold Condition | Severity | Notification Channel | Runbook |
|---|---|:---:|---|:---:|
| **Database Pool Unreachable** | `/api/health` returns 503 or `db: "error"` for 2 consecutive checks | P1 (Critical) | SMS + Emergency Email to On-Call | [db-down.md](file:///docs/runbooks/db-down.md) |
| **Application Crash Spike** | > 10 new unhandled exceptions in 5 minutes on Sentry | P1 (Critical) | Pager / Telegram Alert | [high-error-rate.md](file:///docs/runbooks/high-error-rate.md) |
| **ESP32 Ingestion Outage** | Zero telemetry packets ingested across entire fleet for 15 minutes | P2 (High) | Slack / On-call Email | [esp32-offline.md](file:///docs/runbooks/esp32-offline.md) |
| **External AI API Failure** | Gemini API returns 5xx for > 5 consecutive crop scan attempts | P3 (Medium) | Engineering Team Email | [high-error-rate.md](file:///docs/runbooks/high-error-rate.md) |
