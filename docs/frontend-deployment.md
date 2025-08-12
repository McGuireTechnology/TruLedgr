# Frontend Deployment Guide

## Overview
The frontend is configured as a **Static Site** in Digital Ocean App Platform, which is the recommended approach for Vue.js/React SPAs.

## Deployment Options

### Option 1: Full Stack Deployment (Recommended)
Use the main `app-platform.yaml` configuration which includes both backend API and frontend:

```bash
# Deploy using the main configuration
# In Digital Ocean Console: Apps → Create App → Import from GitHub
# Select: McGuireTechnology/truledgr
# Use app spec: app-platform.yaml
```

### Option 2: Simple Deployment
Use the `app-simple.yaml` for a minimal setup:

```bash
# Deploy using the simple configuration
# In Digital Ocean Console: Apps → Create App → Import from GitHub  
# Select: McGuireTechnology/truledgr
# Use app spec: app-simple.yaml
```

## Frontend Configuration Details

### Build Process
- **Build Command**: `npm ci && npm run build`
- **Output Directory**: `/dist`
- **Environment**: Node.js (automatically detected from package.json)

### Environment Variables
The frontend uses these environment variables (automatically configured):

```env
VITE_API_URL=https://api.truledgr.app
VITE_APP_TITLE=TruLedgr Dashboard
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_PUSH_NOTIFICATIONS=true
```

### Domain Configuration
- **Frontend URL**: `https://dash.truledgr.app`
- **API URL**: `https://api.truledgr.app`

## Deployment Steps

### 1. Via Digital Ocean Console
1. Go to [Digital Ocean Apps](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Choose "GitHub" as source
4. Select `McGuireTechnology/truledgr` repository
5. Choose `main` branch
6. Import app spec: Use `app-platform.yaml` or `app-simple.yaml`
7. Review and deploy

### 2. Via doctl CLI
```bash
# Install doctl (if not already installed)
brew install doctl

# Authenticate with Digital Ocean
doctl auth init

# Create the app using the spec file
doctl apps create --spec app-platform.yaml

# Or use the simple version
doctl apps create --spec app-simple.yaml
```

### 3. Manual Configuration (Alternative)
If you prefer to configure manually in the DO console:

**Static Site Configuration:**
- **Name**: frontend
- **Source**: GitHub (McGuireTechnology/truledgr)
- **Source Directory**: /frontend
- **Build Command**: `npm ci && npm run build`
- **Output Directory**: /dist
- **Environment Variables**: Add the VITE_* variables listed above

## Key Features

### SPA Routing Support
- **Index Document**: `index.html`
- **Error Document**: `index.html` (for client-side routing)

### Production Optimizations
- Vite production build with optimizations
- Static file caching via CDN
- Gzip compression enabled
- Tree-shaking and code splitting

### API Integration
- Configured to connect to backend at `https://api.truledgr.app`
- CORS properly configured between frontend and backend
- JWT authentication ready

## Troubleshooting

### Build Failures
If the frontend build fails:
1. Check Node.js version compatibility (requires Node 20+)
2. Verify all dependencies are in package.json
3. Check build logs for TypeScript errors

### API Connection Issues
If frontend can't connect to API:
1. Verify VITE_API_URL is set correctly
2. Check CORS configuration in backend
3. Ensure both services are deployed

### Domain Issues
If custom domains don't work:
1. Add domain in DO console: Apps → Settings → Domains
2. Configure DNS records to point to DO nameservers
3. Wait for SSL certificate provisioning

## Monitoring
- **Frontend**: Monitor via Digital Ocean App Platform dashboard
- **Performance**: Use browser dev tools and Lighthouse
- **Uptime**: Configure monitoring alerts in DO console

## Next Steps
1. Deploy using one of the configurations above
2. Configure custom domains in DO console
3. Set up monitoring and alerts
4. Test the full application flow
