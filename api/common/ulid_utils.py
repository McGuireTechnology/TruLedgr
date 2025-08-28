"""
ULID utilities for database models

Provides Field definitions for ULID-based primary and foreign keys
compatible with SQLModel and the existing TruLedgr architecture.
"""

from typing import Any
from sqlmodel import Field
from api.common.utils import generate_id


def ULIDPrimaryKey(**kwargs) -> Any:
    """
    Create a ULID primary key field.
    
    Returns:
        Field: SQLModel field configured for ULID primary key
    """
    return Field(
        default_factory=generate_id,
        primary_key=True,
        index=True,
        max_length=26,  # ULID length
        **kwargs
    )


def ULIDForeignKey(foreign_key: str, **kwargs) -> Any:
    """
    Create a ULID foreign key field.
    
    Args:
        foreign_key: The foreign key reference (e.g., "users.id")
        **kwargs: Additional Field parameters
        
    Returns:
        Field: SQLModel field configured for ULID foreign key
    """
    return Field(
        foreign_key=foreign_key,
        index=True,
        max_length=26,  # ULID length
        **kwargs
    )


def ULIDField(**kwargs) -> Any:
    """
    Create a regular ULID field (not primary or foreign key).
    
    Returns:
        Field: SQLModel field configured for ULID storage
    """
    return Field(
        max_length=26,  # ULID length
        index=True,
        **kwargs
    )
