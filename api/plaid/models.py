"""
Pydantic models for Plaid API integration

Core models for fundamental APIs that are shared across modules.
Specific models for transactions, investments, liabilities, webhooks, and enrich
are located in their respective submodule directories.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# ============================================================================
# Core Link and Token Models
# ============================================================================

class LinkTokenRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    user_name: Optional[str] = Field(None, description="User's name for Plaid Link")

class LinkTokenResponse(BaseModel):
    link_token: str
    expiration: str
    request_id: str

class PublicTokenExchangeRequest(BaseModel):
    public_token: str = Field(..., description="Public token received from Plaid Link")

class PlaidItemCreateRequest(BaseModel):
    """Request model for creating a Plaid item"""
    public_token: str = Field(..., description="Public token received from Plaid Link")
    environment: str = Field(default="sandbox", description="Plaid environment")

class PlaidSyncRequest(BaseModel):
    """Request model for syncing Plaid data"""
    item_id: str = Field(..., description="Plaid item ID to sync")
    sync_transactions: bool = Field(default=True, description="Whether to sync transactions")
    sync_accounts: bool = Field(default=True, description="Whether to sync accounts")
    days_to_sync: int = Field(default=30, description="Number of days to sync")

class AccessTokenResponse(BaseModel):
    access_token: str
    item_id: str
    request_id: str
    message: str = "Successfully connected to bank account"

# ============================================================================
# Core Account Models
# ============================================================================

class AccountBalance(BaseModel):
    available: Optional[float] = None
    current: Optional[float] = None
    limit: Optional[float] = None
    iso_currency_code: Optional[str] = None

class Account(BaseModel):
    account_id: str
    name: str
    official_name: Optional[str] = None
    type: str
    subtype: Optional[str] = None
    balances: AccountBalance
    mask: Optional[str] = None

class AccountsRequest(BaseModel):
    access_token: str = Field(..., description="Access token for the connected account")

class AccountsResponse(BaseModel):
    accounts: List[Account]
    request_id: str

# ============================================================================
# Core Transaction Models (Basic/Shared)
# ============================================================================

class TransactionLocation(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    date: str
    name: str
    merchant_name: Optional[str] = None
    category: List[str] = []
    category_id: Optional[str] = None
    type: Optional[str] = None
    pending: bool = False
    account_owner: Optional[str] = None
    location: Optional[TransactionLocation] = None
    payment_meta: Dict[str, Any] = {}

class TransactionsRequest(BaseModel):
    access_token: str = Field(..., description="Access token for the connected account")
    start_date: Optional[date] = Field(None, description="Start date for transaction query (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date for transaction query (YYYY-MM-DD)")
    account_ids: Optional[List[str]] = Field(None, description="Specific account IDs to query")
    count: int = Field(100, ge=1, le=500, description="Number of transactions to retrieve (1-500)")
    offset: int = Field(0, ge=0, description="Number of transactions to skip")

class TransactionsResponse(BaseModel):
    transactions: List[Transaction]
    total_transactions: int
    accounts: List[Account]
    request_id: str

# ============================================================================
# Institution Models
# ============================================================================

class Institution(BaseModel):
    institution_id: str
    name: str
    products: List[str]
    country_codes: List[str]
    url: Optional[str] = None
    primary_color: Optional[str] = None
    logo: Optional[str] = None

class InstitutionResponse(BaseModel):
    institution: Institution
    request_id: str

# ============================================================================
# Error and Status Models
# ============================================================================

class PlaidError(BaseModel):
    error_type: str
    error_code: str
    error_message: str
    display_message: Optional[str] = None
    request_id: Optional[str] = None

# ============================================================================
# Connection Management Models (Future Database Integration)
# ============================================================================

class StoredConnection(BaseModel):
    user_id: str
    item_id: str
    access_token: str
    institution_id: str
    institution_name: str
    created_at: datetime
    last_sync: Optional[datetime] = None

class ConnectionStatus(BaseModel):
    user_id: str
    connections: List[Dict[str, Any]]
    total_accounts: int
    last_updated: datetime
