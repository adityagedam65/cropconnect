# CropConnect: Production Hosting Plan & Cloud Topology (Layer 9)

## 1. Hosting Architecture & Regional Strategy
- **Target User Base**: Farmers and agricultural cooperatives across India.
- **Primary Cloud Region**: `ap-south-1` (Mumbai, India) or `sin1` (Singapore) to ensure sub-60ms round-trip latency and comply with India's DPDP Act data residency provisions.
- **Operational Strategy**: Serverless frontend + Managed PaaS backend to ensure zero server patching, minimal DevOps overhead, and instantaneous horizontal scalability.

---

## 2. Component-by-Component Topology & Cost Breakdown

| Component | Provider & Plan at Launch | Monthly Cost (Launch) | Setup at 10x Scale (10,000 Farms) | Monthly Cost (10x) | Changes Needed at 10x Scale |
|---|---|:---:|---|:---:|---|
| **Frontend Web Dashboard** | **Vercel** (Hobby/Pro)<br>Edge CDN + React Vite SPA | $0 - $20 | Vercel Pro with Custom Domains & Edge Middleware | $20 | Enable Vercel Edge caching and ISR for public landing & crop education |
| **FastAPI Backend API** | **Railway** (PaaS)<br>1x Web Service (2 vCPU, 2GB RAM) | $10 - $15 | Railway 3x Autoscale Web Instances (High CPU) | $60 | Enable autoscaling on CPU > 75%; add connection pooling proxy |
| **Relational Database** | **Railway MySQL 8.4**<br>Managed Container + 20GB NVMe | $10 | Dedicated MySQL / Neon / AWS RDS (db.t4g.medium) | $65 | Add Read Replicas for analytics & read-heavy mandi feeds; automated daily R2 snapshots |
| **Object File Storage** | **Cloudflare R2**<br>Zero egress fee S3 bucket | $0 (Free tier) | Cloudflare R2 Standard (1TB storage) | $15 | Implement automated lifecycle rule deleting temporary diagnostic images after 60 days |
| **Background Jobs & Worker** | In-process Asyncio Lifespan worker | $0 (Included in Railway) | Railway Redis (Upstash) + Celery / BullMQ worker | $25 | Decouple WhatsApp alert dispatcher into dedicated queue worker |
| **Email Delivery** | **Resend / SendGrid**<br>Free Developer tier (3,000 emails/mo) | $0 | Resend Growth Plan (50,000 emails/mo) | $20 | Configure SPF, DKIM, and DMARC records on primary sending domain |
| **Error Monitoring & APM** | **Sentry**<br>Developer Tier | $0 | Sentry Team Plan | $26 | Configure alert rules to ping Slack/Telegram when error spike > 10 in 5 min |
| **Total Estimated Infrastructure** | — | **~$20 - $45 / mo** | — | **~$231 - $280 / mo** | — |

---

## 3. Environment Variable Isolation

| Variable Name | Local Development | Staging (Preview) | Production |
|---|---|---|---|
| `ENVIRONMENT` | `development` | `staging` | `production` |
| `MYSQL_HOST` | `127.0.0.1` (Docker) | `mysql-staging.railway.internal` | `mysql-production.railway.internal` |
| `FRONTEND_ORIGINS` | `http://localhost:3000` | `https://cropconnect-staging.vercel.app` | `https://cropconnect01.vercel.app` |
| `AUTH_COOKIE_SECURE` | `false` | `true` | `true` |
| `AUTH_COOKIE_SAMESITE`| `lax` | `none` | `none` |
| `TRUST_PROXY_HEADERS` | `false` | `true` | `true` |
| `CROP_DATA_SECRET_KEY`| Local random key | Staging isolated secret | Vault-generated 48-char secret |
| `CROP_AUTH_TOKEN_SECRET`| Local random key | Staging isolated secret | Vault-generated 48-char secret |
| `SENTRY_DSN` | (Optional empty) | Staging Sentry DSN | Production Sentry DSN |

> [!IMPORTANT]
> Staging and production MUST NEVER share the same MySQL database instance or cryptographic secret keys.
