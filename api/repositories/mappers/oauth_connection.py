"""Mapper between OAuthConnection entity and OAuthConnectionModel."""

from uuid import UUID

from ..models.oauth_connection import OAuthConnectionModel
from ...entities.oauth_connection import OAuthConnection, OAuthProvider
from ...value_objects import UserId


class OAuthConnectionMapper:
    """Maps between OAuthConnection entity and OAuthConnectionModel."""
    
    @staticmethod
    def to_entity(model: OAuthConnectionModel) -> OAuthConnection:
        """Convert OAuthConnectionModel to OAuthConnection entity.
        
        Args:
            model: SQLAlchemy OAuthConnectionModel instance
            
        Returns:
            OAuthConnection domain entity
        """
        return OAuthConnection(
            id=str(model.id),
            user_id=UserId(model.user_id),
            provider=OAuthProvider(model.provider),
            provider_user_id=model.provider_user_id,
            provider_email=model.provider_email,
            provider_name=model.provider_name,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            token_expires_at=model.token_expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_used_at=model.last_used_at
        )
    
    @staticmethod
    def to_model(entity: OAuthConnection) -> OAuthConnectionModel:
        """Convert OAuthConnection entity to OAuthConnectionModel.
        
        Args:
            entity: OAuthConnection domain entity
            
        Returns:
            SQLAlchemy OAuthConnectionModel instance
        """
        return OAuthConnectionModel(
            id=UUID(entity.id) if isinstance(entity.id, str) else entity.id,
            user_id=entity.user_id.value,
            provider=entity.provider.value,
            provider_user_id=entity.provider_user_id,
            provider_email=entity.provider_email,
            provider_name=entity.provider_name,
            access_token=entity.access_token,
            refresh_token=entity.refresh_token,
            token_expires_at=entity.token_expires_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_used_at=entity.last_used_at
        )
    
    @staticmethod
    def update_model_from_entity(
        model: OAuthConnectionModel,
        entity: OAuthConnection
    ) -> None:
        """Update existing model with entity data.
        
        Args:
            model: Existing OAuthConnectionModel to update
            entity: OAuthConnection entity with new data
        """
        model.provider_user_id = entity.provider_user_id
        model.provider_email = entity.provider_email
        model.provider_name = entity.provider_name
        model.access_token = entity.access_token
        model.refresh_token = entity.refresh_token
        model.token_expires_at = entity.token_expires_at
        model.updated_at = entity.updated_at
        model.last_used_at = entity.last_used_at
