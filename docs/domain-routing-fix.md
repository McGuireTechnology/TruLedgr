# Domain Routing Fix Guide

## Problem
When deploying both API and frontend in the same app, Digital Ocean may route both domains to the first service (API), causing `dash.truledgr.app` to show the API instead of the frontend.

## ✅ Solution: Separate Apps (Clean Structure)
Deploy API and frontend as separate Digital Ocean apps using the standard `.do/app.yaml` configuration.

### Deploy API
1. Go to [DO Apps Console](https://cloud.digitalocean.com/apps)
2. Create App → GitHub → `McGuireTechnology/truledgr`
3. **Source Directory**: Select `/api` folder
4. Digital Ocean will automatically use `api/.do/app.yaml`
5. After deployment, add custom domain: `api.truledgr.app`

### Deploy Frontend (Dashboard)
1. Create another App → GitHub → `McGuireTechnology/truledgr` 
2. **Source Directory**: Select `/dash` folder  
3. Digital Ocean will automatically use `dash/.do/app.yaml`
4. After deployment, add custom domain: `dash.truledgr.app`

## 🏗️ Project Structure
```
truledgr/
├── api/
│   ├── .do/
│   │   └── app.yaml     # ← API deployment config
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Dependencies
└── dash/
    ├── .do/
    │   └── app.yaml     # ← Frontend deployment config
    ├── src/             # Vue.js source
    └── package.json     # Dependencies
```

## 🌐 DNS Configuration
After deployment, update your DNS:

```dns
api.truledgr.app     → CNAME → [your-api-app].ondigitalocean.app
dash.truledgr.app    → CNAME → [your-dash-app].ondigitalocean.app
```

## 🎯 Benefits
- ✅ **Standard DO Structure**: Uses `.do/app.yaml` convention
- ✅ **Clean Separation**: Each service has its own deployment
- ✅ **Independent Scaling**: Scale API and frontend separately  
- ✅ **No Routing Conflicts**: Each app gets its own domain
- ✅ **Easier Debugging**: Isolated deployments and logs
- ✅ **Better Resource Management**: Right-size each service

## 🚀 Deployment Process
1. **API First**: Deploy from `/api` folder → `api.truledgr.app`
2. **Frontend Second**: Deploy from `/dash` folder → `dash.truledgr.app`  
3. **Configure DNS**: Point domains to respective apps
4. **Test Integration**: Verify frontend connects to API

This structure follows Digital Ocean's best practices and provides maximum flexibility!
