#!/bin/bash

# Migration Validation Script
# Validates migrations for production safety

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🔍 TruLedgr Migration Validation"
echo "================================"

# Check if migration files exist
if [ ! -d "migrations/versions" ]; then
    print_error "Migration directory not found"
    exit 1
fi

VALIDATION_PASSED=true

# Check for dangerous operations
print_status "Checking for dangerous operations..."

DANGEROUS_PATTERNS=(
    "drop_table"
    "DROP TABLE"
    "drop_column"
    "DROP COLUMN"
    "ALTER TABLE.*DROP"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if grep -r "$pattern" migrations/versions/ 2>/dev/null; then
        print_warning "Found potentially dangerous operation: $pattern"
        print_warning "Please review carefully and ensure backup exists"
    fi
done

# Check migration file naming
print_status "Checking migration file naming convention..."

for file in migrations/versions/*.py; do
    if [[ ! "$file" =~ migrations/versions/[0-9]{3}_[a-z_]+\.py$ ]]; then
        print_warning "Migration file doesn't follow naming convention: $file"
        print_warning "Expected: XXX_descriptive_name.py"
    fi
done

# Check for proper revision IDs
print_status "Checking revision ID consistency..."

python3 << 'EOF'
import os
import re
import sys

def check_revision_consistency():
    """Check that revision IDs are consistent across migration files."""
    migrations_dir = "migrations/versions"
    files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
    files.sort()
    
    revisions = []
    down_revisions = []
    
    for file in files:
        filepath = os.path.join(migrations_dir, file)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Extract revision ID
        revision_match = re.search(r'revision:\s*str\s*=\s*["\']([^"\']+)["\']', content)
        if revision_match:
            revisions.append((file, revision_match.group(1)))
        
        # Extract down_revision ID
        down_revision_match = re.search(r'down_revision:\s*.*?=\s*["\']([^"\']*)["\']', content)
        if down_revision_match:
            down_revision = down_revision_match.group(1)
            if down_revision:
                down_revisions.append((file, down_revision))
    
    # Check for duplicates
    revision_ids = [r[1] for r in revisions]
    if len(revision_ids) != len(set(revision_ids)):
        print("❌ Duplicate revision IDs found!")
        return False
    
    # Check revision chain
    for i, (file, revision_id) in enumerate(revisions[1:], 1):
        expected_down_revision = revisions[i-1][1]
        actual_down_revision = next((dr[1] for dr in down_revisions if dr[0] == file), None)
        
        if actual_down_revision != expected_down_revision:
            print(f"❌ Broken revision chain in {file}")
            print(f"   Expected down_revision: {expected_down_revision}")
            print(f"   Actual down_revision: {actual_down_revision}")
            return False
    
    print("✅ Revision chain is consistent")
    return True

if not check_revision_consistency():
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    VALIDATION_PASSED=false
fi

# Check for foreign key constraints
print_status "Checking foreign key constraint order..."

python3 << 'EOF'
import os
import re

def check_fk_order():
    """Check that tables are created before their foreign keys are referenced."""
    migrations_dir = "migrations/versions"
    files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
    files.sort()
    
    tables_created = set()
    fk_violations = []
    
    for file in files:
        filepath = os.path.join(migrations_dir, file)
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find table creations
        table_matches = re.findall(r'op\.create_table\(\s*["\']([^"\']+)["\']', content)
        for table in table_matches:
            tables_created.add(table)
        
        # Find foreign key constraints
        fk_matches = re.findall(r'sa\.ForeignKeyConstraint\([^)]*\[["\']\w+["\']\],\s*\[["\']([\w_]+)\.', content)
        for referenced_table in fk_matches:
            if referenced_table not in tables_created:
                fk_violations.append((file, referenced_table))
    
    if fk_violations:
        print("❌ Foreign key constraint violations found:")
        for file, table in fk_violations:
            print(f"   {file} references {table} before it's created")
        return False
    
    print("✅ Foreign key constraints are properly ordered")
    return True

if not check_fk_order():
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    VALIDATION_PASSED=false
fi

# Check migration syntax
print_status "Checking migration syntax..."

for file in migrations/versions/*.py; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        print_error "Syntax error in $file"
        VALIDATION_PASSED=false
    fi
done

# Summary
echo
if [ "$VALIDATION_PASSED" = true ]; then
    print_success "🎉 All migration validations passed!"
    echo
    print_status "Migrations are ready for production deployment"
else
    print_error "❌ Migration validation failed!"
    echo
    print_error "Please fix the issues above before deploying to production"
    exit 1
fi
