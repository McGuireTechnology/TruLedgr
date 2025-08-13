#!/bin/bash
# Alternative build script - simpler approach

echo "Simple build for TruLedgr marketing site..."

# Just copy everything from www to current directory
if [ -d "www" ]; then
    echo "Copying www contents to root..."
    cp -rv www/. .
    
    # Verify the copy worked
    if [ -f "index.html" ]; then
        echo "✓ Build successful - index.html found"
        ls -la *.html
    else
        echo "✗ Build failed - no index.html"
        exit 1
    fi
else
    echo "✗ www directory not found"
    exit 1
fi
