"""SQLAlchemy ORM model for User."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class UserModel(Base):
    """SQLAlchemy model for User table.
    
    This is infrastructure code - it should never be imported by
    services or domain layer. Only repositories work with models.
    """
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
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
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<UserModel(id={self.id}, username={self.username}, "
            f"email={self.email})>"
        )
