Cloudflare Pages deployment instructions for the TruLedgr landing site.

Recommended Cloudflare Pages settings
- Framework: None / Static site (build with npm)
- Build command: npm ci && npm run build
- Build output directory: dist
- Branch: staging (or whichever branch you want to deploy)

Environment variables
- If you need a runtime API url, set VITE_API_URL in Pages environment variables. Example:
  - VITE_API_URL=https://api.truledgr.app

Optional: Add a custom domain in the Pages UI and point DNS accordingly.

Notes
- This project uses Vite. The default output directory is `dist`.
- We pinned `vite` to ^5.4.20 to avoid plugin peer-dependency issues.
