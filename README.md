# TicketDesk

A secure, role-based IT help desk portfolio application built with Python, Flask, SQLAlchemy, SQLite, Jinja, and BEM-organized CSS. Requesters submit and track issues; agents triage, assign, prioritize, communicate, and resolve them; audit events and SLA targets provide operational accountability.

## One-command local setup

Prerequisite: Python 3. No database server or container software is required.

```bash
chmod +x setup.sh
./setup.sh
```

The script creates a private Python virtual environment, installs dependencies, generates a random application secret, initializes a local SQLite database, seeds three demo roles plus sample tickets, and starts <http://localhost:8000>. It is idempotent and safe to rerun.

Stop with `Ctrl+C`. Application data is stored in `instance/ticketing.db` and persists between runs.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Administrator | admin@example.com | ChangeMe123! |
| Agent | agent@example.com | Agent123! |
| Requester | requester@example.com | Requester123! |

Change these before any non-local use.

## Capabilities

- Role-based requester, agent, and administrator access
- Guided ticket intake with categories, priorities, validation, and human-readable references
- Assignment and open, in-progress, pending, resolved, and closed workflows
- SLA target calculations (critical 4h, high 8h, medium 24h, low 72h)
- Public replies plus staff-only internal notes
- Search and queue filters
- Authentication/ticket audit trail and database health endpoint
- Responsive accessible interface using BEM class naming
- Zero-configuration SQLite persistence for local use

## Architecture

The Flask application-factory pattern wires separate authentication, dashboard, and ticket blueprints. Models hold domain state; `TicketService` owns transactional workflow changes and audit records; routes handle HTTP concerns; Jinja templates and BEM CSS form the presentation layer. SQLAlchemy supplies parameterized persistence, while SQLite keeps local setup simple and isolated in-memory databases keep tests deterministic.

## Quality checks

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
bandit -r ticketing -q
```

See [QA_TEST_PLAN.md](QA_TEST_PLAN.md) for the exploratory session, severity model, exit criteria, and defect format. See [SECURITY.md](SECURITY.md) for implemented controls and production hardening.

## Research basis

Implementation decisions were checked against official Flask patterns, SQLAlchemy transaction guidance, pytest fixture and project-layout guidance, and OWASP application-security verification and logging guidance.

## Optional MySQL configuration

The SQLAlchemy model layer remains compatible with MySQL. If you already have a local MySQL server, create a database and account, then change `DATABASE_URL` in `.env` to a PyMySQL URL such as `mysql+pymysql://user:password@127.0.0.1/ticketing`. Run `./setup.sh` again to create and seed the tables. SQLite remains the recommended zero-configuration local option.
