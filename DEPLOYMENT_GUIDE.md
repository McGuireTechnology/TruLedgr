# TruLedgr Digital Ocean Deployment Guide

## Overview

This guide covers deploying the TruLedgr API to Digital Ocean App Platform### Step 3: Database Configuration

**Using Existing PostgreSQL Database:**

1. **Prepare your database connection:**
   - Ensure your PostgreSQL database is accessible from Digital Ocean App Platform
   - Format: `postgresql://user:password@host:port/database`
   - Example: `postgresql://myuser:mypass@myhost.com:5432/truledgr`

2. **Set DATABASE_URL in deployment:**

   ```bash
   export DATABASE_URL="your-postgresql-connection-string"
   ./scripts/deploy-do.sh deploy
   ```

   Or set it manually in the Digital Ocean App Platform dashboard after deployment.aged PostgreSQL database. The deployment includes:

- **API Service**: FastAPI application with automatic scaling
- **Database**: Managed PostgreSQL database
- **Domain**: Custom domain configuration (api.truledgr.app)
- **SSL**: Automatic SSL certificate management
- **Monitoring**: Built-in health checks and metrics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Cloudflare    │    │  Digital Ocean  │
│   Pages         │    │  App Platform   │
│                 │    │                 │
│ • Landing Page  │    │ • API Service   │
│   (truledgr.com)│    │   (api.truledgr.app)
│                 │    │ • External DB   │
│ • Dashboard     │    │ • Redis Cache   │
│   (dash.truledgr.app)│    │ • Monitoring   │
└─────────────────┘    └─────────────────┘
```

## Prerequisites

### 1. Digital Ocean Account

- Create a Digital Ocean account
- Generate an API token
- Install `doctl` CLI tool

### 2. Domain Setup

- Own the `truledgr.com` and `truledgr.app` domains
- Configure DNS records to point to Digital Ocean and Cloudflare

### 3. Environment Variables

Prepare the following environment variables:

```bash
# Required
SECRET_KEY="your-32-character-secret-key"

# Optional but recommended
SENTRY_DSN="your-sentry-dsn"
SMTP_HOST="your-smtp-host"
SMTP_USER="your-smtp-user"
SMTP_PASSWORD="your-smtp-password"
```

## Deployment Steps

### Step 1: Authenticate with Digital Ocean

```bash
# Install doctl (if not already installed)
# macOS
brew install doctl

# Linux
# Download from: https://github.com/digitalocean/doctl/releases

# Authenticate
doctl auth init
```

### Step 2: Deploy the Application

**For App Platform Wizard:**

1. Connect your GitHub repository to Digital Ocean App Platform
2. The wizard should automatically detect the `.do/app.yaml` configuration
3. **Important**: If it detects Node.js, do not change settings - the configuration is correct
4. The deployment will use Docker and Python as specified in the app.yaml

**For Manual Deployment:**

```bash
# Navigate to project root
cd /path/to/truledgr

# Set environment variables (optional)
export SENTRY_DSN="your-sentry-dsn"
export SMTP_HOST="smtp.gmail.com"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

# Deploy
./scripts/deploy-do.sh deploy
```

### Step 3: Configure Custom Domain

1. **Add Domain to Digital Ocean:**

   ```bash
   # Get app ID
   APP_ID=$(doctl apps list | grep truledgr-api | awk '{print $1}')

   # Add domain
   doctl apps update $APP_ID --domain api.truledgr.app
   ```

2. **Update DNS Records:**
   Add these records to your DNS provider:

   ```text
   Type: CNAME
   Name: api
   Value: your-app-name.ondigitalocean.app
   TTL: 3600
   ```

   For the `truledgr.app` domain, also add:

   ```text
   Type: CNAME
   Name: dash
   Value: your-dashboard-app.pages.dev
   TTL: 3600
   ```

3. **Verify SSL Certificate:**
   Digital Ocean will automatically provision SSL certificates.

### Step 4: Database Configuration

The database is automatically created with the app deployment. To access it:

```bash
# List databases
doctl databases list

# Get connection details
doctl databases get <database-id> --format Name,URI
```

### Step 5: Environment Variables Setup

Set production environment variables in the Digital Ocean dashboard:

1. Go to your app in Digital Ocean dashboard
2. Navigate to Settings → Environment Variables
3. Add the following variables:

**Required:**

- `SECRET_KEY`: 32+ character random string
- `DATABASE_URL`: Connection string for your existing PostgreSQL database (format: `postgresql://user:password@host:port/database`)

**Recommended:**

- `SENTRY_DSN`: For error tracking
- `SMTP_HOST`: For email functionality
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `REDIS_URL`: For caching (if using Redis)

## Configuration Files

### App Specification (.do/app.yaml)

The main configuration file defines the Digital Ocean App Platform deployment:

```yaml
name: truledgr-api
region: nyc1

services:
  - name: api
    source_dir: /
    build:
      method: docker
      dockerfile_path: Dockerfile
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 8000
    health_check:
      http_path: /health
    routes:
      - path: /
```

### App Platform Wizard Setup

**Important**: The repository is configured to deploy as a **Python/FastAPI** application, not Node.js. The app platform wizard should automatically detect this from the `.do/app.yaml` configuration file.

