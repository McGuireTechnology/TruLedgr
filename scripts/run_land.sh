#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Install dependencies first
./scripts/preflight_land.sh

# Run land dev server
export PORT=3001
exec npm run dev:land
