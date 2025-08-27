"""
Permission enforcement decorators and dependencies.

This module provides FastAPI dependencies for checking user permissions
and role-based access control enforcement.
"""

from typing import List, Callable
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.authentication.deps import get_current_user
from api.db.deps import get_db
from .service import get_user_permissions, check_user_permission


class PermissionDependency:
    """FastAPI dependency for permission checking."""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    async def __call__(
        self,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
    ):
        """Check if current user has required permission."""
        has_permission = await check_user_permission(
            session, 
            current_user.id, 
            self.required_permission
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {self.required_permission}"
            )
        
        return current_user


def require_permission(permission: str) -> Callable:
    """
    Create a dependency that requires a specific permission.
    
    Args:
        permission: Required permission scope (e.g., "users:create")
        
    Returns:
        Callable: FastAPI dependency function
        
    Usage:
        @router.get("/users")
        async def list_users(
            _: None = Depends(require_permission("users:list"))
        ):
            ...
    """
    return PermissionDependency(permission)


def require_role(role_name: str) -> Callable:
    """
    Create a dependency that requires a specific role.
    
    Args:
        role_name: Required role name (e.g., "admin")
        
    Returns:
        Callable: FastAPI dependency function
    """
    async def check_role(current_user = Depends(get_current_user)):
        if not hasattr(current_user, 'role') or not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' required"
            )
        
        # Handle both role object and role_id cases
        user_role_name = None
        if hasattr(current_user.role, 'name'):
            user_role_name = current_user.role.name
        elif hasattr(current_user, 'role_id') and current_user.role_id:
            # Would need to fetch role name from database
            # For now, assume role_id contains role name
            user_role_name = current_user.role_id
        
        if user_role_name != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' required"
            )
        
        return current_user
    
    return check_role


class MultiPermissionDependency:
    """FastAPI dependency for checking multiple permissions."""
    
    def __init__(self, required_permissions: List[str], require_all: bool = False):
        self.required_permissions = required_permissions
        self.require_all = require_all
    
    async def __call__(
        self,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
    ):
        """Check if current user has required permissions."""
        user_permissions = await get_user_permissions(session, current_user.id)
        
        if self.require_all:
            # User must have ALL permissions
            missing_permissions = [
                perm for perm in self.required_permissions 
                if perm not in user_permissions
            ]
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Missing permissions: {', '.join(missing_permissions)}"
                )
        else:
            # User must have ANY permission
            has_any_permission = any(
                perm in user_permissions 
                for perm in self.required_permissions
            )
            if not has_any_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required any of: {', '.join(self.required_permissions)}"
                )
        
        return current_user


def require_any_permission(permissions: List[str]) -> Callable:
    """
    Create a dependency that requires any of the specified permissions.
    
    Args:
        permissions: List of permission scopes
        
    Returns:
        Callable: FastAPI dependency function
    """
    return MultiPermissionDependency(permissions, require_all=False)


def require_all_permissions(permissions: List[str]) -> Callable:
    """
    Create a dependency that requires all of the specified permissions.
    
    Args:
        permissions: List of permission scopes
        
    Returns:
        Callable: FastAPI dependency function
    """
    return MultiPermissionDependency(permissions, require_all=True)


def is_admin() -> Callable:
    """
    Create a dependency that requires admin role.
    
    Returns:
        Callable: FastAPI dependency function
    """
    return require_role("admin")


def is_moderator() -> Callable:
    """
    Create a dependency that requires moderator role.
    
    Returns:
        Callable: FastAPI dependency function
    """
    return require_role("moderator")


def is_admin_or_moderator() -> Callable:
    """
    Create a dependency that requires admin or moderator role.
    
    Returns:
        Callable: FastAPI dependency function
    """
    async def check_admin_or_moderator(current_user = Depends(get_current_user)):
        if not hasattr(current_user, 'role') or not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or moderator role required"
            )
        
        # Handle both role object and role_id cases
        user_role_name = None
        if hasattr(current_user.role, 'name'):
            user_role_name = current_user.role.name
        elif hasattr(current_user, 'role_id') and current_user.role_id:
            user_role_name = current_user.role_id
        
        if user_role_name not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or moderator role required"
            )
        
        return current_user
    
    return check_admin_or_moderator
