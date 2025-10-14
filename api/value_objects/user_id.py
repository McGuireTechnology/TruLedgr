"""UserId value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class UserId:
    """Value object for user ID.
    
    Immutable identifier for users.
    """
    value: UUID
    
    def __init__(self, value: str | UUID):
        """Create UserId from string or UUID."""
        if isinstance(value, str):
            object.__setattr__(self, 'value', UUID(value))
        elif isinstance(value, UUID):
            object.__setattr__(self, 'value', value)
        else:
            raise TypeError(f"UserId must be str or UUID, got {type(value)}")
    
    def __str__(self) -> str:
        """String representation."""
        return str(self.value)
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"UserId('{self.value}')"
    
    @classmethod
    def generate(cls) -> 'UserId':
        """Generate a new random UserId."""
        return cls(uuid4())
