"""
Plaid Sandbox Router

FastAPI endpoints for Sandbox testing and simulation operations.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
import logging

from .models import (
    SandboxPublicTokenCreateRequest,
    SandboxItemFireWebhookRequest,
    SandboxItemSetVerificationStatusRequest,
    SandboxItemResetLoginRequest,
    SandboxTransactionsRefreshRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sandbox")

@router.post("/create-public-token")
async def create_public_token(
    request: SandboxPublicTokenCreateRequest
) -> Dict[str, Any]:
    """
    Create a public token for testing in sandbox environment.
    
    This endpoint allows you to create test data and simulate different
    bank scenarios for development and testing purposes.
    """
    try:
        # This will be implemented when we integrate with the main service
        return {
            "message": "Sandbox public token creation endpoint - to be integrated with main Plaid service",
            "institution_id": request.institution_id,
            "initial_products": request.initial_products,
            "options": request.options
        }
        
    except Exception as e:
        logger.error(f"Error creating sandbox public token: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/fire-webhook")
async def fire_webhook(
    request: SandboxItemFireWebhookRequest
) -> Dict[str, Any]:
    """
    Trigger a webhook for testing in sandbox environment.
    
    Useful for testing webhook handling and processing logic.
    """
    try:
        # This will be implemented when we integrate with the main service
        return {
            "message": "Sandbox webhook firing endpoint - to be integrated with main Plaid service",
            "access_token": request.access_token[:10] + "...",  # Truncated for security
            "webhook_code": request.webhook_code
        }
        
    except Exception as e:
        logger.error(f"Error firing sandbox webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/set-verification-status")
async def set_verification_status(
    request: SandboxItemSetVerificationStatusRequest
) -> Dict[str, Any]:
    """
    Set verification status for an account in sandbox.
    
    Allows testing different account verification scenarios.
    """
    try:
        # This will be implemented when we integrate with the main service
        return {
            "message": "Sandbox verification status endpoint - to be integrated with main Plaid service",
            "access_token": request.access_token[:10] + "...",  # Truncated for security
            "account_id": request.account_id,
            "verification_status": request.verification_status
        }
        
    except Exception as e:
        logger.error(f"Error setting sandbox verification status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-login")
async def reset_login(
    request: SandboxItemResetLoginRequest
) -> Dict[str, Any]:
    """
    Reset login for an item to trigger authentication errors.
    
    Useful for testing error handling and re-authentication flows.
    """
    try:
        # This will be implemented when we integrate with the main service
        return {
            "message": "Sandbox reset login endpoint - to be integrated with main Plaid service",
            "access_token": request.access_token[:10] + "...",  # Truncated for security
            "reset_triggered": True
        }
        
    except Exception as e:
        logger.error(f"Error resetting sandbox login: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
