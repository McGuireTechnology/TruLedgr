# Project Structure Migration Guide

## Overview
The TruLedgr project has been restructured for better separation of concerns and cleaner deployments.

## New Structure

### Before (Mixed Structure)
```
truledgr/
├── main.py              # FastAPI app in root
├── requirements.txt     # Python deps in root  
├── frontend/           # Vue.js app
├── docs/              # Documentation
└── configs...         # Various configs
```

### After (Clean Separation)
```
truledgr/
├── api/                # 🐍 FastAPI Backend
│   ├── main.py         # Application entry
│   ├── requirements.txt# Python dependencies
│   ├── runtime.txt     # Python version
│   ├── start.sh        # Startup script
│   ├── .venv/          # Virtual environment
│   └── test_main.py    # Tests
├── dash/               # 🌐 Vue.js Frontend
│   ├── src/            # Source code
│   ├── package.json    # Node dependencies
│   ├── vite.config.ts  # Build configuration
│   └── dist/           # Built assets
├── docs/               # 📚 Documentation
└── *.yaml              # 🚀 Deployment configs
```

## Benefits of New Structure

### ✅ Clean Separation
- **Backend**: All Python/FastAPI code in `/api/`
- **Frontend**: All Vue.js/TypeScript code in `/dash/`
- **Docs**: Shared documentation in `/docs/`

### ✅ Independent Development
- Each component has its own dependencies
- Separate virtual environments and node_modules
- Independent testing and deployment

### ✅ Better Deployments
- **`api-only.yaml`**: Deploy just the API
- **`dash-only.yaml`**: Deploy just the frontend
- No deployment conflicts or routing issues

### ✅ Scalability
- Components can scale independently
- Different resource allocations per service
- Easier to add new services (mobile API, admin panel, etc.)

## Migration Impact

### Development Commands
```bash
# Backend development
cd api
source .venv/bin/activate
python main.py

# Frontend development  
cd dash
npm run dev

# Testing
cd api && python -m pytest
cd dash && npm run test:unit
```

### Deployment Configurations
- **`api-only.yaml`**: `source_dir: /api`
- **`dash-only.yaml`**: `source_dir: /dash`
- All combined configs updated to use new paths

### Documentation Updates
- All references updated to new structure
- Deployment guides reflect new approach
- Mobile integration unchanged (API endpoints same)

## Next Steps

1. **Deploy API**: Use `api-only.yaml` → `api.truledgr.app`
2. **Deploy Dashboard**: Use `dash-only.yaml` → `dash.truledgr.app`
3. **Configure DNS**: Point domains to respective deployments
4. **Test Integration**: Verify frontend connects to API

This structure provides a solid foundation for scaling the TruLedgr platform!
