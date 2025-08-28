"""
Plaid Integration Package

This package provides a comprehensive integration with Plaid APIs, organized into logical modules:

Core APIs (in main module):
- Link token creation and public token exchange
- Account information and balances  
- Basic transaction retrieval
- Institution search and information
- Multi-environment support (production/sandbox)

Modular APIs (in submodules):
- transactions/: Advanced transaction retrieval and management
- investments/: Investment holdings and transactions
- liabilities/: Credit cards, mortgages, student loans  
- enrich/: Transaction enrichment services
- webhooks/: Webhook handling and verification
- institutions/: Institution search, details, and metadata
- categories/: Transaction category management and analysis

Legacy APIs (existing submodules):
- items/: Item management and status (connection to financial institution)
- accounts/: Extended account management
- link/: Link token management
- sandbox/: Testing and simulation in sandbox environment
- users/: User management and consent

Each module contains:
- models.py: Pydantic models for requests and responses
- service.py: Business logic and API interactions
- router.py: FastAPI endpoints
- __init__.py: Module exports
"""

from .service import PlaidService, get_plaid_service
from .router import router
from .models import (
    LinkTokenRequest,
    LinkTokenResponse,
    PublicTokenExchangeRequest,
    AccessTokenResponse,
    TransactionsRequest,
    TransactionsResponse,
    AccountsRequest,
    AccountsResponse,
    PlaidError
)

__all__ = [
    "PlaidService",
    "get_plaid_service", 
    "router",
    "LinkTokenRequest",
    "LinkTokenResponse",
    "PublicTokenExchangeRequest",
    "AccessTokenResponse",
    "TransactionsRequest",
    "TransactionsResponse",
    "AccountsRequest",
    "AccountsResponse",
    "PlaidError"
]
