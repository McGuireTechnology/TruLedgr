"""
Plaid Enrich Module

Transaction enrichment functionality.
"""

from .models import (
    EnrichmentLocation,
    Counterparty,
    PersonalFinanceCategory,
    Recurrence,
    TransactionEnrichments,
    ClientProvidedTransaction,
    EnrichedTransaction,
    EnrichOptions,
    TransactionsEnrichRequest,
    TransactionsEnrichResponse,
    CounterpartyAccountNumbers
)
from .service import EnrichService
from .router import router

__all__ = [
    "EnrichmentLocation",
    "Counterparty",
    "PersonalFinanceCategory",
    "Recurrence",
    "TransactionEnrichments",
    "ClientProvidedTransaction",
    "EnrichedTransaction",
    "EnrichOptions",
    "TransactionsEnrichRequest",
    "TransactionsEnrichResponse",
    "CounterpartyAccountNumbers",
    "EnrichService",
    "router"
]