# Database Migration Strategy for DigitalOcean App Platform

## Overview

This document explains how database migrations are handled automatically during deployments on DigitalOcean App Platform.

## How It Works

### Build Phase (Automatic)
When a PRE_DEPLOY job is configured with `environment_slug: python`, DigitalOcean automatically:

1. **Clones the repository** to `/workspace/`
2. **Detects Python project** using the Heroku Python buildpack
3. **Installs Poetry** (detected from `pyproject.toml`)
4. **Installs all dependencies** via `poetry sync --only main`
   - This includes: `alembic`, `sqlalchemy`, `asyncpg`, `aiosqlite`, and all other production dependencies
5. **Builds the container image** with all packages available in the Python environment

### Run Phase (Our Script)
After the build completes, the PRE_DEPLOY job executes:

```yaml
run_command: python3 /workspace/api/run_migrations.py
```

This simple command works because:
- **Python 3.13** is available at `/workspace/.heroku/python/bin/python3`
- **All packages** are installed and available on the Python path
- **CNB launcher** automatically initializes the environment (PATH, PYTHONPATH, etc.)
- **Our script** (`run_migrations.py`) handles the migration logic with proper error handling

## The Migration Script

Located at `api/run_migrations.py`, this script:

```python
#!/usr/bin/env python3
"""
Simple migration runner script for DigitalOcean App Platform.
"""
import sys
import os
from pathlib import Path

# Ensure we're in the API directory
api_dir = Path(__file__).parent
os.chdir(api_dir)

try:
    print("🚀 Starting database migrations...")
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    print("✅ Migrations completed successfully!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)
```

### Why This Approach?

1. **Robust**: Leverages DigitalOcean's built-in build system
2. **Simple**: No manual package installation needed
3. **Maintainable**: Standard Python script, easy to test and debug
4. **Reliable**: All dependencies guaranteed to be available
5. **Fast**: Build cache speeds up subsequent deployments

## Configuration

### PRE_DEPLOY Job Spec

```yaml
jobs:
- name: db-migrate
  kind: PRE_DEPLOY
  environment_slug: python
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    value: ${DATABASE_URL}
  - key: SECRET_KEY
    scope: RUN_TIME
    value: ${SECRET_KEY}
  github:
    branch: main
    deploy_on_push: false  # Only trigger manually or via service deployment
    repo: McGuireTechnology/TruLedgr
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb
  run_command: python3 /workspace/api/run_migrations.py
  source_dir: /
```

### Key Configuration Points

- **`environment_slug: python`**: Triggers Python buildpack and dependency installation
- **`kind: PRE_DEPLOY`**: Runs before the service starts
- **`deploy_on_push: false`**: Job only runs when service deployment happens
- **`source_dir: /`**: Uses repository root (where `pyproject.toml` is located)
- **`scope: RUN_TIME`**: Environment variables only needed at runtime, not build time

## Deployment Flow

```
1. Code Push to GitHub
   ↓
2. DigitalOcean detects change
   ↓
3. PRE_DEPLOY Job Starts
   ├─ Build Phase: Install Poetry + Dependencies
   ├─ Run Phase: Execute run_migrations.py
   └─ Success/Failure
   ↓
4. If PRE_DEPLOY succeeds:
   └─ Service deployment proceeds
   
5. If PRE_DEPLOY fails:
   └─ Automatic rollback to previous version
```

## Benefits

### Zero Race Conditions
- Only one PRE_DEPLOY job runs at a time
- Service instances wait for job completion
- Alembic handles migration locking internally

### Automatic Rollback
- If migrations fail, deployment is automatically rolled back
- Previous working version remains active
- No manual intervention required

### Clear Logging
- All migration output visible in deployment logs
- Easy to diagnose issues
- Emoji indicators for quick status checks

## Testing Locally

You can test the migration script locally:

```bash
# Using Poetry
cd api
poetry run python run_migrations.py

# Or directly if venv is activated
python run_migrations.py
```

## Troubleshooting

### "Module not found" errors
- Check that `pyproject.toml` is in the repository root
- Ensure `source_dir: /` points to the correct location
- Verify Poetry lockfile is committed

### Migration fails but deployment succeeds
- Check that `kind: PRE_DEPLOY` is set (not `POST_DEPLOY`)
- Verify the job is linked to the service deployment

### Timeout issues
- Increase `instance_size_slug` for faster execution
- Consider breaking large migrations into smaller chunks
- Check database connection latency

## Production Checklist

- [x] `run_migrations.py` is executable and committed
- [x] `pyproject.toml` includes all required dependencies
- [x] `poetry.lock` is up-to-date and committed
- [x] `DATABASE_URL` environment variable is configured
- [x] PRE_DEPLOY job is properly linked in app spec
- [x] Job has `deploy_on_push: false` to avoid double deployments
- [x] Test migrations locally before pushing

## Additional Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Heroku Python Buildpack](https://github.com/heroku/heroku-buildpack-python)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)
