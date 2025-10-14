"""Session repository interface for TruLedgr domain."""

from abc import abstractmethod
from typing import List, Optional, Protocol
from datetime import datetime

from ..entities import Session
from ..value_objects import SessionId, UserId


class SessionRepository(Protocol):
    """Session repository interface."""
    
    @abstractmethod
    async def create(self, session: Session) -> Session:
        """Create a new session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: SessionId) -> Optional[Session]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    async def get_by_token_jti(self, token_jti: str) -> Optional[Session]:
        """Get session by JWT token ID."""
        pass
    
    @abstractmethod
    async def get_active_sessions_by_user(self, user_id: UserId) -> List[Session]:
        """Get all active sessions for a user."""
        pass
    
    @abstractmethod
    async def update(self, session: Session) -> Session:
        """Update existing session."""
        pass
    
    @abstractmethod
    async def delete(self, session_id: SessionId) -> bool:
        """Delete session by ID."""
        pass
    
    @abstractmethod
    async def invalidate_user_sessions(self, user_id: UserId) -> int:
        """Invalidate all sessions for a user. Returns count of invalidated sessions."""
        pass
    
    @abstractmethod
    async def cleanup_expired_sessions(self, cutoff_time: Optional[datetime] = None) -> int:
        """Clean up expired sessions. Returns count of cleaned sessions."""
        pass