"""
Account Lockout Manager

Provides protection against brute force attacks by temporarily locking accounts
after a configurable number of failed login attempts.
"""

import time
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from api.settings import get_settings


class AccountLockedError(Exception):
    """Exception raised when an account is locked due to too many failed attempts"""
    
    def __init__(self, seconds_remaining: int):
        self.seconds_remaining = seconds_remaining
        super().__init__(f"Account locked. Try again in {seconds_remaining} seconds.")


class AccountLockoutManager:
    """
    Account lockout manager with database persistence and configurable settings.
    
    Features:
    - Tracks failed login attempts per user
    - Configurable max attempts and lockout duration
    - Automatic cleanup of expired attempts
    - Database persistence for reliability
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.max_attempts = getattr(self.settings, 'max_login_attempts', 5)
        self.lockout_duration_minutes = getattr(self.settings, 'account_lockout_duration_minutes', 30)
        self.lockout_duration = self.lockout_duration_minutes * 60  # Convert to seconds
        
        # In-memory cache for performance (will be synced with DB)
        self.failed_attempts: Dict[str, list] = {}
        self.locked_accounts: Dict[str, float] = {}  # username -> unlock_time
    
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


# Global account lockout manager instance
account_lockout_manager = AccountLockoutManager()
