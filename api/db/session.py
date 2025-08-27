"""
Database engine and session management for async operations.

This module provides the async database engine, session factory,
and session management utilities for the application.
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from api.settings import get_settings

settings = get_settings()

# Configure SQLAlchemy logging to suppress SQL commands in development
if not settings.db_echo:
    # Suppress SQLAlchemy engine logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# Create async engine with appropriate configuration
if settings.database_url.startswith("sqlite"):
    # SQLite configuration with async support
    engine: AsyncEngine = create_async_engine(
        settings.database_url_for_env,
        echo=settings.db_echo,
        # SQLite specific options
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        }
    )
else:
    # PostgreSQL/MySQL configuration
    engine: AsyncEngine = create_async_engine(
        settings.database_url_for_env,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle,
    )

# Create async session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.
    
    This is the main dependency function for getting database sessions
    in FastAPI endpoints and services.
    
    Yields:
        AsyncSession: Async database session
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    Get a standalone database session.
    
    This is useful for background tasks and non-FastAPI contexts.
    Remember to close the session manually.
    
    Returns:
        AsyncSession: Async database session
    """
    return SessionLocal()
