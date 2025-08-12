# Digital Ocean App Platform Deployment Guide

## 🚀 Quick Deployment Steps

### Option 1: Single App Deployment (Recommended)

1. **Create New App in Digital Ocean**
   - Go to Digital Ocean App Platform console
   - Click "Create App"
   - Choose "GitHub" as source

2. **Configure Repository**
   - Select `McGuireTechnology/TruLedgr`
   - Branch: `main`
   - **Import app spec**: Upload the `app-platform.yaml` file from the root

3. **Configure Domains**
   - In the Digital Ocean console, add your domains:
     - `api.truledgr.app` → API service
     - `dash.truledgr.app` → Frontend static site

4. **Set Environment Variables**
   ```
   APP_SECRET_KEY=your-super-secure-secret-key-here
   JWT_SECRET=your-jwt-secret-key-here
   ```

5. **Deploy**
   - Click "Create Resources"
   - Digital Ocean will automatically:
     - Create PostgreSQL database
     - Build and deploy backend API
     - Build and deploy frontend static site
     - Configure SSL certificates for HTTPS (443)
     - Route traffic on standard ports (80/443)

### Option 2: Separate Apps (Advanced)

If you prefer separate apps for backend and frontend:

#### Backend API App
- Use configuration from `.do/app.yaml`
- Will be accessible on standard ports 80/443
- Health check endpoint: `/health`

#### Frontend Static Site
- Use configuration from `frontend/.do/app.yaml` 
- Static site deployment (faster, more cost-effective)
- Automatic SPA routing configuration

## 🌐 Port Configuration

The application is configured to be accessible on **standard web ports**:
- **HTTP**: Port 80 (automatically redirects to HTTPS)
- **HTTPS**: Port 443 (SSL certificates auto-managed by Digital Ocean)

**Internal Application Ports:**
- Backend runs on `$PORT` (dynamically assigned by DO)
- Frontend builds to static assets (no server required)

## 🔧 Network Configuration

When configuring in the Digital Ocean console UI:
- **Public HTTP Port**: Leave blank (uses 80/443 automatically)
- **Internal Ports**: Not needed for static sites
- **HTTP Request Routes**: 
  - Backend: `/api`, `/docs`, `/health`
  - Frontend: `/` (catch-all for SPA routing)

## 🔑 Required Environment Variables

**Backend (API Service):**
```bash
ENVIRONMENT=production
SECRET_KEY=${APP_SECRET_KEY}  # Set this in DO console as secret
JWT_SECRET_KEY=${JWT_SECRET}  # Set this in DO console as secret
DATABASE_URL=${truledgr-db.DATABASE_URL}  # Auto-configured by DO
ALLOWED_ORIGINS=https://dash.truledgr.app,https://truledgr.app
```

**Frontend (Static Site):**
```bash
VITE_API_URL=https://api.truledgr.app
VITE_APP_TITLE=TruLedgr Dashboard
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_PUSH_NOTIFICATIONS=true
```

## 🏥 Health Checks

- **Endpoint**: `/health`
- **Expected Response**: `{"status": "healthy", "message": "All systems operational", "version": "1.0.0"}`
- **Status Code**: 200

## 📊 Monitoring & Scaling

- **Instance Size**: `basic-xxs` (can be upgraded)
- **Instance Count**: 1 (can be scaled horizontally)
- **Database**: PostgreSQL 14, basic tier
- **Auto-scaling**: Available for higher tiers

## 🔒 Security Features

- **Automatic SSL**: Digital Ocean manages SSL certificates
- **HTTPS Redirect**: HTTP traffic automatically redirects to HTTPS  
- **CORS Configuration**: Properly configured for cross-domain requests
- **Environment Secrets**: Sensitive data stored as encrypted environment variables

## 💰 Cost Optimization

- **Frontend**: Static site deployment (most cost-effective)
- **Backend**: Smallest instance size that meets requirements
- **Database**: Basic tier suitable for development/small production

## 🐛 Troubleshooting

**Common Issues:**
1. **502 Bad Gateway**: Check if backend health endpoint returns 200
2. **CORS Errors**: Verify domain configuration in ALLOWED_ORIGINS
3. **Build Failures**: Check build logs in Digital Ocean console
4. **Database Connection**: Ensure DATABASE_URL is correctly configured

**Debugging:**
- Check application logs in Digital Ocean console
- Test API endpoints: `https://api.truledgr.app/health`
- Test frontend: `https://dash.truledgr.app`

## 📝 Post-Deployment Checklist

- [ ] API health check responds at `https://api.truledgr.app/health`
- [ ] API documentation accessible at `https://api.truledgr.app/docs`
- [ ] Frontend loads at `https://dash.truledgr.app`
- [ ] Frontend can communicate with API
- [ ] SSL certificates are active (lock icon in browser)
- [ ] Mobile config endpoint works: `https://api.truledgr.app/api/v1/mobile/config`

Your TruLedgr application will be accessible on standard web ports (80/443) with automatic SSL management! 🎉
