#!/bin/bash
# Build script for Vue/Vite on Cloudflare Pages

echo "Building TruLedgr Vue marketing site..."

# We're now running from inside the www directory
if [ -f "package.json" ]; then
    echo "Building Vue/Vite version..."
    
    # Install dependencies
    echo "Installing dependencies..."
    npm ci
    
    # Build the Vue app
    echo "Building Vue app..."
    npm run build
    
    # Verify the build
    if [ -f "dist/index.html" ]; then
        echo "✓ Vue build successful - index.html found in dist/"
        echo "Files in dist directory:"
        ls -la dist/*.html
        ls -la dist/assets/ 2>/dev/null || true
        
        # Show build output location
        echo "Build output is in: dist/"
        echo "Cloudflare Pages serves from: dist"
    else
        echo "✗ Vue build failed - no index.html in dist/"
        exit 1
    fi
else
    echo "✗ No package.json found - not in Vue project directory"
    exit 1
fi

echo "Build completed successfully!"
echo "Note: Build script now runs from within the www directory."
