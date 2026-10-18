# 1. Adopt Modular Monolith with FastAPI

## Context
When building CropConnect for early deployment, we needed an architecture that minimizes operational overhead for a small engineering team while delivering sub-50ms API response times for ESP32 hardware telemetry and seamless AI integrations.

## Decision
We chose a **Modular Monolith** using **Python 3.12 and FastAPI**. All core domains (auth, sensors, pumps, weather, market, AI) reside in dedicated modules (`/routers` and `/services`) within a single deployable unit.

## Alternatives Considered
- **Microservices (Kubernetes / gRPC)**: Rejected due to excessive operational complexity, distributed transaction overhead, and premature infrastructure cost for early-stage SaaS.
- **Node.js (Express / Fastify)**: Rejected because Python natively supports the AI and computer vision packages (YOLO, OpenCV, NumPy, Gemini SDK) required for our agronomy models.
- **Django**: Rejected due to heavy ORM overhead and slower telemetry ingestion throughput.

## Consequences
- **Positive**: Single CI/CD pipeline, rapid iteration, zero network latency between services, simplified local Docker Compose development.
- **Negative**: Long-running synchronous tasks could block the event loop if not offloaded to async threads or external queues.
