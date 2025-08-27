"""
OAuth2 Authentication API endpoints.

This module provides REST API endpoints for OAuth2 social login operations
including authorization, callbacks, account linking, and provider management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.session import get_async_session
from api.users.models import User
from api.authentication.deps import get_current_user
from ..schemas import (
    OAuth2CallbackRequest,
    OAuth2LinkRequest
)
from .service import OAuth2Service

# Initialize router
router = APIRouter(prefix="/oauth2", tags=["OAuth2"])
oauth2_service = OAuth2Service()


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection
    if request.client:
        return request.client.host
    
    return "unknown"


def _get_user_agent(request: Request) -> str:
    """Extract user agent from request."""
    return request.headers.get("User-Agent", "unknown")


@router.get("/authorize/{provider}")
async def oauth2_authorize(
    provider: str,
    state: Optional[str] = None
):
    """
    Get OAuth2 authorization URL for provider.
    """
    result = oauth2_service.get_authorization_url(provider, state)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "authorization_url": result["authorization_url"],
        "state": result["state"],
        "provider": result["provider"]
    }


@router.post("/callback/{provider}")
async def oauth2_callback(
    provider: str,
    callback_data: OAuth2CallbackRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Handle OAuth2 callback and authenticate user.
    """
    client_ip = _get_client_ip(request)
    user_agent = _get_user_agent(request)
    
    # Exchange code for token
    token_result = await oauth2_service.exchange_code_for_token(
        provider, callback_data.code, callback_data.state
    )
    
    if "error" in token_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=token_result["error"]
        )
    
    # Get user info from provider
    user_info = await oauth2_service.get_user_info(
        provider, token_result["access_token"]
    )
    
    if "error" in user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user_info["error"]
        )
    
    # TODO: Implement user lookup/creation logic
    # For now, return the user info
    return {
        "success": True,
        "provider": provider,
        "user_info": user_info,
        "token_info": token_result
    }


@router.get("/accounts")
async def get_oauth_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get user's linked OAuth accounts.
    """
    accounts = await oauth2_service.get_user_oauth_accounts(session, current_user)
    return {"accounts": accounts}


@router.post("/link/{provider}")
async def link_oauth_account(
    provider: str,
    link_data: OAuth2LinkRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Link OAuth account to current user.
    """
    # TODO: Implement OAuth account linking
    return {"message": f"OAuth account linking for {provider} not yet implemented"}


@router.delete("/unlink/{provider}")
async def unlink_oauth_account(
    provider: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Unlink OAuth account from current user.
    """
    result = await oauth2_service.unlink_oauth_account(
        session, current_user, provider
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": result["message"]}


@router.get("/providers")
async def get_oauth_providers():
    """
    Get list of available OAuth2 providers.
    """
    providers = oauth2_service.get_available_providers()
    return {"providers": providers}