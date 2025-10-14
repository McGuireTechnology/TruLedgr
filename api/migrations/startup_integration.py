"""
Application Startup with Automatic Migrations

Demonstrates how to run migrations automatically on application startup
in a multi-host SaaS environment with proper locking.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan_with_migrations(app: FastAPI):
    """
    FastAPI lifespan handler that runs migrations on startup.
    
    Only one instance will run migrations using PostgreSQL advisory locks.
    Other instances will wait for migrations to complete.
    """
    # Startup: Run migrations
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)
    
    # Convert to async URL if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
    elif database_url.startswith("sqlite://"):
        # SQLite doesn't support advisory locks, skip for dev
        logger.warning("SQLite detected, skipping migration locks")
    else:
        from api.migrations.lock_manager import run_migrations_with_lock
        
        logger.info("Attempting to run database migrations...")
        try:
            await run_migrations_with_lock(database_url)
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            # Decide: fail fast or continue?
            # For production, you probably want to fail fast
            sys.exit(1)
    
    yield  # Application runs
    
    # Shutdown: cleanup if needed
    logger.info("Application shutting down")


# Example 1: Integrated with FastAPI app
def create_app_with_auto_migrations() -> FastAPI:
    """Create FastAPI app with automatic migrations."""
    app = FastAPI(
        title="TruLedgr API",
        version="0.1.1",
        lifespan=lifespan_with_migrations
    )
    
    # Include routers, etc.
    return app


# Example 2: Standalone migration runner (recommended for production)
async def run_migrations_standalone():
    """
    Run migrations as a standalone process.
    
    Use this in:
    - Kubernetes init containers
    - DigitalOcean pre-deploy jobs
    - CI/CD deployment pipelines
    """
    import asyncio
    from api.migrations.lock_manager import run_migrations_with_lock
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)
    
    # Convert to async URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
    
    logger.info("Running migrations...")
    try:
        success = await run_migrations_with_lock(database_url)
        if success:
            logger.info("Migrations completed successfully")
            sys.exit(0)
        else:
            logger.info("Another instance ran migrations")
            sys.exit(0)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # For standalone migration runs
    import asyncio
    asyncio.run(run_migrations_standalone())
