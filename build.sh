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
    
    # Verify the build
    if [ -f "dist/index.html" ]; then
        echo "✓ Vue build successful - index.html found in dist/"
        echo "Files in dist directory:"
        ls -la dist/*.html
        ls -la dist/assets/ 2>/dev/null || true
        
        # Show build output location
        echo "Build output is in: www/dist/"
        echo "Cloudflare Pages should be configured to serve from: www/dist"
    else
        echo "✗ Vue build failed - no index.html in dist/"
        exit 1
    fi
    
    cd ..
else
    # Fallback to static version if Vue build fails
    echo "Vue build not available, checking for static version..."
    if [ -d "www-old" ]; then
        echo "Using static HTML version from www-old..."
        
        # Create a dist directory in www-old for consistency
        mkdir -p www-old/dist
        cp -r www-old/*.html www-old/*.css www-old/*.js www-old/*.ico www-old/_* www-old/dist/ 2>/dev/null || true
        
        if [ -f "www-old/index.html" ]; then
            echo "✓ Static build available in www-old/"
            echo "Cloudflare Pages should be configured to serve from: www-old"
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
echo "Note: Files are kept in their respective directories and not copied to root."
