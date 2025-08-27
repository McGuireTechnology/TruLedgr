"""
Groups models for organizing users into logical collections.

This module defines the database models for groups and user-group relationships,
enabling group-based user management and permissions.
"""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from api.common.models import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from api.users.models import User


class UserGroup(SQLModel, table=True):
    """Association table for users and groups (many-to-many)."""
    __tablename__ = "user_groups"  # type: ignore
    
    user_id: str = Field(foreign_key="users.id", primary_key=True)
    group_id: str = Field(foreign_key="groups.id", primary_key=True)
    
    # Membership metadata
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    joined_by: Optional[str] = Field(default=None)  # User ID who added them
    role_in_group: Optional[str] = Field(default="member", max_length=50)  # member, admin, moderator, etc.
    is_active: bool = Field(default=True)


class Group(TimestampMixin, SoftDeleteMixin, table=True):
    """Groups table for organizing users."""
    __tablename__ = "groups"  # type: ignore
    
    # Core identifiers
    id: str = Field(primary_key=True, index=True)
    name: str = Field(unique=True, index=True, max_length=100)
    slug: str = Field(unique=True, index=True, max_length=100)  # URL-friendly name
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Group settings
    is_public: bool = Field(default=True, index=True)  # Can users see this group?
    is_open: bool = Field(default=False)  # Can users join without approval?
    is_system: bool = Field(default=False)  # System groups can't be deleted
    is_active: bool = Field(default=True, index=True)
    
    # Metadata
    member_count: int = Field(default=0, index=True)
    max_members: Optional[int] = Field(default=None)  # Optional member limit
    group_type: str = Field(default="general", max_length=50)  # general, department, project, etc.
    tags: Optional[str] = Field(default=None, max_length=500)  # Comma-separated tags
    
    # Ownership and management
    owner_id: str = Field(foreign_key="users.id")
    created_by: str = Field(foreign_key="users.id")
    
    # Additional settings
    settings: Optional[str] = Field(default=None, max_length=2000)  # JSON string for group settings
    
    # Relationships
    owner: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Group.owner_id]", "post_update": True}
    )
    creator: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Group.created_by]", "post_update": True}
    )
