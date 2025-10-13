"""Session service exceptions."""


class SessionServiceError(Exception):
    """Base exception for session service errors."""
    pass


class SessionNotFoundError(SessionServiceError):
    """Raised when session is not found."""
    pass


class SessionExpiredError(SessionServiceError):
    """Raised when session has expired."""
    pass


class SessionInvalidError(SessionServiceError):
    """Raised when session is invalid."""
    pass


class SessionCreationError(SessionServiceError):
    """Raised when session creation fails."""
    pass
