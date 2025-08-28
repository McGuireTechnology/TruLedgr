#!/bin/bash

# Build script for Digital Ocean deployment
set -e

echo "🚀 Building FastAPI Security Sample for Digital Ocean"

# Build information
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD)
VERSION=${GITHUB_REF_NAME:-$(git describe --tags --always)}

echo "📋 Build Information:"
echo "  Date: $BUILD_DATE"
echo "  VCS Ref: $VCS_REF"
echo "  Version: $VERSION"

# Build Docker image
echo "🐳 Building Docker image..."
docker build \
  --build-arg BUILD_DATE="$BUILD_DATE" \
  --build-arg VCS_REF="$VCS_REF" \
  --build-arg VERSION="$VERSION" \
  --tag truledgr:latest \
  --tag truledgr:$VERSION \
  .

# Run security scan
echo "🔍 Running security scan..."
if command -v trivy &> /dev/null; then
  trivy image --exit-code 0 --severity HIGH,CRITICAL truledgr:latest
else
  echo "⚠️  Trivy not installed, skipping security scan"
fi

# Test the built image
echo "🧪 Testing built image..."
docker run --rm -d --name test-container -p 8000:8000 \
  -e ENVIRONMENT=test \
  -e SECRET_KEY=test-secret-key-for-docker-build-32-chars \
  truledgr:latest

# Wait for container to start
sleep 10

# Health check
if curl -f http://localhost:8000/health; then
  echo "✅ Health check passed"
else
  echo "❌ Health check failed"
  docker logs test-container
  exit 1
fi

# Cleanup
docker stop test-container

echo "✅ Build completed successfully!"

# Optional: Push to registry
if [ "$PUSH_TO_REGISTRY" = "true" ]; then
  echo "📤 Pushing to registry..."
  
  # Tag for registry
  REGISTRY=${REGISTRY:-ghcr.io}
  REPO=${GITHUB_REPOSITORY:-McGuireTechnology/TruLedgr}
  
  docker tag truledgr:latest $REGISTRY/$REPO:latest
  docker tag truledgr:$VERSION $REGISTRY/$REPO:$VERSION
  
  # Push
  docker push $REGISTRY/$REPO:latest
  docker push $REGISTRY/$REPO:$VERSION
  
  echo "✅ Images pushed to $REGISTRY/$REPO"
fi
