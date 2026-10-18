# Alert Runbook: ESP32 Hardware Telemetry Ingest Outage (Layer 14c)

## What this alert means
Zero sensor telemetry packets were received across active registered devices for over 15 minutes.

## How to check impact
1. Hit `/api/esp32/relay-command` manually with a test device API key.
2. Query the latest telemetry timestamp in MySQL:
   ```sql
   SELECT MAX(created_at) FROM sensor_readings;
   ```
3. Check Railway backend logs for `/api/telemetry/ingest` access logs.

## Likely Causes
1. Rural 2G cellular network outage affecting SIM800L carriers in the region.
2. Expired prepaid SIM cards on deployed hardware.
3. Ingestion endpoint misconfiguration or accidental routing block.
4. `ALLOW_GLOBAL_ESP32_API_KEY` setting changed.

## Step-by-Step Fixes
1. Test the ingestion endpoint with a simulated payload via curl:
   ```bash
   curl -X POST https://cropconnect01-production.up.railway.app/api/telemetry/ingest \
     -H "Content-Type: application/json" \
     -d '{"device_id":"test_node","soil_moisture":35.2,"temperature":24.0,"humidity":60.0}'
   ```
2. If HTTP 200 is returned, the backend ingestion pipeline is functional; the issue is on the physical hardware or cellular telecom provider side.
3. Notify affected regional farm managers to inspect SIM800L LED status on hardware (blinking every 3s = registered to network; blinking every 800ms = searching/no signal).

## When to Escalate
If backend returns 500 or drops packets due to database locks, restart the backend service and investigate table locks on `sensor_readings`.
