"""API configuration routes."""

from fastapi import APIRouter

from ..schemas.config import APIConfigResponse, AuthenticationMethod
from ..config.settings import get_settings

settings = get_settings()

router = APIRouter(tags=["configuration"])


@router.get(
    "/config",
    response_model=APIConfigResponse,
    summary="Get API configuration",
    description=(
        "Returns API configuration information including available "
        "authentication methods. Frontend can use this to show/hide "
        "login options based on what's configured."
    )
)
async def get_api_config() -> APIConfigResponse:
    """Get API configuration.
    
    Returns information about the API's configuration, including:
    - Available authentication methods (OAuth providers)
    - Whether each authentication method is enabled/configured
    - Password authentication status
    
    Frontend applications should call this endpoint on startup to
    determine which authentication options to display to users.
    
    Returns:
        API configuration with authentication methods
    """
    # Check which OAuth providers are configured
    google_enabled = bool(
        settings.oauth_google_client_id and
        settings.oauth_google_client_secret
    )
    
    microsoft_enabled = bool(
        settings.oauth_microsoft_client_id and
        settings.oauth_microsoft_client_secret
    )
    
    apple_enabled = bool(
        settings.oauth_apple_client_id and
        settings.oauth_apple_client_secret
    )
    
    # Build authentication methods list
    auth_methods = [
        AuthenticationMethod(
            type="google",
            enabled=google_enabled,
            name="Google"
        ),
        AuthenticationMethod(
            type="microsoft",
            enabled=microsoft_enabled,
            name="Microsoft"
        ),
        AuthenticationMethod(
            type="apple",
            enabled=apple_enabled,
            name="Apple"
        ),
    ]
    
    # Password authentication is always enabled
    password_auth_enabled = True
    
    return APIConfigResponse(
        authentication_methods=auth_methods,
        password_auth_enabled=password_auth_enabled
    )
