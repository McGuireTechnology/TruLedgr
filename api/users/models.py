"""
User database models.

This module defines the core User model and related database models
for user management, including session tracking and OAuth accounts.
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from api.common.models import TimestampMixin, SoftDeleteMixin


class User(TimestampMixin, SoftDeleteMixin, table=True):
    """Core user model."""
    __tablename__ = "users" # type: ignore
    
    # Core identifiers
    id: str = Field(primary_key=True, index=True)
    username: str = Field(index=True, unique=True, max_length=100)
    email: str = Field(index=True, unique=True, max_length=255)
    
    # Authentication
    hashed_password: Optional[str] = Field(default=None, max_length=255)
    totp_secret: Optional[str] = Field(default=None, max_length=32)
    totp_enabled: bool = Field(default=False)
    backup_codes: Optional[str] = Field(default=None, max_length=1000)  # Comma-separated backup codes
    
    # Profile information
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    profile_picture_url: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = Field(default=None, max_length=1000)
    
    # Account status
    is_active: bool = Field(default=True, index=True)
    is_verified: bool = Field(default=False, index=True)
    email_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    
    # Role-based access control
    role_id: Optional[str] = Field(default=None, foreign_key="roles.id")
    
    # OAuth integration
    is_oauth_user: bool = Field(default=False)
    oauth_provider: Optional[str] = Field(default=None, max_length=50)
    oauth_provider_id: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships
    role: Optional["Role"] = Relationship(back_populates="users")
    sessions: List["UserSession"] = Relationship(back_populates="user")
    oauth_accounts: List["OAuthAccount"] = Relationship(back_populates="user")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username


class UserSession(TimestampMixin, table=True):
    """User session tracking."""
    __tablename__ = "user_sessions"
    
    id: str = Field(primary_key=True, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    session_token_hash: str = Field(index=True, unique=True, max_length=255)
    
    # Client information
    client_ip: str = Field(max_length=45)  # IPv6 support
    user_agent: Optional[str] = Field(default=None, max_length=512)
    device_fingerprint: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=255)
    
    # Session lifecycle
    is_active: bool = Field(default=True, index=True)
    last_activity: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True)
    revoked_at: Optional[datetime] = Field(default=None)
    revocation_reason: Optional[str] = Field(default=None, max_length=100)
    login_method: Optional[str] = Field(default="password", max_length=50)
    
    # Security tracking
    request_count: int = Field(default=0)
    suspicious_activity: bool = Field(default=False)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="sessions")


class SessionActivity(TimestampMixin, table=True):
    """Session activity audit log."""
    __tablename__ = "session_activities"
    
    id: str = Field(primary_key=True, index=True)
    session_id: str = Field(foreign_key="user_sessions.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    
    # Activity details
    activity_type: str = Field(max_length=50, index=True)
    endpoint: Optional[str] = Field(default=None, max_length=255)
    method: Optional[str] = Field(default=None, max_length=10)
    client_ip: str = Field(max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=512)
    request_id: Optional[str] = Field(default=None, max_length=100)
    response_status: Optional[int] = Field(default=None)
    extra_data: Optional[str] = Field(default=None)  # JSON string
    
    # Relationships
    session: Optional[UserSession] = Relationship()
    user: Optional[User] = Relationship()


class OAuthAccount(TimestampMixin, table=True):
    """OAuth account linking for multiple providers."""
    __tablename__ = "oauth_accounts"
    
    id: str = Field(primary_key=True, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    
    # Provider information
    provider: str = Field(max_length=50, index=True)
    provider_user_id: str = Field(max_length=255, index=True)
    provider_email: str = Field(max_length=255, index=True)
    provider_name: Optional[str] = Field(default=None, max_length=255)
    provider_picture: Optional[str] = Field(default=None, max_length=500)
    
    # Token management (encrypted)
    access_token: Optional[str] = Field(default=None, max_length=1000)
    refresh_token: Optional[str] = Field(default=None, max_length=1000)
    token_expires_at: Optional[datetime] = Field(default=None)
    
    # Raw provider data (JSON)
    raw_user_data: Optional[str] = Field(default=None)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="oauth_accounts")


class PasswordResetToken(TimestampMixin, table=True):
    """Password reset token management."""
    __tablename__ = "password_reset_tokens"
    
    id: str = Field(primary_key=True, index=True)
    token_hash: str = Field(index=True, unique=True, max_length=255)
    user_id: str = Field(foreign_key="users.id", index=True)
    email: str = Field(index=True, max_length=255)
    
    # Token lifecycle
    expires_at: datetime = Field(index=True)
    used_at: Optional[datetime] = Field(default=None)
    revoked_at: Optional[datetime] = Field(default=None)
    
    # Tracking
    client_ip: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=512)
    previous_token_id: Optional[str] = Field(default=None, max_length=50)
    
    # Relationships
    user: Optional[User] = Relationship()
