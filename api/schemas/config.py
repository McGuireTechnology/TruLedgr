"""Pydantic schemas for API configuration."""

from pydantic import BaseModel, Field
from typing import List


class AuthenticationMethod(BaseModel):
    """Authentication method information."""
    
    type: str = Field(
        ...,
        description="Authentication method type"
    )
    enabled: bool = Field(
        ...,
        description="Whether this method is enabled"
    )
    name: str = Field(
        ...,
        description="Display name for this method"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "google",
                "enabled": True,
                "name": "Google"
            }
        }
    }


class APIConfigResponse(BaseModel):
    """API configuration response."""
    
    authentication_methods: List[AuthenticationMethod] = Field(
        ...,
        description="List of available authentication methods"
    )
    password_auth_enabled: bool = Field(
        ...,
        description="Whether password authentication is enabled"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "authentication_methods": [
                    {
                        "type": "google",
                        "enabled": True,
                        "name": "Google"
                    },
                    {
                        "type": "microsoft",
                        "enabled": True,
                        "name": "Microsoft"
                    },
                    {
                        "type": "apple",
                        "enabled": False,
                        "name": "Apple"
                    }
                ],
                "password_auth_enabled": True
            }
        }
    }
