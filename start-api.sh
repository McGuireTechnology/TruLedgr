#!/bin/bash
# Start the TruLedgr API server for local development

cd "$(dirname "$0")"

echo "🚀 Starting TruLedgr API..."
echo ""
echo "The API will be available at:"
echo "  - http://localhost:8000"
echo "  - http://127.0.0.1:8000"
echo "  - http://api.truledgr.app:8000 (Android emulator)"
echo ""
echo "Endpoints:"
echo "  - GET / (root message)"
echo "  - GET /health (health check)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with poetry if available, otherwise try uvicorn directly
if command -v poetry &> /dev/null; then
    poetry run python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
else
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
fi
