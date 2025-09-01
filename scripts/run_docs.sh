#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Install dependencies first
./scripts/preflight_docs.sh

# Activate venv
# shellcheck source=/dev/null
. .venv/bin/activate

# Run docs server
cd truledgr-docs
exec python -m mkdocs serve --dev-addr 127.0.0.1:8001
