#!/bin/bash
set -e

echo "Starting TruLedgr API..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "PORT: ${PORT:-8000}"

# Install dependencies if requirements.txt is newer than installed packages
if [ requirements.txt -nt .deps_installed ] || [ ! -f .deps_installed ]; then
    echo "Installing Python dependencies..."
    pip install --no-cache-dir -r requirements.txt
    touch .deps_installed
fi

# Start the application
echo "Starting uvicorn server on port ${PORT:-8000}..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
