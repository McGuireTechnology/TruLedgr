"""User repository interface for TruLedgr domain."""

from abc import abstractmethod
from typing import Optional, Protocol

from ..entities import User
from ..value_objects import UserId, EmailAddress


class UserRepository(Protocol):
    """User repository interface."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: EmailAddress) -> Optional[User]:
        """Get user by email address."""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """List all users with pagination."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total number of users."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email."""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        pass