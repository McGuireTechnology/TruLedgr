#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Install dependencies first
./scripts/preflight_dash.sh

# Run dash dev server
export PORT=3000
exec npm run dev:dash
