"""
Plaid Transactions Models

Database and API models for Transaction retrieval and transaction-related operations.
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from sqlalchemy import func
from pydantic import BaseModel
from decimal import Decimal
from enum import Enum
import json

from api.common.ulid_utils import ULIDPrimaryKey, ULIDForeignKey


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    PLACE = "place"
    DIGITAL = "digital"
    SPECIAL = "special"
    UNRESOLVED = "unresolved"


class PaymentChannel(str, Enum):
    """Payment channel enumeration"""
    ONLINE = "online"
    IN_STORE = "in store"
    OTHER = "other"


class CounterpartyType(str, Enum):
    """Counterparty type enumeration"""
    MERCHANT = "merchant"
    MARKETPLACE = "marketplace"
    PAYMENT_TERMINAL = "payment_terminal"
    FINANCIAL_INSTITUTION = "financial_institution"


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration"""
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TransactionSyncStatus(str, Enum):
    """Transaction sync status enumeration"""
    INITIAL_UPDATE_COMPLETE = "INITIAL_UPDATE_COMPLETE"
    HISTORICAL_UPDATE_COMPLETE = "HISTORICAL_UPDATE_COMPLETE"
    DEFAULT_UPDATE_COMPLETE = "DEFAULT_UPDATE_COMPLETE"


