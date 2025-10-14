"""EmailAddress value object."""

import re
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


@dataclass(frozen=True)
class EmailAddress:
    """Value object for email address.
    
    Validates email format and provides immutable email representation.
    """
    value: str
    
    def __init__(self, value: str):
        """Create EmailAddress with validation."""
        if not isinstance(value, str):
            raise TypeError(f"Email must be str, got {type(value)}")
        if not EMAIL_PATTERN.match(value):
            raise ValueError(f"Invalid email address: {value}")
        object.__setattr__(self, 'value', value.lower())
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"EmailAddress('{self.value}')"
