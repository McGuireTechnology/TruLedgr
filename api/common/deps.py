"""
Common dependency injection functions for FastAPI.

This module provides reusable dependency functions for:
- Pagination parameters
- Common utilities
"""


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = min(limit, 1000)  # Max 1000 items per page


def get_pagination_params(skip: int = 0, limit: int = 100) -> PaginationParams:
    """
    Pagination dependency.
    
    Args:
        skip: Number of items to skip (offset)
        limit: Maximum number of items to return
        
    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(skip, limit)
