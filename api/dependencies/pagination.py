"""Pagination dependencies."""

from typing import Optional
from fastapi import Query


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
        order_by: Optional[str] = Query(None, description="Field to order by"),
        order_desc: bool = Query(False, description="Order descending")
    ):
        self.skip = skip
        self.limit = limit
        self.order_by = order_by
        self.order_desc = order_desc


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
) -> dict:
    """
    Simple pagination parameters.
    
    Usage:
        @router.get("/items")
        async def get_items(pagination: dict = Depends(get_pagination_params)):
            skip = pagination["skip"]
            limit = pagination["limit"]
            ...
    """
    return {"skip": skip, "limit": limit}
