# Domain Routing Fix Guide

## Problem
When deploying both API and frontend in the same app, Digital Ocean may route both domains to the first service (API), causing `dash.truledgr.app` to show the API instead of the frontend.

## Solution Options

### Option 1: Separate Apps (Recommended)
Deploy API and frontend as separate Digital Ocean apps for cleaner domain management.

#### Deploy API:
1. Go to [DO Apps Console](https://cloud.digitalocean.com/apps)
2. Create App → GitHub → `McGuireTechnology/truledgr`
3. Use spec file: `api-only.yaml`
4. After deployment, add custom domain: `api.truledgr.app`

#### Deploy Frontend:
1. Create another App → GitHub → `McGuireTechnology/truledgr` 
2. Use spec file: `frontend-only.yaml`
3. After deployment, add custom domain: `dash.truledgr.app`

### Option 2: Manual Domain Configuration
If using the combined `app-simple.yaml`:

1. Deploy the app first
2. Go to Apps → Your App → Settings → Domains
3. **IMPORTANT**: Configure domains manually:
   - Remove default domain
   - Add `api.truledgr.app` → Route to `api` service
   - Add `dash.truledgr.app` → Route to `frontend` static site

### Option 3: Single App with Path Routing
Keep everything under one domain but use path-based routing:
- `https://truledgr.app/api/*` → API
- `https://truledgr.app/*` → Frontend

## DNS Configuration
For either option, update your DNS:

```
api.truledgr.app     → CNAME → [your-api-app].ondigitalocean.app
dash.truledgr.app    → CNAME → [your-frontend-app].ondigitalocean.app
```

## Recommended: Option 1 (Separate Apps)
This provides:
- ✅ Clean separation of concerns
- ✅ Independent scaling and configuration  
- ✅ Easier domain management
- ✅ Better debugging and monitoring
- ✅ No routing conflicts
