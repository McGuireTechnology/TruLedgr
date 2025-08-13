#!/bin/bash
# Build script for Cloudflare Pages
# This ensures the www directory contents are properly deployed

echo "Building TruLedgr marketing site..."

# Debug: Show current directory and contents
echo "Current directory: $(pwd)"
echo "Contents of current directory:"
ls -la

echo "Contents of www directory:"
ls -la www/

# Copy all files from www to the root build directory
echo "Copying files from www/ to build root..."
cp -r www/* .

# Debug: Show what was copied
echo "Contents after copy:"
ls -la

# Ensure index.html exists in root
if [ -f "index.html" ]; then
    echo "✓ index.html found in build root"
    echo "File size: $(wc -c < index.html) bytes"
else
    echo "✗ ERROR: index.html not found!"
    echo "Looking for HTML files:"
    find . -name "*.html" -type f
    exit 1
fi

echo "Build completed successfully!"
