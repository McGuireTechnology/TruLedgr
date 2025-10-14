# Database Migrations

This directory contains Alembic database migrations for TruLedgr API.

## Overview

We use [Alembic](https://alembic.sqlalchemy.org/) for managing database schema changes. Alembic provides:

- **Version control** for database schema
- **Automatic migration generation** from SQLAlchemy models
- **Up/down migration** support for safe rollbacks
- **Async SQLAlchemy** support for modern async/await patterns

## Quick Start

### Prerequisites

Ensure you have:
1. Poetry environment activated: `poetry shell`
2. Environment variables loaded: `set -a && source api/.env && set +a`
3. Database URL configured in `.env`: `DATABASE_URL=sqlite+aiosqlite:///./truledgr.db`

### Common Commands

All commands should be run from the `api/` directory:

```bash
cd api

# Create a new migration (autogenerate from models)
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
poetry run alembic upgrade head

# Apply migrations up to a specific revision
poetry run alembic upgrade <revision_id>

# Rollback last migration
poetry run alembic downgrade -1

# Rollback to a specific revision
poetry run alembic downgrade <revision_id>

# Show current migration version
poetry run alembic current

# Show migration history
poetry run alembic history

# Show pending migrations
poetry run alembic heads
```

## Creating Migrations

### Automatic Generation (Recommended)

1. Make changes to your SQLAlchemy models in `api/repositories/models/`
2. Generate migration from model changes:
   ```bash
   cd api
   poetry run alembic revision --autogenerate -m "Add user profile fields"
   ```
3. Review the generated migration in `api/migrations/versions/`
4. Edit if needed (Alembic can't detect everything)
5. Apply the migration:
   ```bash
   poetry run alembic upgrade head
   ```

### Manual Migration

For changes Alembic can't detect automatically (e.g., data migrations):

```bash
cd api
poetry run alembic revision -m "Migrate user data to new format"
```

Then edit the generated file in `versions/` to add your custom migration logic.

## Migration Best Practices

### 1. Always Review Generated Migrations

Alembic's autogenerate is smart but not perfect. It can't detect:
- Table/column renames (appears as drop + create)
- Changes to column constraints
- Custom SQL or data migrations

Always review generated migrations before applying!

### 2. Test Migrations

Before deploying:
1. Test upgrade: `alembic upgrade head`
2. Test downgrade: `alembic downgrade -1`
3. Test upgrade again: `alembic upgrade head`

### 3. Never Edit Applied Migrations

Once a migration has been applied to production:
- Don't edit it
- Create a new migration to fix issues
- This ensures consistency across all environments

### 4. Use Descriptive Messages

Good: `"Add oauth_provider column to users table"`
Bad: `"Update database"`

### 5. Keep Migrations Small

- One logical change per migration
- Easier to review, test, and rollback
- Better git history

## Migration Workflow

### Development

```bash
# 1. Update models
vim api/repositories/models/user.py

# 2. Generate migration
cd api
poetry run alembic revision --autogenerate -m "Add user timezone field"

# 3. Review and edit migration
vim migrations/versions/xxxx_add_user_timezone_field.py

# 4. Apply migration
poetry run alembic upgrade head

# 5. Test the API
cd ..
poetry run uvicorn api.main:app --reload

# 6. Commit migration
git add api/migrations/versions/xxxx_add_user_timezone_field.py
git commit -m "feat(db): add user timezone field"
```

### Production Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Backup database (if using PostgreSQL)
pg_dump truledgr > backup-$(date +%Y%m%d).sql

# 3. Apply migrations
cd api
poetry run alembic upgrade head

# 4. Restart API service
systemctl restart truledgr-api
```

## Database URLs

The migration system supports multiple database backends through SQLAlchemy:

### SQLite (Development)
```bash
DATABASE_URL=sqlite+aiosqlite:///./truledgr.db
```

### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/truledgr
```

### MySQL (If needed)
```bash
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/truledgr
```

## Troubleshooting

### "Target database is not up to date"

Your database is behind the migration version:
```bash
poetry run alembic upgrade head
```

### "Can't locate revision identified by 'xxxx'"

The migration file is missing. Options:
1. Restore from git: `git checkout api/migrations/versions/xxxx_*.py`
2. Roll back to a known revision: `alembic downgrade <previous_revision>`

### "FAILED: Can't locate revision identified by 'head'"

No migrations have been applied yet:
```bash
poetry run alembic upgrade head
```

### "Multiple head revisions are present"

You have branched migration history. Merge the branches:
```bash
poetry run alembic merge heads -m "Merge migration branches"
poetry run alembic upgrade head
```

### Environment variable not loaded

Alembic can't find DATABASE_URL:
```bash
# Load .env file first
set -a && source api/.env && set +a
cd api
poetry run alembic upgrade head
```

## Configuration

### alembic.ini

Located at `api/alembic.ini`, contains:
- Migration script location
- Logging configuration
- Post-write hooks (black, ruff)

Database URL is **not** stored here for security. It's loaded from:
1. `DATABASE_URL` environment variable (preferred)
2. Fallback to `sqlite+aiosqlite:///./truledgr.db`

### env.py

Located at `api/migrations/env.py`, contains:
- Model metadata import (`api.repositories.models.Base`)
- Async migration support
- Environment variable handling

## File Structure

```
api/
├── alembic.ini              # Alembic configuration
├── migrations/
│   ├── env.py              # Migration environment setup
│   ├── script.py.mako      # Template for new migrations
│   ├── README.md           # This file
│   └── versions/           # Migration files
│       └── 8be61d0cc541_initial_migration_with_users_and_oauth_.py
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Auto Generate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Alembic Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
