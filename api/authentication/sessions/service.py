"""
Session Service

This module provides session management functionality for user authentication and tracking.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, or_, desc, asc

from api.users.models import User, UserSession, SessionActivity
from api.settings import get_settings

settings = get_settings()


class SessionService:
    """
    Service for session management operations.
    
    Provides session functionality including:
    - Session creation and validation
    - Session lifecycle management
    - Activity tracking
    - Security monitoring
    """
    
    def __init__(self):
        self.session_duration = getattr(settings, 'session_duration_hours', 24)
        self.max_sessions_per_user = getattr(settings, 'max_sessions_per_user', 5)
        self.activity_tracking = getattr(settings, 'session_activity_tracking', True)
    
    async def create_session(
        self,
        session: AsyncSession,
        user: User,
        client_ip: str,
        user_agent: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        location: Optional[str] = None,
        login_method: str = "password"
    ) -> Dict[str, Any]:
        """
        Create a new user session.
        
        Args:
            session: Database session
            user: User creating session
            client_ip: Client IP address
            user_agent: User agent string
            device_fingerprint: Device fingerprint
            location: Geographic location
            login_method: Login method used
            
        Returns:
            Dictionary with session data
        """
        # Clean up expired sessions first
        await self._cleanup_expired_sessions(session, user.id)
        
        # Check session limits
        active_sessions = await self._get_active_sessions_count(session, user.id)
        if active_sessions >= self.max_sessions_per_user:
            # Remove oldest session
            await self._remove_oldest_session(session, user.id)
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        session_token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        
        # Create session record
        user_session = UserSession(
            id=secrets.token_urlsafe(16),
            user_id=user.id,
            session_token_hash=session_token_hash,
            client_ip=client_ip,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            location=location,
            login_method=login_method,
            expires_at=datetime.utcnow() + timedelta(hours=self.session_duration),
            is_active=True,
            last_activity=datetime.utcnow()
        )
        
        session.add(user_session)
        
        # Update user last login
        user.last_login = datetime.utcnow()
        
        await session.commit()
        await session.refresh(user_session)
        
        # Track session creation activity
        if self.activity_tracking:
            await self._track_activity(
                session,
                user_session.id,
                user.id,
                "session_created",
                client_ip,
                user_agent
            )
        
        return {
            "session_id": user_session.id,
            "session_token": session_token,
            "expires_at": user_session.expires_at,
            "login_method": login_method
        }
    
    async def validate_session(
        self,
        session: AsyncSession,
        session_token: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[User]:
        """
        Validate a session token and return the user.
        
        Args:
            session: Database session
            session_token: Session token to validate
            client_ip: Client IP address
            user_agent: User agent string
            
        Returns:
            User if session is valid, None otherwise
        """
        # Hash the token
        session_token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        
        # Find active session
        stmt = select(UserSession).where(
            and_(
                UserSession.session_token_hash == session_token_hash,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        
        result = await session.execute(stmt)
        user_session = result.scalar_one_or_none()
        
        if not user_session:
            return None
        
        # Get user
        user = await session.get(User, user_session.user_id)
        if not user or not user.is_active:
            return None
        
        # Update session activity
        user_session.last_activity = datetime.utcnow()
        user_session.request_count += 1
        
        # Check for suspicious activity (basic checks)
        if client_ip and user_session.client_ip != client_ip:
            user_session.suspicious_activity = True
        
        await session.commit()
        
        # Track session activity
        if self.activity_tracking:
            await self._track_activity(
                session,
                user_session.id,
                user.id,
                "session_validated",
                client_ip or user_session.client_ip,
                user_agent
            )
        
        return user
    
    async def revoke_session(
        self,
        session: AsyncSession,
        session_token: str,
        revocation_reason: str = "user_logout"
    ) -> bool:
        """
        Revoke a specific session.
        
        Args:
            session: Database session
            session_token: Session token to revoke
            revocation_reason: Reason for revocation
            
        Returns:
            True if session was revoked, False otherwise
        """
        # Hash the token
        session_token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        
        # Find session
        stmt = select(UserSession).where(
            UserSession.session_token_hash == session_token_hash
        )
        
        result = await session.execute(stmt)
        user_session = result.scalar_one_or_none()
        
        if not user_session:
            return False
        
        # Revoke session
        user_session.is_active = False
        user_session.revoked_at = datetime.utcnow()
        user_session.revocation_reason = revocation_reason
        
        await session.commit()
        
        # Track revocation activity
        if self.activity_tracking:
            await self._track_activity(
                session,
                user_session.id,
                user_session.user_id,
                "session_revoked",
                user_session.client_ip,
                None,
                extra_data={"reason": revocation_reason}
            )
        
        return True
    
    async def revoke_all_user_sessions(
        self,
        session: AsyncSession,
        user_id: str,
        except_session_id: Optional[str] = None,
        revocation_reason: str = "revoke_all"
    ) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            session: Database session
            user_id: User ID
            except_session_id: Session ID to exclude from revocation
            revocation_reason: Reason for revocation
            
        Returns:
            Number of sessions revoked
        """
        # Build query
        conditions = [
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ]
        
        if except_session_id:
            conditions.append(UserSession.id != except_session_id)
        
        stmt = select(UserSession).where(and_(*conditions))
        result = await session.execute(stmt)
        sessions_to_revoke = result.scalars().all()
        
        # Revoke sessions
        revoked_count = 0
        for user_session in sessions_to_revoke:
            user_session.is_active = False
            user_session.revoked_at = datetime.utcnow()
            user_session.revocation_reason = revocation_reason
            revoked_count += 1
        
        await session.commit()
        
        return revoked_count
    
    async def get_user_sessions(
        self,
        session: AsyncSession,
        user_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get user's sessions.
        
        Args:
            session: Database session
            user_id: User ID
            active_only: Whether to return only active sessions
            
        Returns:
            List of session information
        """
        conditions = [UserSession.user_id == user_id]
        
        if active_only:
            conditions.append(UserSession.is_active == True)
            conditions.append(UserSession.expires_at > datetime.utcnow())
        
        stmt = select(UserSession).where(and_(*conditions)).order_by(desc(UserSession.created_at))
        result = await session.execute(stmt)
        user_sessions = result.scalars().all()
        
        sessions_info = []
        for user_session in user_sessions:
            sessions_info.append({
                "id": user_session.id,
                "created_at": user_session.created_at,
                "last_activity": user_session.last_activity,
                "expires_at": user_session.expires_at,
                "client_ip": user_session.client_ip,
                "location": user_session.location,
                "device_fingerprint": user_session.device_fingerprint,
                "login_method": user_session.login_method,
                "is_active": user_session.is_active,
                "request_count": user_session.request_count,
                "suspicious_activity": user_session.suspicious_activity,
                "revoked_at": user_session.revoked_at,
                "revocation_reason": user_session.revocation_reason
            })
        
        return sessions_info
    
    async def _cleanup_expired_sessions(
        self,
        session: AsyncSession,
        user_id: Optional[str] = None
    ) -> int:
        """
        Clean up expired sessions.
        
        Args:
            session: Database session
            user_id: Optional user ID to limit cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        conditions = [
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_active == True
        ]
        
        if user_id:
            conditions.append(UserSession.user_id == user_id)
        
        stmt = select(UserSession).where(and_(*conditions))
        result = await session.execute(stmt)
        expired_sessions = result.scalars().all()
        
        # Mark as inactive
        cleanup_count = 0
        for expired_session in expired_sessions:
            expired_session.is_active = False
            expired_session.revoked_at = datetime.utcnow()
            expired_session.revocation_reason = "expired"
            cleanup_count += 1
        
        await session.commit()
        
        return cleanup_count
    
    async def _get_active_sessions_count(
        self,
        session: AsyncSession,
        user_id: str
    ) -> int:
        """
        Get count of active sessions for user.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            Number of active sessions
        """
        stmt = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )
        
        result = await session.execute(stmt)
        return len(result.scalars().all())
    
    async def _remove_oldest_session(
        self,
        session: AsyncSession,
        user_id: str
    ) -> None:
        """
        Remove the oldest active session for user.
        
        Args:
            session: Database session
            user_id: User ID
        """
        stmt = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).order_by(asc(UserSession.created_at)).limit(1)
        
        result = await session.execute(stmt)
        oldest_session = result.scalar_one_or_none()
        
        if oldest_session:
            oldest_session.is_active = False
            oldest_session.revoked_at = datetime.utcnow()
            oldest_session.revocation_reason = "session_limit_exceeded"
            await session.commit()
    
    async def _track_activity(
        self,
        session: AsyncSession,
        session_id: str,
        user_id: str,
        activity_type: str,
        client_ip: str,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        response_status: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track session activity.
        
        Args:
            session: Database session
            session_id: Session ID
            user_id: User ID
            activity_type: Type of activity
            client_ip: Client IP address
            user_agent: User agent string
            endpoint: API endpoint
            method: HTTP method
            response_status: HTTP response status
            extra_data: Additional data
        """
        if not self.activity_tracking:
            return
        
        activity = SessionActivity(
            id=secrets.token_urlsafe(16),
            session_id=session_id,
            user_id=user_id,
            activity_type=activity_type,
            endpoint=endpoint,
            method=method,
            client_ip=client_ip,
            user_agent=user_agent,
            response_status=response_status,
            extra_data=str(extra_data) if extra_data else None
        )
        
        session.add(activity)
        await session.commit()
