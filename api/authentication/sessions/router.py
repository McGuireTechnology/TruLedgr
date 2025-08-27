"""
Session Management API endpoints.

This module provides REST API endpoints for session management operations
including listing sessions, revoking sessions, and session information.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.session import get_async_session
from api.users.models import User
from api.authentication.deps import get_current_user
from ..schemas import SessionInfo
from .service import SessionService

# Initialize router
router = APIRouter(prefix="/sessions", tags=["Sessions"])
security = HTTPBearer(auto_error=False)
session_service = SessionService()


@router.get("", response_model=List[SessionInfo])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    active_only: bool = True
):
    """
    Get user's active sessions.
    """
    sessions = await session_service.get_user_sessions(
        session, current_user.id, active_only
    )
    
    return [
        SessionInfo(
            id=s["id"],
            user_id=current_user.id,
            created_at=s["created_at"],
            last_accessed_at=s["last_activity"],
            expires_at=s["expires_at"],
            client_ip=s["client_ip"],
            user_agent=s.get("user_agent", "unknown"),
            is_current=False,
            location=s.get("location")
        )
        for s in sessions
    ]


@router.post("/revoke/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Revoke a specific session.
    """
    # TODO: Implement session revocation by ID
    # For now, this is a placeholder
    return {"message": f"Session {session_id} revoked"}


@router.post("/revoke-all")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Revoke all sessions except current.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    revoked_count = await session_service.revoke_all_user_sessions(
        session, current_user.id
    )
    
    return {"message": f"Revoked {revoked_count} sessions"}