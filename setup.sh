#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it from https://www.python.org/downloads/ and rerun ./setup.sh"
  exit 1
fi
if [ ! -f .env ]; then
  secret="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  cp .env.example .env
  sed -i.bak "s/replace-with-a-long-random-value/$secret/" .env
  rm .env.bak
  echo "Created .env with a random application secret."
fi
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt
set -a
source .env
set +a
.venv/bin/python -m flask --app wsgi init-db
.venv/bin/python -m flask --app wsgi seed-demo
echo ""
echo "TicketDesk is ready at http://localhost:8000"
echo "Admin: admin@example.com / ChangeMe123!"
echo "Requester: requester@example.com / Requester123!"
echo "Agent: agent@example.com / Agent123!"
echo "Stop it with Ctrl+C"
exec .venv/bin/python -m flask --app wsgi run --host 127.0.0.1 --port 8000
