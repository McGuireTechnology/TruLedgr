#!/bin/sh
# Shell script to clone subprojects and set up Python virtual environments

REPOS="\
  TruLedgr-API=https://github.com/McGuireTechnology/TruLedgr-API.git \
  TruLedgr-App=https://github.com/McGuireTechnology/TruLedgr-App.git \
  TruLedgr-Docs=https://github.com/McGuireTechnology/TruLedgr-Docs.git \
  TruLedgr-Web=https://github.com/McGuireTechnology/TruLedgr-Web.git \
  TruLedgr-Apple=https://github.com/McGuireTechnology/TruLedgr-Apple.git \
  TruLedgr-Android=https://github.com/McGuireTechnology/TruLedgr-Android.git \
"

for entry in $REPOS; do
  NAME=$(echo $entry | cut -d= -f1)
  URL=$(echo $entry | cut -d= -f2)
  if [ ! -d "$NAME" ]; then
    git clone "$URL"
  fi
  if [ -f "$NAME/requirements.txt" ]; then
    if [ ! -d "$NAME/.venv" ]; then
      python3 -m venv "$NAME/.venv"
    fi
    "$NAME/.venv/bin/pip" install -r "$NAME/requirements.txt"
  fi
done

echo "All subprojects cloned and Python environments set up."
