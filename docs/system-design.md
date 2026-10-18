# CropConnect: System Design Document (Layer 1)

## 1. Problem Statement
Smallholder and commercial farmers in India face unpredictable irrigation demands, crop loss from plant diseases, lack of localized soil data, and opaque mandi commodity market prices. CropConnect solves this by providing an integrated, low-cost smart agriculture platform that connects field-deployed IoT hardware (ESP32 microcontrollers with SIM800L cellular modems) to an intelligent web application for real-time telemetry, automated pump actuation, AI-driven crop health diagnostics, and market pricing intelligence.

## 2. User Roles
CropConnect supports four primary roles under a Role-Based Access Control (RBAC) model:
- **Owner**: Full administrator of the farm/organization. Manages subscription, invites/removes members, sets pump automation rules, exports or deletes tenant data.
- **Admin**: Farm manager. Configures devices, sets irrigation schedules, triggers manual pump overrides, invites workers, and generates agronomy reports.
- **Member**: Farm operator/technician. Views live telemetry, runs AI crop scans, requests agronomic advice, and monitors irrigation status.
- **Viewer**: Read-only stakeholder (e.g. cooperative auditor or agronomist advisor). Can view sensor history, market prices, and weather forecasts without actuation permissions.

## 3. Core User Flows (The 5 Things Users Actually Do)
1. **IoT Sensor Telemetry Ingestion & Live Monitoring**: ESP32 wake cycle sends soil moisture, temperature, and humidity via HTTP POST over SIM800L cellular link to `/api/telemetry/ingest`. Farmers view live dashboard widgets with optimal vs warning indicators.
2. **Automated & Manual Pump Actuation**: Farmers toggle pump switches on the React dashboard or rely on automatic soil-moisture thresholds. Commands are enqueued in MySQL and retrieved by the ESP32 via `/api/esp32/relay-command`.
3. **AI Crop Disease Diagnosis & Agronomy Chat**: Farmers upload photos of stressed leaves via `/crop-scan`. The YOLO/Gemini vision pipeline identifies diseases (e.g. early blight, leaf rust), provides organic and chemical remedies, and suggests irrigation adjustments.
4. **Live Mandi Market Price Intelligence**: Users track daily modal commodity prices across regional mandis fetched from Data.gov.in APIs, calculating expected profit and optimal selling windows.
5. **Weather-Aware Irrigation Advisory**: Farmers review 7-day precipitation forecasts from Open-Meteo, allowing the system to delay scheduled watering cycles before impending rain.

## 4. Tenancy Model
- **Account Model**: Multi-tenant with organization/farm scoping.
- **Data Scoping**: Every tenant-owned record (`devices`, `sensors`, `pumps`, `crop_plans`, `chat_history`) is linked to a user/organization via `organization_id` (or user ownership foreign key).
- **Isolation Enforcement**: Every database query filters by `organization_id`. API authorization rejects cross-tenant requests with `404 Not Found` (to avoid leaking resource existence) or `403 Forbidden`.
- **Hardware Association**: Each physical ESP32 sensor device is assigned a unique `sensor_device_id` and hashed API key bound directly to the owning organization account.

## 5. Data Stored & Sensitivity Classification
| Data Type | Description | Sensitivity Level | Protection / Storage Strategy |
|---|---|---|---|
| User Credentials | Email, password hashes, auth tokens | Critical | PBKDF2 password hashing with salt; SHA-256 token hashing; HttpOnly SameSite cookies |
| Personal Identifiable Info (PII) | Farmer name, phone, state, district, village | High | Encrypted at rest using AES-256-GCM (`CROP_DATA_SECRET_KEY`); excluded from application logs |
| Device API Keys | ESP32 hardware authentication keys | High | Hashed in database; validated at the ingestion boundary |
| Sensor Telemetry | Soil moisture %, temperature, humidity, timestamps | Low | Time-series records in MySQL with composite indexes; raw payload validated |
| Pump Relay State | On/Off state, last heartbeat, runtime duration | Medium | Relational record with concurrency safety and relay state verification |
| Crop Leaf Images | Diagnostic leaf photos | Medium | Stored in object storage with unique UUID keys; temporary processing buffer in memory |

