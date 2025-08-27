"""
User schemas for API request/response models.

This module defines Pydantic models for user data validation
and serialization in API endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(min_length=8)
    role_id: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserRead(BaseModel):
    """Schema for reading user information."""
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    email_verified: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role_id: Optional[str] = None
    is_oauth_user: bool = False
    oauth_provider: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username


class UserPublic(BaseModel):
    """Public user schema with limited information."""
    id: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username