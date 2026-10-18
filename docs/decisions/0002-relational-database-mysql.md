# 2. Relational Database with MySQL 8.4 and Field-Level Encryption

## Context
CropConnect handles sensitive personal farmer data (phone, village, land size), multi-sensor telemetry, device ownership, and pump relay states. We required a stable, ACID-compliant storage engine that prevents cross-tenant data corruption.

## Decision
We chose **MySQL 8.4** (with MariaDB compatibility) using parameterized JSON types and **AES-256-GCM** encryption at rest for sensitive PII columns.

## Alternatives Considered
- **MongoDB**: Evaluated during initial prototyping. Rejected because schema flexibility led to inconsistent device associations, missing foreign key constraints, and multi-tenant scoping risks.
- **PostgreSQL**: Strong candidate, but MySQL 8.4 provided native integration with our Railway hosting template and zero-configuration connection pooling.

## Consequences
- **Positive**: Strict foreign key constraints (`ON DELETE CASCADE`), time-series indexing on `(device_id, created_at)`, reliable point-in-time recovery via mysqldump.
- **Negative**: Schema alterations require explicit migration scripts (`migrate_db.py`).
