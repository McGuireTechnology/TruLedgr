# Production Migration Deployment Workflow

## Overview

This document outlines the complete workflow for deploying database migrations to production in the TruLedgr application.

## ⚠️ CRITICAL: Current Issue

**Your application currently uses `create_tables()` in production, which is NOT safe for production deployments.** 

### What needs to change:
1. **Remove `create_tables()` from production startup**
2. **Add migration execution to deployment process**
3. **Implement pre-deployment migration validation**

## 🔄 Production Migration Workflow

### Phase 1: Pre-Deployment (Local)

#### 1. Develop and Test Migrations Locally

```bash
# 1. Create new migration (if needed)
python scripts/migrate.py create "add new feature table"

# 2. Review generated migration
# Edit the migration file if necessary

# 3. Test migration locally
python scripts/migrate.py upgrade

# 4. Test rollback
python scripts/migrate.py downgrade <previous_version>
python scripts/migrate.py upgrade  # Re-apply

# 5. Verify schema matches models
python scripts/migrate.py check

# 6. Update ERD documentation
python scripts/generate_erd.py
```

#### 2. Validate Migration Safety

```bash
# Check migration for dangerous operations
./scripts/validate-migration.sh

# Backup local database and test on copy
./scripts/test-migration-on-copy.sh
```

#### 3. Code Review Process

- **Review migration files** for correctness
- **Check dependency order** (no circular dependencies)
- **Validate foreign key constraints**
- **Ensure proper indexes** for performance
- **Review downgrade functions** for data safety

### Phase 2: Staging Deployment

#### 1. Deploy to Staging Environment

```bash
# 1. Deploy code to staging
git push origin staging

# 2. Run migrations on staging database
ENVIRONMENT=staging python scripts/migrate.py upgrade

# 3. Validate staging environment
./scripts/validate-staging.sh
```

#### 2. Staging Validation

- **Test all API endpoints**
- **Verify data integrity**
- **Check application functionality**
- **Performance test with migration**

### Phase 3: Production Deployment

#### 1. Pre-Production Checklist

```bash
# Database backup
./scripts/backup-production-db.sh

# Migration dry run (check what will happen)
ENVIRONMENT=production python scripts/migrate.py show <target_version>

# Check for pending migrations
ENVIRONMENT=production python scripts/migrate.py current
```

#### 2. Production Deployment Steps

**Option A: Automated Deployment (Recommended)**

```bash
# Use deployment script with migration support
./scripts/deploy-production.sh
```

**Option B: Manual Deployment**

```bash
# 1. Enable maintenance mode (optional)
./scripts/maintenance-mode.sh enable

# 2. Deploy application code (without restart)
./scripts/deploy-do.sh update

# 3. Run database migrations
ENVIRONMENT=production python scripts/migrate.py upgrade

# 4. Restart application
doctl apps restart $APP_ID

# 5. Disable maintenance mode
./scripts/maintenance-mode.sh disable

# 6. Validate deployment
./scripts/validate-production.sh
```

### Phase 4: Post-Deployment

#### 1. Validation Steps

```bash
# 1. Check application health
curl https://api.truledgr.app/health

# 2. Verify database state
ENVIRONMENT=production python scripts/migrate.py current

# 3. Check for schema drift
ENVIRONMENT=production python scripts/migrate.py check

# 4. Monitor application logs
doctl apps logs $APP_ID --follow
```

#### 2. Monitoring

- **Monitor application performance**
- **Check error rates in Sentry**
- **Validate database performance**
- **Monitor user experience**

## 🛠️ Migration Tools and Scripts

### Core Migration Commands

```bash
# Check current migration state
python scripts/migrate.py current

# Apply all pending migrations
python scripts/migrate.py upgrade

# Apply to specific migration
python scripts/migrate.py upgrade 005_auth_tables

# Rollback to previous migration
python scripts/migrate.py downgrade 004_groups_tables

# Show migration history
python scripts/migrate.py history

# Create new migration
python scripts/migrate.py create "description of changes"

# Check for schema drift
python scripts/migrate.py check
```

### Environment-Specific Configuration

**Development:**
```bash
export DATABASE_URL="sqlite:///./dev.db"
python scripts/migrate.py upgrade
```

**Staging:**
```bash
export DATABASE_URL="postgresql://user:pass@staging-host:5432/truledgr_staging"
python scripts/migrate.py upgrade
```

**Production:**
```bash
export DATABASE_URL="postgresql://user:pass@prod-host:5432/truledgr_production"
python scripts/migrate.py upgrade
```

## 🚨 Emergency Procedures

### Migration Rollback

If a migration causes issues in production:

```bash
# 1. Identify current migration
ENVIRONMENT=production python scripts/migrate.py current

# 2. Rollback to previous stable version
ENVIRONMENT=production python scripts/migrate.py downgrade <previous_version>

# 3. Restart application
doctl apps restart $APP_ID

# 4. Validate rollback
curl https://api.truledgr.app/health
```

### Data Recovery

If data loss occurs:

```bash
# 1. Stop application
doctl apps scale $APP_ID --instance-count 0

# 2. Restore from backup
./scripts/restore-production-db.sh <backup_timestamp>

# 3. Re-run migrations if needed
ENVIRONMENT=production python scripts/migrate.py upgrade <target_version>

# 4. Restart application
doctl apps scale $APP_ID --instance-count 1
```

## 📋 Pre-Migration Checklist

### Before Every Production Migration:

- [ ] Migration tested on local development database
- [ ] Migration tested on staging environment
- [ ] Database backup completed
- [ ] Migration rollback plan prepared
- [ ] Team notified of maintenance window
- [ ] Monitoring alerts configured
- [ ] Emergency contacts available

### Migration Safety Checks:

- [ ] No data-destructive operations without proper backup
- [ ] Foreign key constraints properly ordered
- [ ] Indexes added for performance-critical queries
- [ ] Migration can be rolled back safely
- [ ] Migration tested with production-sized data

## 🔧 Best Practices

### Migration Development

1. **Keep migrations small and focused**
2. **Test both upgrade and downgrade paths**
3. **Avoid data transformation in schema migrations**
4. **Use separate data migrations for complex transformations**
5. **Always backup before production migrations**

### Performance Considerations

1. **Add indexes concurrently for large tables**
2. **Avoid blocking operations during peak hours**
3. **Test migration time on production-sized data**
4. **Consider maintenance windows for large migrations**

### Security

1. **Never commit database passwords**
2. **Use environment-specific connection strings**
3. **Audit migration access and execution**
4. **Validate migration signatures in production**

## 📚 Related Documentation

- [Migration Structure Guide](./migration-structure.md)
- [Database Overview](./database-overview.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Emergency Procedures](./emergency-procedures.md)

---

**Remember: Migrations are irreversible operations in production. Always backup, test, and have a rollback plan ready.**
