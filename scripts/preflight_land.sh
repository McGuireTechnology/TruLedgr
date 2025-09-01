#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Installing truledgr-land workspace deps into repo root..."
npm install --workspace=truledgr-land --no-audit --no-fund
