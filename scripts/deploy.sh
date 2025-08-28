#!/bin/bash

# Digital Ocean deployment script
set -e

echo "🚀 Deploying TruLedgr to Digital Ocean"

# Configuration
APP_NAME="truledgr"
NAMESPACE="production"
REGISTRY="ghcr.io"
REPO="${GITHUB_REPOSITORY:-McGuireTechnology/TruLedgr}"
IMAGE_TAG="${GITHUB_SHA:-latest}"

# Check required tools
check_tool() {
  if ! command -v $1 &> /dev/null; then
    echo "❌ $1 is required but not installed"
    exit 1
  fi
}

echo "🔍 Checking required tools..."
check_tool kubectl
check_tool doctl

# Authenticate with Digital Ocean
echo "🔐 Authenticating with Digital Ocean..."
if [ -z "$DIGITALOCEAN_ACCESS_TOKEN" ]; then
  echo "❌ DIGITALOCEAN_ACCESS_TOKEN environment variable is required"
  exit 1
fi

doctl auth init --access-token "$DIGITALOCEAN_ACCESS_TOKEN"

# Connect to Kubernetes cluster
echo "🔗 Connecting to Kubernetes cluster..."
if [ -z "$DO_CLUSTER_NAME" ]; then
  echo "❌ DO_CLUSTER_NAME environment variable is required"
  exit 1
fi

doctl kubernetes cluster kubeconfig save "$DO_CLUSTER_NAME"

# Create namespace if it doesn't exist
echo "📁 Creating namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Deploy secrets (if they don't exist)
echo "🔐 Deploying secrets..."
if ! kubectl get secret app-secrets -n "$NAMESPACE" &> /dev/null; then
  echo "⚠️  Creating placeholder secret - UPDATE WITH REAL VALUES!"
  kubectl create secret generic app-secrets \
    --from-literal=secret-key="CHANGE-THIS-IN-PRODUCTION-32-CHARS-MIN" \
    --from-literal=database-url="postgresql://user:pass@host:5432/db" \
    -n "$NAMESPACE"
fi

# Apply Kubernetes manifests
echo "📦 Applying Kubernetes manifests..."
kubectl apply -f k8s/ -n "$NAMESPACE"

# Update deployment image
echo "🔄 Updating deployment image..."
kubectl set image deployment/"$APP_NAME" \
  "$APP_NAME"="$REGISTRY/$REPO:$IMAGE_TAG" \
  -n "$NAMESPACE"

# Wait for rollout
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/"$APP_NAME" -n "$NAMESPACE" --timeout=300s

# Verify deployment
echo "✅ Verifying deployment..."
kubectl get pods -n "$NAMESPACE" -l app="$APP_NAME"

# Get service information
echo "📋 Service information:"
kubectl get service "$APP_NAME-service" -n "$NAMESPACE"

# Get ingress information
echo "🌐 Ingress information:"
kubectl get ingress "$APP_NAME-ingress" -n "$NAMESPACE"

echo "🎉 Deployment completed successfully!"

# Optional: Run smoke tests
if [ "$RUN_SMOKE_TESTS" = "true" ]; then
  echo "🧪 Running smoke tests..."
  
  # Get service URL
  SERVICE_URL=$(kubectl get ingress "$APP_NAME-ingress" -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].host}')
  
  if [ -n "$SERVICE_URL" ]; then
    # Test health endpoint
    if curl -f "https://$SERVICE_URL/health"; then
      echo "✅ Health check passed"
    else
      echo "❌ Health check failed"
      exit 1
    fi
    
    # Test API documentation
    if curl -f "https://$SERVICE_URL/docs"; then
      echo "✅ API documentation accessible"
    else
      echo "⚠️  API documentation not accessible"
    fi
  else
    echo "⚠️  Could not determine service URL for smoke tests"
  fi
fi
