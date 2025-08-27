"""
Groups schemas for API request/response models.

This module defines the Pydantic schemas for group-related API operations,
including request validation and response serialization.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re


class GroupBase(BaseModel):
    """Base group schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    description: Optional[str] = Field(None, max_length=1000, description="Group description")
    is_public: bool = Field(True, description="Whether the group is publicly visible")
    is_open: bool = Field(False, description="Whether users can join without approval")
    group_type: str = Field("general", max_length=50, description="Type of group")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    max_members: Optional[int] = Field(None, ge=1, description="Maximum number of members")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate group name."""
        if not v or not v.strip():
            raise ValueError('Group name cannot be empty')
        
        # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Group name can only contain letters, numbers, spaces, hyphens, and underscores')
        
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if not v:
            return v
        
        # Split, clean, and rejoin tags
        tags = [tag.strip() for tag in v.split(',') if tag.strip()]
        return ','.join(tags) if tags else None


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    pass


class GroupUpdate(BaseModel):
    """Schema for updating a group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: Optional[bool] = None
    is_open: Optional[bool] = None
    group_type: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = Field(None, max_length=500)
    max_members: Optional[int] = Field(None, ge=1)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate group name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Group name cannot be empty')
            
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
                raise ValueError('Group name can only contain letters, numbers, spaces, hyphens, and underscores')
            
            return v.strip()
        return v


class UserInGroup(BaseModel):
    """Schema for user information within a group context."""
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_in_group: Optional[str] = "member"
    joined_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class GroupMembershipInfo(BaseModel):
    """Schema for group membership information."""
    user_id: str
    group_id: str
    role_in_group: str = "member"
    joined_at: datetime
    joined_by: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True


class Group(GroupBase):
    """Full group schema for responses."""
    id: str
    slug: str
    is_system: bool = False
    is_active: bool = True
    member_count: int = 0
    owner_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GroupWithMembers(Group):
    """Group schema with member information."""
    members: List[UserInGroup] = []


class GroupWithSettings(Group):
    """Group schema with parsed settings."""
    settings: Optional[Dict[str, Any]] = None


class GroupMembershipRequest(BaseModel):
    """Schema for group membership requests."""
    user_ids: List[str] = Field(..., min_items=1, description="List of user IDs to add to group")
    role_in_group: str = Field("member", description="Role to assign to users in the group")
    
    @validator('role_in_group')
    def validate_role(cls, v):
        """Validate role in group."""
        allowed_roles = ['member', 'admin', 'moderator', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class GroupMembershipUpdate(BaseModel):
    """Schema for updating group membership."""
    role_in_group: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role_in_group')
    def validate_role(cls, v):
        """Validate role in group."""
        if v is not None:
            allowed_roles = ['member', 'admin', 'moderator', 'viewer']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class GroupStats(BaseModel):
    """Schema for group statistics."""
    total_groups: int
    active_groups: int
    public_groups: int
    private_groups: int
    open_groups: int
    total_memberships: int
    average_group_size: float
    largest_group_size: int


class GroupListResponse(BaseModel):
    """Schema for paginated group list response."""
    groups: List[Group]
    total: int
    page: int
    size: int
    pages: int
