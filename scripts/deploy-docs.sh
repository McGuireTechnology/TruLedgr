#!/bin/bash

# TruLedgr Documentation Deployment Script
# This script builds and deploys the documentation to docs.truledgr.app

set -e  # Exit on any error

echo "🚀 Deploying TruLedgr Documentation to docs.truledgr.app"
echo "=================================================="

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "📦 Installing MkDocs dependencies..."
    pip install -e ".[docs]"
fi

# Build documentation
echo "🏗️  Building documentation..."
mkdocs build --clean --strict

# Check build status
if [ $? -eq 0 ]; then
    echo "✅ Documentation built successfully!"
    echo ""
    echo "📖 Local preview: http://localhost:8001"
    echo "🌐 Production URL: https://docs.truledgr.app"
    echo ""
    echo "To deploy manually:"
    echo "  npm run docs:deploy"
    echo ""
    echo "To serve locally:"
    echo "  npm run docs:serve"
else
    echo "❌ Documentation build failed!"
    exit 1
fi
