"""User repository implementation."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .user import UserRepository
from .models.user import UserModel
from .mappers.user import UserMapper
from ..entities import User
from ..value_objects import UserId, EmailAddress


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository.
    
    This is infrastructure code that implements the repository interface
    defined in the domain layer.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session
    
    async def create(self, user: User) -> User:
        """Create a new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user entity with database-generated fields
        """
        model = UserMapper.to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID to find
            
        Returns:
            User entity if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.
        
        Args:
            username: Username to find
            
        Returns:
            User entity if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None
    
    async def get_by_email(self, email: EmailAddress) -> Optional[User]:
        """Get user by email address.
        
        Args:
            email: Email address to find
            
        Returns:
            User entity if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None
    
    async def update(self, user: User) -> User:
        """Update existing user.
        
        Args:
            user: User entity with updated data
            
        Returns:
            Updated user entity
        """
        stmt = select(UserModel).where(UserModel.id == user.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"User with ID {user.id} not found")
        
        UserMapper.update_model_from_entity(model, user)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        return True
    
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """List all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user entities
        """
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [UserMapper.to_entity(model) for model in models]
    
    async def count(self) -> int:
        """Count total number of users.
        
        Returns:
            Total number of users
        """
        from sqlalchemy import func
        stmt = select(func.count(UserModel.id))
        result = await self._session.execute(stmt)
        return result.scalar_one()
    
    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email.
        
        Args:
            email: Email address to check
            
        Returns:
            True if user exists, False otherwise
        """
        stmt = select(UserModel.id).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username.
        
        Args:
            username: Username to check
            
        Returns:
            True if user exists, False otherwise
        """
        stmt = select(UserModel.id).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
