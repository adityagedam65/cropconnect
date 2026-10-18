# CropConnect: Scaling Strategy & Capacity Review (Layer 15)

## 1. Scaling Readiness Audit & What Breaks First

| Rank | Potential Bottleneck | Impact at 10x Scale (10,000 Farms) | Impact at 100x Scale (100,000 Farms) | Current Architecture Status & Mitigation |
|---|---|---|---|---|
| **#1** | **Database Connection Pool Exhaustion** | Backend exhausts pool connections during synchronized morning sensor bursts. | Database crashes due to thousands of concurrent threads. | **Mitigated**: Persistent connection pooling in `db/mysql.py` with 30s timeout and connection recycle. Future: PgBouncer / ProxySQL pooler. |
| **#2** | **Telemetry History Queries Without Composite Index** | Dashboard charts load in 2–4s. | Full table scans on 40M+ telemetry rows; query timeouts (> 30s). | **Mitigated**: Composite index on `(device_id, created_at DESC)` ensures index-only range scans. |
| **#3** | **Synchronous AI Image Inference** | Request timeout on slow cellular connections during simultaneous leaf scans. | Severe CPU spikes stalling event loop. | **Mitigated**: Image resizing at boundary; inference capped with timeouts; option to route to dedicated worker container. |
| **#4** | **Unbounded Mandi Table Lookups** | Minor memory spike on backend. | Out-of-memory if all historical commodity entries are requested without pagination. | **Mitigated**: Server-side cursor pagination and in-memory TTL caching (4h). |
| **#5** | **Multi-Instance Statelessness** | Rate limit counters and sessions in local memory drift between instances. | Users hit inconsistent rate limits across serverless instances. | **Mitigated**: Auth uses cryptographic HMAC tokens and client cookies; rate limiting designed for Redis transition. |

---

## 2. Load Testing Benchmark (k6 Execution)
A dedicated k6 load testing suite is provided at `cropconnect-backend/tests/load_test_k6.js`.

### Test Profile:
- **Stages**: Ramp from 1 to 20 users (2m) → Sustain 50 users (5m) → Burst 100 users (2m) → Cool-down (1m).
- **Tested Surface**:
  1. `/api/health/live` (lightweight liveness check)
  2. `/api/health` (deep health check)
  3. `/api/market/crops` (commodity price query)
  4. `/api/weather` (forecast lookup)
  5. `/api/esp32/relay-command` (hardware command poll)
- **Target SLO**:
  - Error rate: < 1%
  - p95 latency: < 300ms

---

## 3. Infrastructure Cost Modeling at Scale

| Infrastructure Layer | Launch Scale (1,000 Farms) | 10x Scale (10,000 Farms) | 100x Scale (100,000 Farms) | Optimization Levers at 100x |
|---|:---:|:---:|:---:|---|
| **FastAPI Backend (Railway/AWS)** | $15 / mo | $80 / mo | $450 / mo | Horizontal container autoscaling on AWS ECS Fargate |
| **Database (MySQL / RDS)** | $10 / mo | $65 / mo | $380 / mo | Read replicas for analytics; telemetry partitioned by month |
| **Object Storage (Cloudflare R2)** | $0 / mo | $15 / mo | $85 / mo | Lifecycle policy archiving images older than 90 days to cold tier |
| **Redis Cache & Queue (Upstash)** | $0 / mo | $25 / mo | $120 / mo | Offloads rate limits, mandi cache, and background notifications |
| **Third-Party AI & Mandi APIs** | $15 / mo | $120 / mo | $800 / mo | Heuristic cache for repetitive pest symptoms; local YOLO edge inference |
| **Total Monthly Infrastructure** | **~$40 / mo** | **~$305 / mo** | **~$1,835 / mo** | **Monthly cost per farm drops from $0.04 to $0.018** |
