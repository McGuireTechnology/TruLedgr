"""
Password Management Submodule

This module handles password-related authentication operations including:
- Password validation and strength checking
- Password reset functionality
- Password change operations
- Secure password storage
"""

from .service import PasswordService, AccountLockedError
from .models import PasswordResetToken
from .router import router

__all__ = [
    "PasswordService",
    "AccountLockedError",
    "PasswordResetToken",
    "router"
]
