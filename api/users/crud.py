"""
User CRUD operations.

This module provides pure database operations for user management.
Contains only basic database queries without business logic or validation.
Business logic should be handled in the service layer.
"""

from typing import Optional, List
from sqlmodel import select, func, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from .models import User


async def get_user_by_id(session: AsyncSession, user_id: str, include_deleted: bool = False) -> Optional[User]:
    """Get user by ID."""
    statement = select(User).where(User.id == user_id)
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str, include_deleted: bool = False) -> Optional[User]:
    """Get user by username."""
    statement = select(User).where(User.username == username)
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str, include_deleted: bool = False) -> Optional[User]:
    """Get user by email."""
    statement = select(User).where(User.email == email)
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def list_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    filters: Optional[dict] = None
) -> List[User]:
    """List users with optional filters and pagination."""
    statement = select(User)
    
    # Apply base filter for deleted users
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    # Apply additional filters if provided
    if filters:
        for field, value in filters.items():
            if hasattr(User, field) and value is not None:
                statement = statement.where(getattr(User, field) == value)
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def search_users(
    session: AsyncSession,
    search_term: str,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False
) -> List[User]:
    """Search users by username, email, first_name, or last_name."""
    search_pattern = f"%{search_term}%"
    
    statement = select(User).where(
        or_(
            User.username.contains(search_term),
            User.email.contains(search_term),
            User.first_name.contains(search_term) if User.first_name else False,
            User.last_name.contains(search_term) if User.last_name else False
        )
    )
    
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    statement = statement.offset(skip).limit(limit)
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def count_users(session: AsyncSession, include_deleted: bool = False, filters: Optional[dict] = None) -> int:
    """Count users with optional filters."""
    statement = select(func.count(User.id))
    
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    # Apply additional filters if provided
    if filters:
        for field, value in filters.items():
            if hasattr(User, field) and value is not None:
                statement = statement.where(getattr(User, field) == value)
    
    result = await session.execute(statement)
    return result.scalar_one()


async def create_user(session: AsyncSession, user: User) -> User:
    """Create a new user in the database."""
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise


async def update_user(session: AsyncSession, user: User) -> User:
    """Update an existing user in the database."""
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise


async def delete_user(session: AsyncSession, user: User) -> None:
    """Hard delete a user from the database."""
    await session.delete(user)
    await session.commit()


async def hard_delete_user(session: AsyncSession, user_id: str) -> bool:
    """Hard delete a user by ID from the database."""
    user = await get_user_by_id(session, user_id, include_deleted=True)
    if not user:
        return False
    
    await session.delete(user)
    await session.commit()
    return True


async def get_users_by_role(session: AsyncSession, role_id: str, include_deleted: bool = False) -> List[User]:
    """Get all users with a specific role."""
    statement = select(User).where(User.role_id == role_id)
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_oauth_users(session: AsyncSession, provider: Optional[str] = None, include_deleted: bool = False) -> List[User]:
    """Get OAuth users, optionally filtered by provider."""
    statement = select(User).where(User.is_oauth_user == True)
    
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    if provider:
        statement = statement.where(User.oauth_provider == provider)
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_users_by_status(
    session: AsyncSession,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    email_verified: Optional[bool] = None,
    include_deleted: bool = False
) -> List[User]:
    """Get users filtered by various status fields."""
    statement = select(User)
    
    if not include_deleted:
        statement = statement.where(User.is_deleted == False)
    
    if is_active is not None:
        statement = statement.where(User.is_active == is_active)
    
    if is_verified is not None:
        statement = statement.where(User.is_verified == is_verified)
    
    if email_verified is not None:
        statement = statement.where(User.email_verified == email_verified)
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def count_users_by_provider(session: AsyncSession) -> dict:
    """Get count of users by OAuth provider."""
    # Regular users (non-OAuth)
    regular_statement = select(func.count(User.id)).where(
        User.is_oauth_user == False,
        User.is_deleted == False
    )
    regular_result = await session.execute(regular_statement)
    regular_count = regular_result.scalar_one()
    
    # OAuth users by provider
    oauth_statement = select(User.oauth_provider, func.count(User.id)).where(
        User.is_oauth_user == True,
        User.is_deleted == False
    ).group_by(User.oauth_provider)
    oauth_result = await session.execute(oauth_statement)
    oauth_counts = {provider: count for provider, count in oauth_result.all() if provider}
    
    return {
        "regular": regular_count,
        **oauth_counts
    }