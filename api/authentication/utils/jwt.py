"""
JWT token creation, validation, and management.

This module provides JWT token functionality for authentication
including access tokens, refresh tokens, and token validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from pydantic import BaseModel

from api.settings import get_settings


class TokenData(BaseModel):
    """Token payload data structure."""
    username: Optional[str] = None
    user_id: Optional[str] = None
    scopes: list[str] = []


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time delta
        secret_key: JWT secret key (uses settings if None)
        algorithm: JWT algorithm (uses settings if None)
        
    Returns:
        str: Encoded JWT token
    """
    settings = get_settings()
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    secret = secret_key or settings.secret_key
    alg = algorithm or settings.algorithm
    
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=alg)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time delta (default: 7 days)
        secret_key: JWT secret key (uses settings if None)
        algorithm: JWT algorithm (uses settings if None)
        
    Returns:
        str: Encoded JWT refresh token
    """
    settings = get_settings()
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh tokens
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    secret = secret_key or settings.secret_key
    alg = algorithm or settings.algorithm
    
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=alg)
    return encoded_jwt


def decode_access_token(
    token: str, 
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token to decode
        secret_key: JWT secret key (uses settings if None)
        algorithm: JWT algorithm (uses settings if None)
        
    Returns:
        dict or None: Token payload if valid, None if invalid
    """
    settings = get_settings()
    
    try:
        secret = secret_key or settings.secret_key
        alg = algorithm or settings.algorithm
        
        payload = jwt.decode(token, secret, algorithms=[alg])
        
        # Verify token type
        token_type = payload.get("type")
        if token_type != "access":
            return None
            
        return payload
        
    except JWTError:
        return None


def decode_refresh_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT refresh token.
    
    Args:
        token: JWT refresh token to decode
        secret_key: JWT secret key (uses settings if None)
        algorithm: JWT algorithm (uses settings if None)
        
    Returns:
        dict or None: Token payload if valid, None if invalid
    """
    settings = get_settings()
    
    try:
        secret = secret_key or settings.secret_key
        alg = algorithm or settings.algorithm
        
        payload = jwt.decode(token, secret, algorithms=[alg])
        
        # Verify token type
        token_type = payload.get("type")
        if token_type != "refresh":
            return None
            
        return payload
        
    except JWTError:
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Get token expiration time without validation.
    
    Args:
        token: JWT token
        
    Returns:
        datetime or None: Token expiration time if decodable
    """
    try:
        # Decode without verification to get expiry
        payload = jwt.get_unverified_claims(token)
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired without full validation.
    
    Args:
        token: JWT token
        
    Returns:
        bool: True if expired, False if valid or can't determine
    """
    expiry = get_token_expiry(token)
    if expiry is None:
        return True
    return datetime.utcnow() > expiry


def create_token_response(
    user_id: str,
    username: str,
    scopes: Optional[list[str]] = None,
    include_refresh: bool = True
) -> Token:
    """
    Create a complete token response with access and refresh tokens.
    
    Args:
        user_id: User ID
        username: Username
        scopes: User permission scopes
        include_refresh: Whether to include refresh token
        
    Returns:
        Token: Complete token response
    """
    settings = get_settings()
    
    token_data = {
        "sub": user_id,
        "username": username,
        "scopes": scopes or []
    }
    
    access_token = create_access_token(token_data)
    expires_in = settings.access_token_expire_minutes * 60  # Convert to seconds
    
    response = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in
    )
    
    if include_refresh:
        response.refresh_token = create_refresh_token(token_data)
    
    return response
