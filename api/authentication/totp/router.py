"""
TOTP/2FA API endpoints.

This module provides REST API endpoints for TOTP (Time-based One-Time Password)
two-factor authentication operations including setup, verification, and management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.session import get_async_session
from api.users.models import User
from api.authentication.deps import get_current_user
from ..schemas import (
    TOTPSetupResponse,
    TOTPVerifyRequest,
    TOTPDisableRequest
)
from .service import TOTPService

# Initialize router
router = APIRouter(prefix="/totp", tags=["TOTP"])
totp_service = TOTPService()


@router.post("/setup", response_model=TOTPSetupResponse)
async def setup_totp(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Setup TOTP two-factor authentication.
    """
    result = await totp_service.setup_totp(session, current_user)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return TOTPSetupResponse(
        secret=result["secret"],
        qr_uri=result.get("qr_setup_url", ""),
        backup_codes=result["backup_codes"]
    )


@router.post("/verify")
async def verify_totp_setup(
    verify_data: TOTPVerifyRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Verify TOTP setup and enable 2FA.
    """
    result = await totp_service.verify_and_enable_totp(
        session, current_user, verify_data.code
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": result["message"]}


@router.post("/disable")
async def disable_totp(
    disable_data: TOTPDisableRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Disable TOTP two-factor authentication.
    """
    result = await totp_service.disable_totp(
        session, current_user, disable_data.totp_code
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": result["message"]}


@router.get("/status")
async def get_totp_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get TOTP status for current user.
    """
    backup_codes_count = 0
    if current_user.backup_codes:
        try:
            import json
            codes = json.loads(current_user.backup_codes)
            backup_codes_count = len([code for code in codes if not code.get('used', False)])
        except:
            backup_codes_count = 0
    
    return {
        "enabled": current_user.totp_enabled,
        "setup_required": not current_user.totp_enabled and not current_user.totp_secret,
        "backup_codes_remaining": backup_codes_count
    }