"""Unit of Work implementation."""

from sqlalchemy.ext.asyncio import AsyncSession

from .base import UnitOfWork
from .user_repository import SqlAlchemyUserRepository
from .oauth_connection_repository import SqlAlchemyOAuthConnectionRepository


class SqlAlchemyUnitOfWork:
    """SQLAlchemy implementation of Unit of Work pattern.
    
    Manages transactions across multiple repositories.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize Unit of Work with session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session
        self._users = SqlAlchemyUserRepository(session)
        self._oauth_connections = SqlAlchemyOAuthConnectionRepository(
            session
        )
    
    @property
    def users(self) -> SqlAlchemyUserRepository:
        """Get user repository."""
        return self._users
    
    @property
    def oauth_connections(self) -> SqlAlchemyOAuthConnectionRepository:
        """Get OAuth connection repository."""
        return self._oauth_connections
    
    async def commit(self) -> None:
        """Commit transaction."""
        await self._session.commit()
    
    async def rollback(self) -> None:
        """Rollback transaction."""
        await self._session.rollback()
    
    def get_session(self) -> AsyncSession:
        """Get the current database session."""
        return self._session
    
    async def __aenter__(self):
        """Enter async context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        if exc_type:
            await self.rollback()
