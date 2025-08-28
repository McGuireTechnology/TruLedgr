#!/bin/bash

# TruLedgr Digital Ocean Deployment Script
# This script helps deploy the TruLedgr API to Digital Ocean App Platform

set -e

echo "🚀 TruLedgr Digital Ocean Deployment"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="truledgr-api"
REGION="nyc"  # New York region
DB_SIZE="db-s-1vcpu-1gb"
INSTANCE_SIZE="basic-xxs"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        print_error "doctl is not installed. Please install it first:"
        echo "  curl -sL https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz | tar -xzv"
        echo "  sudo mv doctl /usr/local/bin"
        exit 1
    fi

    # Check if authenticated
    if ! doctl account get &> /dev/null; then
        print_error "Not authenticated with Digital Ocean. Please run:"
        echo "  doctl auth init"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Create the app
create_app() {
    print_status "Creating Digital Ocean App..."

    if doctl apps list | grep -q "$APP_NAME"; then
        print_warning "App '$APP_NAME' already exists. Skipping creation."
        return
    fi

    doctl apps create --spec .do/app.yaml \
        --wait \
        --format ID,Name,Phase,PublicURL \
        --no-header

    print_success "App created successfully"
}

# Set up environment variables
setup_environment() {
    print_status "Setting up environment variables..."

    # Get app ID
    APP_ID=$(doctl apps list | grep "$APP_NAME" | awk '{print $1}')

    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID for '$APP_NAME'"
        exit 1
    fi

    print_status "App ID: $APP_ID"

    # Set environment variables
    print_status "Setting SECRET_KEY..."
    doctl apps update "$APP_ID" \
        --set-env SECRET_KEY="$(openssl rand -hex 32)" \
        --format ID,Name,Phase

    print_status "Setting DATABASE_URL (if available)..."
    if [ -n "$DATABASE_URL" ]; then
        doctl apps update "$APP_ID" \
            --set-env DATABASE_URL="$DATABASE_URL" \
            --format ID,Name,Phase
    else
        print_warning "DATABASE_URL not provided. You must set this manually in the Digital Ocean dashboard."
        print_warning "Format: postgresql://user:password@host:port/database"
    fi

    print_status "Setting SENTRY_DSN (if available)..."
    if [ -n "$SENTRY_DSN" ]; then
        doctl apps update "$APP_ID" \
            --set-env SENTRY_DSN="$SENTRY_DSN" \
            --format ID,Name,Phase
    fi

    print_status "Setting SMTP credentials (if available)..."
    if [ -n "$SMTP_HOST" ] && [ -n "$SMTP_USER" ] && [ -n "$SMTP_PASSWORD" ]; then
        doctl apps update "$APP_ID" \
            --set-env SMTP_HOST="$SMTP_HOST" \
            --set-env SMTP_USER="$SMTP_USER" \
            --set-env SMTP_PASSWORD="$SMTP_PASSWORD" \
            --format ID,Name,Phase
    fi

    print_success "Environment variables configured"
}

# Get deployment status
get_deployment_status() {
    print_status "Getting deployment status..."

    APP_ID=$(doctl apps list | grep "$APP_NAME" | awk '{print $1}')

    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID for '$APP_NAME'"
        exit 1
    fi

    doctl apps get "$APP_ID" \
        --format ID,Name,Phase,PublicURL,CreatedAt,UpdatedAt

    # Get database info
    print_status "Database information:"
    echo "Using external PostgreSQL database (DATABASE_URL must be configured)"
}

# Main deployment function
deploy() {
    echo
    print_status "Starting TruLedgr deployment to Digital Ocean..."
    echo

    check_prerequisites
    create_app
    setup_environment
    get_deployment_status

    echo
    print_success "🎉 Deployment initiated successfully!"
    echo
    print_status "Next steps:"
    echo "1. Monitor deployment progress: doctl apps logs $APP_ID"
    echo "2. Set up custom domain: api.truledgr.app"
    echo "3. Configure DNS records for your domain"
    echo "4. Update frontend applications to use the new API URL"
    echo "5. Set up monitoring and alerts in Digital Ocean dashboard"
}

# Show usage
usage() {
    echo "TruLedgr Digital Ocean Deployment Script"
    echo
    echo "Usage:"
    echo "  $0 deploy          - Deploy the application"
    echo "  $0 status          - Check deployment status"
    echo "  $0 logs            - Show application logs"
    echo "  $0 update          - Update the application"
    echo "  $0 delete          - Delete the application"
    echo
    echo "Environment Variables:"
    echo "  DATABASE_URL        - PostgreSQL connection string (required)"
    echo "  SENTRY_DSN          - Sentry DSN for error tracking (optional)"
    echo "  SMTP_HOST           - SMTP server hostname (optional)"
    echo "  SMTP_USER           - SMTP username (optional)"
    echo "  SMTP_PASSWORD       - SMTP password (optional)"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "status")
        get_deployment_status
        ;;
    "logs")
        APP_ID=$(doctl apps list | grep "$APP_NAME" | awk '{print $1}')
        if [ -n "$APP_ID" ]; then
            doctl apps logs "$APP_ID" --follow
        else
            print_error "App '$APP_NAME' not found"
        fi
        ;;
    "update")
        print_status "Updating application..."
        APP_ID=$(doctl apps list | grep "$APP_NAME" | awk '{print $1}')
        if [ -n "$APP_ID" ]; then
            doctl apps update "$APP_ID" --spec .do/app.yaml --wait
            print_success "Application updated"
        else
            print_error "App '$APP_NAME' not found"
        fi
        ;;
    "delete")
        print_warning "This will delete the application and all associated resources!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            APP_ID=$(doctl apps list | grep "$APP_NAME" | awk '{print $1}')
            if [ -n "$APP_ID" ]; then
                doctl apps delete "$APP_ID" --force
                print_success "Application deleted"
            else
                print_error "App '$APP_NAME' not found"
            fi
        fi
        ;;
    *)
        usage
        exit 1
        ;;
esac
