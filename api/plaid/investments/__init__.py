"""
Plaid Investments Module - Official Implementation

This module provides comprehensive support for Plaid's investments product including:

Core Features:
- Investment account management with balances and metadata
- Securities data (stocks, bonds, ETFs, mutual funds, options, crypto, cash)
- Holdings tracking with quantities, values, and pricing
- Investment transactions (buy, sell, dividend, transfer, fee, etc.)
- Option contracts and fixed income security details
- Real-time webhook processing for data updates
- Change history tracking for audit purposes

Data Models:
- PlaidInvestmentAccount: Investment accounts with balances
- PlaidInvestmentSecurity: Security metadata for all asset types  
- PlaidInvestmentHolding: Holdings of securities in accounts
- PlaidInvestmentTransaction: Investment transactions
- PlaidInvestmentOptionContract: Option contract details
- PlaidInvestmentFixedIncome: Bond and CD information
- PlaidInvestmentHistory: Change tracking
- PlaidInvestmentWebhookEvent: Webhook processing

API Endpoints:
- POST /plaid/investments/sync/holdings/{item_id} - Sync holdings data
- POST /plaid/investments/sync/transactions/{item_id} - Sync transaction data
- GET /plaid/investments/holdings - Get user holdings
- GET /plaid/investments/transactions - Get user transactions
- GET /plaid/investments/accounts - Get investment accounts
- GET /plaid/investments/securities - Get securities information
- GET /plaid/investments/stats - Get investment statistics
- POST /plaid/investments/webhook/process - Process webhooks

Key Features:
- Full compliance with official Plaid Investments API
- Support for all investment account types (401k, IRA, brokerage, etc.)
- Complete security type coverage (equity, fixed income, derivatives, crypto)
- Real-time pricing and valuation data
- Transaction categorization and history
- Webhook-driven automatic updates
- Comprehensive error handling and validation
"""

# Import existing models for backward compatibility
from .models import (
    Security,
    InvestmentHolding,
    InvestmentTransaction,
    InvestmentsHoldingsRequest,
    InvestmentsHoldingsResponse,
    InvestmentsTransactionsRequest,
    InvestmentsTransactionsResponse,
    InvestmentsRefreshRequest,
    InvestmentsRefreshResponse,
    HoldingsWebhookRequest,
    InvestmentsTransactionsWebhookRequest,
    OptionContract,
    FixedIncome
)

# Import official implementation models
from .models_official import (
    # Database Models
    PlaidInvestmentAccount,
    PlaidInvestmentSecurity,
    PlaidInvestmentOptionContract,
    PlaidInvestmentFixedIncome,
    PlaidInvestmentHolding,
    PlaidInvestmentTransaction,
    PlaidInvestmentHistory,
    PlaidInvestmentWebhookEvent,
    
    # Response Models
    InvestmentHoldingsResponse,
    InvestmentTransactionsResponse,
    InvestmentAccountResponse,
    InvestmentHoldingResponse,
    InvestmentSecurityResponse,
    InvestmentTransactionResponse
)

from .service import InvestmentsService
from .service_official import InvestmentsService as OfficialInvestmentsService, get_investments_service
from .router import router
from .router_official import router as official_router

__all__ = [
    # Legacy models (backward compatibility)
    "Security",
    "InvestmentHolding",
    "InvestmentTransaction",
    "InvestmentsHoldingsRequest",
    "InvestmentsHoldingsResponse",
    "InvestmentsTransactionsRequest",
    "InvestmentsTransactionsResponse",
    "InvestmentsRefreshRequest",
    "InvestmentsRefreshResponse",
    "HoldingsWebhookRequest",
    "InvestmentsTransactionsWebhookRequest",
    "OptionContract",
    "FixedIncome",
    
    # Official implementation models
    "PlaidInvestmentAccount",
    "PlaidInvestmentSecurity", 
    "PlaidInvestmentOptionContract",
    "PlaidInvestmentFixedIncome",
    "PlaidInvestmentHolding",
    "PlaidInvestmentTransaction", 
    "PlaidInvestmentHistory",
    "PlaidInvestmentWebhookEvent",
    
    # Response Models
    "InvestmentHoldingsResponse",
    "InvestmentTransactionsResponse",
    "InvestmentAccountResponse",
    "InvestmentHoldingResponse",
    "InvestmentSecurityResponse",
    "InvestmentTransactionResponse",
    
    # Services and Routers
    "InvestmentsService",
    "OfficialInvestmentsService",
    "get_investments_service",
    "router",
    "official_router"
]