"""Pydantic schemas for authentication and user management."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegistrationRequest(BaseModel):
    """Request schema for user registration."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 chars, alphanumeric, _, -)"
    )
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="User password (8-72 characters)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }
    }


class LoginRequest(BaseModel):
    """Request schema for user login.
    
    Login can be performed with either username or email.
    """
    
    username: Optional[str] = Field(
        None,
        description="Username (alternative to email)"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="User email address (alternative to username)"
    )
    password: str = Field(..., description="User password")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!"
                },
                {
                    "username": "johndoe",
                    "password": "SecurePassword123!"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Response schema for authentication token."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class UserResponse(BaseModel):
    """Response schema for user data."""
    
    id: str = Field(..., description="User ID (UUID)")
    username: str = Field(..., description="Username (public profile name)")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether user is active")
    is_admin: bool = Field(
        default=False,
        description="Whether user has admin privileges"
    )
    created_at: datetime = Field(..., description="Account creation time")
    last_login: Optional[datetime] = Field(
        None,
        description="Last login time"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "user@example.com",
                "is_active": True,
                "is_admin": False,
                "created_at": "2025-10-12T10:00:00Z",
                "last_login": "2025-10-12T15:30:00Z"
            }
        }
    }


class UserUpdateRequest(BaseModel):
    """Request schema for updating user (PUT - full update)."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 chars, alphanumeric, _, -)"
    )
    email: EmailStr = Field(..., description="User email address")
    is_active: bool = Field(True, description="Whether user is active")
    is_admin: bool = Field(
        False,
        description="Whether user has admin privileges"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe_updated",
                "email": "updated@example.com",
                "is_active": True,
                "is_admin": False
            }
        }
    }


class UserPartialUpdateRequest(BaseModel):
    """Request schema for partially updating user (PATCH)."""
    
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 chars, alphanumeric, _, -)"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="User email address"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether user is active"
    )
    is_admin: Optional[bool] = Field(
        None,
        description="Whether user has admin privileges"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe_new"
            }
        }
    }


class UserListResponse(BaseModel):
    """Response schema for list of users."""
    
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of items per page")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "johndoe",
                        "email": "user@example.com",
                        "is_active": True,
                        "is_admin": False,
                        "created_at": "2025-10-12T10:00:00Z",
                        "last_login": "2025-10-12T15:30:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
        }
    }


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    
    detail: str = Field(..., description="Error message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Invalid credentials"
            }
        }
    }
