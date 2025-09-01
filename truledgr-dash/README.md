# TruLedgr Dashboard (Vue + Vite)

This is a minimal starter for the TruLedgr web dashboard using Vue 3 and Vite.

Quick start

```bash
cd truledgr-dash
npm install
npm run dev
```

The sample Dashboard will attempt to GET `/api/health` for a simple health check; adjust the endpoint to match your API host (or proxy in Vite).

Notes

- This is intentionally small and dependency-light. Add your state management, routing, and component library as needed.
- If your backend runs on a different port, configure a proxy in `vite.config.ts`:

```ts
// example
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```
