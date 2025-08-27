"""
User management API endpoints.

This module provides REST API endpoints for user management operations
including CRUD operations, authentication, and user profile management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.session import get_async_session
from api.authentication.deps import get_current_user
from api.db.deps import get_db
from api.authorization.policy import require_permission
from . import service
from .models import User
from .schemas import UserCreate, UserUpdate, UserRead, UserPublic
from api.users.service import (
    UserValidationError,
    UserNotFoundError,
    UserPermissionError
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    role_id: Optional[str] = Query(None, description="Filter by role ID"),
    search: Optional[str] = Query(None, description="Search in username, email, or name"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:list"))
):
    """
    List users with filtering and pagination.
    
    Requires 'users:list' permission.
    """
    try:
        result = await service.list_users_with_filters(
            session=session,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
            is_active=is_active,
            is_verified=is_verified,
            role_id=role_id,
            search=search
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information.
    
    No special permissions required - users can always view their own profile.
    """
    return current_user


@router.put("/me", response_model=UserRead)
async def update_current_user_profile(
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile information.
    
    No special permissions required - users can always edit their own profile.
    """
    try:
        updated_user = await service.update_user_with_validation(
            session=session,
            user_id=current_user.id,
            user_data=user_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/me/change-password")
async def change_current_user_password(
    current_password: str,
    new_password: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change current user's password.
    
    No special permissions required - users can always change their own password.
    """
    try:
        await service.change_user_password(
            session=session,
            user_id=current_user.id,
            current_password=current_password,
            new_password=new_password
        )
        
        return {"message": "Password changed successfully"}
        
    except UserPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_user_statistics(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:list"))
):
    """
    Get user statistics and metrics.
    
    Requires 'users:list' permission.
    """
    try:
        stats = await service.get_user_statistics(session)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user statistics: {str(e)}"
        )


@router.get("/search", response_model=List[UserPublic])
async def search_users(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:read"))
):
    """
    Search users by query.
    
    Requires 'users:read' permission.
    """
    try:
        users = await service.search_users(
            session=session,
            query=q,
            limit=limit,
            include_deleted=include_deleted
        )
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )


@router.post("", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:create"))
):
    """
    Create a new user.
    
    Requires 'users:create' permission.
    """
    try:
        new_user = await service.create_user_with_validation(
            session=session,
            user_data=user_data
        )
        return new_user
        
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    include_deleted: bool = Query(False, description="Include soft-deleted user"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:read"))
):
    """
    Get user by ID.
    
    Requires 'users:read' permission.
    """
    try:
        user = await service.get_user_by_id(
            session=session,
            user_id=user_id,
            include_deleted=include_deleted
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:update"))
):
    """
    Update user by ID.
    
    Requires 'users:update' permission.
    """
    try:
        updated_user = await service.update_user_with_validation(
            session=session,
            user_id=user_id,
            user_data=user_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    hard_delete: bool = Query(False, description="Permanently delete user (default: soft delete)"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:delete"))
):
    """
    Delete user by ID.
    
    By default performs soft delete (marks as deleted).
    Use hard_delete=true for permanent deletion.
    
    Requires 'users:delete' permission.
    """
    # Prevent users from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    try:
        if hard_delete:
            # Hard delete - permanently remove from database
            user = await service.get_user_by_id(session, user_id, include_deleted=True)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Use CRUD layer for hard delete
            from . import crud
            success = await crud.hard_delete_user(session, user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "User permanently deleted"}
        else:
            # Soft delete
            success = await service.soft_delete_user_account(session, user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "User deleted (soft delete)"}
            
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.post("/{user_id}/restore", response_model=UserRead)
async def restore_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:update"))
):
    """
    Restore a soft-deleted user.
    
    Requires 'users:update' permission.
    """
    try:
        restored_user = await service.restore_user_account(session, user_id)
        
        if not restored_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or not deleted"
            )
        
        return restored_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore user: {str(e)}"
        )


@router.post("/{user_id}/activate", response_model=UserRead)
async def activate_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:update"))
):
    """
    Activate a user account.
    
    Requires 'users:update' permission.
    """
    try:
        activated_user = await service.activate_user_account(session, user_id)
        
        if not activated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return activated_user
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )


@router.post("/{user_id}/deactivate", response_model=UserRead)
async def deactivate_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:update"))
):
    """
    Deactivate a user account.
    
    Requires 'users:update' permission.
    """
    # Prevent users from deactivating themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    try:
        deactivated_user = await service.deactivate_user_account(session, user_id)
        
        if not deactivated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return deactivated_user
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )


@router.post("/{user_id}/verify-email", response_model=UserRead)
async def verify_user_email(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("users:update"))
):
    """
    Verify a user's email address.
    
    Requires 'users:update' permission.
    """
    try:
        verified_user = await service.verify_user_email_address(session, user_id)
        
        if not verified_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return verified_user
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify user email: {str(e)}"
        )


@router.get("/{user_id}/public", response_model=UserPublic)
async def get_user_public_profile(
    user_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get user's public profile information.
    
    No authentication required - returns only public information.
    """
    try:
        user = await service.get_user_by_id(session, user_id)
        
        if not user or not user.is_active or user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return only public information
        return UserPublic(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_picture_url=user.profile_picture_url,
            bio=user.bio
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )
