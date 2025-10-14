"""User entity for TruLedgr domain."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import UserId, EmailAddress


@dataclass
class User:
    """User domain entity.
    
    Represents a user in the TruLedgr system with identity,
    authentication, and authorization properties.
    """
    id: UserId
    username: str
    email: EmailAddress
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def activate(self) -> None:
        """Activate user account."""
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def record_login(self) -> None:
        """Record user login time."""
        object.__setattr__(self, 'last_login', datetime.utcnow())
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on user ID."""
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on user ID."""
        return hash(self.id)
