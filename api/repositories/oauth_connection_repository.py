"""OAuth connection repository implementation."""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .oauth_connection import OAuthConnectionRepository
from .models.oauth_connection import OAuthConnectionModel
from .mappers.oauth_connection import OAuthConnectionMapper
from ..entities.oauth_connection import OAuthConnection, OAuthProvider
from ..value_objects import UserId


class SqlAlchemyOAuthConnectionRepository(OAuthConnectionRepository):
    """SQLAlchemy implementation of OAuthConnectionRepository."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session
    
    async def create(
        self,
        connection: OAuthConnection
    ) -> OAuthConnection:
        """Create a new OAuth connection.
        
        Args:
            connection: OAuthConnection entity to create
            
        Returns:
            Created OAuth connection entity
        """
        model = OAuthConnectionMapper.to_model(connection)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return OAuthConnectionMapper.to_entity(model)
    
    async def get_by_id(
        self,
        connection_id: str
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection by ID.
        
        Args:
            connection_id: Connection ID to find
            
        Returns:
            OAuthConnection entity if found, None otherwise
        """
        stmt = select(OAuthConnectionModel).where(
            OAuthConnectionModel.id == UUID(connection_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return OAuthConnectionMapper.to_entity(model) if model else None
    
    async def get_by_user_and_provider(
        self,
        user_id: UserId,
        provider: OAuthProvider
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection by user ID and provider.
        
        Args:
            user_id: User ID
            provider: OAuth provider
            
        Returns:
            OAuthConnection entity if found, None otherwise
        """
        stmt = select(OAuthConnectionModel).where(
            and_(
                OAuthConnectionModel.user_id == user_id.value,
                OAuthConnectionModel.provider == provider.value
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return OAuthConnectionMapper.to_entity(model) if model else None
    
    async def get_by_provider_user_id(
        self,
        provider: OAuthProvider,
        provider_user_id: str
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection by provider and provider user ID.
        
        Args:
            provider: OAuth provider
            provider_user_id: User ID from OAuth provider
            
        Returns:
            OAuthConnection entity if found, None otherwise
        """
        stmt = select(OAuthConnectionModel).where(
            and_(
                OAuthConnectionModel.provider == provider.value,
                OAuthConnectionModel.provider_user_id == provider_user_id
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return OAuthConnectionMapper.to_entity(model) if model else None
    
    async def list_by_user(
        self,
        user_id: UserId
    ) -> list[OAuthConnection]:
        """List all OAuth connections for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of OAuthConnection entities
        """
        stmt = select(OAuthConnectionModel).where(
            OAuthConnectionModel.user_id == user_id.value
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [
            OAuthConnectionMapper.to_entity(model)
            for model in models
        ]
    
    async def update(
        self,
        connection: OAuthConnection
    ) -> OAuthConnection:
        """Update existing OAuth connection.
        
        Args:
            connection: OAuthConnection entity with updated data
            
        Returns:
            Updated OAuthConnection entity
        """
        stmt = select(OAuthConnectionModel).where(
            OAuthConnectionModel.id == UUID(connection.id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(
                f"OAuth connection with ID {connection.id} not found"
            )
        
        OAuthConnectionMapper.update_model_from_entity(model, connection)
        await self._session.flush()
        await self._session.refresh(model)
        return OAuthConnectionMapper.to_entity(model)
    
    async def delete(self, connection_id: str) -> bool:
        """Delete OAuth connection by ID.
        
        Args:
            connection_id: Connection ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        stmt = select(OAuthConnectionModel).where(
            OAuthConnectionModel.id == UUID(connection_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True
    
    async def delete_by_user_and_provider(
        self,
        user_id: UserId,
        provider: OAuthProvider
    ) -> bool:
        """Delete OAuth connection by user ID and provider.
        
        Args:
            user_id: User ID
            provider: OAuth provider
            
        Returns:
            True if deleted, False if not found
        """
        stmt = select(OAuthConnectionModel).where(
            and_(
                OAuthConnectionModel.user_id == user_id.value,
                OAuthConnectionModel.provider == provider.value
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True
