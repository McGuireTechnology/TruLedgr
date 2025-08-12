# TruLedgr Deployment Guide

## 🏗️ Project Structure
```
truledgr/
├── api/
│   ├── .do/
│   │   └── app.yaml      # ← Digital Ocean deployment config
│   ├── main.py           # FastAPI application  
│   ├── requirements.txt  # Python dependencies
│   └── .venv/           # Python virtual environment
└── dash/
    ├── .do/
    │   └── app.yaml      # ← Digital Ocean deployment config
    ├── src/              # Vue.js source code
    ├── package.json      # Node.js dependencies
    └── node_modules/     # Node.js packages
```

## 🚀 Deployment Steps

### 1. Deploy API Backend

**Create New App:**
1. Go to [Digital Ocean Apps Console](https://cloud.digitalocean.com/apps)
2. Click "Create App" 
3. Choose "GitHub" as source
4. Select repository: `McGuireTechnology/TruLedgr`
5. **Important**: Set source directory to `/api`
6. Digital Ocean will automatically detect and use `api/.do/app.yaml`
7. Review settings and deploy

**Configure Domain:**
- After deployment, go to App Settings → Domains
- Add custom domain: `api.truledgr.app`
- Update DNS: `api.truledgr.app CNAME [app-name].ondigitalocean.app`

### 2. Deploy Dashboard Frontend

**Create Another App:**
1. Go back to [Digital Ocean Apps Console](https://cloud.digitalocean.com/apps)
2. Click "Create App" again
3. Choose "GitHub" as source  
4. Select repository: `McGuireTechnology/TruLedgr`
5. **Important**: Set source directory to `/dash`
6. Digital Ocean will automatically detect and use `dash/.do/app.yaml`
7. Review settings and deploy

**Configure Domain:**
- After deployment, go to App Settings → Domains
- Add custom domain: `dash.truledgr.app`  
- Update DNS: `dash.truledgr.app CNAME [app-name].ondigitalocean.app`

## 🌐 Final Architecture

```
┌─────────────────────┐    ┌─────────────────────┐
│  dash.truledgr.app  │    │  api.truledgr.app   │
│                     │    │                     │
│   Vue.js Frontend   │◄──►│   FastAPI Backend   │
│   Static Site       │    │   Python Service    │
│   (DO App #1)       │    │   (DO App #2)       │
└─────────────────────┘    └─────────────────────┘
```

## ✅ Benefits of This Structure

- **Standard Compliance**: Uses Digital Ocean's `.do/app.yaml` convention
- **Clean Separation**: Each service deployed independently  
- **No Routing Conflicts**: Separate apps = separate domains
- **Independent Scaling**: Scale frontend and backend separately
- **Easier Debugging**: Isolated logs and monitoring
- **Better Resource Management**: Right-size each component

## 🔧 Configuration Details

### API Configuration (`api/.do/app.yaml`)
- **Runtime**: Python with automatic dependency installation
- **Command**: `python -m uvicorn main:app --host 0.0.0.0 --port 8080`
- **Health Check**: `/health` endpoint
- **Port**: 8080 (standard for DO services)

### Dashboard Configuration (`dash/.do/app.yaml`)  
- **Type**: Static Site (optimized for Vue.js SPAs)
- **Build**: `npm ci && npm run build`
- **Output**: `/dist` directory
- **SPA Support**: Routes all requests to `index.html`
- **API Connection**: `VITE_API_URL=https://api.truledgr.app`

## 🧪 Testing Deployment

1. **API Health Check**: Visit `https://api.truledgr.app/health`
2. **Frontend Load**: Visit `https://dash.truledgr.app`  
3. **Integration**: Verify dashboard can connect to API
4. **Mobile Config**: Test `https://api.truledgr.app/api/v1/mobile/config`

## 📚 Additional Resources

- **Mobile Integration**: See `docs/mobile-integration.md`
- **Domain Configuration**: See `docs/domain-routing-fix.md`
- **Project Structure**: See `docs/project-structure.md`

This deployment structure provides a robust, scalable foundation for the TruLedgr platform!
