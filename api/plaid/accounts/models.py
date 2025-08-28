"""
Plaid Accounts Models

Database and API models for Account information and balance operations.
"""

from sqlmodel import SQLModel, Field, Column, String, DateTime
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import func
from pydantic import BaseModel
from enum import Enum
from decimal import Decimal
import json

from api.common.ulid_utils import ULIDPrimaryKey, ULIDForeignKey


class AccountType(str, Enum):
    """Plaid account type enumeration"""
    DEPOSITORY = "depository"
    CREDIT = "credit"
    LOAN = "loan"
    INVESTMENT = "investment"
    OTHER = "other"


class AccountSubtype(str, Enum):
    """Plaid account subtype enumeration - extended with all known subtypes"""
    # Depository subtypes
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money market"
    CASH_MANAGEMENT = "cash management"
    CD = "cd"
    HSA = "hsa"
    
    # Credit subtypes
    CREDIT_CARD = "credit card"
    PAYPAL = "paypal"
    PREPAID = "prepaid"
    
    # Loan subtypes
    AUTO = "auto"
    BUSINESS = "business"
    COMMERCIAL = "commercial"
    CONSTRUCTION = "construction"
    CONSUMER = "consumer"
    HOME_EQUITY = "home equity"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    OVERDRAFT = "overdraft"
    LINE_OF_CREDIT = "line of credit"
    STUDENT = "student"
    
    # Investment subtypes
    INVESTMENT_401A = "401a"
    INVESTMENT_401K = "401k"
    INVESTMENT_403B = "403b"
    INVESTMENT_457B = "457b"
    INVESTMENT_529 = "529"
    BROKERAGE = "brokerage"
    CASH_ISA = "cash isa"
    EDUCATION_SAVINGS_ACCOUNT = "education savings account"
    GIC = "gic"
    HEALTH_REIMBURSEMENT_ARRANGEMENT = "health reimbursement arrangement"
    HSA_INVESTMENT = "hsa"
    IRA = "ira"
    ISA = "isa"
    KEOGH = "keogh"
    LIF = "lif"
    LIRA = "lira"
    LRIF = "lrif"
    LRSP = "lrsp"
    NON_TAXABLE_BROKERAGE_ACCOUNT = "non-taxable brokerage account"
    PENSION = "pension"
    PRIF = "prif"
    PROFIT_SHARING_PLAN = "profit sharing plan"
    RDSP = "rdsp"
    RESP = "resp"
    RETIREMENT = "retirement"
    RLIF = "rlif"
    ROTH = "roth"
    ROTH_401K = "roth 401k"
    RRIF = "rrif"
    RRSP = "rrsp"
    SARSEP = "sarsep"
    SEP_IRA = "sep ira"
    SIMPLE_IRA = "simple ira"
    SIPP = "sipp"
    STOCK_PLAN = "stock plan"
    TFSA = "tfsa"
    THRIFT_SAVINGS_PLAN = "thrift savings plan"
    TRUST = "trust"
    UGMA = "ugma"
    UTMA = "utma"
    VARIABLE_ANNUITY = "variable annuity"


class HolderCategory(str, Enum):
    """Account holder category enumeration"""
    PERSONAL = "personal"
    BUSINESS = "business"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    """Account verification status enumeration"""
    PENDING_AUTOMATIC_VERIFICATION = "pending_automatic_verification"
    PENDING_MANUAL_VERIFICATION = "pending_manual_verification"
    MANUALLY_VERIFIED = "manually_verified"
    VERIFICATION_EXPIRED = "verification_expired"
    VERIFICATION_FAILED = "verification_failed"
    DATABASE_MATCHED = "database_matched"
    DATABASE_INSIGHTS_PASS = "database_insights_pass"
    DATABASE_INSIGHTS_PASS_WITH_CAUTION = "database_insights_pass_with_caution"
    DATABASE_INSIGHTS_FAIL = "database_insights_fail"


