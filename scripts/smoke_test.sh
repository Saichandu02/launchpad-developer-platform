#!/usr/bin/env bash
# Scaffold a throwaway service, test it, run it, call /api/info. See docs/verification.md for recorded output.
set -euo pipefail
NAME=${1:-smoke-svc-01}; OUT=$(mktemp -d)/$NAME; python3 scaffold.py create --name "$NAME" --description "Smoke test service" --owner team-a --environment dev --output "$OUT"
cd "$OUT"; python3 -m venv .venv; .venv/bin/pip -q install -r requirements-dev.txt; .venv/bin/pytest -q
.venv/bin/uvicorn app.main:app --port 8137 & PID=$!; trap "kill $PID" EXIT; sleep 3; curl -fsS http://127.0.0.1:8137/healthz; echo; curl -fsS http://127.0.0.1:8137/api/info; echo