# Database Models
class PlaidTransaction(SQLModel, table=True):
    """Plaid Transaction database model - enhanced to store complete transaction data"""
    __tablename__ = "plaid_transactions"
    
    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("plaid_accounts.id")
    user_id: str = ULIDForeignKey("users.id")
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Plaid identifiers
    transaction_id: str = Field(unique=True, index=True)
    pending_transaction_id: Optional[str] = Field(default=None, index=True)
    
    # Core transaction information
    amount: float = Field()
    iso_currency_code: str = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Transaction dates
    transaction_date: date = Field(index=True)
    transaction_datetime: Optional[datetime] = None
    authorized_date: Optional[date] = None
    authorized_datetime: Optional[datetime] = None
    
    # Transaction identification and naming
    name: str = Field()
    merchant_name: Optional[str] = None
    merchant_entity_id: Optional[str] = None
    
    # Transaction classification
    transaction_type: Optional[str] = None  # place, digital, special, unresolved
    transaction_code: Optional[str] = None
    payment_channel: Optional[str] = None  # online, in store, other
    
    # Status and ownership
    pending: bool = Field(default=False, index=True)
    account_owner: Optional[str] = None
    
    # Check information
    check_number: Optional[str] = None
    
    # Web and visual information
    logo_url: Optional[str] = None
    website: Optional[str] = None
    
    # Personal finance categorization
    personal_finance_category_primary: Optional[str] = None
    personal_finance_category_detailed: Optional[str] = None
    personal_finance_category_confidence_level: Optional[str] = None
    personal_finance_category_icon_url: Optional[str] = None
    
    # Legacy category information (for backwards compatibility)
    category: Optional[str] = None  # JSON array of category hierarchy
    category_id: Optional[str] = None
    subcategory: Optional[str] = None
    
    # Location information (stored as JSON)
    location_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Payment metadata (stored as JSON)
    payment_meta_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Sync and processing metadata
    sync_cursor: Optional[str] = None  # Cursor from the sync that added this transaction
    transaction_update_status: Optional[str] = None  # Status when this transaction was received
    last_modified: Optional[datetime] = None  # When transaction was last modified by Plaid
    
    # Environment context
    environment: str = Field(default="production")
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    last_sync: Optional[datetime] = None
    
    # JSON property accessors
    @property
    def location_dict(self) -> Optional[Dict[str, Any]]:
        """Get location as dictionary"""
        if self.location_json:
            try:
                return json.loads(self.location_json)
            except (json.JSONDecodeError, TypeError):
                pass
        return None
    
    @location_dict.setter
    def location_dict(self, value: Optional[Dict[str, Any]]):
        """Set location from dictionary"""
        if value is None:
            self.location_json = None
        elif isinstance(value, dict):
            self.location_json = json.dumps(value)
        else:
            # Handle Location objects or other non-dict types
            if hasattr(value, 'to_dict'):
                self.location_json = json.dumps(value.to_dict())
            elif hasattr(value, '__dict__'):
                # Convert object attributes to dict, excluding private attributes
                dict_value = {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                self.location_json = json.dumps(dict_value)
            else:
                # Try to convert to dict, or use empty dict as fallback
                try:
                    self.location_json = json.dumps(dict(value))
                except (TypeError, ValueError):
                    self.location_json = json.dumps({})
    
    @property
    def payment_meta_dict(self) -> Optional[Dict[str, Any]]:
        """Get payment meta as dictionary"""
        if self.payment_meta_json:
            try:
                return json.loads(self.payment_meta_json)
            except (json.JSONDecodeError, TypeError):
                pass
        return None
    
    @payment_meta_dict.setter
    def payment_meta_dict(self, value: Optional[Dict[str, Any]]):
        """Set payment meta from dictionary"""
        if value is None:
            self.payment_meta_json = None
        elif isinstance(value, dict):
            self.payment_meta_json = json.dumps(value)
        else:
            # Handle PaymentMeta objects or other non-dict types
            if hasattr(value, 'to_dict'):
                self.payment_meta_json = json.dumps(value.to_dict())
            elif hasattr(value, '__dict__'):
                # Convert object attributes to dict, excluding private attributes
                dict_value = {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                self.payment_meta_json = json.dumps(dict_value)
            else:
                # Try to convert to dict, or use empty dict as fallback
                try:
                    self.payment_meta_json = json.dumps(dict(value))
                except (TypeError, ValueError):
                    self.payment_meta_json = json.dumps({})
    
    @property
    def category_list(self) -> List[str]:
        """Get category as list"""
        if self.category:
            try:
                return json.loads(self.category)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @category_list.setter
    def category_list(self, value: List[str]):
        """Set category from list"""
        self.category = json.dumps(value) if value else None


class PlaidTransactionCounterparty(SQLModel, table=True):
    """Track counterparties associated with transactions"""
    __tablename__ = "plaid_transaction_counterparties"
    
    id: Optional[str] = ULIDPrimaryKey()
    transaction_id: str = ULIDForeignKey("plaid_transactions.id")
    
    # Counterparty information
    name: str = Field()
    type: str = Field()  # merchant, marketplace, payment_terminal, financial_institution
    entity_id: Optional[str] = Field(default=None, index=True)
    confidence_level: Optional[str] = None  # VERY_HIGH, HIGH, MEDIUM, LOW
    
    # Visual and web information
    logo_url: Optional[str] = None
    website: Optional[str] = None
    
    # Order for multiple counterparties
    display_order: int = Field(default=0)
    
    # Environment context
    environment: str = Field()
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class PlaidTransactionSyncHistory(SQLModel, table=True):
    """Track transaction sync operations and results"""
    __tablename__ = "plaid_transaction_sync_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    account_id: Optional[str] = ULIDForeignKey("plaid_accounts.id")
    
    # Sync operation details
    sync_type: str = Field()  # initial, historical, default, manual
    cursor: Optional[str] = None
    has_more: bool = Field(default=False)
    
    # Transaction counts
    added_count: int = Field(default=0)
    modified_count: int = Field(default=0)
    removed_count: int = Field(default=0)
    total_count: int = Field(default=0)
    
    # Status and completion
    status: str = Field()  # INITIAL_UPDATE_COMPLETE, HISTORICAL_UPDATE_COMPLETE, etc.
    success: bool = Field(default=True)
    error_message: Optional[str] = None
    
    # Request metadata
    request_id: Optional[str] = None
    environment: str = Field()
    
    # Timestamps
    sync_started_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    sync_completed_at: Optional[datetime] = None


class PlaidTransactionWebhookEvent(SQLModel, table=True):
    """Track webhook events for transaction updates"""
    __tablename__ = "plaid_transaction_webhook_events"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Webhook information
    webhook_type: str = Field(default="TRANSACTIONS")
    webhook_code: str = Field()  # DEFAULT_UPDATE, HISTORICAL_UPDATE, INITIAL_UPDATE
    
    # Transaction update details
    new_transactions: Optional[int] = Field(default=0)
    
    # Full webhook payload
    webhook_payload: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Processing status
    processed: bool = Field(default=False)
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    
    # Environment
    environment: str = Field()
    
    # Timestamps
    received_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    @property
    def webhook_payload_dict(self) -> dict:
        """Get webhook payload as dictionary"""
        if self.webhook_payload:
            try:
                return json.loads(self.webhook_payload)
            except (json.JSONDecodeError, TypeError):
                pass
        return {}
    
    @webhook_payload_dict.setter
    def webhook_payload_dict(self, value: dict):
        """Set webhook payload from dictionary"""
        self.webhook_payload = json.dumps(value) if value else None


class PlaidTransactionModificationHistory(SQLModel, table=True):
    """Track transaction modifications over time"""
    __tablename__ = "plaid_transaction_modification_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    transaction_id: str = ULIDForeignKey("plaid_transactions.id")
    
    # Modification details
    modification_type: str = Field()  # added, modified, removed
    previous_amount: Optional[float] = None
    new_amount: Optional[float] = None
    
    # Change context
    sync_cursor: Optional[str] = None
    webhook_event_id: Optional[str] = None
    change_reason: Optional[str] = None
    
    # Environment
    environment: str = Field()
    
    # Timestamps
    modified_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# API Models
class TransactionLocation(BaseModel):
    """Location information for a transaction - enhanced"""
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    store_number: Optional[str] = None

class TransactionCounterparty(BaseModel):
    """Counterparty information for a transaction"""
    name: str = Field(..., description="Counterparty name")
    type: str = Field(..., description="Counterparty type (merchant, marketplace, etc.)")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    website: Optional[str] = Field(None, description="Website URL")
    entity_id: Optional[str] = Field(None, description="Entity identifier")
    confidence_level: Optional[str] = Field(None, description="Confidence level")

class TransactionPersonalFinanceCategory(BaseModel):
    """Personal finance category classification - enhanced"""
    primary: str = Field(..., description="Primary category")
    detailed: str = Field(..., description="Detailed subcategory")
    confidence_level: Optional[str] = Field(None, description="Confidence level for categorization")

class TransactionPaymentMeta(BaseModel):
    """Payment metadata information"""
    by_order_of: Optional[str] = None
    payee: Optional[str] = None
    payer: Optional[str] = None
    payment_method: Optional[str] = None
    payment_processor: Optional[str] = None
    ppd_id: Optional[str] = None
    reason: Optional[str] = None
    reference_number: Optional[str] = None

class Transaction(BaseModel):
    """Complete transaction information matching Plaid API response"""
    # Core identifiers
    transaction_id: str = Field(..., description="Plaid transaction identifier")
    account_id: str = Field(..., description="Account identifier")
    pending_transaction_id: Optional[str] = Field(None, description="Pending transaction ID")
    
    # Account ownership
    account_owner: Optional[str] = Field(None, description="Account owner")
    
    # Amount and currency
    amount: float = Field(..., description="Transaction amount")
    iso_currency_code: Optional[str] = Field(None, description="ISO 4217 currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    
    # Check information
    check_number: Optional[str] = Field(None, description="Check number if applicable")
    
    # Counterparties (merchants, marketplaces, etc.)
    counterparties: Optional[List[TransactionCounterparty]] = Field(None, description="Associated counterparties")
    
    # Dates and timestamps
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    datetime: Optional[str] = Field(None, description="Transaction datetime (ISO 8601)")
    authorized_date: Optional[str] = Field(None, description="Authorization date")
    authorized_datetime: Optional[str] = Field(None, description="Authorization datetime")
    
    # Location information
    location: Optional[TransactionLocation] = Field(None, description="Transaction location")
    
    # Naming and merchant information
    name: str = Field(..., description="Transaction name/description")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")
    logo_url: Optional[str] = Field(None, description="Merchant/transaction logo URL")
    website: Optional[str] = Field(None, description="Merchant website")
    
    # Payment information
    payment_meta: Optional[TransactionPaymentMeta] = Field(None, description="Payment metadata")
    payment_channel: Optional[str] = Field(None, description="Payment channel (online, in store, etc.)")
    
    # Transaction status and type
    pending: bool = Field(..., description="Whether transaction is pending")
    
    # Personal finance categorization
    personal_finance_category: Optional[TransactionPersonalFinanceCategory] = Field(None, description="Personal finance category")
    personal_finance_category_icon_url: Optional[str] = Field(None, description="Category icon URL")
    
    # Transaction classification
    transaction_code: Optional[str] = Field(None, description="Transaction code")
    transaction_type: Optional[str] = Field(None, description="Transaction type (place, digital, etc.)")
    
    # Legacy category support (for backwards compatibility)
    category: Optional[List[str]] = Field(None, description="Transaction category hierarchy")
    category_id: Optional[str] = Field(None, description="Category ID")

class TransactionsSyncResponse(BaseModel):
    """Response model for transactions sync operation"""
    # Accounts included in response
    accounts: List[Dict[str, Any]] = Field(..., description="Account information")
    
    # Transaction updates
    added: List[Transaction] = Field(default_factory=list, description="Newly added transactions")
    modified: List[Transaction] = Field(default_factory=list, description="Modified transactions") 
    removed: List[Dict[str, str]] = Field(default_factory=list, description="Removed transactions (account_id, transaction_id)")
    
    # Pagination and status
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    has_more: bool = Field(..., description="Whether more transactions are available")
    request_id: str = Field(..., description="Request ID")
    transactions_update_status: str = Field(..., description="Update status")

class TransactionsSyncRequest(BaseModel):
    """Request model for syncing transactions"""
    access_token: str = Field(..., description="Access token for the Item")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    count: Optional[int] = Field(100, ge=1, le=500, description="Number of transactions to retrieve")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")

class TransactionsRequest(BaseModel):
    """Request model for getting transactions (legacy)"""
    access_token: str = Field(..., description="Access token for the connected account")
    start_date: Optional[date] = Field(None, description="Start date for transaction query (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date for transaction query (YYYY-MM-DD)")
    account_ids: Optional[List[str]] = Field(None, description="Specific account IDs to query")
    count: int = Field(100, ge=1, le=500, description="Number of transactions to retrieve (1-500)")
    offset: int = Field(0, ge=0, description="Number of transactions to skip")

class TransactionsRefreshRequest(BaseModel):
    """Request model for refreshing transactions"""
    access_token: str = Field(..., description="Access token for the connected account")

class TransactionsResponse(BaseModel):
    """Response model for transactions (legacy)"""
    transactions: List[Transaction]
    total_transactions: int
    accounts: List[Dict[str, Any]]
    request_id: str

# Webhook Models
class TransactionsWebhookRequest(BaseModel):
    """Webhook request for transaction updates"""
    webhook_type: str = Field("TRANSACTIONS", description="Always 'TRANSACTIONS' for this webhook")
    webhook_code: str = Field(..., description="INITIAL_UPDATE, HISTORICAL_UPDATE, or DEFAULT_UPDATE")
    item_id: str = Field(..., description="Plaid item ID")
    new_transactions: Optional[int] = Field(None, description="Number of new transactions available")
    removed_transactions: Optional[List[str]] = Field(None, description="Transaction IDs that were removed")
    environment: str = Field("production", description="Plaid environment")

# Enhanced Response Models
class PlaidTransactionResponse(SQLModel):
    """Enhanced response model for Plaid transactions"""
    id: str  # ULID
    transaction_id: str
    pending_transaction_id: Optional[str] = None
    
    # Core transaction data
    amount: float
    iso_currency_code: str = "USD"
    unofficial_currency_code: Optional[str] = None
    
    # Dates
    date: str  # Changed to 'date' to match frontend expectations and ensure proper JSON serialization
    transaction_datetime: Optional[datetime] = None
    authorized_date: Optional[str] = None  # Changed to string for proper JSON serialization
    authorized_datetime: Optional[datetime] = None
    
    # Identification and naming
    name: str
    merchant_name: Optional[str] = None
    merchant_entity_id: Optional[str] = None
    
    # Classification
    transaction_type: Optional[str] = None
    payment_channel: Optional[str] = None
    
    # Status
    pending: bool = False
    account_owner: Optional[str] = None
    
    # Personal finance category
    personal_finance_category_primary: Optional[str] = None
    personal_finance_category_detailed: Optional[str] = None
    personal_finance_category_confidence_level: Optional[str] = None
    
    # Visual elements
    logo_url: Optional[str] = None
    website: Optional[str] = None
    personal_finance_category_icon_url: Optional[str] = None
    
    # Account and item context
    account_name: str
    account_id: str
    institution_name: str
    
    # Complex data as dictionaries
    location: Optional[Dict[str, Any]] = None
    payment_meta: Optional[Dict[str, Any]] = None
    counterparties: Optional[List[Dict[str, Any]]] = None
    category: Optional[List[str]] = None
    
    # Metadata
    environment: str = "production"
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
