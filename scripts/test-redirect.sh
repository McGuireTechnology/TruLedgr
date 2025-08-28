#!/bin/bash

# TruLedgr Landing Page Redirect Test Script
# Tests the www to apex domain redirect configuration

echo "🔍 Testing TruLedgr Landing Page Redirects"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_redirect() {
    local url=$1
    local expected_location=$2
    local description=$3

    echo -e "\n${YELLOW}Testing: ${description}${NC}"
    echo "URL: $url"

    # Make request and capture response
    response=$(curl -s -I -w "%{http_code}" "$url" 2>/dev/null)
    status_code=$(echo "$response" | tail -n1)
    location=$(echo "$response" | grep -i "location:" | sed 's/.*: //' | tr -d '\r')

    echo "Status Code: $status_code"
    echo "Location: $location"

    # Check if redirect is working
    if [ "$status_code" = "301" ] && [ "$location" = "$expected_location" ]; then
        echo -e "${GREEN}✅ PASS: Correct redirect${NC}"
    elif [ "$status_code" = "200" ] && [ "$url" = "$expected_location" ]; then
        echo -e "${GREEN}✅ PASS: Direct access to apex domain${NC}"
    else
        echo -e "${RED}❌ FAIL: Unexpected response${NC}"
    fi
}

# Test cases
echo -e "\n🚀 Starting redirect tests...\n"

# Test WWW to Apex redirect
test_redirect "https://www.truledgr.com" "https://truledgr.com/" "WWW to Apex Redirect"

# Test Apex domain direct access
test_redirect "https://truledgr.com" "https://truledgr.com" "Apex Domain Direct Access"

# Test HTTP to HTTPS redirect (if configured)
test_redirect "http://truledgr.com" "https://truledgr.com/" "HTTP to HTTPS Redirect"

# Test WWW HTTP to HTTPS redirect
test_redirect "http://www.truledgr.com" "https://truledgr.com/" "WWW HTTP to HTTPS Redirect"

echo -e "\n${YELLOW}📋 Manual Testing Checklist:${NC}"
echo "1. Open https://www.truledgr.com in browser"
echo "2. Verify it redirects to https://truledgr.com"
echo "3. Check that all links and resources load correctly"
echo "4. Test on mobile devices"
echo "5. Clear browser cache if issues persist"

echo -e "\n${YELLOW}🔧 Troubleshooting:${NC}"
echo "- DNS propagation may take up to 24 hours"
echo "- Clear Cloudflare cache if redirects aren't working"
echo "- Check Cloudflare Pages domain configuration"
echo "- Verify SSL certificate is active"

echo -e "\n${GREEN}✨ Test complete!${NC}"
