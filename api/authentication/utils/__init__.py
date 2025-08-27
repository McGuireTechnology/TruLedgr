"""
Authentication utilities.

This package provides authentication-related utilities:
- password: Password hashing, verification, and strength checking
- jwt: JWT token creation, validation, and management
"""

from .password import get_password_hash, verify_password, is_password_strong, generate_password_reset_token
from .jwt import (
    create_access_token, 
    decode_access_token, 
    create_refresh_token, 
    decode_refresh_token,
    create_token_response,
    Token,
    TokenData,
    get_token_expiry,
    is_token_expired
)

__all__ = [
    # Password utilities
    "get_password_hash",
    "verify_password",
    "is_password_strong",
    "generate_password_reset_token",
    
    # JWT utilities
    "create_access_token",
    "decode_access_token",
    "create_refresh_token",
    "decode_refresh_token",
    "create_token_response",
    "Token",
    "TokenData",
    "get_token_expiry",
    "is_token_expired"
]
