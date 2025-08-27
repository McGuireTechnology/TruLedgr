"""
Common utility functions used across the application.

This module provides helper functions for ID generation, text processing,
pagination, and other common operations.
"""

import re
import math
from typing import Dict, Any
from ulid import new as ulid_new


def generate_id() -> str:
    """Generate a unique ULID string."""
    return str(ulid_new())


def create_slug(text: str) -> str:
    """
    Create a URL-friendly slug from text.
    
    Args:
        text: Input text to convert to slug
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    return slug[:50]


def calculate_pagination(
    page: int, 
    size: int, 
    total: int
) -> Dict[str, Any]:
    """
    Calculate pagination metadata.
    
    Args:
        page: Current page number (1-based)
        size: Number of items per page
        total: Total number of items
        
    Returns:
        Dictionary with pagination metadata
    """
    total_pages = math.ceil(total / size) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None
    }


def normalize_email(email: str) -> str:
    """
    Normalize email address for consistent storage and comparison.
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized email address
    """
    return email.lower().strip()


def normalize_username(username: str) -> str:
    """
    Normalize username for consistent storage and comparison.
    
    Args:
        username: Username to normalize
        
    Returns:
        Normalized username
    """
    return username.lower().strip()


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if username format is valid
    """
    # Username must be 3-30 characters, alphanumeric with underscores/hyphens
    pattern = r'^[a-zA-Z0-9_-]{3,30}$'
    return bool(re.match(pattern, username))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of result
        suffix: Suffix to add if text is truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove/replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = "file"
        
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"