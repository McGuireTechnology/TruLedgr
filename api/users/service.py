"""
User service layer functions.

This module provides business logic for user management operations
including validation, business rules, and complex user operations.
It orchestrates CRUD operations with additional business logic.
"""

from typing import Optional, List, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
import re
from ulid import new as ulid_new

from .models import User
from .schemas import UserCreate, UserUpdate, UserPublic
from . import crud
from api.authentication.utils.password import get_password_hash, verify_password


class UserValidationError(Exception):
    """Exception raised for user validation errors."""
    pass


class UserNotFoundError(Exception):
    """Exception raised when user is not found."""
    pass


class UserPermissionError(Exception):
    """Exception raised for user permission errors."""
    pass


def validate_password_strength(password: str) -> List[str]:
    """
    Validate password strength and return list of issues.
    
    Args:
        password: Password to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    
    return issues


def validate_email_format(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username_format(username: str) -> List[str]:
    """
    Validate username format and return list of issues.
    
    Args:
        username: Username to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    if len(username) < 3:
        issues.append("Username must be at least 3 characters long")
    
    if len(username) > 50:
        issues.append("Username must not exceed 50 characters")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        issues.append("Username can only contain letters, numbers, underscores, and hyphens")
    
    if username.startswith(('_', '-')) or username.endswith(('_', '-')):
        issues.append("Username cannot start or end with underscore or hyphen")
    
    return issues


async def get_user_by_id(session: AsyncSession, user_id: str, include_deleted: bool = False) -> Optional[User]:
    """
    Get user by ID with business logic validation.
    
    Args:
        session: Database session
        user_id: User ID to search for
        include_deleted: Whether to include soft-deleted users
        
    Returns:
        User model instance or None if not found
    """
    if not user_id:
        return None
    
    return await crud.get_user_by_id(session, user_id, include_deleted)


async def get_user_by_username(session: AsyncSession, username: str, include_deleted: bool = False) -> Optional[User]:
    """
    Get user by username with validation.
    
    Args:
        session: Database session
        username: Username to search for
        include_deleted: Whether to include soft-deleted users
        
    Returns:
        User model instance or None if not found
    """
    if not username:
        return None
    
    return await crud.get_user_by_username(session, username.lower(), include_deleted)


async def get_user_by_email(session: AsyncSession, email: str, include_deleted: bool = False) -> Optional[User]:
    """
    Get user by email with validation.
    
    Args:
        session: Database session
        email: Email to search for
        include_deleted: Whether to include soft-deleted users
        
    Returns:
        User model instance or None if not found
    """
    if not email or not validate_email_format(email):
        return None
    
    return await crud.get_user_by_email(session, email.lower(), include_deleted)


