# Security Notes

TicketDesk is a local portfolio application, not a production-certified service. It applies practical baseline controls: salted PBKDF2-SHA256 password hashing, CSRF tokens on state changes, ORM parameter binding, generic login errors, object-level authorization, role checks, secure cookie settings, restrictive response headers, request-size limits, server-side validation, and an audit trail for authentication and ticket events.

For internet deployment, set a unique `SECRET_KEY`, rotate all demo credentials, set `COOKIE_SECURE=true`, terminate TLS at a trusted proxy, move from local SQLite to an appropriately managed database, use a least-privileged database account, add centralized rate limiting, configure backups and log retention, run dependency scanning, and complete an OWASP ASVS review.

Report security concerns privately to the project owner; do not include sensitive data in a public issue.
