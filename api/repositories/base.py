"""Base repository interfaces for TruLedgr domain."""

from abc import abstractmethod
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserRepository
    from .tenant import TenantRepository, PersonRepository, ResourceGroupRepository, SubscriptionRepository, InvitationRepository
    from .financial import AccountRepository, TransactionRepository, CategoryRepository
    from .session import SessionRepository


class UnitOfWork(Protocol):
    """Unit of work interface for transaction management."""
    
    users: "UserRepository"
    tenants: "TenantRepository"
    persons: "PersonRepository"
    accounts: "AccountRepository"
    transactions: "TransactionRepository"
    categories: "CategoryRepository"
    resource_groups: "ResourceGroupRepository"
    subscriptions: "SubscriptionRepository"
    invitations: "InvitationRepository"
    sessions: "SessionRepository"
    
    @abstractmethod
    async def __aenter__(self) -> 'UnitOfWork':
        """Enter async context manager."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        pass
    
    @abstractmethod
    async def commit(self):
        """Commit the transaction."""
        pass
    
    @abstractmethod
    async def rollback(self):
        """Rollback the transaction."""
        pass
    
    @abstractmethod
    def get_session(self):
        """Get the current database session."""
        pass