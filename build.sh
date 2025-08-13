#!/bin/bash
# Build script for Cloudflare Pages
# This ensures the www directory contents are properly deployed

echo "Building TruLedgr marketing site..."

# Copy all files from www to the root build directory
echo "Copying files from www/ to build root..."
cp -r www/* .

# Ensure index.html exists in root
if [ -f "index.html" ]; then
    echo "✓ index.html found in build root"
else
    echo "✗ ERROR: index.html not found!"
    exit 1
fi

# List all files for debugging
echo "Files in build directory:"
ls -la

# Verify HTML content
echo "Checking index.html content (first 200 chars):"
head -c 200 index.html

echo "Build completed successfully!"
