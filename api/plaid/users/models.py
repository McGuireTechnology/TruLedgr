"""
Plaid Users Models

Pydantic models for User management operations.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class UserCreateRequest(BaseModel):
    """Request to create a user"""
    client_user_id: str = Field(..., description="Unique identifier for the user")
    consumer_report_user_identity: Optional[Dict[str, Any]] = Field(None, description="Identity verification data")

class UserCreateResponse(BaseModel):
    """Response for user creation"""
    user: Dict[str, Any]
    request_id: str

class UserGetRequest(BaseModel):
    """Request to get user information"""
    client_user_id: str = Field(..., description="Unique identifier for the user")

class UserGetResponse(BaseModel):
    """Response for user information"""
    user: Dict[str, Any]
    request_id: str

class UserUpdateRequest(BaseModel):
    """Request to update user information"""
    client_user_id: str = Field(..., description="Unique identifier for the user")
    consumer_report_user_identity: Optional[Dict[str, Any]] = Field(None, description="Updated identity data")

class UserUpdateResponse(BaseModel):
    """Response for user update"""
    user: Dict[str, Any]
    request_id: str
