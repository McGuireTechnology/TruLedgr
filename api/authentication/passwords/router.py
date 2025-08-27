"""
Password Management API endpoints.

This module provides REST API endpoints for password-related operations
including password reset requests, confirmations, and password changes.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.session import get_async_session
from api.users.models import User
from api.authentication.deps import get_current_user
from ..schemas import (
    PasswordResetRequest,
    PasswordResetConfirm, 
    PasswordChangeRequest
)
from .service import PasswordService, AccountLockedError

# Initialize router
router = APIRouter(prefix="/password", tags=["Password"])
password_service = PasswordService()


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


@router.post("/reset/request")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Initiate password reset process.
    """
    client_ip = _get_client_ip(request)
    
    result = await password_service.request_password_reset(
        session, reset_data.email, client_ip, "unknown"
    )
    
    # Always return success for security (don't reveal if email exists)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Complete password reset with token and new password.
    """
    client_ip = _get_client_ip(request)
    
    result = await password_service.confirm_password_reset(
        session, reset_data.token, reset_data.new_password
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": result["message"]}


@router.post("/change")
async def change_password(
    change_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Change user password.
    """
    success = await password_service.change_password(
        session, current_user, change_data.current_password, change_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Current password may be incorrect."
        )
    
    return {"message": "Password changed successfully"}


@router.get("/lockout/status/{username}")
async def get_lockout_status(
    username: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get account lockout status for a username.
    """
    status_info = await password_service.get_lockout_status(session, username)
    return status_info


@router.post("/lockout/clear/{username}")
async def clear_lockout_attempts(
    username: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Clear failed attempts for a user (admin only).
    """
    # TODO: Add admin permission check
    await password_service.clear_failed_attempts(session, username)
    return {"message": f"Failed attempts cleared for {username}"}


@router.post("/lockout/cleanup")
async def cleanup_expired_lockouts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Clean up expired lockouts (admin only).
    """
    # TODO: Add admin permission check
    cleaned_count = await password_service.cleanup_expired_lockouts(session)
    return {"message": f"Cleaned up {cleaned_count} expired lockouts"}