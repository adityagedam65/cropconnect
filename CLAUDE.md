# Project: CropConnect

## What this product does
CropConnect is an AI-assisted farming platform designed for Indian farmers and agricultural organizations. It connects field-deployed ESP32 microcontrollers with SIM800L cellular modules to stream real-time soil moisture, temperature, and humidity telemetry, automate pump irrigation cycles, diagnose plant diseases using computer vision and Gemini AI, and track live commodity mandi market prices from Data.gov.in.

## Stack (do not change without asking)
- Frontend: React 18 + Vite + Tailwind CSS + Radix UI / Sonner (Single Page Application)
- Backend: Python 3.12 + FastAPI (Modular Monolith with Pydantic validation)
- Database: MySQL 8.4 / MariaDB (relational with JSON parameters, AES-256-GCM field encryption for PII)
- Auth: Cookie/Bearer token authentication with PBKDF2 password hashing, CSRF tokens, and RBAC permissions (Owner, Admin, Member, Viewer)
- Hosting: Vercel (Frontend SPA) + Railway (FastAPI backend + MySQL) + Cloudflare/UptimeRobot (CDN & Monitoring)

## Rules
- Never commit secrets. All secrets go in environment variables, documented in `.env.example`.
- Every new API endpoint needs: input validation (Pydantic), auth check, authorization check (`can(user, action, resource)`), and automated tests.
- Every database change goes through a migration file (`migrate_db.py`). Never edit the database by hand.
- Run lint, typecheck, and tests before saying a task is done.
- Ask before adding a new dependency.
- Prefer small, reviewable changes. One feature per branch.
- Conventional Commits: use `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Server is the source of truth for validation, permissions, and business rules.

## Commands
- Dev Frontend: `cd cropconnect-frontend && npm run start`
- Dev Backend: `cd cropconnect-backend && uvicorn esp32_ingest:app --host 0.0.0.0 --port 8001`
- Test Frontend: `cd cropconnect-frontend && npm run test`
- Test Backend: `cd cropconnect-backend && python -m unittest discover -s tests`
- Lint/Typecheck Frontend: `cd cropconnect-frontend && npm run lint && npm run check`
- Lint Backend: `cd cropconnect-backend && ruff check .`
- Migrate Database: `cd cropconnect-backend && python migrate_db.py`

## Architecture decisions
See `/docs/decisions/` for the log of Architecture Decision Records (ADRs) and why each decision was made.

## Universal "Don't Fool Me" Verification Standard
Before declaring any task or feature complete:
1. Run lint, typecheck, and the full test suite, and verify the output passes.
2. List every file changed and the concrete rationale for the change.
3. Explicitly list anything that was skipped, stubbed, mocked, or hard-coded.
4. List assumptions made that require human confirmation.
Do not describe work as complete if any test is failing or skipped without a documented reason.

## Appendix A: Golden Rules of Agentic Coding for SaaS
1. You are the architect; the agent is the builder. Decide, then delegate.
2. Plan before code, every time. Fixing a plan is cheap; fixing code is expensive.
3. Write it down. `CLAUDE.md`, `AGENTS.md`, and `/docs/` are the project memory.
4. Small tasks, small diffs. One feature per branch, one concern per commit.
5. The agent must prove it works. Tests, lint, typecheck, and output shown to you.
6. Never let it edit a test to pass. Bugs are fixed in code.
7. Review with a fresh pair of eyes. Use a separate reviewer session for security and code review.
8. Server is the source of truth. Validation, permissions, and limits are always enforced on the backend.
9. Every tenant query is scoped. `organization_id` everywhere, tested.
10. Read the diff. If you don't understand a change, ask for an explanation before merging.
