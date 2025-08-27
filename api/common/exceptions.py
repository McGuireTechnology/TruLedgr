"""
Common exception classes for the API.

This module defines custom exceptions used across different modules
for consistent error handling and response formatting.
"""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(HTTPException):
    """Exception raised for validation errors."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class ConflictError(HTTPException):
    """Exception raised when there's a conflict with existing data."""
    
    def __init__(self, detail: str = "Conflict with existing data"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class PermissionError(HTTPException):
    """Exception raised when user lacks required permissions."""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class AuthenticationError(HTTPException):
    """Exception raised for authentication failures."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class BadRequestError(HTTPException):
    """Exception raised for bad request data."""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass


class DatabaseError(ServiceError):
    """Exception raised for database-related errors."""
    pass


class BusinessLogicError(ServiceError):
    """Exception raised for business logic violations."""
    pass