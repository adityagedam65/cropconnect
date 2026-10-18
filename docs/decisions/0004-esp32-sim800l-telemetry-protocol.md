# 4. ESP32 SIM800L Telemetry Ingestion and Relay Polling Protocol

## Context
Agricultural sensor nodes in rural India operate in environments without stable WiFi. Telemetry must be delivered reliably over patchy 2G/GPRS cellular connections with minimal power drain on solar batteries.

## Decision
We adopted an HTTP-based pull/push protocol:
1. ESP32 wakes from deep sleep every 5 minutes.
2. Ingests soil moisture, DHT22 temperature/humidity, battery voltage.
3. Sends HTTP POST with `X-API-Key` to `/api/telemetry/ingest`.
4. Polls `/api/esp32/relay-command` to check for pending pump activation commands.
5. Transmits serial command to secondary pump relay ESP32 if triggered, then re-enters sleep mode.

## Alternatives Considered
- **MQTT / WebSockets**: Requires constant TCP connection maintenance, which repeatedly drops and drains battery over rural cellular networks.
- **SMS-based telemetry**: High per-message telecom cost and low bandwidth.

## Consequences
- **Positive**: Stateless, battery-friendly, simple retry mechanism, easily inspected in proxy logs.
- **Negative**: Relay commands execute on the next polling cycle (up to 5-minute latency) rather than instantaneous push.
