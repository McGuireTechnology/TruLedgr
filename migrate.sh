#!/bin/bash
# Database migration helper script for TruLedgr
# This script simplifies common Alembic operations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to api directory
cd "$(dirname "$0")/api"

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${BLUE}Loading environment from .env${NC}"
    set -a
    source .env
    set +a
else
    echo -e "${YELLOW}Warning: .env file not found${NC}"
fi

# Function to print usage
usage() {
    echo -e "${BLUE}TruLedgr Database Migration Helper${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  create <message>  - Create new migration with autogenerate"
    echo "  upgrade           - Apply all pending migrations (to head)"
    echo "  downgrade [n]     - Rollback n migrations (default: 1)"
    echo "  current           - Show current migration version"
    echo "  history           - Show migration history"
    echo "  status            - Show current status and pending migrations"
    echo "  init              - Initialize fresh database (WARNING: drops all data)"
    echo ""
    echo "Examples:"
    echo "  $0 create \"Add user timezone field\""
    echo "  $0 upgrade"
    echo "  $0 downgrade 2"
    echo "  $0 current"
    exit 1
}

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry is not installed${NC}"
    echo "Install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Parse command
COMMAND="${1:-help}"

case "$COMMAND" in
    create)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Migration message required${NC}"
            echo "Usage: $0 create \"Description of changes\""
            exit 1
        fi
        echo -e "${GREEN}Creating new migration: $2${NC}"
        poetry run alembic revision --autogenerate -m "$2"
        echo -e "${GREEN}✓ Migration created${NC}"
        echo -e "${YELLOW}Review the migration file in migrations/versions/${NC}"
        ;;
    
    upgrade)
        echo -e "${GREEN}Applying all pending migrations...${NC}"
        poetry run alembic upgrade head
        echo -e "${GREEN}✓ Database updated to latest version${NC}"
        ;;
    
    downgrade)
        STEPS="${2:-1}"
        echo -e "${YELLOW}Rolling back $STEPS migration(s)...${NC}"
        poetry run alembic downgrade "-$STEPS"
        echo -e "${GREEN}✓ Rollback complete${NC}"
        ;;
    
    current)
        echo -e "${BLUE}Current migration version:${NC}"
        poetry run alembic current
        ;;
    
    history)
        echo -e "${BLUE}Migration history:${NC}"
        poetry run alembic history --verbose
        ;;
    
    status)
        echo -e "${BLUE}Current version:${NC}"
        poetry run alembic current
        echo ""
        echo -e "${BLUE}Latest version:${NC}"
        poetry run alembic heads
        echo ""
        echo -e "${BLUE}History:${NC}"
        poetry run alembic history | head -10
        ;;
    
    init)
        echo -e "${RED}⚠️  WARNING: This will delete the existing database!${NC}"
        read -p "Are you sure? (yes/no): " -r
        echo
        if [[ $REPLY =~ ^yes$ ]]; then
            echo -e "${YELLOW}Removing existing database...${NC}"
            cd ..
            rm -f truledgr.db
            cd api
            echo -e "${GREEN}Creating fresh database...${NC}"
            poetry run alembic upgrade head
            echo -e "${GREEN}✓ Database initialized${NC}"
        else
            echo -e "${BLUE}Operation cancelled${NC}"
        fi
        ;;
    
    help|--help|-h)
        usage
        ;;
    
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo ""
        usage
        ;;
esac
