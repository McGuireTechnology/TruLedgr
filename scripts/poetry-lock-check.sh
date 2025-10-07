#!/usr/bin/env bash
set -euo pipefail

# If pyproject.toml is staged, attempt to regenerate the lockfile non-interactively
if git diff --cached --name-only | grep -q "^pyproject.toml$"; then
  echo "pyproject.toml changed: regenerating lockfile to verify..."
  if ! poetry lock -n; then
    echo "poetry lock failed; fix pyproject or run 'poetry lock' locally"
    exit 1
  fi

  if git diff --name-only | grep -q "^poetry.lock$"; then
    echo "poetry.lock was updated by 'poetry lock' — please stage and commit the updated poetry.lock before creating the PR."
    git --no-pager diff -- poetry.lock || true
    exit 1
  fi
fi

exit 0
