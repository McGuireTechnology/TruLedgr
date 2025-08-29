# TruLedgr Workspace Setup

This workspace is now configured with centralized package management, where all Node.js dependencies are installed in the root `node_modules` directory.

## Structure

- **Root (`/`)**: Main workspace with consolidated `package.json` containing all dependencies
- **`/dash`**: Dashboard application (Vue.js)
- **`/landing`**: Landing page application (Vue.js) - now uses root packages
- **Other directories**: Backend, docs, mobile apps, etc.

## Package Management

All Node.js packages are now managed from the root workspace:

```bash
# Install all dependencies
npm install

# Add new dependencies (will be added to root package.json)
npm install <package-name>

# Development dependencies
npm install --save-dev <package-name>
```

## Landing Page Commands

The landing page has been configured to use packages from the root workspace:

```bash
# Development server
npm run dev:landing

# Build for production
npm run build:landing

# Type checking
npm run type-check:landing

# Linting
npm run lint:landing

# Preview built version
npm run preview:landing
```

## Configuration Changes Made

1. **Root `package.json`**:
   - Merged dependencies from `landing/package.json`
   - Updated versions to latest compatible versions
   - Added landing-specific scripts

2. **Landing Configuration**:
   - `vite.config.ts`: Updated to use root as working directory
   - `tsconfig.*.json`: Updated build info paths to use root `node_modules`
   - `package.json`: Simplified to contain only project metadata
   - `eslint.config.ts`: Updated to ignore generated files

3. **Benefits**:
   - Single source of truth for dependencies
   - Reduced disk space usage
   - Simplified dependency management
   - Consistent package versions across projects
   - Faster installs due to shared packages

## Development Workflow

1. Install dependencies from root: `npm install`
2. Run development servers as needed:
   - Dashboard: `npm run dev:dash`
   - Landing: `npm run dev:landing`
   - All servers: `npm run 🚀 Start All Development Servers` (via VS Code tasks)

The landing project now shares the same `node_modules` as the rest of the workspace while maintaining its independent build and development configuration.