If the wizard incorrectly detects Node.js:

1. **Do not change settings** - the configuration is correct
2. The `.do/app.yaml` file explicitly specifies Python/Docker deployment
3. The root `package.json` is only used for documentation and is excluded from deployment

### Deployment Files

- **`.do/app.yaml`**: Digital Ocean App Platform specification
- **`.do/.doignore`**: Files to exclude from deployment
- **`Dockerfile`**: Container build configuration
- **`pyproject.toml`**: Python project configuration

## Monitoring & Health Checks

### Built-in Health Checks

- **HTTP Health Check**: `/health` endpoint
- **Database Connectivity**: Automatic DB connection tests
- **Readiness Probe**: `/ready` endpoint for Kubernetes compatibility

### Monitoring Setup

1. **Enable Metrics**: Set `METRICS_ENABLED=true`
2. **Configure Tracing**: Set `TRACING_ENABLED=true`
3. **Error Tracking**: Configure `SENTRY_DSN`

### Alerts Configuration

The app includes pre-configured alerts for:

- CPU utilization > 80%
- Memory utilization > 80%
- Restart count > 5

## Scaling

### Automatic Scaling

- **Min Instances**: 2
- **Max Instances**: Based on load
- **CPU Threshold**: 80%
- **Memory Threshold**: 80%

### Manual Scaling

```bash
# Scale up
doctl apps update $APP_ID --instance-count 4

# Scale down
doctl apps update $APP_ID --instance-count 2
```

## Backup & Recovery

### Database Backups

**External Database Backups:**

- Configure backups according to your database provider's recommendations
- Ensure your backup strategy covers the TruLedgr database
- Test backup restoration procedures regularly

### Application Backups

- Code is version controlled
- Configuration as code
- Easy redeployment

## Security

### Network Security

- Automatic SSL/TLS encryption
- HTTPS-only traffic
- CORS configuration
- Rate limiting

### Application Security

- JWT token authentication
- CSRF protection
- Input validation
- SQL injection prevention

### Access Control

- Environment variable secrets
- Private database access
- Restricted API endpoints

## Troubleshooting

### Common Issues

1. **App Platform detects buildpack instead of Docker**

   **Solution**: The `.do/app.yaml` now includes explicit Docker build configuration:
   
   ```yaml
   build:
     method: docker
     dockerfile_path: Dockerfile
   ```
   
   This forces Digital Ocean to use Docker instead of buildpack detection.

   **Why this happens**:
   - DO App Platform may default to buildpack when it detects multiple build files
   - The explicit `method: docker` overrides automatic detection
   - `.do/.doignore` excludes conflicting build files

2. **Deployment Failures**

   ```bash
   # Check logs
   ./scripts/deploy-do.sh logs

   # Check app status
   ./scripts/deploy-do.sh status
   ```

3. **Database Connection Issues**

   - Verify DATABASE_URL environment variable
   - Check database firewall rules
   - Ensure database is running

4. **Domain Issues**

   - Verify DNS propagation (may take 24-48 hours)
   - Check domain configuration in DO dashboard
   - Ensure SSL certificate is provisioned

### Logs & Debugging

```bash
# View application logs
doctl apps logs $APP_ID

# View specific component logs
doctl apps logs $APP_ID --component api

# Follow logs in real-time
doctl apps logs $APP_ID --follow
```

## Cost Estimation

### Monthly Costs (Approximate)

- **App Platform**: $12 (Basic XXS instance)
- **External PostgreSQL Database**: $0 (using your existing database)
- **Domain**: $0 (using existing domain)
- **SSL**: $0 (included)
- **Bandwidth**: $0 (first 1TB free)

**Total Estimated Monthly Cost**: ~$12

## Next Steps

After successful deployment:

1. **Update Frontend Applications**

   - Update API base URLs in frontend configs
   - Test API integration
   - Update CORS settings if needed

2. **Set Up Monitoring**

   - Configure alerts
   - Set up log aggregation
   - Enable performance monitoring

3. **Configure CI/CD**

   - Set up automatic deployments
   - Configure staging environment
   - Set up deployment approvals

4. **Security Hardening**

   - Review and update security headers
   - Configure rate limiting rules
   - Set up intrusion detection

5. **Performance Optimization**

   - Configure caching strategies
   - Optimize database queries
   - Set up CDN integration

## Support

For deployment issues:

1. Check Digital Ocean documentation
2. Review application logs
3. Verify configuration files
4. Contact DevOps team

## Rollback Procedure

If deployment fails:

```bash
# Rollback to previous deployment
doctl apps get $APP_ID --format ID,Name,Phase
doctl apps update $APP_ID --rollback

# Or redeploy with previous configuration
git checkout previous-commit
./scripts/deploy-do.sh update
```

---

**Deployment Checklist:**

- [ ] Digital Ocean account configured
- [ ] Domain DNS records updated
- [ ] Environment variables set
- [ ] SSL certificate provisioned
- [ ] Database connection verified
- [ ] Health checks passing
- [ ] Frontend applications updated
- [ ] Monitoring configured
- [ ] Backup strategy implemented
