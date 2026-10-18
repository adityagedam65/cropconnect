Act as a security reviewer. Audit the CropConnect codebase for:
- broken access control and missing org scoping (`organization_id` or user ownership)
- SQL/NoSQL injection and unsafe raw queries
- XSS (unsafe HTML rendering)
- CSRF on state-changing requests
- open redirects and SSRF (server fetching user-supplied URLs)
- insecure file uploads
- secrets in code or logs, sensitive data in logs (AES encryption, PII redaction)
- missing security headers (CSP, HSTS, X-Frame-Options, nosniff, etc.)
- verbose error messages leaking internals
- insecure cookie settings (HttpOnly, Secure, SameSite)

Report each finding with: file, line, severity, exploit scenario, and suggested fix.
Do not fix anything yet.
