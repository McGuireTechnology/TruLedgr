"""
Database dependency injection functions for FastAPI.

This module provides reusable dependency functions for:
- Database session management
- Connection handling
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import get_async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database dependency that provides an async session.
    
    Yields:
        AsyncSession: Database session for async operations
    """
    async for session in get_async_session():
        yield session
