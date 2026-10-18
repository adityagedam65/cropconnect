Review CropConnect for scaling readiness:
- is the app stateless (no in-memory sessions, uploads, or rate limit counters that fail across multiple instances)?
- database connection pooling configured correctly for serverless / multiple instances?
- slow queries and missing indexes (use EXPLAIN on the top queries)?
- heavy work that should be in background jobs (notifications, emails, image inference)?
- unbounded queries or list endpoints without pagination?
- large payloads?

Rank by what will break first as traffic grows 10x and 100x.
