"""SQLAlchemy ORM model for OAuthConnection."""

from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    String,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class OAuthConnectionModel(Base):
    """SQLAlchemy model for OAuth connections table.
    
    Tracks OAuth provider connections for users.
    Each user can have one connection per provider.
    """
    __tablename__ = "oauth_connections"
    
    # Add unique constraint for user_id + provider
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'provider',
            name='uq_user_provider'
        ),
    )
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    provider = Column(
        String(20),
        nullable=False,
        index=True
    )
    provider_user_id = Column(
        String(255),
        nullable=False,
        index=True
    )
    provider_email = Column(String(255), nullable=True)
    provider_name = Column(String(255), nullable=True)
    access_token = Column(String(2048), nullable=True)
    refresh_token = Column(String(2048), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<OAuthConnectionModel(id={self.id}, "
            f"user_id={self.user_id}, provider={self.provider})>"
        )
