#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Installing truledgr-dash workspace deps into repo root..."
npm install --workspace=truledgr-dash --no-audit --no-fund
