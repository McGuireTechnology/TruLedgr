"""
Authorization models for Role-Based Access Control (RBAC).

This module defines the database models for roles, permissions,
and their associations for implementing RBAC in the application.
"""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from api.common.models import TimestampMixin

if TYPE_CHECKING:
    from api.users.models import User


class RolePermission(SQLModel, table=True):
    """Association table for roles and permissions (many-to-many)."""
    __tablename__ = "role_permissions" # type: ignore
    
    role_id: str = Field(foreign_key="roles.id", primary_key=True)
    permission_id: str = Field(foreign_key="permissions.id", primary_key=True)
    
    # Optional metadata about the assignment
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_by: Optional[str] = Field(default=None)  # User ID who assigned


class Role(TimestampMixin, table=True):
    """Roles table for RBAC system."""
    __tablename__ = "roles" # type: ignore
    
    id: str = Field(primary_key=True, index=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_system: bool = Field(default=False)  # System roles can't be deleted
    is_active: bool = Field(default=True, index=True)
    
    # Relationships
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission
    )
    users: List["User"] = Relationship(back_populates="role")


class Permission(TimestampMixin, table=True):
    """Permissions table for RBAC system."""
    __tablename__ = "permissions" # type: ignore
    
    id: str = Field(primary_key=True, index=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    resource: str = Field(max_length=50, index=True)  # e.g., "users", "groups"
    action: str = Field(max_length=50, index=True)    # e.g., "create", "read"
    is_system: bool = Field(default=False)  # System permissions can't be deleted
    
    # Relationships
    roles: List[Role] = Relationship(
        back_populates="permissions",
        link_model=RolePermission
    )
