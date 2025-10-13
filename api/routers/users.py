"""User management routes for administrators and users."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from ..schemas.auth import (
    UserResponse,
    UserUpdateRequest,
    UserPartialUpdateRequest,
    UserListResponse,
    ErrorResponse
)
from ..dependencies.database import get_uow
from ..dependencies.auth import get_current_user, require_admin
from ..repositories.uow import SqlAlchemyUnitOfWork
from ..entities import User
from ..value_objects import UserId, EmailAddress
from ..config.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/users", tags=["user-management"])


@router.get(
    "",
    response_model=UserListResponse,
    responses={
        200: {"description": "List of users"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin access required"}
    },
    summary="List all users",
    description="Get paginated list of all users (admin only)"
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Items per page"
    ),
    admin: User = Depends(require_admin),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> UserListResponse:
    """
    List all users with pagination.
    
    Admin-only endpoint to retrieve all users in the system.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (1-100)
        admin: Current admin user (injected)
        uow: Unit of Work for database operations
        
    Returns:
        Paginated list of users
    """
    try:
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get users and total count
        users = await uow.users.list_all(skip=skip, limit=page_size)
        total = await uow.users.count()
        
        # Convert to response models
        user_responses = [
            UserResponse(
                id=str(user.id),
                username=user.username,
                email=str(user.email),
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"description": "User found"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "User not found"}
    },
    summary="Get user by ID",
    description="Get specific user by ID (admin or own profile)"
)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> UserResponse:
    """
    Get user by ID.
    
    Users can get their own profile, admins can get any user.
    
    Args:
        user_id: UUID of the user to retrieve
        current_user: Current authenticated user
        uow: Unit of Work for database operations
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found or access denied
    """
    try:
        # Parse user ID
        target_user_id = UserId(user_id)
        
        # Check authorization: must be admin or requesting own profile
        if not current_user.is_admin and current_user.id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: can only view your own profile"
            )
        
        # Get user
        user = await uow.users.get_by_id(target_user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=str(user.email),
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin access required"}
    },
    summary="Create new user",
    description="Create a new user account (admin only)"
)
async def create_user(
    request: UserUpdateRequest,
    admin: User = Depends(require_admin),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> UserResponse:
    """
    Create a new user (admin only).
    
    This endpoint allows admins to create users without passwords.
    Users should use /auth/register for normal registration.
    
    Args:
        request: User data
        admin: Current admin user
        uow: Unit of Work for database operations
        
    Returns:
        Created user information
    """
    try:
        # Check if username already exists
        existing_username = await uow.users.get_by_username(
            request.username
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Check if email already exists
        email = EmailAddress(request.email)
        existing = await uow.users.get_by_email(email)
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            id=UserId.generate(),
            username=request.username,
            email=email,
            hashed_password="",  # No password set (admin-created)
            is_active=request.is_active,
            is_admin=request.is_admin
        )
        
        created_user = await uow.users.create(user)
        await uow.commit()
        
        return UserResponse(
            id=str(created_user.id),
            username=created_user.username,
            email=str(created_user.email),
            is_active=created_user.is_active,
            is_admin=created_user.is_admin,
            created_at=created_user.created_at,
            last_login=created_user.last_login
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"description": "User updated"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "User not found"}
    },
    summary="Update user (full)",
    description="Full update of user (admin or own profile, limited fields)"
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> UserResponse:
    """
    Full update of user (PUT).
    
    Admins can update any user and all fields.
    Regular users can only update their own email and business flag.
    
    Args:
        user_id: UUID of user to update
        request: Updated user data
        current_user: Current authenticated user
        uow: Unit of Work for database operations
        
    Returns:
        Updated user information
    """
    try:
        # Parse user ID
        target_user_id = UserId(user_id)
        
        # Get existing user
        user = await uow.users.get_by_id(target_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Check authorization
        is_own_profile = current_user.id == target_user_id
        if not current_user.is_admin and not is_own_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: can only update your own profile"
            )
        
        # Update email if changed
        new_email = EmailAddress(request.email)
        if new_email != user.email:
            # Check if new email is available
            existing = await uow.users.get_by_email(new_email)
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = new_email
        
        # Update username if provided
        if request.username != user.username:
            # Check if new username is available
            existing_username = await uow.users.get_by_username(
                request.username
            )
            if existing_username and existing_username.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = request.username
        
        # Update fields based on permissions
        if current_user.is_admin:
            # Admin can update everything
            user.is_active = request.is_active
            user.is_admin = request.is_admin
        
        # Save changes
        updated_user = await uow.users.update(user)
        await uow.commit()
        
        return UserResponse(
            id=str(updated_user.id),
            username=updated_user.username,
            email=str(updated_user.email),
            is_active=updated_user.is_active,
            is_admin=updated_user.is_admin,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        200: {"description": "User updated"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "User not found"}
    },
    summary="Update user (partial)",
    description="Partial update of user (admin or own profile, limited fields)"
)
async def partial_update_user(
    user_id: str,
    request: UserPartialUpdateRequest,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> UserResponse:
    """
    Partial update of user (PATCH).
    
    Only updates fields that are provided in the request.
    Admins can update any user and all fields.
    Regular users can only update their own email and business flag.
    
    Args:
        user_id: UUID of user to update
        request: Fields to update
        current_user: Current authenticated user
        uow: Unit of Work for database operations
        
    Returns:
        Updated user information
    """
    try:
        # Parse user ID
        target_user_id = UserId(user_id)
        
        # Get existing user
        user = await uow.users.get_by_id(target_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Check authorization
        is_own_profile = current_user.id == target_user_id
        if not current_user.is_admin and not is_own_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: can only update your own profile"
            )
        
        # Update username if provided
        if request.username is not None:
            if request.username != user.username:
                # Check if new username is available
                existing_username = await uow.users.get_by_username(
                    request.username
                )
                if existing_username and existing_username.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
                user.username = request.username
        
        # Update email if provided
        if request.email is not None:
            new_email = EmailAddress(request.email)
            if new_email != user.email:
                # Check if new email is available
                existing = await uow.users.get_by_email(new_email)
                if existing and existing.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use"
                    )
                user.email = new_email
        
        # Update other fields based on permissions
        if current_user.is_admin:
            # Admin can update everything
            if request.is_active is not None:
                if request.is_active:
                    user.activate()
                else:
                    user.deactivate()
            if request.is_admin is not None:
                user.is_admin = request.is_admin
        
        # Save changes
        updated_user = await uow.users.update(user)
        await uow.commit()
        
        return UserResponse(
            id=str(updated_user.id),
            username=updated_user.username,
            email=str(updated_user.email),
            is_active=updated_user.is_active,
            is_admin=updated_user.is_admin,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "User deleted"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "User not found"}
    },
    summary="Delete user",
    description="Delete user account (admin only)"
)
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """
    Delete user by ID (admin only).
    
    Permanently removes a user from the system.
    
    Args:
        user_id: UUID of user to delete
        admin: Current admin user
        uow: Unit of Work for database operations
        
    Returns:
        No content (204)
        
    Raises:
        HTTPException: If user not found
    """
    try:
        # Parse user ID
        target_user_id = UserId(user_id)
        
        # Prevent admin from deleting themselves
        if admin.id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Delete user
        deleted = await uow.users.delete(target_user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        await uow.commit()
        return None
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
