"""
SQLModel base configuration and table management utilities.

This module provides the base SQLModel configuration and utilities
for creating and managing database tables in development and tests.
"""

from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine

from api.settings import get_settings

# Import all models to ensure they are registered with SQLModel metadata
# This must be done before create_all() is called
def import_all_models():
    """Import all SQLModel models to register them with metadata."""
    # Import all model modules to register tables
    try:
        from api.users.models import User, UserSession, SessionActivity
        from api.authorization.models import Role, Permission, RolePermission
        from api.authentication.passwords.models import PasswordResetToken
        from api.items.models import Item
        from api.groups.models import Group, UserGroup
        
        # Import new security models
        from api.authentication.sessions.analytics import SessionAnalytics
        from api.authentication.oauth2.user_manager import OAuth2Account
        
    except ImportError as e:
        # Models may not exist yet during initial setup
        print(f"Warning: Could not import some models during setup: {e}")
        pass

# Call this to register models
import_all_models()

# SQLModel metadata - this will contain all registered tables
Base = SQLModel


async def create_tables(engine: AsyncEngine):
    """
    Create all database tables.
    
    This is typically used in development and tests.
    In production, use proper database migrations.
    
    Args:
        engine: Async database engine
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine: AsyncEngine):
    """
    Drop all database tables.
    
    This is typically used in tests for cleanup.
    
    Args:
        engine: Async database engine
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