# Database Model
class PlaidAccount(SQLModel, table=True):
    """Plaid Account database model - represents a financial account with comprehensive Plaid data"""
    __tablename__ = "plaid_accounts"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    user_id: str = ULIDForeignKey("users.id")
    
    # Plaid identifiers
    account_id: str = Field(unique=True, index=True)
    persistent_account_id: Optional[str] = Field(default=None, index=True)
    
    # Account information
    name: str = Field()
    official_name: Optional[str] = None
    type: str = Field(index=True)
    subtype: Optional[str] = None
    mask: Optional[str] = None
    
    # Account holder and classification
    holder_category: Optional[str] = Field(default="personal")  # personal, business, unknown
    
    # Balance information (current snapshot)
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    limit_balance: Optional[float] = None
    iso_currency_code: str = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Balance metadata
    balance_last_updated_datetime: Optional[datetime] = None
    
    # Verification and status
    verification_status: Optional[str] = None  # pending_automatic_verification, manually_verified, etc.
    is_active: bool = Field(default=True)
    is_closed: bool = Field(default=False)
    
    # Display preferences (affects view only, not underlying data)
    invert_balance: bool = Field(default=False, description="Invert account balance display")
    invert_transactions: bool = Field(default=False, description="Invert transaction amounts display")
    
    # Additional Plaid metadata (stored as JSON for extensibility)
    plaid_metadata: Optional[str] = Field(default=None)  # JSON for additional fields
    
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
    
    @property
    def plaid_metadata_dict(self) -> dict:
        """Get plaid metadata as dictionary"""
        if self.plaid_metadata:
            try:
                return json.loads(self.plaid_metadata)
            except (json.JSONDecodeError, TypeError):
                pass
        return {}
    
    @plaid_metadata_dict.setter
    def plaid_metadata_dict(self, value: dict):
        """Set plaid metadata from dictionary"""
        self.plaid_metadata = json.dumps(value) if value else None


# Related Tables for comprehensive Account management
class PlaidAccountBalanceHistory(SQLModel, table=True):
    """Track balance changes for Plaid Accounts over time"""
    __tablename__ = "plaid_account_balance_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("plaid_accounts.id")
    
    # Balance snapshot
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    limit_balance: Optional[float] = None
    iso_currency_code: str = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Balance source and metadata
    source: str = Field(default="api_sync")  # api_sync, webhook, manual
    balance_updated_datetime: Optional[datetime] = None
    
    # Change calculation (if previous balance exists)
    available_change: Optional[float] = None
    current_change: Optional[float] = None
    
    # Environment
    environment: str = Field()
    
    # Timestamps
    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class PlaidAccountStatusHistory(SQLModel, table=True):
    """Track status and verification changes for Plaid Accounts"""
    __tablename__ = "plaid_account_status_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("plaid_accounts.id")
    
    # Status information
    is_active: bool = Field()
    is_closed: bool = Field()
    previous_active: Optional[bool] = None
    previous_closed: Optional[bool] = None
    
    # Verification status
    verification_status: Optional[str] = None
    previous_verification_status: Optional[str] = None
    
    # Change metadata
    change_reason: Optional[str] = None  # webhook, api_sync, manual, etc.
    environment: str = Field()
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class PlaidAccountWebhookEvent(SQLModel, table=True):
    """Track webhook events received for Plaid Accounts"""
    __tablename__ = "plaid_account_webhook_events"
    
    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("plaid_accounts.id")
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Webhook information
    webhook_type: str = Field()  # TRANSACTIONS, HOLDINGS, etc.
    webhook_code: str = Field()  # DEFAULT_UPDATE, HISTORICAL_UPDATE, etc.
    
    # Event data (stored as JSON)
    webhook_payload: Optional[str] = Field(default=None)  # Full webhook JSON
    
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


