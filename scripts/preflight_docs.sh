#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# ensure venv
if [ ! -d .venv ]; then
  echo "Creating .venv..."
  python3 -m venv .venv
fi
# activate venv
# shellcheck source=/dev/null
. .venv/bin/activate
echo "Upgrading pip..."
python -m pip install --upgrade pip
if [ -f truledgr-docs/requirements.txt ]; then
  pip install -r truledgr-docs/requirements.txt
else
  echo "truledgr-docs/requirements.txt not found"
fi
