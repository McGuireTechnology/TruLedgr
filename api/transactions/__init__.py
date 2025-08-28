"""
Transactions Module

This module provides comprehensive transaction management functionality for TruLedgr.
It aggregates transaction data from multiple sources (Plaid, manual entries, etc.)
and provides unified APIs for transaction operations.

Key Features:
- Transaction CRUD operations with automatic duplicate detection
- Advanced filtering and search capabilities
- Transaction reconciliation and categorization
- Recurring transaction detection and management
- Bulk operations for efficiency
- Comprehensive audit trails and modification history
- Integration with accounts and institutions

Components:
- models.py: SQLModel definitions for transaction entities
- schemas.py: Pydantic schemas for API requests/responses
- service.py: Business logic layer for transaction operations
- router.py: FastAPI router with REST endpoints
"""

from .models import (
    Transaction,
    TransactionSourceMapping,
    TransactionModificationHistory,
    RecurringTransaction,
    TransactionReconciliation,
    TransactionType,
    TransactionStatus,
    TransactionSource,
    TransactionCategory,
    TransactionSubcategory,
    RecurrencePattern
)
from .schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionSummaryResponse,
    TransactionSearchRequest,
    TransactionReconciliationRequest,
    TransactionReconciliationResponse,
    RecurringTransactionCreate,
    RecurringTransactionResponse,
    PlaidTransactionSyncRequest,
    BulkTransactionUpdateRequest,
    TransactionDuplicateCheckRequest,
    TransactionDuplicateResponse
)
from .service import transaction_service
from .router import router

__all__ = [
    # Models
    "Transaction",
    "TransactionSourceMapping",
    "TransactionModificationHistory",
    "RecurringTransaction",
    "TransactionReconciliation",
    "TransactionType",
    "TransactionStatus",
    "TransactionSource",
    "TransactionCategory",
    "TransactionSubcategory",
    "RecurrencePattern",

    # Schemas
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionListResponse",
    "TransactionSummaryResponse",
    "TransactionSearchRequest",
    "TransactionReconciliationRequest",
    "TransactionReconciliationResponse",
    "RecurringTransactionCreate",
    "RecurringTransactionResponse",
    "PlaidTransactionSyncRequest",
    "BulkTransactionUpdateRequest",
    "TransactionDuplicateCheckRequest",
    "TransactionDuplicateResponse",

    # Service
    "transaction_service",

    # Router
    "router"
]
