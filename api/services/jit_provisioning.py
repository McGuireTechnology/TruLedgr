"""JIT (Just-In-Time) user provisioning service."""

import uuid
import re
from typing import Tuple

from ..entities import User
from ..value_objects import UserId, EmailAddress


def sanitize_username(text: str) -> str:
    """Sanitize text for use as username.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized username (alphanumeric, underscore, hyphen only)
    """
    # Remove non-alphanumeric characters (except underscore and hyphen)
    sanitized = re.sub(r'[^\w\-]', '', text.lower())
    # Remove leading/trailing hyphens and underscores
    sanitized = sanitized.strip('-_')
    return sanitized


def generate_username_from_email(email: str) -> str:
    """Generate username from email address.
    
    Args:
        email: Email address
        
    Returns:
        Username derived from email local part
    """
    # Get local part of email (before @)
    local_part = email.split('@')[0]
    
    # Sanitize
    username = sanitize_username(local_part)
    
    # Ensure minimum length
    if len(username) < 3:
        username = username + str(uuid.uuid4())[:8]
    
    # Ensure maximum length
    if len(username) > 50:
        username = username[:50]
    
    return username


def generate_username_from_name(name: str, email: str) -> str:
    """Generate username from full name.
    
    Args:
        name: Full name from OAuth provider
        email: Email address (used as fallback)
        
    Returns:
        Username derived from name or email
    """
    if not name or len(name.strip()) < 3:
        # Fall back to email-based username
        return generate_username_from_email(email)
    
    # Sanitize name
    username = sanitize_username(name)
    
    # Ensure minimum length
    if len(username) < 3:
        username = generate_username_from_email(email)
    
    # Ensure maximum length
    if len(username) > 50:
        username = username[:50]
    
    return username


async def ensure_unique_username(
    username: str,
    user_repository,
    max_attempts: int = 10
) -> str:
    """Ensure username is unique by appending numbers if needed.
    
    Args:
        username: Desired username
        user_repository: User repository to check existence
        max_attempts: Maximum number of attempts to find unique username
        
    Returns:
        Unique username
        
    Raises:
        ValueError: If unable to generate unique username
    """
    base_username = username
    
    for attempt in range(max_attempts):
        # Check if username exists
        existing = await user_repository.exists_by_username(username)
        
        if not existing:
            return username
        
        # Try with number suffix
        suffix = str(attempt + 1)
        # Ensure total length doesn't exceed 50 chars
        max_base_len = 50 - len(suffix)
        username = base_username[:max_base_len] + suffix
    
    # If all attempts failed, use UUID suffix
    uuid_suffix = str(uuid.uuid4())[:8]
    max_base_len = 50 - len(uuid_suffix)
    return base_username[:max_base_len] + uuid_suffix


async def create_user_from_oauth(
    oauth_user_info: dict,
    user_repository
) -> Tuple[User, str]:
    """Create new user from OAuth provider information.
    
    JIT (Just-In-Time) provisioning: Automatically creates user account
    when signing in with OAuth for the first time.
    
    Args:
        oauth_user_info: User info from OAuth provider
        user_repository: User repository for database operations
        
    Returns:
        Tuple of (User entity, generated username)
        
    Raises:
        ValueError: If email is missing or invalid
    """
    # Extract user info
    email = oauth_user_info.get("email")
    if not email:
        raise ValueError("OAuth provider did not provide email address")
    
    name = oauth_user_info.get("name", "")
    
    # Generate username
    if name:
        base_username = generate_username_from_name(name, email)
    else:
        base_username = generate_username_from_email(email)
    
    # Ensure username is unique
    unique_username = await ensure_unique_username(
        base_username,
        user_repository
    )
    
    # Create user entity
    user = User(
        id=UserId(uuid.uuid4()),
        username=unique_username,
        email=EmailAddress(email),
        hashed_password="",  # OAuth-only account, no password
        is_active=True,
        is_admin=False,
    )
    
    return user, unique_username
