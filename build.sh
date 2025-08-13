#!/bin/bash
# Build script for Vue/Vite on Cloudflare Pages

echo "Building TruLedgr Vue marketing site..."

# Build the Vue version (www is now the Vue directory)
if [ -d "www" ] && [ -f "www/package.json" ]; then
    echo "Building Vue/Vite version..."
    cd www
    
    # Install dependencies
    echo "Installing dependencies..."
    npm ci
    
    # Build the Vue app
    echo "Building Vue app..."
    npm run build
    
    # Copy built files to root
    echo "Copying built files to root..."
    cp -rv dist/* ../
    
    # Verify the build
    cd ..
    if [ -f "index.html" ]; then
        echo "✓ Vue build successful - index.html found"
        echo "Files in build directory:"
        ls -la *.html
        ls -la assets/ 2>/dev/null || true
    else
        echo "✗ Vue build failed - no index.html"
        exit 1
    fi
else
    # Fallback to static version if Vue build fails
    echo "Vue build not available, checking for static version..."
    if [ -d "www-old" ]; then
        echo "Using static HTML version from www-old..."
        cp -rv www-old/. .
        
        if [ -f "index.html" ]; then
            echo "✓ Static build successful - index.html found"
        else
            echo "✗ Static build failed - no index.html"
            exit 1
        fi
    else
        echo "✗ No buildable website found"
        exit 1
    fi
fi

echo "Build completed successfully!"
