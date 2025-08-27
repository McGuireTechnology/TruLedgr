"""
Password hashing and verification utilities.

This module provides secure password hashing using BCrypt
and password verification functionality.
"""

from passlib.context import CryptContext
from typing import Optional

# BCrypt password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password using BCrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: BCrypt hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: BCrypt hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Check if a password meets strength requirements.
    
    Args:
        password: Password to check
        
    Returns:
        tuple: (is_strong, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one number")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one special character")
    
    return len(issues) == 0, issues


def generate_password_reset_token() -> str:
    """
    Generate a secure random token for password reset.
    
    Returns:
        str: Random password reset token
    """
    import secrets
    return secrets.token_urlsafe(32)
