"""Authentication and authorization dependencies."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..entities import User
from ..value_objects import UserId
from ..repositories.base import UnitOfWork
from .database import get_uow

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract bearer token from Authorization header.
    
    Usage:
        @router.get("/protected")
        async def protected_route(token: str = Depends(get_token)):
            ...
    """
    return credentials.credentials


async def get_current_user_id(token: str = Depends(get_token)) -> UserId:
    """
    Get current user ID from JWT token.
    
    Usage:
        @router.get("/me")
        async def get_me(user_id: UserId = Depends(get_current_user_id)):
            ...
    """
    # Import here to avoid circular dependency
    from ..services.auth import TokenService
    
    user_id = TokenService.verify_and_get_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


async def get_current_user(
    user_id: UserId = Depends(get_current_user_id),
    uow = Depends(get_uow)
) -> User:
    """
    Get current authenticated user entity.
    
    Usage:
        @router.get("/profile")
        async def get_profile(user: User = Depends(get_current_user)):
            return {"email": str(user.email)}
    """
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        return user


async def get_current_active_user(
    user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (convenience wrapper).
    
    Usage:
        @router.post("/data")
        async def create_data(user: User = Depends(get_current_active_user)):
            ...
    """
    # get_current_user already checks is_active
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Require user to be an admin.
    
    Usage:
        @router.delete("/users/{id}")
        async def delete_user(
            id: str,
            admin: User = Depends(require_admin)
        ):
            ...
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# Optional auth for endpoints that work with or without authentication
async def get_current_user_optional(
    token: Optional[str] = Depends(get_token),
    uow = Depends(get_uow)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise None.
    
    Usage:
        @router.get("/public-data")
        async def get_data(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # Return personalized data
            else:
                # Return public data
    """
    if not token:
        return None
    
    try:
        user_id = await get_current_user_id(token)
        async with uow:
            return await uow.users.get_by_id(user_id)
    except HTTPException:
        return None
