"""
Password reset token models.

This module defines database models for password reset functionality.
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class PasswordResetToken(SQLModel, table=True):
    """
    Password reset token for secure password recovery.
    
    This model stores password reset tokens with enhanced security features:
    - Token hashing for database security
    - Expiration tracking
    - Usage tracking to prevent replay attacks
    - Client information for audit trails
    """
    
    id: str = Field(primary_key=True, description="Unique token identifier")
    token_hash: str = Field(..., description="Hashed reset token")
    user_id: str = Field(..., foreign_key="users.id", description="User requesting reset")
    email: str = Field(..., description="Email address for reset")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Token creation time")
    expires_at: datetime = Field(..., description="Token expiration time")
    used_at: Optional[datetime] = Field(default=None, description="Token usage time")
    revoked_at: Optional[datetime] = Field(default=None, description="Token revocation time")
    
    # Client information for security tracking
    client_ip: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    
    # Additional security fields
    max_uses: int = Field(default=1, description="Maximum allowed uses")
    use_count: int = Field(default=0, description="Current use count")
    revocation_reason: Optional[str] = Field(default=None, description="Reason for revocation")
