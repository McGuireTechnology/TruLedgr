"""
Enhanced Password Reset Service

Provides secure password reset functionality with database persistence,
configurable expiration, and comprehensive security logging.
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import time

from api.settings import get_settings
from api.authentication.passwords.models import PasswordResetToken


class SecurePasswordResetManager:
    """
    Enhanced password reset manager with database persistence and security features.
    
    Features:
    - Database-backed token storage
    - Configurable token expiration
    - Rate limiting for reset requests
    - Security logging and monitoring
    - Token usage tracking
    - Automatic cleanup of expired tokens
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.token_expiry_hours = getattr(self.settings, 'password_reset_token_expiry_hours', 24)
        self.max_reset_attempts = getattr(self.settings, 'max_password_reset_attempts', 3)
        self.rate_limit_minutes = getattr(self.settings, 'password_reset_rate_limit_minutes', 15)
    
    async def create_reset_token(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Create a new password reset token and store it in database"""
        
        # Check rate limiting
        await self._check_rate_limit(session, email)
        
        # Generate secure token
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        
        # Invalidate any existing tokens for this user
        await self._invalidate_existing_tokens(session, user_id)
        
        # Create new token record
        reset_token = PasswordResetToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            email=email,
            expires_at=expires_at,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        session.add(reset_token)
        await session.commit()
        
        # Log token creation
        await self._log_reset_event(
            session, "token_created", {
                "user_id": user_id,
                "email": email,
                "client_ip": client_ip,
                "expires_at": expires_at.isoformat()
            }
        )
        
        return raw_token
    
    async def verify_reset_token(
        self,
        session: AsyncSession,
        raw_token: str,
        client_ip: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Verify a password reset token and return user info if valid.
        Returns None if token is invalid, expired, or used.
        """
        
        token_hash = self._hash_token(raw_token)
        
        # Find token in database
        query = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at == None
        )
        result = await session.execute(query)
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            await self._log_reset_event(
                session, "token_not_found", {
                    "token_hash": token_hash[:8] + "...",
                    "client_ip": client_ip
                }
            )
            return None
        
        # Update attempt tracking
        token_record.use_count += 1
        # Note: last_attempt_at doesn't exist in the existing model
        
        # Check if token is expired
        if datetime.utcnow() > token_record.expires_at:
            await self._log_reset_event(
                session, "token_expired", {
                    "user_id": token_record.user_id,
                    "email": token_record.email,
                    "expired_at": token_record.expires_at.isoformat(),
                    "client_ip": client_ip
                }
            )
            await session.commit()
            return None
        
        # Check attempt limit
        if token_record.use_count > self.max_reset_attempts:
            await self._log_reset_event(
                session, "token_attempt_limit_exceeded", {
                    "user_id": token_record.user_id,
                    "email": token_record.email,
                    "attempt_count": token_record.use_count,
                    "client_ip": client_ip
                }
            )
            await session.commit()
            return None
        
        await session.commit()
        
        return {
            "user_id": token_record.user_id,
            "email": token_record.email,
            "token_record": token_record
        }
    
    async def use_reset_token(
        self,
        session: AsyncSession,
        raw_token: str,
        client_ip: Optional[str] = None
    ) -> bool:
        """
        Mark a reset token as used. Returns True if successful.
        """
        
        token_hash = self._hash_token(raw_token)
        
        # Find and verify token
        query = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at == None
        )
        result = await session.execute(query)
        token_record = result.scalar_one_or_none()
        
        if not token_record or datetime.utcnow() > token_record.expires_at:
            return False
        
        # Mark as used
        token_record.used_at = datetime.utcnow()
        await session.commit()
        
        # Log token usage
        await self._log_reset_event(
            session, "token_used", {
                "user_id": token_record.user_id,
                "email": token_record.email,
                "client_ip": client_ip
            }
        )
        
        return True
    
    async def get_reset_token_info(
        self,
        session: AsyncSession,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get information about active reset tokens for a user"""
        
        query = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at == None,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
        result = await session.execute(query)
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            return None
        
        return {
            "created_at": token_record.created_at,
            "expires_at": token_record.expires_at,
            "use_count": token_record.use_count,
            "max_uses": token_record.max_uses,
            "time_remaining": int((token_record.expires_at - datetime.utcnow()).total_seconds())
        }
    
    async def cleanup_expired_tokens(self, session: AsyncSession) -> int:
        """Remove expired password reset tokens"""
        
        query = select(PasswordResetToken).where(
            PasswordResetToken.expires_at < datetime.utcnow()
        )
        result = await session.execute(query)
        expired_tokens = result.scalars().all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            await session.delete(token)
        
        await session.commit()
        
        if count > 0:
            await self._log_reset_event(
                session, "tokens_cleanup", {
                    "expired_tokens_removed": count
                }
            )
        
        return count
    
    async def revoke_user_tokens(self, session: AsyncSession, user_id: str) -> int:
        """Revoke all active reset tokens for a user"""
        
        query = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at == None
        )
        result = await session.execute(query)
        active_tokens = result.scalars().all()
        
        count = len(active_tokens)
        
        for token in active_tokens:
            token.used_at = datetime.utcnow()
        
        await session.commit()
        
        if count > 0:
            await self._log_reset_event(
                session, "user_tokens_revoked", {
                    "user_id": user_id,
                    "tokens_revoked": count
                }
            )
        
        return count
    
    async def _check_rate_limit(self, session: AsyncSession, email: str) -> None:
        """Check if user is making too many reset requests"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.rate_limit_minutes)
        
        query = select(PasswordResetToken).where(
            PasswordResetToken.email == email,
            PasswordResetToken.created_at > cutoff_time
        )
        result = await session.execute(query)
        recent_tokens = result.scalars().all()
        
        if len(recent_tokens) >= 3:  # Max 3 requests per rate limit window
            raise Exception(f"Too many reset requests. Try again in {self.rate_limit_minutes} minutes.")
    
    async def _invalidate_existing_tokens(self, session: AsyncSession, user_id: str) -> None:
        """Mark existing tokens for user as used"""
        
        query = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at == None
        )
        result = await session.execute(query)
        existing_tokens = result.scalars().all()
        
        for token in existing_tokens:
            token.used_at = datetime.utcnow()
    
    def _hash_token(self, raw_token: str) -> str:
        """Hash a token for secure storage"""
        return hashlib.sha256(raw_token.encode()).hexdigest()
    
    async def _log_reset_event(
        self,
        session: AsyncSession,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log password reset events"""
        timestamp = int(time.time())
        print(f"[PASSWORD_RESET] {timestamp}: {event_type} - {details}")


# Global password reset manager instance
password_reset_manager = SecurePasswordResetManager()
