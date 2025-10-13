"""Mapper between User entity and UserModel."""

from ..models.user import UserModel
from ...entities import User
from ...value_objects import UserId, EmailAddress


class UserMapper:
    """Maps between User entity and UserModel.
    
    This is infrastructure code colocated with repositories.
    Mappers translate between domain (entities) and persistence (models).
    """
    
    @staticmethod
    def to_entity(model: UserModel) -> User:
        """Convert UserModel to User entity.
        
        Args:
            model: SQLAlchemy UserModel instance
            
        Returns:
            User domain entity
        """
        return User(
            id=UserId(model.id),
            username=model.username,
            email=EmailAddress(model.email),
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_admin=model.is_admin,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert User entity to UserModel.
        
        Args:
            entity: User domain entity
            
        Returns:
            SQLAlchemy UserModel instance
        """
        return UserModel(
            id=entity.id.value,
            username=entity.username,
            email=str(entity.email),
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_admin=entity.is_admin,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login=entity.last_login
        )
    
    @staticmethod
    def update_model_from_entity(
        model: UserModel,
        entity: User
    ) -> None:
        """Update existing model with entity data.
        
        Args:
            model: Existing UserModel to update
            entity: User entity with new data
        """
        model.username = entity.username
        model.email = str(entity.email)
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        model.is_admin = entity.is_admin
        model.updated_at = entity.updated_at
        model.last_login = entity.last_login
