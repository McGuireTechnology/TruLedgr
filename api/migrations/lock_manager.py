"""
Database Migration Lock Manager

Ensures only one application instance runs migrations in a multi-host environment
using PostgreSQL advisory locks.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

logger = logging.getLogger(__name__)

# Unique lock ID for migrations (arbitrary number, must be consistent)
MIGRATION_LOCK_ID = 987654321


class MigrationLockManager:
    """Manages distributed locks for database migrations."""

    def __init__(self, database_url: str):
        """
        Initialize the lock manager.
        
        Args:
            database_url: Async database URL (postgresql+asyncpg://...)
        """
        self.database_url = database_url
        self.engine: AsyncEngine | None = None

    async def _get_engine(self) -> AsyncEngine:
        """Get or create the async engine."""
        if self.engine is None:
            self.engine = create_async_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=1,  # Only need one connection for locking
            )
        return self.engine

    @asynccontextmanager
    async def acquire_migration_lock(
        self, timeout_seconds: int = 300
    ) -> AsyncGenerator[bool, None]:
        """
        Acquire an advisory lock for migrations.
        
        This ensures only one process can run migrations at a time across
        multiple application instances.
        
        Args:
            timeout_seconds: How long to wait for the lock
            
        Yields:
            bool: True if lock was acquired, False if timeout
            
        Example:
            async with lock_manager.acquire_migration_lock() as acquired:
                if acquired:
                    # Run migrations
                    alembic.upgrade("head")
                else:
                    # Another instance is running migrations
                    logger.info("Waiting for migrations to complete...")
        """
        engine = await self._get_engine()
        
        async with engine.begin() as conn:
            # Try to acquire the lock with timeout
            logger.info(
                f"Attempting to acquire migration lock (ID: {MIGRATION_LOCK_ID})"
            )
            
            acquired = False
            start_time = asyncio.get_event_loop().time()
            
            while True:
                result = await conn.execute(
                    text("SELECT pg_try_advisory_lock(:lock_id)"),
                    {"lock_id": MIGRATION_LOCK_ID}
                )
                acquired = result.scalar()
                
                if acquired:
                    logger.info("Migration lock acquired successfully")
                    break
                
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout_seconds:
                    logger.warning(
                        f"Failed to acquire migration lock after {timeout_seconds}s"
                    )
                    break
                
                # Wait a bit before retrying
                await asyncio.sleep(1)
                logger.debug(
                    f"Waiting for migration lock... ({elapsed:.0f}s elapsed)"
                )
            
            try:
                yield acquired
            finally:
                if acquired:
                    # Release the lock
                    await conn.execute(
                        text("SELECT pg_advisory_unlock(:lock_id)"),
                        {"lock_id": MIGRATION_LOCK_ID}
                    )
                    logger.info("Migration lock released")

    async def close(self):
        """Close the database connection."""
        if self.engine:
            await self.engine.dispose()


async def run_migrations_with_lock(database_url: str) -> bool:
    """
    Run migrations with distributed locking.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        bool: True if migrations ran successfully, False if another instance is running them
    """
    from alembic import command
    from alembic.config import Config
    
    lock_manager = MigrationLockManager(database_url)
    
    try:
        async with lock_manager.acquire_migration_lock(timeout_seconds=300) as acquired:
            if not acquired:
                logger.info(
                    "Another instance is running migrations. "
                    "Waiting for completion..."
                )
                # Wait for the other instance to finish
                await asyncio.sleep(5)
                return False
            
            logger.info("Running database migrations...")
            
            # Run Alembic migrations synchronously (Alembic doesn't support async)
            alembic_cfg = Config("api/alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", database_url)
            
            command.upgrade(alembic_cfg, "head")
            
            logger.info("Database migrations completed successfully")
            return True
    finally:
        await lock_manager.close()


# For synchronous usage (e.g., in startup scripts)
def run_migrations_with_lock_sync(database_url: str) -> bool:
    """
    Synchronous wrapper for running migrations with lock.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        bool: True if migrations ran successfully
    """
    return asyncio.run(run_migrations_with_lock(database_url))
