"""
Accounts Module

This module provides comprehensive account management functionality for TruLedgr.
It aggregates account data from multiple sources including Plaid and manual entries,
providing a unified interface for account operations.

Key Features:
- Account creation and management
- Balance tracking and history
- Multi-source data aggregation
- Status and health monitoring
- Comprehensive search and filtering
- Plaid integration support

Components:
- models.py: SQLModel definitions for accounts and related entities
- schemas.py: Pydantic schemas for API requests/responses
- service.py: Business logic layer for account operations
- router.py: FastAPI router with REST endpoints

The accounts module serves as a foundation for transaction management
and provides the core account data that powers the financial dashboard.
"""

from .models import (
    Account,
    AccountSourceMapping,
    AccountBalanceHistory,
    AccountStatusHistory,
    AccountType,
    AccountSubtype,
    AccountSource,
    HolderCategory,
    AccountStatus
)
from .schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountListResponse,
    AccountSummaryResponse,
    AccountSearchRequest,
    AccountBalanceUpdate,
    PlaidAccountSyncRequest,
    AccountBalanceHistoryResponse,
    AccountStatusHistoryResponse
)
from .service import account_service
from .router import router

__all__ = [
    # Models
    "Account",
    "AccountSourceMapping",
    "AccountBalanceHistory",
    "AccountStatusHistory",
    "AccountType",
    "AccountSubtype",
    "AccountSource",
    "HolderCategory",
    "AccountStatus",

    # Schemas
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountListResponse",
    "AccountSummaryResponse",
    "AccountSearchRequest",
    "AccountBalanceUpdate",
    "PlaidAccountSyncRequest",
    "AccountBalanceHistoryResponse",
    "AccountStatusHistoryResponse",

    # Service
    "account_service",

    # Router
    "router"
]
