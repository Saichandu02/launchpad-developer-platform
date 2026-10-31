#!/usr/bin/env bash
set -euo pipefail
start=$(date +%s)
for c in python3 git; do command -v $c >/dev/null || { echo "MISSING: $c"; exit 1; }; done
python3 --version; git --version
for c in docker kind kubectl helm terraform node yarn; do command -v $c >/dev/null && echo "found: $c $($c --version 2>/dev/null | head -1)" || echo "optional-missing: $c (config-only features that need it are documented in docs/verification.md)"; done
python3 -m venv .venv && .venv/bin/pip -q install -r requirements-dev.txt && echo "venv ready"
echo "bootstrap_seconds=$(( $(date +%s) - start ))"
