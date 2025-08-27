"""
Authorization utilities.

This package provides authorization-related utilities:
- scopes: Permission scopes and scope management
"""

from .scopes import (
    Scopes,
    ScopeGroup,
    check_permission,
    require_permission,
    check_any_permission,
    check_all_permissions,
    require_any_permission,
    require_all_permissions,
    parse_scope_string,
    format_scopes
)

__all__ = [
    "Scopes",
    "ScopeGroup",
    "check_permission",
    "require_permission",
    "check_any_permission",
    "check_all_permissions",
    "require_any_permission",
    "require_all_permissions",
    "parse_scope_string",
    "format_scopes"
]
