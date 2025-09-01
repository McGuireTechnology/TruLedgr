#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Install dependencies first
./scripts/preflight_api.sh

# Activate venv
# shellcheck source=/dev/null
. .venv/bin/activate

# Run API server
cd truledgr-api
exec python -m uvicorn truledgr_api.main:app --reload --host 127.0.0.1 --port 8000
