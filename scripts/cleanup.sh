#!/usr/bin/env bash
rm -rf .venv examples/*/.venv 2>/dev/null; find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; echo cleaned
