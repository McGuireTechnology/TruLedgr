"""Pydantic schemas for OAuth authentication."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# NOTE: AuthMethodsRequest/Response schemas removed.
# New flow: All auth options shown upfront on login screen.
# No need to enumerate available auth methods per user.
# May be re-added later for multi-factor authentication.


class OAuthConnectionResponse(BaseModel):
    """Response schema for OAuth connection data."""
    
    id: str = Field(..., description="Connection ID")
    provider: str = Field(..., description="OAuth provider name")
    provider_email: Optional[str] = Field(
        None,
        description="Email from OAuth provider"
    )
    provider_name: Optional[str] = Field(
        None,
        description="Name from OAuth provider"
    )
    connected_at: datetime = Field(
        ...,
        description="When connection was created"
    )
    last_used_at: Optional[datetime] = Field(
        None,
        description="When connection was last used"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "provider": "google",
                "provider_email": "user@gmail.com",
                "provider_name": "John Doe",
                "connected_at": "2025-10-12T10:00:00Z",
                "last_used_at": "2025-10-13T15:30:00Z"
            }
        }
    }


class OAuthConnectionsListResponse(BaseModel):
    """Response schema for list of OAuth connections."""
    
    connections: list[OAuthConnectionResponse] = Field(
        ...,
        description="List of OAuth connections"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "connections": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "provider": "google",
                        "provider_email": "user@gmail.com",
                        "provider_name": "John Doe",
                        "connected_at": "2025-10-12T10:00:00Z",
                        "last_used_at": "2025-10-13T15:30:00Z"
                    }
                ]
            }
        }
    }


class OAuthInitiateRequest(BaseModel):
    """Request schema for initiating OAuth flow."""
    
    provider: str = Field(
        ...,
        description="OAuth provider (google, microsoft, apple)"
    )
    redirect_uri: Optional[str] = Field(
        None,
        description="Optional custom redirect URI"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "google",
                "redirect_uri": "https://app.truledgr.com/auth/callback"
            }
        }
    }


class OAuthInitiateResponse(BaseModel):
    """Response schema for OAuth initiation."""
    
    authorization_url: str = Field(
        ...,
        description="URL to redirect user to for OAuth authorization"
    )
    state: str = Field(
        ...,
        description="State parameter for OAuth flow security"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "authorization_url": (
                    "https://accounts.google.com/o/oauth2/v2/auth?..."
                ),
                "state": "random-state-string"
            }
        }
    }


class OAuthCallbackRequest(BaseModel):
    """Request schema for OAuth callback."""
    
    provider: str = Field(
        ...,
        description="OAuth provider (google, microsoft, apple)"
    )
    code: str = Field(
        ...,
        description="Authorization code from OAuth provider"
    )
    state: str = Field(
        ...,
        description="State parameter for verification"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "google",
                "code": "4/0AX4XfWh...",
                "state": "random-state-string"
            }
        }
    }


class OAuthCallbackResponse(BaseModel):
    """Response schema for OAuth callback completion."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    is_new_user: bool = Field(
        ...,
        description="Whether this is a newly created user"
    )
    oauth_connection_created: bool = Field(
        ...,
        description="Whether a new OAuth connection was created"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "is_new_user": False,
                "oauth_connection_created": True
            }
        }
    }
