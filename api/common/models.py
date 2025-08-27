"""
Common database models and mixins
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps"""
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class SoftDeleteMixin(SQLModel):
    """Mixin for soft delete functionality"""
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
