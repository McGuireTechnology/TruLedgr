"""
Common dependency injection functions for FastAPI.

This module provides reusable dependency functions for:
- Database session management
- Current user authentication
- Settings injection
- Common security checks
"""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from api.settings import Settings, get_settings_dependency
from api.db.session import get_async_session
from api.authentication.utils.jwt import decode_access_token
from api.users.service import get_user_by_id


# Security scheme for Bearer token
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database dependency that provides an async session.
    
    Yields:
        AsyncSession: Database session for async operations
    """
    async for session in get_async_session():
        yield session


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings_dependency)
) -> dict:
    """
    Extract and validate JWT token from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials
        settings: Application settings
        
    Returns:
        dict: Token payload containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token, settings.secret_key, settings.algorithm)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_payload: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token_payload: Decoded JWT token payload
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If user not found or inactive
    """
    from api.users.models import User
    
    user_id = token_payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is soft deleted
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get current user and ensure they are active.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Active authenticated user
        
    Raises:
        HTTPException: If user is inactive
    """
    # Additional checks can be added here
    # For now, get_current_user already checks for soft delete
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    settings: Settings = Depends(get_settings_dependency),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user if authenticated, otherwise return None.
    
    This is useful for endpoints that work for both authenticated 
    and anonymous users.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        settings: Application settings
        db: Database session
        
    Returns:
        User or None: Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token, settings.secret_key, settings.algorithm)
        
        if payload is None:
            return None
            
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        user = await get_user_by_id(db, user_id)
        if user is None or user.is_deleted:
            return None
            
        return user
        
    except Exception:
        return None


def get_settings() -> Settings:
    """
    Settings dependency for FastAPI dependency injection.
    
    Returns:
        Settings: Application settings instance
    """
    return get_settings_dependency()


# Pagination dependencies
class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = min(limit, 1000)  # Max 1000 items per page


def get_pagination_params(skip: int = 0, limit: int = 100) -> PaginationParams:
    """
    Pagination dependency.
    
    Args:
        skip: Number of items to skip (offset)
        limit: Maximum number of items to return
        
    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(skip, limit)
