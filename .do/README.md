# DigitalOcean App Platform Configuration

This directory contains the app specification for deploying TruLedgr API on DigitalOcean App Platform.

## 📋 App Specification

**File:** `app.yaml`

Defines the infrastructure and deployment configuration for the truledgr-api application.

## 🚀 Components

### PRE_DEPLOY Job: `db-migrate`

Runs database migrations **before** application instances start.

**Configuration:**
- **Type:** PRE_DEPLOY job
- **Instance:** apps-s-1vcpu-0.5gb (1 vCPU, 512MB RAM)
- **Command:** `./migrate.sh upgrade head`
- **Source:** GitHub (McGuireTechnology/TruLedgr, staging branch)

**Process:**
1. Poetry installs dependencies
2. Runs Alembic migrations via migrate.sh
3. Only starts app instances after successful completion

**Benefits:**
- ✅ Zero race conditions (only one job runs)
- ✅ Migrations complete before traffic hits app
- ✅ Clean separation of concerns
- ✅ Easy rollback if migrations fail

### Service: `truledgr`

Main FastAPI application service.

**Configuration:**
- **Instance:** apps-s-1vcpu-0.5gb (1 vCPU, 512MB RAM)
- **Count:** 1 instance (can scale up)
- **Port:** 8080 (HTTP)
- **Domain:** api.truledgr.app
- **Region:** NYC (nyc)

**Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `VITE_API_URL` - API base URL for CORS

## 🔧 Managing the App

### View Current Configuration

```bash
# Get app ID
doctl apps list

# View full spec
doctl apps spec get 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da

# View specific app details
doctl apps get 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da
```

### Update Configuration

```bash
# Update from local file
doctl apps update 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --spec .do/app.yaml

# Update and trigger deployment
doctl apps create-deployment 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da
```

### Monitor Deployments

```bash
# List deployments
doctl apps list-deployments 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da

# View logs (migration job)
doctl apps logs 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --type job --follow

# View logs (app service)
doctl apps logs 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --type deploy --follow
doctl apps logs 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --type run --follow
```

## 📊 Deployment Flow

```
1. Code pushed to staging branch
   ↓
2. DigitalOcean detects change
   ↓
3. Builds container image
   ↓
4. Runs PRE_DEPLOY job (db-migrate)
   - Installs Poetry dependencies
   - Runs ./migrate.sh upgrade head
   - Waits for completion
   ↓
5. If migration succeeds:
   - Starts app instances (truledgr service)
   - Routes traffic to new instances
   - Deployment complete ✅
   
6. If migration fails:
   - Deployment stops
   - App instances NOT started
   - Previous version keeps running
   - Manual intervention required ⚠️
```

## 🔒 Environment Variables

Set via DigitalOcean Console or CLI:

```bash
# Set environment variable
doctl apps update 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da \
  --env DATABASE_URL="postgresql://..."

# View environment variables
doctl apps spec get 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da | grep -A 5 "envs:"
```

**Required Variables:**
- `DATABASE_URL` - Managed PostgreSQL database connection string
- `SECRET_KEY` - Random secure key for JWT tokens
- `VITE_API_URL` - Public API URL (https://api.truledgr.app)

## 🎛️ Scaling

### Vertical Scaling (Change Instance Size)

Edit `instance_size_slug` in app.yaml:
- `apps-s-1vcpu-0.5gb` - $5/month (current)
- `apps-s-1vcpu-1gb` - $10/month
- `apps-s-2vcpu-2gb` - $20/month

### Horizontal Scaling (Add Instances)

Edit `instance_count` in app.yaml:
```yaml
services:
- name: truledgr
  instance_count: 3  # Scale to 3 instances
```

**Note:** With PRE_DEPLOY job, scaling is safe:
- Migrations run once before ANY instances start
- All instances get the same schema version
- No coordination needed between instances

## 🔄 Rollback

### Rollback Code

```bash
# List deployments
doctl apps list-deployments 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da

# Rollback to previous deployment
doctl apps create-deployment 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da \
  --deployment-id <previous-deployment-id>
```

### Rollback Database

```bash
# SSH into a one-off container
doctl apps create-deployment 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --wait

# Run migration rollback
./migrate.sh downgrade -1

# Or rollback to specific version
./migrate.sh downgrade <revision_id>
```

## 📚 Related Documentation

- [Multi-Host Migration Strategy](../api/migrations/MULTI_HOST_STRATEGY.md)
- [Migration Quick Reference](../api/migrations/QUICK_REFERENCE.md)
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [DigitalOcean Jobs](https://docs.digitalocean.com/products/app-platform/how-to/manage-jobs/)

## 🆘 Troubleshooting

### Migration Job Fails

```bash
# Check migration job logs
doctl apps logs 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --type job

# Common issues:
# - DATABASE_URL not set or invalid
# - Migration script syntax error
# - Database lock or timeout
# - Insufficient permissions
```

### App Won't Start

```bash
# Check build logs
doctl apps logs 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --type build

# Check deployment logs
doctl apps logs 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --type deploy

# Verify environment variables are set
doctl apps spec get 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da | grep -A 10 "envs:"
```

### Performance Issues

```bash
# View app metrics
doctl apps tier instance-size list

# Scale up
# Edit app.yaml and update instance_size_slug or instance_count
doctl apps update 43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da --spec .do/app.yaml
```

## 💡 Tips

1. **Always test in staging first** - This app is already on staging branch
2. **Monitor migration duration** - Set alerts for slow migrations
3. **Keep migrations backward compatible** - For zero-downtime deployments
4. **Use database backups** - DO managed DB has automatic backups
5. **Watch the logs** - Monitor PRE_DEPLOY job completion

---

**App ID:** `43f5f9a6-52e1-41d0-8ac1-bb3fa96f35da`  
**App Name:** truledgr-api  
**Region:** NYC  
**Domain:** https://api.truledgr.app
