#!/usr/bin/env python3
"""
Prepare database for Alembic migrations.

This script will:
1. Create a snapshot of current database state
2. Drop all existing tables to start fresh with Alembic
3. Apply initial migration to recreate all tables from current models

This ensures we have a clean migration baseline aligned with current models.
"""

import asyncio
import logging
import os
import shutil
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from api.db.session import engine, get_async_session
from api.db.base import Base, import_all_models
from api.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def backup_database():
    """Create a backup of the current database."""
    settings = get_settings()
    
    if "sqlite" in settings.database_url_for_env:
        # Extract database file path
        db_path = settings.database_url_for_env.replace("sqlite+aiosqlite://", "").replace("sqlite+aiosqlite:///", "")
        
        if db_path != ":memory:" and os.path.exists(db_path):
            backup_path = f"{db_path}.backup"
            shutil.copy2(db_path, backup_path)
            logger.info(f"✅ Database backup created: {backup_path}")
            return backup_path
        else:
            logger.info("⚠️ In-memory database or file doesn't exist - no backup needed")
            return None
    else:
        logger.info("⚠️ Non-SQLite database - create backup manually if needed")
        return None


async def get_current_tables():
    """Get list of current tables in the database."""
    async with engine.connect() as conn:
        if "sqlite" in str(engine.url):
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            )
        else:
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
        
        tables = [row[0] for row in result.fetchall()]
        return tables


async def stamp_database_as_current():
    """Mark the database as being at the current migration level."""
    # This requires running the Alembic stamp command
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "alembic", "stamp", "head"
    ], capture_output=True, text=True, cwd="/Users/nathan/Documents/truledgr")
    
    if result.returncode == 0:
        logger.info("✅ Database stamped with current migration")
        return True
    else:
        logger.error(f"❌ Failed to stamp database: {result.stderr}")
        return False


async def recreate_tables_from_models():
    """Drop all tables and recreate from current models."""
    logger.info("🔄 Recreating all tables from current models...")
    
    # Import all models to ensure they're registered
    import_all_models()
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("✅ All tables dropped")
        
        # Create all tables from current models
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ All tables created from current models")


async def main():
    """Main function to prepare database for Alembic."""
    logger.info("🚀 Preparing database for Alembic migrations...")
    
    backup_path = None
    try:
        # 1. Create backup
        backup_path = await backup_database()
        
        # 2. Get current table list
        current_tables = await get_current_tables()
        logger.info(f"📊 Current tables: {len(current_tables)} tables found")
        for table in sorted(current_tables):
            logger.info(f"  - {table}")
        
        # 3. Ask for confirmation
        print("\n" + "="*60)
        print("⚠️  WARNING: This will DROP ALL TABLES and recreate them!")
        print("⚠️  Make sure you have backed up any important data!")
        if backup_path:
            print(f"✅ Backup created at: {backup_path}")
        print("="*60)
        
        confirm = input("\nDo you want to continue? (yes/no): ").lower().strip()
        if confirm not in ['yes', 'y']:
            logger.info("❌ Operation cancelled by user")
            return False
        
        # 4. Recreate tables from current models
        await recreate_tables_from_models()
        
        # 5. Stamp database as current (this will be done outside)
        logger.info("✅ Database prepared for Alembic!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Run: alembic stamp head")
        logger.info("2. Future schema changes: alembic revision --autogenerate -m 'description'")
        logger.info("3. Apply migrations: alembic upgrade head")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to prepare database: {e}")
        if backup_path and os.path.exists(backup_path):
            logger.info(f"💾 Restore from backup: {backup_path}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
