#!/bin/bash
# Simple build script for Cloudflare Pages
# This ensures the www directory contents are in the root of the build output

echo "Copying www directory contents to build root..."
cp -r www/* .
echo "Build complete!"

# List files to verify
echo "Files in build directory:"
ls -la
