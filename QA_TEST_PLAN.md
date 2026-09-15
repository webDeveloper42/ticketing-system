# TicketDesk Software QA Test Session

## Purpose

Validate that the ticket lifecycle is usable, reliable, secure, and correctly restricted by role before this portfolio project is demonstrated or deployed.

## Research-informed strategy

The suite follows a layered approach: deterministic model and service checks, Flask request-level integration tests with isolated fixtures, role/authorization and abuse-case tests, then a short exploratory browser session. This keeps failures easy to diagnose while still exercising complete user workflows. SQLAlchemy sessions are scoped to an application/request operation, and every automated test receives an isolated in-memory SQLite database.

## Automated session

Run from a clean checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
bandit -r ticketing -q
```

Coverage includes authentication, password hashing, CSRF enforcement, response headers, request-size limits, input validation, object-level authorization, staff-only workflow controls, ticket creation, assignment, status changes, filtering, public replies, private notes, SLA calculations, and audit logging.

## Manual exploratory session (30-40 minutes)

Environment: current Chrome or Firefox, desktop plus a 390px responsive viewport. Start with `./setup.sh` and use the seeded accounts printed by the script.

| Charter | Steps | Expected result |
|---|---|---|
| Request intake | Sign in as requester; submit vague/empty values, then a valid network incident | Errors explain exactly what to fix; a valid ticket receives a reference and appears in the queue |
| Least privilege | As requester, alter a ticket ID in the address bar and try `/manage` | Another user's ticket returns 404; staff management returns 403 |
| Agent workflow | Sign in as agent; assign the ticket, raise priority, move it through in-progress and resolved | Every change persists; ownership/status are obvious; audit events are written |
| Communication privacy | Add one public reply and one internal note; reopen as requester | Public reply is visible; internal note is never rendered |
| Search/filter | Search by title and filter by priority/status; test zero matches | Correct records appear; the empty state explains the next action |
| Accessibility/usability | Navigate only by keyboard, zoom to 200%, check labels, focus, contrast, mobile layout | All actions remain reachable and readable; no horizontal page overflow except the deliberate table scroller |
| Resilience | Stop the server with Ctrl+C, rerun `./setup.sh`, and sign back in | SQLite data persists; existing tickets remain; health endpoint returns 200 after recovery |

## Severity and exit criteria

- P0: unauthorized data access, authentication bypass, data loss, or app unavailable. Release blocked.
- P1: core ticket lifecycle broken or internal notes disclosed. Release blocked.
- P2: filter, validation, audit, or responsive-flow defect. Fix before portfolio demo where practical.
- P3: cosmetic inconsistency with a clear workaround. Record for follow-up.

Exit when all automated checks pass, no open P0/P1 defects remain, the six exploratory charters pass, and the health endpoint reports both app and database healthy.

## Defect template

`ID | Date | Environment | Severity | Title | Preconditions | Steps | Expected | Actual | Evidence | Status`
