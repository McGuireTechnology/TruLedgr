# TruLedgr Marketing Website Deployment

This directory contains the Vue.js marketing website for TruLedgr.

## Deployment Platform

### Cloudflare Pages
Configuration file: `wrangler.toml`

**Dashboard Settings:**
- Framework preset: Vue
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `www`

**Environment Variables:** None required

## Local Development

```bash
# From the www directory
npm install
npm run dev
```

## Production Build

```bash
# From the www directory
npm run build
```

The built files will be in the `dist/` directory.

## Directory Structure

```
www/
├── src/                    # Vue.js source code
├── public/                 # Static assets
├── dist/                   # Build output (generated)
├── functions/              # Cloudflare Pages Functions
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── wrangler.toml          # Cloudflare Pages config
├── cloudflare-pages.md    # Deployment documentation
└── DEPLOYMENT.md          # This file
```
