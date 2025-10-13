"""Authentication service exceptions."""


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found."""
    pass


class UserInactiveError(AuthenticationError):
    """Raised when user account is inactive."""
    pass


class PasswordHashingError(AuthenticationError):
    """Raised when password hashing fails."""
    pass


class TokenGenerationError(AuthenticationError):
    """Raised when token generation fails."""
    pass


class TokenValidationError(AuthenticationError):
    """Raised when token validation fails."""
    pass


class PasswordValidationError(AuthenticationError):
    """Raised when password doesn't meet requirements."""
    pass
