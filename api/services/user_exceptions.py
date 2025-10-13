"""User service exceptions."""


class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass


class UserAlreadyExistsError(UserServiceError):
    """Raised when attempting to create a user that already exists."""
    pass


class InvalidEmailFormatError(UserServiceError):
    """Raised when email format is invalid."""
    pass


class UserRegistrationError(UserServiceError):
    """Raised when user registration fails."""
    pass


class UserUpdateError(UserServiceError):
    """Raised when user update fails."""
    pass
