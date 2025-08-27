from fastapi import HTTPException, status
from typing import Optional


class UserException(HTTPException):
    """Base exception for user-related errors"""
    pass


class UserNotFoundError(UserException):
    def __init__(self, username: Optional[str] = None):
        detail = f"User '{username}' not found" if username else "User not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserAlreadyExistsError(UserException):
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field.capitalize()} '{value}' already exists"
        )

