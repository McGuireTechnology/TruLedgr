# TruLedgr Landing Page - Deployment Guide

## Overview

This guide covers deploying the TruLedgr landing page to Cloudflare Pages using Wrangler CLI or GitHub Actions.

## Prerequisites

1. **Cloudflare Account**: Sign up at [cloudflare.com](https://cloudflare.com)
2. **Domain**: `truledgr.com` configured in Cloudflare
3. **Wrangler CLI**: Install globally with `npm install -g wrangler`
4. **Authentication**: Login with `wrangler login`

## Local Development

```bash
# Navigate to landing directory
cd landing

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

## Manual Deployment

### Production Deployment

```bash
# Build the project
npm run build

# Deploy to production
npm run deploy

# Or use wrangler directly
wrangler pages deploy dist --project-name=truledgr-www
```

### Staging Deployment

```bash
# Deploy to staging
npm run deploy:staging

# Or use wrangler directly  
wrangler pages deploy dist --project-name=truledgr-www-staging
```

## Automatic Deployment (GitHub Actions)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy-landing.yml`) that automatically deploys:

- **Production**: Pushes to `main` branch
- **Preview**: Pull requests

### Required Secrets

Add these secrets in your GitHub repository settings:

```
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_ACCOUNT_ID=your_account_id
```

## Cloudflare Pages Configuration

**Dashboard Settings:**
- Framework preset: Vue
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `landing`
- Node.js version: `20`

## Environment Variables

Set these in Cloudflare Pages dashboard:

### Production
```
VITE_API_BASE_URL=https://api.truledgr.app
VITE_ENV=production
VITE_FEATURE_FLAGS=users,groups,items,oauth,payments
VITE_ANALYTICS_ENABLED=true
VITE_ENABLE_DEVTOOLS=false
```

### Staging
```
VITE_API_BASE_URL=https://api-staging.truledgr.app
VITE_ENV=staging
VITE_FEATURE_FLAGS=users,groups,items,oauth,payments
VITE_ANALYTICS_ENABLED=true
VITE_ENABLE_DEVTOOLS=true
```

## Domain Configuration

### DNS Records

Configure these DNS records in Cloudflare:

```
Type: CNAME
Name: www
Content: truledgr-www.pages.dev
Proxy: Yes

Type: A/AAAA  
Name: @ (root)
Content: [Cloudflare Pages IPs]
Proxy: Yes
```

### Custom Domains in Pages

1. Go to Cloudflare Pages → truledgr-www → Custom domains
2. Add domains:
   - `truledgr.com`
   - `www.truledgr.com`

## Security & Performance

### Headers (`_headers` file)
- **CSP**: Content Security Policy
- **HSTS**: HTTP Strict Transport Security  
- **Cache Control**: Optimized for assets

### Redirects (`_redirects` file)
- **WWW → Apex**: `www.truledgr.com` → `truledgr.com`
- **API Proxy**: `/api/*` → `https://api.truledgr.app/*`
- **Dashboard**: `/dashboard/*` → `https://dash.truledgr.app/*`
- **SPA Routing**: Fallback to `index.html`

## Directory Structure

```
landing/
├── src/                    # Vue.js source code
├── public/                 # Static assets
│   ├── _headers           # Cloudflare headers
│   └── _redirects         # Cloudflare redirects
├── dist/                   # Build output (generated)
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── wrangler.toml          # Cloudflare configuration
└── DEPLOYMENT.md          # This file
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version (use 20+)
   - Verify all dependencies installed
   - Check build logs in Pages dashboard

2. **Domain Issues**
   - Verify DNS propagation
   - Check SSL certificate status
   - Ensure domains added to Pages project

3. **Redirects Not Working**
   - Verify `_redirects` file in `dist` folder after build
   - Check redirect syntax
   - Use Cloudflare's redirect rules as fallback
