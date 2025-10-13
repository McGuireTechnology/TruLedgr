"""OAuth connection repository interface."""

from abc import abstractmethod
from typing import Optional, Protocol

from ..entities.oauth_connection import OAuthConnection, OAuthProvider
from ..value_objects import UserId


class OAuthConnectionRepository(Protocol):
    """OAuth connection repository interface."""
    
    @abstractmethod
    async def create(
        self,
        connection: OAuthConnection
    ) -> OAuthConnection:
        """Create a new OAuth connection."""
        pass
    
    @abstractmethod
    async def get_by_id(
        self,
        connection_id: str
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_and_provider(
        self,
        user_id: UserId,
        provider: OAuthProvider
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection by user ID and provider."""
        pass
    
    @abstractmethod
    async def get_by_provider_user_id(
        self,
        provider: OAuthProvider,
        provider_user_id: str
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection by provider and provider user ID."""
        pass
    
    @abstractmethod
    async def list_by_user(
        self,
        user_id: UserId
    ) -> list[OAuthConnection]:
        """List all OAuth connections for a user."""
        pass
    
    @abstractmethod
    async def update(
        self,
        connection: OAuthConnection
    ) -> OAuthConnection:
        """Update existing OAuth connection."""
        pass
    
    @abstractmethod
    async def delete(
        self,
        connection_id: str
    ) -> bool:
        """Delete OAuth connection by ID."""
        pass
    
    @abstractmethod
    async def delete_by_user_and_provider(
        self,
        user_id: UserId,
        provider: OAuthProvider
    ) -> bool:
        """Delete OAuth connection by user ID and provider."""
        pass
