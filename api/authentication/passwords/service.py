"""
Password Service

This module provides password-related authentication services including:
- Password validation and strength checking
- Password reset operations
- Secure password hashing
- Account lockout protection
"""

import re
import secrets
import hashlib
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from api.users.models import User
from api.users.service import get_user_by_email, get_user_by_username
from api.authentication.utils.password import verify_password, get_password_hash
from api.settings import get_settings
from .models import PasswordResetToken

settings = get_settings()


class AccountLockedError(Exception):
    """Exception raised when an account is locked due to too many failed attempts"""
    
    def __init__(self, seconds_remaining: int):
        self.seconds_remaining = seconds_remaining
        super().__init__(f"Account locked. Try again in {seconds_remaining} seconds.")


class PasswordService:
    """
    Service for password-related authentication operations.
    
    Provides secure password management including:
    - User authentication with password and account lockout protection
    - Password strength validation
    - Password reset functionality
    - Password change operations
    - Account lockout management
    """
    
    def __init__(self):
        self.min_password_length = 8
        self.password_reset_expiry_minutes = 15
        self.max_reset_tokens_per_user = 3
        
        # Account lockout settings
        self.max_attempts = getattr(settings, 'max_login_attempts', 5)
        self.lockout_duration_minutes = getattr(settings, 'account_lockout_duration_minutes', 30)
        self.lockout_duration = self.lockout_duration_minutes * 60  # Convert to seconds
        
        # In-memory cache for account lockout (will be synced with DB)
        self.failed_attempts: Dict[str, list] = {}
        self.locked_accounts: Dict[str, float] = {}  # username -> unlock_time
    
    async def authenticate_user(
        self, 
        session: AsyncSession, 
        username: str, 
        password: str,
        client_ip: Optional[str] = None
    ) -> Optional[User]:
        """
        Authenticate user with username/email and password, including account lockout protection.
        
        Args:
            session: Database session
            username: Username or email
            password: Plain text password
            client_ip: Client IP address for security logging
            
        Returns:
            User object if authentication successful, None otherwise
            
        Raises:
            AccountLockedError: If account is currently locked
        """
        # Check if account is locked
        is_locked, seconds_remaining = await self.is_account_locked(session, username)
        if is_locked and seconds_remaining is not None:
            raise AccountLockedError(seconds_remaining)
        
        # Try to get user by username first, then by email
        user = await get_user_by_username(session, username)
        if not user:
            user = await get_user_by_email(session, username)
        
        if not user:
            # Record failed attempt even for non-existent users to prevent enumeration
            await self.record_failed_attempt(session, username, client_ip or "unknown")
            return None
        
        # Check if user is active and not deleted
        if not user.is_active or user.is_deleted:
            await self.record_failed_attempt(session, username, client_ip or "unknown")
            return None
        
        # Verify password
        if not user.hashed_password or not verify_password(password, user.hashed_password):
            await self.record_failed_attempt(session, username, client_ip or "unknown")
            return None
        
        # Successful authentication - clear failed attempts
        await self.clear_failed_attempts(session, username)
        
        return user
    
    async def change_password(
        self,
        session: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password with current password verification.
        
        Args:
            session: Database session
            user: User changing password
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            True if password changed successfully, False otherwise
        """
        # Verify current password
        if not user.hashed_password or not verify_password(current_password, user.hashed_password):
            return False
        
        # Validate new password strength
        validation_errors = self.validate_password_strength(new_password)
        if validation_errors:
            raise ValueError(f"Password validation failed: {'; '.join(validation_errors)}")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(user)
        
        return True
    
    async def request_password_reset(
        self,
        session: AsyncSession,
        email: str,
        client_ip: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """
        Request password reset for email address.
        
        Args:
            session: Database session
            email: Email address
            client_ip: Client IP address
            user_agent: User agent string
            
        Returns:
            Dictionary with request results
        """
        # Get user by email
        user = await get_user_by_email(session, email)
        
        # Always return success to prevent email enumeration
        if not user:
            return {
                "success": True,
                "message": "If the email exists, a password reset link has been sent"
            }
        
        # Check if user is active
        if not user.is_active or user.is_deleted:
            return {
                "success": True,
                "message": "If the email exists, a password reset link has been sent"
            }
        
        # Clean up old tokens and enforce limits
        await self._cleanup_user_reset_tokens(session, user.id)
        
        # Generate reset token
        reset_token = self._generate_reset_token()
        token_hash = self._hash_token(reset_token)
        expires_at = datetime.utcnow() + timedelta(minutes=self.password_reset_expiry_minutes)
        
        # Create token record
        token_record = PasswordResetToken(
            id=secrets.token_urlsafe(16),
            token_hash=token_hash,
            user_id=user.id,
            email=email,
            expires_at=expires_at,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        session.add(token_record)
        await session.commit()
        
        # TODO: Send email with reset token
        # For now, just log it (in production, use proper email service)
        print(f"Password reset token for {email}: {reset_token}")
        
        return {
            "success": True,
            "message": "If the email exists, a password reset link has been sent",
            "token_id": token_record.id  # For testing purposes
        }
    
    async def confirm_password_reset(
        self,
        session: AsyncSession,
        token: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Confirm password reset with token and new password.
        
        Args:
            session: Database session
            token: Reset token
            new_password: New password
            
        Returns:
            Dictionary with confirmation results
        """
        # Validate new password
        validation_errors = self.validate_password_strength(new_password)
        if validation_errors:
            return {
                "success": False,
                "error": "password_validation_failed",
                "details": validation_errors
            }
        
        # Find and verify token
        token_hash = self._hash_token(token)
        now = datetime.utcnow()
        
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at == None,
            PasswordResetToken.revoked_at == None,
            PasswordResetToken.expires_at > now
        )
        
        result = await session.execute(statement)
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            return {
                "success": False,
                "error": "invalid_or_expired_token",
                "message": "Password reset token is invalid or has expired"
            }
        
        # Get user
        user = await session.get(User, token_record.user_id)
        if not user or not user.is_active or user.is_deleted:
            return {
                "success": False,
                "error": "user_not_found",
                "message": "User account not found or inactive"
            }
        
        # Mark token as used
        token_record.used_at = datetime.utcnow()
        token_record.use_count += 1
        
        # Update user password
        user.hashed_password = get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        
        await session.commit()
        
        return {
            "success": True,
            "message": "Password has been reset successfully",
            "user_id": user.id
        }
    
    def validate_password_strength(self, password: str) -> List[str]:
        """
        Validate password strength and return list of issues.
        
        Args:
            password: Password to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if len(password) < self.min_password_length:
            issues.append(f"Password must be at least {self.min_password_length} characters long")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            issues.append("Password must contain at least one special character")
        
        # Check for common weak passwords
        common_passwords = [
            "password", "123456", "password123", "admin", "letmein",
            "welcome", "monkey", "dragon", "pass123", "qwerty"
        ]
        
        if password.lower() in common_passwords:
            issues.append("Password is too common and easily guessed")
        
        return issues
    
    def _generate_reset_token(self) -> str:
        """Generate a cryptographically secure reset token."""
        return secrets.token_urlsafe(48)  # 48 bytes = 384 bits of entropy
    
    def _hash_token(self, token: str) -> str:
        """Hash token for secure database storage."""
        # Use PBKDF2 with the secret key as salt for additional security
        salt = settings.secret_key.encode()
        return hashlib.pbkdf2_hmac('sha256', token.encode(), salt, 100000).hex()
    
    async def _cleanup_user_reset_tokens(
        self, 
        session: AsyncSession, 
        user_id: str
    ) -> int:
        """
        Clean up old and expired reset tokens for user.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            Number of tokens cleaned up
        """
        now = datetime.utcnow()
        
        # Get all tokens for user
        statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id
        )
        result = await session.execute(statement)
        all_tokens = result.scalars().all()
        
        # Find tokens to delete
        tokens_to_delete = []
        active_tokens = []
        
        for token in all_tokens:
            # Delete used tokens older than 1 hour (for audit trail)
            if token.used_at and token.used_at < (now - timedelta(hours=1)):
                tokens_to_delete.append(token)
            # Delete expired tokens
            elif token.expires_at <= now:
                tokens_to_delete.append(token)
            # Delete revoked tokens older than 1 hour
            elif token.revoked_at and token.revoked_at < (now - timedelta(hours=1)):
                tokens_to_delete.append(token)
            else:
                active_tokens.append(token)
        
        # If too many active tokens, revoke oldest ones
        if len(active_tokens) >= self.max_reset_tokens_per_user:
            # Sort by creation date and revoke oldest
            active_tokens.sort(key=lambda t: t.created_at)
            tokens_to_revoke = active_tokens[:-self.max_reset_tokens_per_user + 1]
            
            for token in tokens_to_revoke:
                token.revoked_at = now
                token.revocation_reason = "token_limit_exceeded"
        
        # Delete old tokens
        for token in tokens_to_delete:
            await session.delete(token)
        
        if tokens_to_delete or len(active_tokens) >= self.max_reset_tokens_per_user:
            await session.commit()
        
        return len(tokens_to_delete)
    
    # Account Lockout Methods
    
    async def record_failed_attempt(self, session: AsyncSession, username: str, client_ip: str) -> None:
        """Record a failed login attempt for a user"""
        now = time.time()
        
        # Initialize if not exists
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        # Add current attempt
        self.failed_attempts[username].append(now)
        
        # Clean old attempts (older than lockout duration)
        cutoff_time = now - self.lockout_duration
        self.failed_attempts[username] = [
            attempt_time for attempt_time in self.failed_attempts[username]
            if attempt_time > cutoff_time
        ]
        
        # Check if account should be locked
        if len(self.failed_attempts[username]) >= self.max_attempts:
            unlock_time = now + self.lockout_duration
            self.locked_accounts[username] = unlock_time
            
            # Log security event
            await self._log_security_event(
                session, username, "account_locked", 
                {"attempts": len(self.failed_attempts[username]), "client_ip": client_ip}
            )
    
    async def is_account_locked(self, session: AsyncSession, username: str) -> Tuple[bool, Optional[int]]:
        """Check if account is locked. Returns (is_locked, seconds_until_unlock)"""
        now = time.time()
        
        if username in self.locked_accounts:
            unlock_time = self.locked_accounts[username]
            if now < unlock_time:
                seconds_remaining = int(unlock_time - now)
                return True, seconds_remaining
            else:
                # Lock has expired, remove it
                await self.clear_failed_attempts(session, username)
        
        return False, None
    
    async def clear_failed_attempts(self, session: AsyncSession, username: str) -> None:
        """Clear failed attempts for successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        if username in self.locked_accounts:
            del self.locked_accounts[username]
            
            # Log unlock event
            await self._log_security_event(
                session, username, "account_unlocked", {"reason": "successful_login"}
            )
    
    def get_failed_attempt_count(self, username: str) -> int:
        """Get current number of failed attempts"""
        if username not in self.failed_attempts:
            return 0
        
        now = time.time()
        cutoff_time = now - self.lockout_duration
        
        # Count recent attempts
        recent_attempts = [
            attempt_time for attempt_time in self.failed_attempts[username]
            if attempt_time > cutoff_time
        ]
        
        return len(recent_attempts)
    
    async def get_lockout_status(self, session: AsyncSession, username: str) -> Dict[str, Any]:
        """Get detailed lockout status for a user"""
        is_locked, seconds_remaining = await self.is_account_locked(session, username)
        failed_count = self.get_failed_attempt_count(username)
        
        return {
            "is_locked": is_locked,
            "seconds_remaining": seconds_remaining,
            "failed_attempts": failed_count,
            "max_attempts": self.max_attempts,
            "attempts_remaining": max(0, self.max_attempts - failed_count) if not is_locked else 0
        }
    
    async def cleanup_expired_lockouts(self, session: AsyncSession) -> int:
        """Clean up expired lockouts and old failed attempts"""
        now = time.time()
        cleaned_count = 0
        
        # Clean expired lockouts
        expired_lockouts = []
        for username, unlock_time in self.locked_accounts.items():
            if now >= unlock_time:
                expired_lockouts.append(username)
        
        for username in expired_lockouts:
            await self.clear_failed_attempts(session, username)
            cleaned_count += 1
        
        # Clean old failed attempts
        cutoff_time = now - self.lockout_duration
        for username in list(self.failed_attempts.keys()):
            old_count = len(self.failed_attempts[username])
            self.failed_attempts[username] = [
                attempt_time for attempt_time in self.failed_attempts[username]
                if attempt_time > cutoff_time
            ]
            
            if not self.failed_attempts[username]:
                del self.failed_attempts[username]
            elif len(self.failed_attempts[username]) < old_count:
                cleaned_count += 1
        
        return cleaned_count
    
    async def _log_security_event(
        self, 
        session: AsyncSession, 
        username: str, 
        event_type: str, 
        details: Dict[str, Any]
    ) -> None:
        """Log security events (simplified implementation)"""
        # For now, just print. In production, this would log to database
        print(f"[SECURITY] {event_type}: user={username}, details={details}")
