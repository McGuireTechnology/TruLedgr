"""
Roles submodule for RBAC role management.
"""

from .router import router as roles_router
from .service import (
    create_role, get_role_by_id, get_role_by_name, list_roles, update_role, delete_role,
    create_permission, get_permission_by_id, get_permission_by_name, list_permissions, get_permissions_by_resource,
    assign_permission_to_role, remove_permission_from_role, get_role_permissions, get_user_permissions, user_has_permission
)

__all__ = [
    "roles_router",
    # Role functions
    "create_role", "get_role_by_id", "get_role_by_name", "list_roles", "update_role", "delete_role",
    # Permission functions  
    "create_permission", "get_permission_by_id", "get_permission_by_name", "list_permissions", "get_permissions_by_resource",
    # Role-Permission association functions
    "assign_permission_to_role", "remove_permission_from_role", "get_role_permissions", "get_user_permissions", "user_has_permission"
]