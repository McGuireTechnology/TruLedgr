#!/bin/bash

# TruLedgr Production Deployment Quick Guide

echo "🚀 TruLedgr Production Migration Deployment Workflow"
echo "===================================================="
echo

cat << 'EOF'
## Your Complete Production Migration Workflow:

### 🔧 What Changed:
✅ Created 7 focused migrations (001-007) instead of 1 large migration
✅ Added production-safe startup behavior (no create_tables() in production)
✅ Built comprehensive deployment scripts with migration support
✅ Added migration validation and safety checks

### 📋 Pre-Deployment Checklist:

1. **Validate Migrations Locally:**
   ```bash
   # Test all migrations
   python scripts/migrate.py upgrade
   python scripts/migrate.py check
   
   # Test rollback capability
   python scripts/migrate.py downgrade 005_auth_tables
   python scripts/migrate.py upgrade
   
   # Validate migration safety
   ./scripts/validate-migration.sh
   ```

2. **Test on Staging:**
   ```bash
   # Deploy to staging environment first
   export DATABASE_URL="postgresql://user:pass@staging-host:5432/truledgr_staging"
   python scripts/migrate.py upgrade
   ```

3. **Backup Production Database:**
   - Ensure recent backup exists via your database provider
   - Document backup timestamp
   - Test backup restoration procedure

### 🚀 Production Deployment:

**Option 1: Full Automated Deployment (Recommended)**
```bash
export DATABASE_URL="postgresql://user:pass@prod-host:5432/truledgr_production"
./scripts/deploy-production.sh deploy
```

**Option 2: Step-by-Step Manual Deployment**
```bash
# 1. Run migrations only
export DATABASE_URL="postgresql://user:pass@prod-host:5432/truledgr_production"
./scripts/deploy-production.sh migrate-only

# 2. Deploy application code
./scripts/deploy-production.sh deploy-only
```

**Option 3: Emergency Migrations Only**
```bash
export DATABASE_URL="postgresql://user:pass@prod-host:5432/truledgr_production"
python scripts/migrate.py upgrade
```

### 🔍 Available Commands:

**Migration Management:**
```bash
python scripts/migrate.py current              # Check current migration
python scripts/migrate.py upgrade              # Apply all pending migrations
python scripts/migrate.py upgrade 005_auth_tables  # Apply to specific migration
python scripts/migrate.py downgrade 004_groups_tables  # Rollback
python scripts/migrate.py history              # Show all migrations
python scripts/migrate.py check                # Check for schema drift
```

**Deployment Commands:**
```bash
./scripts/deploy-production.sh deploy          # Full deployment with migrations
./scripts/deploy-production.sh migrate-only    # Migrations only
./scripts/deploy-production.sh deploy-only     # Code deployment only
./scripts/deploy-production.sh status          # Check current status
./scripts/deploy-production.sh validate        # Validate current state
./scripts/deploy-production.sh rollback 005_auth_tables  # Emergency rollback
```

**Validation:**
```bash
./scripts/validate-migration.sh                # Validate migration files
python scripts/generate_erd.py                 # Update documentation
```

### 🚨 Emergency Procedures:

**If migration fails:**
```bash
./scripts/deploy-production.sh rollback 006_session_tables
```

**If application fails after migration:**
```bash
# Check logs
doctl apps logs $APP_ID --follow

# Restart application
doctl apps restart $APP_ID
```

### 📊 Post-Deployment:

```bash
# Verify health
curl https://api.truledgr.app/health

# Check migration status
python scripts/migrate.py current

# Update documentation
python scripts/generate_erd.py
```

### 🔐 Security Notes:

1. **Never run create_tables() in production** - Now fixed in main.py
2. **Always backup before migrations** - Built into deployment script
3. **Test rollback procedures** - Validate downgrade functions work
4. **Use environment-specific DATABASE_URL** - Required for all operations

### 📚 Documentation:

- Production Workflow: docs/developer/production-migration-workflow.md
- Migration Structure: docs/developer/migration-structure.md
- Database Overview: docs/developer/database-overview.md
- ERD Documentation: docs/developer/database/README.md

EOF

echo
echo "🎯 Next Steps:"
echo "1. Set your production DATABASE_URL environment variable"
echo "2. Test the workflow on staging first"
echo "3. Run: ./scripts/deploy-production.sh deploy"
echo
echo "📞 Need help? Check the documentation files listed above!"
