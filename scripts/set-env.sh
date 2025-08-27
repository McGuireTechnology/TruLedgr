#!/bin/bash
# Environment Configuration Script
# Usage: ./scripts/set-env.sh [environment]
# Environments: development, sandbox, staging, production, test

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default to development if no environment specified
ENVIRONMENT="${1:-development}"

# Validate environment
case "$ENVIRONMENT" in
    development|sandbox|staging|production|test)
        ;;
    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Valid environments: development, sandbox, staging, production, test"
        exit 1
        ;;
esac

TEMPLATE_FILE="$PROJECT_ROOT/.env.$ENVIRONMENT.template"
ENV_FILE="$PROJECT_ROOT/.env"

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    exit 1
fi

# Backup existing .env if it exists
if [ -f "$ENV_FILE" ]; then
    echo "📦 Backing up existing .env to .env.backup"
    cp "$ENV_FILE" "$ENV_FILE.backup"
fi

# Copy template to .env
echo "🔄 Setting environment to: $ENVIRONMENT"
cp "$TEMPLATE_FILE" "$ENV_FILE"

echo "✅ Environment set to $ENVIRONMENT"
echo "📁 Configuration loaded from: $TEMPLATE_FILE"
echo "🎯 Active configuration: $ENV_FILE"
echo ""
echo "💡 Tips:"
echo "   - Create .env.local for local overrides (not tracked by git)"
echo "   - The .env file is now tracked by git for this environment"
echo "   - Run 'source .venv/bin/activate && python -m api.main' to start the server"
