#!/bin/bash

# TruLedgr Production Deployment Script with Migration Support
# This script safely deploys the application with database migrations

set -e

echo "🚀 TruLedgr Production Deployment with Migrations"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="truledgr-api"
BACKUP_RETENTION_DAYS=30

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

# Get app ID
get_app_id() {
    APP_ID=$(doctl apps list | grep "$APP_NAME" | awk '{print $1}')
    if [ -z "$APP_ID" ]; then
        print_error "Could not find app ID for '$APP_NAME'"
        exit 1
    fi
    echo "$APP_ID"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        print_error "doctl is not installed"
        exit 1
    fi

    # Check if authenticated
    if ! doctl account get &> /dev/null; then
        print_error "Not authenticated with Digital Ocean. Please run: doctl auth init"
        exit 1
    fi

    # Check if python and migration script are available
    if [ ! -f "scripts/migrate.py" ]; then
        print_error "Migration script not found. Please run from project root."
        exit 1
    fi

    # Check if production DATABASE_URL is set
    if [ -z "$DATABASE_URL" ]; then
        print_error "DATABASE_URL environment variable is required for production migrations"
        print_error "Please set: export DATABASE_URL='postgresql://user:pass@host:port/database'"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Backup production database
backup_database() {
    print_status "Creating database backup..."
    
    # Extract database info from DATABASE_URL
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    
    # Create backup filename with timestamp
    BACKUP_FILE="backup_${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
    
    print_status "Backing up database: $DB_NAME"
    print_status "Backup file: $BACKUP_FILE"
    
    # Note: This requires pg_dump to be available and proper authentication
    # In production, you might want to use your database provider's backup tools
    print_warning "Manual backup verification required:"
    echo "  1. Ensure your database provider's automated backups are recent"
    echo "  2. Consider creating a manual backup through your provider's interface"
    echo "  3. Document the backup timestamp: $(date)"
    
    read -p "Have you verified a recent backup exists? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Please ensure a backup exists before proceeding"
        exit 1
    fi
    
    print_success "Backup verification completed"
}

# Check current migration status
check_migration_status() {
    print_status "Checking current migration status..."
    
    # Get current migration
    CURRENT_MIGRATION=$(python scripts/migrate.py current 2>/dev/null | grep -E "^[0-9]" || echo "No migrations applied")
    print_status "Current migration: $CURRENT_MIGRATION"
    
    # Check for pending migrations
    print_status "Checking for pending migrations..."
    python scripts/migrate.py show head
    
    return 0
}

# Validate migrations before applying
validate_migrations() {
    print_status "Validating migrations..."
    
    # Check for schema drift
    if ! python scripts/migrate.py check; then
        print_error "Schema drift detected. Please resolve before deploying."
        exit 1
    fi
    
    # TODO: Add more validation checks
    # - Check for dangerous operations (DROP TABLE, etc.)
    # - Validate foreign key constraints
    # - Check for missing indexes on large tables
    
    print_success "Migration validation passed"
}

# Apply database migrations
apply_migrations() {
    print_status "Applying database migrations..."
    
    # Run migrations with verbose output
    if python scripts/migrate.py upgrade; then
        print_success "Migrations applied successfully"
    else
        print_error "Migration failed! Check logs and consider rollback."
        exit 1
    fi
    
    # Verify final state
    FINAL_MIGRATION=$(python scripts/migrate.py current 2>/dev/null | grep -E "^[0-9]" || echo "Unknown")
    print_status "Final migration: $FINAL_MIGRATION"
}

# Deploy application code
deploy_application() {
    print_status "Deploying application code..."
    
    APP_ID=$(get_app_id)
    
    # Update the application with new code
    if doctl apps update "$APP_ID" --spec .do/app.yaml --wait; then
        print_success "Application deployment successful"
    else
        print_error "Application deployment failed"
        exit 1
    fi
}

# Validate deployment
validate_deployment() {
    print_status "Validating deployment..."
    
    APP_ID=$(get_app_id)
    
    # Get application URL
    APP_URL=$(doctl apps get "$APP_ID" --format PublicURL --no-header)
    
    # Wait a moment for the app to start
    print_status "Waiting for application to start..."
    sleep 30
    
    # Check health endpoint
    if curl -f -s "$APP_URL/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed. Check application logs."
        # Don't exit - show logs instead
        doctl apps logs "$APP_ID" --tail 50
        exit 1
    fi
    
    # Check migration status matches expected
    print_status "Verifying migration status..."
    if python scripts/migrate.py check; then
        print_success "Database schema is up to date"
    else
        print_warning "Schema drift detected after deployment"
    fi
}

# Show deployment summary
show_summary() {
    print_success "🎉 Deployment completed successfully!"
    echo
    print_status "Deployment Summary:"
    echo "  📅 Timestamp: $(date)"
    echo "  🗄️  Database: $(echo "$DATABASE_URL" | sed 's/@.*/@[REDACTED]/')"
    echo "  📝 Final Migration: $(python scripts/migrate.py current 2>/dev/null | grep -E "^[0-9]" || echo "Unknown")"
    
    APP_ID=$(get_app_id)
    APP_URL=$(doctl apps get "$APP_ID" --format PublicURL --no-header)
    echo "  🌐 Application URL: $APP_URL"
    echo
    print_status "Next steps:"
    echo "  1. Monitor application: doctl apps logs $APP_ID --follow"
    echo "  2. Update ERD documentation: python scripts/generate_erd.py"
    echo "  3. Notify team of successful deployment"
    echo "  4. Monitor performance and error rates"
}

# Rollback function (in case of emergency)
rollback_migration() {
    local target_migration="$1"
    
    if [ -z "$target_migration" ]; then
        print_error "Please specify target migration for rollback"
        print_status "Available migrations:"
        python scripts/migrate.py history
        exit 1
    fi
    
    print_warning "🚨 EMERGENCY ROLLBACK INITIATED"
    print_warning "Rolling back to: $target_migration"
    
    read -p "Are you sure you want to rollback? This may cause data loss. (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Rollback cancelled"
        exit 0
    fi
    
    # Stop application
    APP_ID=$(get_app_id)
    print_status "Scaling down application..."
    doctl apps update "$APP_ID" --instance-count 0
    
    # Rollback migration
    print_status "Rolling back database migration..."
    if python scripts/migrate.py downgrade "$target_migration"; then
        print_success "Migration rollback successful"
    else
        print_error "Migration rollback failed!"
        exit 1
    fi
    
    # Restart application
    print_status "Restarting application..."
    doctl apps update "$APP_ID" --instance-count 1
    
    print_success "Rollback completed"
}

# Main deployment function
deploy() {
    echo
    print_status "Starting production deployment with migrations..."
    echo
    
    check_prerequisites
    backup_database
    check_migration_status
    validate_migrations
    apply_migrations
    deploy_application
    validate_deployment
    show_summary
}

# Show usage
usage() {
    echo "TruLedgr Production Deployment Script"
    echo
    echo "Usage:"
    echo "  $0 deploy                    - Full deployment with migrations"
    echo "  $0 migrate-only             - Run migrations only (no code deployment)"
    echo "  $0 deploy-only              - Deploy code only (no migrations)"
    echo "  $0 status                   - Check current status"
    echo "  $0 rollback <migration>     - Emergency rollback to specific migration"
    echo "  $0 validate                 - Validate current state"
    echo
    echo "Environment Variables:"
    echo "  DATABASE_URL                - Production database connection string (required)"
    echo
    echo "Examples:"
    echo "  export DATABASE_URL='postgresql://user:pass@host:5432/truledgr'"
    echo "  $0 deploy"
    echo "  $0 rollback 005_auth_tables"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "migrate-only")
        check_prerequisites
        backup_database
        check_migration_status
        validate_migrations
        apply_migrations
        print_success "Migrations completed"
        ;;
    "deploy-only")
        check_prerequisites
        deploy_application
        validate_deployment
        print_success "Application deployment completed"
        ;;
    "status")
        check_prerequisites
        check_migration_status
        APP_ID=$(get_app_id)
        doctl apps get "$APP_ID" --format ID,Name,Phase,PublicURL
        ;;
    "rollback")
        check_prerequisites
        rollback_migration "$2"
        ;;
    "validate")
        check_prerequisites
        check_migration_status
        validate_migrations
        validate_deployment
        ;;
    *)
        usage
        exit 1
        ;;
esac
