"""
Users module for user management.

This module provides user CRUD operations separate from authentication:
- User creation, reading, updating, deletion
- User profile management
- User search and listing
- User preferences and settings
"""

from .models import User
from .schemas import UserCreate, UserRead, UserUpdate, UserPublic

# Import service functions lazily to avoid circular imports
def get_user_service():
    from .service import (
        get_user_by_id, 
        create_user_with_validation,
        update_user_with_validation,
        soft_delete_user_account
    )
    return {
        "get_user_by_id": get_user_by_id,
        "create_user_with_validation": create_user_with_validation,
        "update_user_with_validation": update_user_with_validation,
        "soft_delete_user_account": soft_delete_user_account
    }

__all__ = [
    "User",
    "UserCreate",
    "UserRead", 
    "UserUpdate",
    "UserPublic",
    "get_user_service"
]
