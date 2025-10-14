"""OAuth connection entity for TruLedgr domain."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

from ..value_objects import UserId


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"


@dataclass
class OAuthConnection:
    """OAuth connection domain entity.
    
    Represents a connection between a user and an OAuth provider.
    Each user can have one connection per provider type.
    """
    id: str  # UUID
    user_id: UserId
    provider: OAuthProvider
    provider_user_id: str  # Unique ID from the OAuth provider
    provider_email: Optional[str] = None
    provider_name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired."""
        if self.token_expires_at is None:
            return True
        return datetime.utcnow() >= self.token_expires_at
    
    def update_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None
    ) -> None:
        """Update OAuth tokens.
        
        Args:
            access_token: New access token
            refresh_token: New refresh token (optional)
            expires_in: Token expiration time in seconds (optional)
        """
        object.__setattr__(self, 'access_token', access_token)
        if refresh_token:
            object.__setattr__(self, 'refresh_token', refresh_token)
        if expires_in:
            expires_at = datetime.utcnow().timestamp() + expires_in
            object.__setattr__(
                self,
                'token_expires_at',
                datetime.fromtimestamp(expires_at)
            )
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def record_usage(self) -> None:
        """Record that this OAuth connection was used."""
        object.__setattr__(self, 'last_used_at', datetime.utcnow())
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on connection ID."""
        if not isinstance(other, OAuthConnection):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on connection ID."""
        return hash(self.id)
