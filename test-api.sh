#!/bin/bash
# Quick test to verify the TruLedgr API is responding correctly

echo "🧪 Testing TruLedgr API..."
echo ""

# Test root endpoint
echo "1. Testing GET / ..."
response=$(curl -s http://localhost:8000/)
if echo "$response" | grep -q "Bonjour"; then
    echo "   ✅ Root endpoint OK: $response"
else
    echo "   ❌ Root endpoint failed or unexpected response: $response"
fi
echo ""

# Test health endpoint
echo "2. Testing GET /health ..."
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    echo "   ✅ Health endpoint OK: $response"
else
    echo "   ❌ Health endpoint failed or unexpected response: $response"
fi
echo ""

# Test CORS headers
echo "3. Testing CORS headers ..."
cors_headers=$(curl -s -I -X OPTIONS http://localhost:8000/health | grep -i "access-control")
if [ -n "$cors_headers" ]; then
    echo "   ✅ CORS headers present:"
    echo "$cors_headers" | sed 's/^/      /'
else
    echo "   ⚠️  No CORS headers found (may be normal for non-preflight requests)"
fi
echo ""

echo "🎉 API test complete!"
echo ""
echo "To start the API if it's not running:"
echo "  ./start-api.sh"
