#!/bin/bash

# TruLedgr Documentation Deployment Script
# This script builds documentation locally for testing
# Production deployment is handled by GitHub Actions

set -e  # Exit on any error

echo "🚀 Building TruLedgr Documentation (Local Build)"
echo "=================================================="

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "📦 Installing MkDocs dependencies..."
    pip install -e ".[docs]"
fi

# Build documentation
echo "🏗️  Building documentation..."
mkdocs build --clean

# Check build status
if [ $? -eq 0 ]; then
    echo "✅ Documentation built successfully!"
    echo ""
    echo "📖 Local preview: http://localhost:8001"
    echo "🌐 Production URL: https://docs.truledgr.app"
    echo ""
    echo "To serve locally:"
    echo "  npm run docs:serve"
    echo ""
    echo "Note: Production deployment is automatic via GitHub Actions"
    echo "when changes are pushed to the main branch."
else
    echo "❌ Documentation build failed!"
    exit 1
fi
