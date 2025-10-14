"""OAuth authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from datetime import datetime, timedelta

from ..schemas.oauth import (
    OAuthConnectionResponse,
    OAuthConnectionsListResponse,
    OAuthInitiateRequest,
    OAuthInitiateResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse,
)
from ..schemas.auth import ErrorResponse
from ..dependencies.database import get_uow
from ..dependencies.auth import get_current_user
from ..repositories.uow import SqlAlchemyUnitOfWork
from ..entities import User, OAuthProvider, OAuthConnection
from ..value_objects import EmailAddress
from ..config.settings import get_settings
from ..services.oauth_providers import (
    get_oauth_provider,
    OAuthProviderError
)
from ..services.oauth_state import oauth_state_manager
from ..services.jit_provisioning import create_user_from_oauth
from ..services.auth import TokenService

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["oauth-authentication"])


# NOTE: Identifier-first auth endpoint (POST /check-auth-methods) removed.
# New login flow: All auth options (password, Google, Microsoft, Apple)
# are displayed on login screen. OAuth providers use JIT provisioning.
# This endpoint may be re-added later for multi-factor authentication.


@router.get(
    "/oauth/connections",
    response_model=OAuthConnectionsListResponse,
    responses={
        200: {"description": "OAuth connections retrieved"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    },
    summary="List OAuth connections",
    description="Get list of OAuth provider connections for current user"
)
async def list_oauth_connections(
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> OAuthConnectionsListResponse:
    """List OAuth connections for current user.
    
    Args:
        current_user: Current authenticated user
        uow: Unit of Work for database operations
        
    Returns:
        List of OAuth connections
    """
    try:
        connections = await uow.oauth_connections.list_by_user(
            current_user.id
        )
        
        connection_responses = [
            OAuthConnectionResponse(
                id=conn.id,
                provider=conn.provider.value,
                provider_email=conn.provider_email,
                provider_name=conn.provider_name,
                connected_at=conn.created_at,
                last_used_at=conn.last_used_at
            )
            for conn in connections
        ]
        
        return OAuthConnectionsListResponse(
            connections=connection_responses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list OAuth connections: {str(e)}"
        )


@router.post(
    "/oauth/initiate",
    response_model=OAuthInitiateResponse,
    responses={
        200: {"description": "OAuth flow initiated"},
        400: {"model": ErrorResponse, "description": "Invalid provider"}
    },
    summary="Initiate OAuth flow",
    description="Start OAuth authentication flow for a provider"
)
async def initiate_oauth(
    request: OAuthInitiateRequest
) -> OAuthInitiateResponse:
    """Initiate OAuth authentication flow.
    
    This endpoint generates the authorization URL for the OAuth provider.
    
    Args:
        request: OAuth initiation request with provider
        
    Returns:
        Authorization URL and state parameter
        
    Raises:
        HTTPException: If provider is not supported or not configured
    """
    try:
        provider = request.provider.lower()
        
        if provider not in ["google", "microsoft", "apple"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )
        
        # Determine redirect URI
        redirect_uri = request.redirect_uri or settings.oauth_redirect_uri
        
        # Generate and store state for CSRF protection
        state = oauth_state_manager.generate_state(provider, redirect_uri)
        
        # Generate authorization URL based on provider
        if provider == "google":
            if not settings.oauth_google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth is not configured"
                )
            
            auth_url = (
                "https://accounts.google.com/o/oauth2/v2/auth"
                f"?client_id={settings.oauth_google_client_id}"
                f"&redirect_uri={redirect_uri}"
                "&response_type=code"
                "&scope=openid email profile"
                f"&state={state}"
            )
            
        elif provider == "microsoft":
            if not settings.oauth_microsoft_client_id:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Microsoft OAuth is not configured"
                )
            
            auth_url = (
                "https://login.microsoftonline.com/common/oauth2/v2.0/"
                "authorize"
                f"?client_id={settings.oauth_microsoft_client_id}"
                f"&redirect_uri={redirect_uri}"
                "&response_type=code"
                "&scope=openid email profile"
                f"&state={state}"
            )
            
        elif provider == "apple":
            if not settings.oauth_apple_client_id:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Apple OAuth is not configured"
                )
            auth_url = (
                "https://appleid.apple.com/auth/authorize"
                f"?client_id={settings.oauth_apple_client_id}"
                f"&redirect_uri={redirect_uri}"
                "&response_type=code"
                "&scope=name email"
                "&response_mode=form_post"
                f"&state={state}"
            )
        
        return OAuthInitiateResponse(
            authorization_url=auth_url,
            state=state
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}"
        )


@router.post(
    "/oauth/callback",
    response_model=OAuthCallbackResponse,
    responses={
        200: {"description": "OAuth authentication successful"},
        400: {
            "model": ErrorResponse,
            "description": "Invalid callback data"
        },
        401: {
            "model": ErrorResponse,
            "description": "OAuth authentication failed"
        }
    },
    summary="Handle OAuth callback",
    description="Complete OAuth authentication flow"
)
async def oauth_callback(
    request: OAuthCallbackRequest,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> OAuthCallbackResponse:
    """Handle OAuth provider callback.
    
    This endpoint completes the OAuth flow by exchanging the authorization
    code for user information and creating/updating the OAuth connection.
    
    JIT (Just-In-Time) Provisioning:
    - If user exists: Link OAuth connection to existing account
    - If user doesn't exist: Create new user account automatically
    - Uses email from OAuth provider as primary identifier
    - Auto-generates username from email or OAuth name
    
    Args:
        request: OAuth callback request with code and state
        uow: Unit of Work for database operations
        
    Returns:
        JWT access token and user/connection status
        
    Raises:
        HTTPException: If OAuth flow fails
    """
    try:
        # 1. Verify state (CSRF protection)
        oauth_state = oauth_state_manager.verify_state(request.state)
        if not oauth_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OAuth state"
            )
        
        provider_name = oauth_state.provider
        redirect_uri = oauth_state.redirect_uri
        
        # 2. Get OAuth provider service
        try:
            provider_service = get_oauth_provider(provider_name)
            oauth_provider = OAuthProvider(provider_name)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            ) from e
        
        # 3. Exchange authorization code for access token
        try:
            token_data = await provider_service.exchange_code_for_token(
                request.code,
                redirect_uri
            )
        except OAuthProviderError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"OAuth token exchange failed: {str(e)}"
            ) from e
        
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No access token received from OAuth provider"
            )
        
        # 4. Get user info from OAuth provider
        try:
            user_info = await provider_service.get_user_info(access_token)
        except OAuthProviderError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get user info: {str(e)}"
            ) from e
        
        provider_user_id = user_info.get("id")
        provider_email = user_info.get("email")
        provider_name_str = user_info.get("name")
        
        if not provider_user_id or not provider_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth provider did not provide required user info"
            )
        
        # 5. Look up existing user
        user = None
        is_new_user = False
        
        # First, try to find by existing OAuth connection
        existing_connection = (
            await uow.oauth_connections.get_by_provider_user_id(
                oauth_provider,
                provider_user_id
            )
        )
        
        if existing_connection:
            # User already has this OAuth connection
            user = await uow.users.get_by_id(existing_connection.user_id)
        else:
            # Try to find by email
            try:
                email_obj = EmailAddress(provider_email)
                user = await uow.users.get_by_email(email_obj)
            except ValueError:
                # Invalid email format
                pass
        
        # 6. JIT Provisioning: Create user if doesn't exist
        if not user:
            is_new_user = True
            user, generated_username = await create_user_from_oauth(
                user_info,
                uow.users
            )
            await uow.users.create(user)
        
        # 7. Create or update OAuth connection
        # Convert expires_in to int if present
        expires_in_int = int(expires_in) if expires_in else None
        
        if existing_connection:
            # Update existing connection with new tokens
            existing_connection.update_tokens(
                access_token,
                refresh_token,
                expires_in_int  # Pass as int (seconds)
            )
            await uow.oauth_connections.update(existing_connection)
        else:
            # Create new connection
            # Calculate token expiration datetime
            token_expires_at = None
            if expires_in_int:
                token_expires_at = datetime.utcnow() + timedelta(
                    seconds=expires_in_int
                )
            
            new_connection = OAuthConnection(
                id=str(uuid.uuid4()),  # Convert UUID to string
                user_id=user.id,
                provider=oauth_provider,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
                provider_name=provider_name_str,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
            )
            await uow.oauth_connections.create(new_connection)
        
        await uow.commit()
        
        # 8. Generate JWT access token for TruLedgr API
        jwt_token = TokenService.create_access_token(
            data={"sub": str(user.id.value)},
            expires_delta=timedelta(days=7)
        )
        
        # 9. Return response
        return OAuthCallbackResponse(
            access_token=jwt_token,
            token_type="bearer",
            user_id=str(user.id.value),
            username=user.username,
            email=str(user.email),
            is_new_user=is_new_user,
            provider=provider_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        ) from e


@router.delete(
    "/oauth/connections/{provider}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "OAuth connection deleted"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {
            "model": ErrorResponse,
            "description": "Connection not found"
        }
    },
    summary="Disconnect OAuth provider",
    description="Remove OAuth connection for a provider"
)
async def disconnect_oauth_provider(
    provider: str,
    current_user: User = Depends(get_current_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """Disconnect OAuth provider.
    
    Args:
        provider: OAuth provider to disconnect
        current_user: Current authenticated user
        uow: Unit of Work for database operations
        
    Returns:
        No content (204)
        
    Raises:
        HTTPException: If provider not found or invalid
    """
    try:
        # Validate provider
        try:
            oauth_provider = OAuthProvider(provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid OAuth provider: {provider}"
            )
        
        # Delete connection
        deleted = await uow.oauth_connections.delete_by_user_and_provider(
            current_user.id,
            oauth_provider
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {provider} connection found"
            )
        
        await uow.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect OAuth provider: {str(e)}"
        )
