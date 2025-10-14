"""OAuth state management for CSRF protection."""

from typing import Optional
from datetime import datetime, timedelta
import secrets

# Simple in-memory state storage (for production, use Redis or database)
_state_storage: dict = {}


class OAuthState:
    """OAuth state for CSRF protection."""
    
    def __init__(
        self,
        state: str,
        provider: str,
        redirect_uri: str,
        expires_at: datetime
    ):
        """Initialize OAuth state.
        
        Args:
            state: Random state string
            provider: OAuth provider name
            redirect_uri: Redirect URI for callback
            expires_at: Expiration timestamp
        """
        self.state = state
        self.provider = provider
        self.redirect_uri = redirect_uri
        self.expires_at = expires_at
    
    def is_expired(self) -> bool:
        """Check if state has expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "state": self.state,
            "provider": self.provider,
            "redirect_uri": self.redirect_uri,
            "expires_at": self.expires_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OAuthState":
        """Create from dictionary."""
        return cls(
            state=data["state"],
            provider=data["provider"],
            redirect_uri=data["redirect_uri"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )


class OAuthStateManager:
    """Manages OAuth state for CSRF protection."""
    
    def __init__(self, expiration_minutes: int = 10):
        """Initialize state manager.
        
        Args:
            expiration_minutes: State expiration time in minutes
        """
        self.expiration_minutes = expiration_minutes
    
    def generate_state(
        self,
        provider: str,
        redirect_uri: str
    ) -> str:
        """Generate and store OAuth state.
        
        Args:
            provider: OAuth provider name
            redirect_uri: Redirect URI for callback
            
        Returns:
            Random state string
        """
        # Generate cryptographically secure random state
        state = secrets.token_urlsafe(32)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(
            minutes=self.expiration_minutes
        )
        
        # Store state
        oauth_state = OAuthState(
            state=state,
            provider=provider,
            redirect_uri=redirect_uri,
            expires_at=expires_at,
        )
        _state_storage[state] = oauth_state.to_dict()
        
        return state
    
    def verify_state(self, state: str) -> Optional[OAuthState]:
        """Verify and consume OAuth state.
        
        Args:
            state: State string to verify
            
        Returns:
            OAuthState if valid, None if invalid or expired
        """
        # Get state from storage
        state_data = _state_storage.get(state)
        if not state_data:
            return None
        
        # Parse state
        oauth_state = OAuthState.from_dict(state_data)
        
        # Check expiration
        if oauth_state.is_expired():
            # Clean up expired state
            del _state_storage[state]
            return None
        
        # Consume state (remove from storage)
        del _state_storage[state]
        
        return oauth_state
    
    def cleanup_expired_states(self):
        """Remove all expired states from storage."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, value in _state_storage.items()
            if datetime.fromisoformat(value["expires_at"]) < now
        ]
        for key in expired_keys:
            del _state_storage[key]


# Global state manager instance
oauth_state_manager = OAuthStateManager()