# API Models
class AccountBalance(BaseModel):
    """Account balance information - enhanced for complete Plaid data"""
    available: Optional[Decimal] = Field(None, description="Available balance")
    current: Optional[Decimal] = Field(None, description="Current balance")
    limit: Optional[Decimal] = Field(None, description="Credit limit for credit accounts")
    iso_currency_code: Optional[str] = Field(None, description="ISO 4217 currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    last_updated_datetime: Optional[str] = Field(None, description="Last balance update")

class Account(BaseModel):
    """Account information - enhanced for complete Plaid data"""
    account_id: str = Field(..., description="Plaid account identifier")
    balances: AccountBalance = Field(..., description="Balance information")
    mask: Optional[str] = Field(None, description="Last 4 digits of account number")
    name: str = Field(..., description="Account name")
    official_name: Optional[str] = Field(None, description="Official account name")
    type: str = Field(..., description="Account type (depository, credit, loan, etc.)")
    subtype: Optional[str] = Field(None, description="Account subtype (checking, savings, etc.)")
    holder_category: Optional[str] = Field(None, description="Account holder category (personal, business)")
    verification_status: Optional[str] = Field(None, description="Verification status")
    persistent_account_id: Optional[str] = Field(None, description="Persistent account identifier")

class AccountsGetRequest(BaseModel):
    """Request to get account information"""
    access_token: str = Field(..., description="Access token for the Item")
    account_ids: Optional[List[str]] = Field(None, description="List of account IDs to retrieve")

class AccountsGetResponse(BaseModel):
    """Response for account information"""
    accounts: List[Account]
    item: Dict[str, Any]
    request_id: str

class AccountsBalanceGetRequest(BaseModel):
    """Request to get account balances"""
    access_token: str = Field(..., description="Access token for the Item")
    account_ids: Optional[List[str]] = Field(None, description="List of account IDs to retrieve")

class AccountsBalanceGetResponse(BaseModel):
    """Response for account balances"""
    accounts: List[Account]
    item: Dict[str, Any]
    request_id: str

class PlaidAccountResponse(SQLModel):
    """Response model for Plaid accounts - enhanced with complete data"""
    id: str  # ULID
    account_id: str
    persistent_account_id: Optional[str] = None
    name: str
    official_name: Optional[str] = None
    type: str
    subtype: Optional[str] = None
    mask: Optional[str] = None
    holder_category: Optional[str] = "personal"
    
    # Balance information
    available_balance: Optional[float] = None
    current_balance: Optional[float] = None
    limit_balance: Optional[float] = None
    iso_currency_code: str = "USD"
    unofficial_currency_code: Optional[str] = None
    balance_last_updated_datetime: Optional[datetime] = None
    
    # Status and verification
    verification_status: Optional[str] = None
    is_active: bool = True
    is_closed: bool = False
    
    # Display preferences (affects view only, not underlying data)
    invert_balance: bool = False
    invert_transactions: bool = False
    
    # Institution context
    institution_name: str
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    
    # Additional metadata
    plaid_metadata: Optional[dict] = None

# Enhanced Request/Response Models for comprehensive account operations
class AccountSyncRequest(BaseModel):
    """Request model for syncing account data"""
    item_id: str = Field(..., description="Item ID to sync accounts for")
    force_refresh: bool = Field(default=False, description="Force refresh from Plaid API")
    include_balances: bool = Field(default=True, description="Include balance updates")

class AccountBalanceHistoryResponse(BaseModel):
    """Response model for account balance history"""
    account_id: str
    balance_history: List[Dict[str, Any]]
    total_records: int
    date_range: Dict[str, Optional[str]]

class AccountStatusHistoryResponse(BaseModel):
    """Response model for account status history"""
    account_id: str
    status_history: List[Dict[str, Any]]
    total_records: int
    current_status: Dict[str, Any]


class AccountInversionSettingsRequest(BaseModel):
    """Request model for updating account inversion display settings"""
    invert_balance: Optional[bool] = Field(None, description="Whether to display account balance as inverted")
    invert_transactions: Optional[bool] = Field(None, description="Whether to display transaction amounts as inverted")