async def list_users_with_filters(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    role_id: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    List users with filtering, pagination, and metadata.
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_deleted: Whether to include soft-deleted users
        is_active: Filter by active status
        is_verified: Filter by verification status
        role_id: Filter by role ID
        search: Search term for username, email, or name
        
    Returns:
        Dictionary with users list, total count, and pagination info
    """
    # Validate pagination parameters
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 1000:
        limit = 100
    
    # Build filters dictionary
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if is_verified is not None:
        filters["is_verified"] = is_verified
    if role_id is not None:
        filters["role_id"] = role_id
    
    # Get users
    if search:
        users = await crud.search_users(session, search, skip, limit, include_deleted)
        # For search, we need to count manually since search_users doesn't have a count equivalent
        total_count = len(await crud.search_users(session, search, 0, 10000, include_deleted))
    else:
        users = await crud.list_users(session, skip, limit, include_deleted, filters)
        total_count = await crud.count_users(session, include_deleted, filters)
    
    return {
        "users": users,
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(users) < total_count
    }


async def create_user_from_model(session: AsyncSession, user: User) -> User:
    """
    Create a user from a pre-built User model instance.
    
    This function is useful when you have a User model instance already
    constructed (e.g., during seeding operations) and want to persist it
    to the database with minimal validation.
    
    Args:
        session: Database session
        user: User model instance to create
        
    Returns:
        Created User model instance
        
    Raises:
        ValueError: If user already exists
    """
    # Check if username already exists (if provided)
    if user.username:
        existing_user = await get_user_by_username(session, user.username)
        if existing_user:
            raise ValueError(f"Username '{user.username}' already exists")
    
    # Check if email already exists (if provided)
    if user.email:
        existing_email = await get_user_by_email(session, user.email)
        if existing_email:
            raise ValueError(f"Email '{user.email}' already exists")
    
    # Set timestamps if not already set
    if not user.created_at:
        user.created_at = datetime.utcnow()
    if not user.updated_at:
        user.updated_at = datetime.utcnow()
    
    # Create user via CRUD layer
    return await crud.create_user(session, user)


async def create_user_with_validation(session: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user with comprehensive validation.
    
    Args:
        session: Database session
        user_data: UserCreate schema with user data
        
    Returns:
        Created User model instance
        
    Raises:
        UserValidationError: If validation fails
        ValueError: If user already exists
    """
    # Validate username
    username_issues = validate_username_format(user_data.username)
    if username_issues:
        raise UserValidationError(f"Username validation failed: {', '.join(username_issues)}")
    
    # Validate email
    if not validate_email_format(user_data.email):
        raise UserValidationError("Invalid email format")
    
    # Validate password strength
    password_issues = validate_password_strength(user_data.password)
    if password_issues:
        raise UserValidationError(f"Password validation failed: {', '.join(password_issues)}")
    
    # Check if username already exists
    existing_user = await get_user_by_username(session, user_data.username)
    if existing_user:
        raise ValueError("Username already exists")
    
    # Check if email already exists
    existing_email = await get_user_by_email(session, user_data.email)
    if existing_email:
        raise ValueError("Email already exists")
    
    # Create new user instance
    user = User(
        id=str(ulid_new()),
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        bio=user_data.bio,
        role_id=user_data.role_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Create user via CRUD layer
    return await crud.create_user(session, user)


async def update_user_with_validation(session: AsyncSession, user_id: str, user_data: UserUpdate) -> Optional[User]:
    """
    Update user with comprehensive validation.
    
    Args:
        session: Database session
        user_id: ID of user to update
        user_data: UserUpdate schema with update data
        
    Returns:
        Updated User model instance or None if not found
        
    Raises:
        UserValidationError: If validation fails
        ValueError: If constraint violations occur
    """
    # Check if user exists
    existing_user = await get_user_by_id(session, user_id)
    if not existing_user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    # Get update data, excluding unset fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Validate updates
    if "username" in update_data:
        username_issues = validate_username_format(update_data["username"])
        if username_issues:
            raise UserValidationError(f"Username validation failed: {', '.join(username_issues)}")
        
        # Check if username already exists for another user
        if update_data["username"] != existing_user.username:
            existing_username = await get_user_by_username(session, update_data["username"])
            if existing_username and existing_username.id != user_id:
                raise ValueError("Username already exists")
        
        update_data["username"] = update_data["username"].lower()
    
    if "email" in update_data:
        if not validate_email_format(update_data["email"]):
            raise UserValidationError("Invalid email format")
        
        # Check if email already exists for another user
        if update_data["email"] != existing_user.email:
            existing_email = await get_user_by_email(session, update_data["email"])
            if existing_email and existing_email.id != user_id:
                raise ValueError("Email already exists")
        
        update_data["email"] = update_data["email"].lower()
    
    if "password" in update_data:
        password_issues = validate_password_strength(update_data["password"])
        if password_issues:
            raise UserValidationError(f"Password validation failed: {', '.join(password_issues)}")
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Apply updates to user instance
    for field, value in update_data.items():
        setattr(existing_user, field, value)
    
    existing_user.updated_at = datetime.utcnow()
    
    # Update user via CRUD layer
    return await crud.update_user(session, existing_user)


async def change_user_password(session: AsyncSession, user_id: str, current_password: str, new_password: str) -> bool:
    """
    Change user password with current password verification.
    
    Args:
        session: Database session
        user_id: ID of user
        current_password: Current password for verification
        new_password: New password to set
        
    Returns:
        True if password was changed successfully
        
    Raises:
        UserNotFoundError: If user not found
        UserValidationError: If validation fails
        UserPermissionError: If current password is incorrect
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    # Verify current password
    if not user.hashed_password or not verify_password(current_password, user.hashed_password):
        raise UserPermissionError("Current password is incorrect")
    
    # Validate new password
    password_issues = validate_password_strength(new_password)
    if password_issues:
        raise UserValidationError(f"New password validation failed: {', '.join(password_issues)}")
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    
    await crud.update_user(session, user)
    return True


async def authenticate_user(session: AsyncSession, username_or_email: str, password: str) -> Optional[User]:
    """
    Authenticate user by username/email and password.
    
    Args:
        session: Database session
        username_or_email: Username or email address
        password: Password to verify
        
    Returns:
        User model instance if authentication successful, None otherwise
    """
    if not username_or_email or not password:
        return None
    
    # Try to find user by username first, then by email
    user = await get_user_by_username(session, username_or_email)
    if not user:
        user = await get_user_by_email(session, username_or_email)
    
    if not user:
        return None
    
    # Check if user is active and not deleted
    if not user.is_active or user.is_deleted:
        return None
    
    # Verify password
    if not user.hashed_password or not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    await crud.update_user(session, user)
    
    return user


async def activate_user_account(session: AsyncSession, user_id: str) -> Optional[User]:
    """
    Activate user account with business logic.
    
    Args:
        session: Database session
        user_id: ID of user to activate
        
    Returns:
        Updated User model instance or None if not found
        
    Raises:
        UserNotFoundError: If user not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    if user.is_deleted:
        raise UserValidationError("Cannot activate deleted user")
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    
    return await crud.update_user(session, user)


async def deactivate_user_account(session: AsyncSession, user_id: str) -> Optional[User]:
    """
    Deactivate user account with business logic.
    
    Args:
        session: Database session
        user_id: ID of user to deactivate
        
    Returns:
        Updated User model instance or None if not found
        
    Raises:
        UserNotFoundError: If user not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    
    return await crud.update_user(session, user)


async def soft_delete_user_account(session: AsyncSession, user_id: str) -> bool:
    """
    Soft delete user account with business logic.
    
    Args:
        session: Database session
        user_id: ID of user to delete
        
    Returns:
        True if user was deleted
        
    Raises:
        UserNotFoundError: If user not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    await crud.update_user(session, user)
    return True


async def restore_user_account(session: AsyncSession, user_id: str) -> Optional[User]:
    """
    Restore soft-deleted user account.
    
    Args:
        session: Database session
        user_id: ID of user to restore
        
    Returns:
        Restored User model instance or None if not found/not deleted
    """
    user = await get_user_by_id(session, user_id, include_deleted=True)
    if not user or not user.is_deleted:
        return None
    
    user.is_deleted = False
    user.deleted_at = None
    user.updated_at = datetime.utcnow()
    
    return await crud.update_user(session, user)


async def verify_user_email_address(session: AsyncSession, user_id: str) -> Optional[User]:
    """
    Verify user email with business logic.
    
    Args:
        session: Database session
        user_id: ID of user to verify
        
    Returns:
        Updated User model instance or None if not found
        
    Raises:
        UserNotFoundError: If user not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    user.email_verified = True
    user.is_verified = True
    user.updated_at = datetime.utcnow()
    
    return await crud.update_user(session, user)


async def get_user_statistics(session: AsyncSession) -> Dict[str, Any]:
    """
    Get comprehensive user statistics.
    
    Args:
        session: Database session
        
    Returns:
        Dictionary with detailed user statistics
    """
    # Get basic counts using existing CRUD functions
    total_users = await crud.count_users(session, include_deleted=False)
    active_users = await crud.count_users(session, include_deleted=False, filters={"is_active": True})
    verified_users = await crud.count_users(session, include_deleted=False, filters={"is_verified": True})
    oauth_users = await crud.count_users(session, include_deleted=False, filters={"is_oauth_user": True})
    deleted_users = await crud.count_users(session, include_deleted=True) - total_users
    
    # Build statistics dictionary
    stats: Dict[str, Any] = {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "verified_users": verified_users,
        "unverified_users": total_users - verified_users,
        "oauth_users": oauth_users,
        "regular_users": total_users - oauth_users,
        "deleted_users": deleted_users
    }
    
    # Add computed statistics
    stats["activation_rate"] = (
        stats["active_users"] / stats["total_users"] * 100 
        if stats["total_users"] > 0 else 0.0
    )
    stats["verification_rate"] = (
        stats["verified_users"] / stats["total_users"] * 100 
        if stats["total_users"] > 0 else 0.0
    )
    stats["oauth_adoption_rate"] = (
        stats["oauth_users"] / stats["total_users"] * 100 
        if stats["total_users"] > 0 else 0.0
    )
    
    return stats


async def search_users(
    session: AsyncSession,
    query: str,
    limit: int = 50,
    include_deleted: bool = False
) -> List[User]:
    """
    Search users by query with business logic.
    
    Args:
        session: Database session
        query: Search query
        limit: Maximum results to return
        include_deleted: Whether to include deleted users
        
    Returns:
        List of matching users
    """
    if not query or len(query.strip()) < 2:
        return []
    
    # Limit results for performance
    if limit > 100:
        limit = 100
    
    return await crud.search_users(session, query.strip(), 0, limit, include_deleted)