## 6. Expected Scale in Year One (Capacity Back-of-the-Envelope)
- **Active Farmers/Organizations**: 1,000 active farms.
- **Active ESP32 Devices**: 1,500 units reporting every 5 minutes (300 seconds).
- **Telemetry Ingestion Rate**:
  $$\text{Requests/sec} = \frac{1,500 \text{ devices}}{300 \text{ seconds}} = 5 \text{ requests/second average}$$
  $$\text{Peak Ingestion (e.g. morning synchronized boot)} = 25 \text{ requests/second}$$
- **Daily Ingestion Volume**:
  $$1,500 \times 288 \text{ pings/day} = 432,000 \text{ telemetry rows/day}$$
- **Database Size Growth**:
  - Telemetry row size: ~150 bytes.
  - Daily data: $432,000 \times 150 \text{ B} \approx 64.8 \text{ MB/day}$.
  - Year One Raw Telemetry: $64.8 \text{ MB} \times 365 \approx 23.6 \text{ GB}$.
  - Retention & Aggregation: Raw 5-minute telemetry retained for 90 days (~5.8 GB); hourly rollups retained for 1 year (~1.2 GB).
- **Uploaded Images**: 500 scans/day $\times$ 1.5 MB = 750 MB/day (~270 GB/year).
- **Background Jobs**: ~15,000 scheduled notifications (WhatsApp/Email alerts) per day.
- **First Bottleneck Component**:
  - Outgoing cellular SIM800L connection latency (rural 2G/GPRS signal drops).
  - Addressed on the backend via fast, non-blocking ingestion endpoints (sub-25ms response time), persistent MySQL connection pooling, and client-side offline caching on the React dashboard.

## 7. Billing and Plans
- **Free Tier (Kisan Free)**: 1 ESP32 device, 1 pump relay, 30-day telemetry retention, 10 AI scans/month.
- **Smart Farmer Pro**: Up to 5 devices, unlimited pump automations, 90-day telemetry retention, WhatsApp alerts, unlimited AI disease scans.
- **Cooperative / Enterprise**: Multi-user team management (Owner, Admin, Member, Viewer), custom sensor integrations, priority agronomy advice, bulk data export.

## 8. Compliance & Regional Requirements
- **DPDP Act (India 2023)**: Full compliance with Digital Personal Data Protection Act:
  - Data minimization and explicit consent at registration.
  - Right to access and download personal data (`GET /api/auth/export-data`).
  - Right to erasure and account anonymization (`POST /api/auth/delete-account`).
  - Localized processing within India / APAC cloud regions.

## 9. Integrations with Other Services
- **Data.gov.in**: National Agricultural Market (e-NAM) open commodity price API.
- **Open-Meteo**: High-precision 7-day agricultural weather forecast API.
- **Google Gemini AI**: Multimodal crop analysis and natural language agronomy advisory.
- **Twilio / WhatsApp Business**: Automated irrigation and extreme weather alerts.
- **Sentry**: Application performance monitoring, crash diagnostics, and error reporting.

## 10. Non-Functional Requirements
- **Performance**: API p95 latency < 300ms for core endpoints; telemetry ingestion ACK < 50ms.
- **Availability**: 99.9% uptime target with automated failover and health monitoring.
- **Security**: TLS 1.3 in transit; AES-256-GCM for PII; rate limiting per IP and per organization; zero secrets in frontend bundle.

## 11. Out-of-Scope Items (Strictly Excluded to Prevent Feature Sprawl)
- Direct tractor or heavy machinery autopilot integration.
- Native cryptocurrency or speculative commodities trading.
- Drone-based aerial LIDAR mapping.
- Custom e-commerce marketplace for selling harvested grain directly to consumers (CropConnect focuses on farm telemetry, decision support, and market pricing intelligence).

## 12. Open Questions
1. Should SIM800L payload format switch to compact binary (Protobuf) or remain JSON over GPRS? (Decision: JSON retained for current stage for observability and debugging).
2. Will multi-sensor mesh networking (ESP-NOW) be supported for large farms with multiple node clusters? (Slated for Phase 2).
