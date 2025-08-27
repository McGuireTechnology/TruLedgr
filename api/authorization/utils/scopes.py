"""
Security scopes and permission management.

This module defines canonical permission strings and provides
utilities for checking user permissions and scopes.
"""

from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status


class Scopes:
    """
    Canonical permission scopes for the application.
    
    These scopes define the fine-grained permissions that can be
    assigned to users through roles and used in API endpoints.
    """
    
    # User management permissions
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_LIST = "users:list"
    
    # Group management permissions
    GROUPS_CREATE = "groups:create"
    GROUPS_READ = "groups:read"
    GROUPS_UPDATE = "groups:update"
    GROUPS_DELETE = "groups:delete"
    GROUPS_LIST = "groups:list"
    GROUPS_MANAGE_MEMBERS = "groups:manage_members"
    
    # Role management permissions
    ROLES_CREATE = "roles:create"
    ROLES_READ = "roles:read"
    ROLES_UPDATE = "roles:update"
    ROLES_DELETE = "roles:delete"
    ROLES_LIST = "roles:list"
    ROLES_ASSIGN = "roles:assign"
    
    # Permission management
    PERMISSIONS_CREATE = "permissions:create"
    PERMISSIONS_READ = "permissions:read"
    PERMISSIONS_UPDATE = "permissions:update"
    PERMISSIONS_DELETE = "permissions:delete"
    PERMISSIONS_LIST = "permissions:list"
    PERMISSIONS_ASSIGN = "permissions:assign"
    
    # Session management
    SESSIONS_READ = "sessions:read"
    SESSIONS_REVOKE = "sessions:revoke"
    SESSIONS_LIST = "sessions:list"
    
    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    ADMIN_MANAGE = "admin:manage"
    ADMIN_MONITOR = "admin:monitor"
    
    @classmethod
    def get_all_scopes(cls) -> List[str]:
        """
        Get all available permission scopes.
        
        Returns:
            List[str]: All permission scopes
        """
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def get_user_scopes(cls) -> List[str]:
        """
        Get basic user permission scopes.
        
        Returns:
            List[str]: Basic user permission scopes
        """
        return [
            cls.GROUPS_READ,
            cls.GROUPS_LIST,
            cls.SESSIONS_READ
        ]
    
    @classmethod
    def get_moderator_scopes(cls) -> List[str]:
        """
        Get moderator permission scopes.
        
        Returns:
            List[str]: Moderator permission scopes
        """
        return cls.get_user_scopes() + [
            cls.USERS_READ,
            cls.USERS_LIST,
            cls.GROUPS_CREATE,
            cls.GROUPS_UPDATE,
            cls.GROUPS_MANAGE_MEMBERS,
            cls.SESSIONS_LIST
        ]
    
    @classmethod
    def get_admin_scopes(cls) -> List[str]:
        """
        Get admin permission scopes (all permissions).
        
        Returns:
            List[str]: All permission scopes
        """
        return cls.get_all_scopes()


class ScopeGroup(Enum):
    """Permission scope groupings for easier management."""
    
    USER_BASIC = "user_basic"
    USER_MANAGEMENT = "user_management"
    GROUP_MANAGEMENT = "group_management"
    ROLE_MANAGEMENT = "role_management"
    PERMISSION_MANAGEMENT = "permission_management"
    SESSION_MANAGEMENT = "session_management"
    ADMIN = "admin"


def check_permission(user_scopes: List[str], required_scope: str) -> bool:
    """
    Check if user has required permission scope.
    
    Args:
        user_scopes: List of user's permission scopes
        required_scope: Required permission scope
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    return required_scope in user_scopes


def require_permission(user_scopes: List[str], required_scope: str) -> None:
    """
    Require user to have specific permission scope.
    
    Args:
        user_scopes: List of user's permission scopes
        required_scope: Required permission scope
        
    Raises:
        HTTPException: If user doesn't have required permission
    """
    if not check_permission(user_scopes, required_scope):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required scope: {required_scope}"
        )


def check_any_permission(user_scopes: List[str], required_scopes: List[str]) -> bool:
    """
    Check if user has any of the required permission scopes.
    
    Args:
        user_scopes: List of user's permission scopes
        required_scopes: List of required permission scopes
        
    Returns:
        bool: True if user has any required permission, False otherwise
    """
    user_set = set(user_scopes)
    required_set = set(required_scopes)
    return bool(user_set.intersection(required_set))


def check_all_permissions(user_scopes: List[str], required_scopes: List[str]) -> bool:
    """
    Check if user has all required permission scopes.
    
    Args:
        user_scopes: List of user's permission scopes
        required_scopes: List of required permission scopes
        
    Returns:
        bool: True if user has all required permissions, False otherwise
    """
    user_set = set(user_scopes)
    required_set = set(required_scopes)
    return required_set.issubset(user_set)


def require_any_permission(user_scopes: List[str], required_scopes: List[str]) -> None:
    """
    Require user to have any of the specified permission scopes.
    
    Args:
        user_scopes: List of user's permission scopes
        required_scopes: List of required permission scopes
        
    Raises:
        HTTPException: If user doesn't have any required permission
    """
    if not check_any_permission(user_scopes, required_scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required any of: {', '.join(required_scopes)}"
        )


def require_all_permissions(user_scopes: List[str], required_scopes: List[str]) -> None:
    """
    Require user to have all specified permission scopes.
    
    Args:
        user_scopes: List of user's permission scopes
        required_scopes: List of required permission scopes
        
    Raises:
        HTTPException: If user doesn't have all required permissions
    """
    if not check_all_permissions(user_scopes, required_scopes):
        missing = set(required_scopes) - set(user_scopes)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Missing permissions: {', '.join(missing)}"
        )


def parse_scope_string(scope_string: str) -> List[str]:
    """
    Parse space-separated scope string into list of scopes.
    
    Args:
        scope_string: Space-separated permission scopes
        
    Returns:
        List[str]: List of permission scopes
    """
    if not scope_string:
        return []
    return scope_string.split()


def format_scopes(scopes: List[str]) -> str:
    """
    Format list of scopes into space-separated string.
    
    Args:
        scopes: List of permission scopes
        
    Returns:
        str: Space-separated permission scopes
    """
    return " ".join(scopes)
