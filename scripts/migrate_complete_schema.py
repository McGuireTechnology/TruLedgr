#!/usr/bin/env python3
"""
Complete database migration to update the users table with OAuth fields
and create session management tables.
"""

import asyncio
import logging
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi_security_sample.db import engine
from fastapi_security_sample.users.models import User, UserSession, SessionActivity, OAuthAccount, PasswordResetToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_column_exists(engine: AsyncEngine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"PRAGMA table_info({table_name})")
        )
        columns = [row[1] for row in result.fetchall()]  # row[1] is column name
        return column_name in columns

async def add_column_if_missing(engine: AsyncEngine, table_name: str, column_name: str, column_definition: str):
    """Add a column to a table if it doesn't exist"""
    exists = await check_column_exists(engine, table_name, column_name)
    if not exists:
        async with engine.connect() as conn:
            await conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
            await conn.commit()
        logger.info(f"✅ Added column {column_name} to {table_name}")
    else:
        logger.info(f"⚠️ Column {column_name} already exists in {table_name}")

async def migrate_users_table():
    """Add OAuth and other missing fields to the users table"""
    logger.info("🔄 Updating users table with OAuth and missing fields...")
    
    # OAuth fields
    await add_column_if_missing(engine, "users", "is_oauth_user", "BOOLEAN DEFAULT 0")
    await add_column_if_missing(engine, "users", "oauth_provider", "VARCHAR(50)")
    await add_column_if_missing(engine, "users", "oauth_provider_id", "VARCHAR(255)")
    await add_column_if_missing(engine, "users", "profile_picture_url", "TEXT")
    await add_column_if_missing(engine, "users", "email_verified", "BOOLEAN DEFAULT 0")
    
    # Create indexes for OAuth fields
    async with engine.connect() as conn:
        try:
            # Check if indexes exist and create them if they don't
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_oauth_provider ON users(oauth_provider)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_oauth_provider_id ON users(oauth_provider_id)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified)"))
            await conn.commit()
            logger.info("✅ Created OAuth indexes on users table")
        except Exception as e:
            logger.warning(f"⚠️ Could not create indexes: {e}")

async def main():
    """Run the complete database migration"""
    logger.info("🚀 Starting complete database migration...")
    
    try:
        # 1. Update users table with OAuth fields
        await migrate_users_table()
        
        # 2. Create all tables (this will create missing tables and won't affect existing ones)
        logger.info("🔄 Creating/updating all database tables...")
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from fastapi_security_sample.users.models import (
                User, UserSession, SessionActivity, OAuthAccount, 
                PasswordResetToken, Role, Permission, RolePermission
            )
            from fastapi_security_sample.db import Base
            
            # This will create missing tables and won't affect existing ones
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ All database tables created/updated successfully!")
        
        # 3. Verify the migration
        logger.info("🔍 Verifying migration...")
        async with engine.connect() as conn:
            # Check users table
            users_result = await conn.execute(text("PRAGMA table_info(users)"))
            users_columns = [row[1] for row in users_result.fetchall()]
            logger.info(f"Users table columns: {', '.join(users_columns)}")
            
            # Check OAuth columns specifically
            oauth_columns = ['is_oauth_user', 'oauth_provider', 'oauth_provider_id', 'profile_picture_url', 'email_verified']
            missing_oauth_columns = [col for col in oauth_columns if col not in users_columns]
            
            if missing_oauth_columns:
                logger.error(f"❌ Missing OAuth columns: {missing_oauth_columns}")
            else:
                logger.info("✅ All OAuth columns present in users table")
            
            # Check session tables
            tables_result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user_sessions', 'session_activities', 'oauth_accounts')")
            )
            tables = [row[0] for row in tables_result.fetchall()]
            logger.info(f"✅ Session and OAuth tables found: {', '.join(tables)}")
            
            await conn.commit()
        
        logger.info("✅ Database migration completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Restart your FastAPI application")
        logger.info("2. The application will now support OAuth2 and database-backed sessions")
        logger.info("3. Test the session analytics endpoints")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
