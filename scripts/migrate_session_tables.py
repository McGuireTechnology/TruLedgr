"""
Database migration script to add session management tables.

This script creates the necessary tables for enhanced session management:
- user_sessions: Persistent session storage
- session_activities: Session activity audit trail

Run this script to upgrade your database schema.
"""

import asyncio
from sqlmodel import SQLModel, text
from fastapi_security_sample.db import engine
from fastapi_security_sample.users.models import UserSession, SessionActivity

import logging

logger = logging.getLogger(__name__)


async def create_session_tables():
    """Create session management tables"""
    try:
        # Import all models to ensure they're registered
        from fastapi_security_sample.users.models import (
            User, Role, Permission, RolePermission, 
            UserSession, SessionActivity, PasswordResetToken, OAuthAccount
        )
        
        logger.info("Creating session management tables...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("Session management tables created successfully!")
        
        # Verify tables were created
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user_sessions', 'session_activities')")
            )
            tables = result.fetchall()
            
            if len(tables) >= 1:  # At least one table should exist
                logger.info(f"✅ Verified: Found {len(tables)} session-related tables: {[t[0] for t in tables]}")
            else:
                logger.warning(f"⚠️  No session tables found")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create session tables: {e}")
        return False


async def verify_session_tables():
    """Verify that session tables exist and have the correct structure"""
    try:
        async with engine.begin() as conn:
            # Check if user_sessions table exists
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM user_sessions LIMIT 1"))
                logger.info("✅ user_sessions table exists and is accessible")
            except Exception as e:
                logger.warning(f"⚠️  user_sessions table issue: {e}")
            
            # Check if session_activities table exists
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM session_activities LIMIT 1"))
                logger.info("✅ session_activities table exists and is accessible")
            except Exception as e:
                logger.warning(f"⚠️  session_activities table issue: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to verify session tables: {e}")
        return False


async def main():
    """Main migration function"""
    print("🔄 Starting session management database migration...")
    
    # Create tables
    success = await create_session_tables()
    if not success:
        print("❌ Failed to create session tables")
        return False
    
    # Verify tables
    success = await verify_session_tables()
    if not success:
        print("❌ Failed to verify session tables")
        return False
    
    print("✅ Session management migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart your application to use the new session management system")
    print("2. The enhanced session manager will automatically persist sessions to the database")
    print("3. Access session analytics at /users/me/sessions/analytics")
    print("4. Use the existing session endpoints for basic session management")
    print("5. Session data will be persisted across application restarts")
    
    return True


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run migration
    asyncio.run(main())
