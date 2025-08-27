"""
Authorization module for Role-Based Access Control (RBAC).

This module provides role and permission management including:
- models: Role, Permission, and association models
- service: RBAC business logic and database operations
- policy: Permission enforcement decorators and dependencies
- router: Admin endpoints for managing roles and permissions
"""

from .models import Role, Permission, RolePermission
from .service import (
    get_user_permissions,
    check_user_permission,
    assign_role_to_user,
    remove_role_from_user
)
from .policy import require_permission, require_role, PermissionDependency

__all__ = [
    "Role",
    "Permission", 
    "RolePermission",
    "get_user_permissions",
    "check_user_permission",
    "assign_role_to_user",
    "remove_role_from_user",
    "require_permission",
    "require_role",
    "PermissionDependency"
]
