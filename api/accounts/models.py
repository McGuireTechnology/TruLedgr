"""
Accounts Models

Core account models that aggregate data from multiple sources:
- Plaid accounts (via api.plaid.accounts)
- Manual account entries
- Other banking integrations

This provides a unified view of all financial accounts.
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime, Boolean, Float
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import func, Index
from enum import Enum
from decimal import Decimal

from api.common.ulid_utils import ULIDPrimaryKey, ULIDForeignKey


class AccountType(str, Enum):
    """Type of financial account"""
    DEPOSITORY = "depository"
    CREDIT = "credit"
    LOAN = "loan"
    INVESTMENT = "investment"
    OTHER = "other"


class AccountSubtype(str, Enum):
    """Account subtype enumeration - extended with all known subtypes"""
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


class AccountSource(str, Enum):
    """Source of account data"""
    PLAID = "plaid"
    MANUAL = "manual"
    YODLEE = "yodlee"  # Future integration
    FINICITY = "finicity"  # Future integration
    OTHER = "other"


class HolderCategory(str, Enum):
    """Account holder category enumeration"""
    PERSONAL = "personal"
    BUSINESS = "business"
    UNKNOWN = "unknown"


class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    PENDING = "pending"
    UNKNOWN = "unknown"


class Account(SQLModel, table=True):
    """
    Core Account model - aggregates data from all sources

    This is the single source of truth for accounts in TruLedgr,
    pulling data from Plaid and allowing manual account creation.
    """
    __tablename__ = "accounts"

    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()

    # Relationships
    institution_id: str = ULIDForeignKey("institutions.id", description="Reference to root institution")
    user_id: str = ULIDForeignKey("users.id", description="Account owner")

    # Core account information
    name: str = Field(index=True, description="Account display name")
    official_name: Optional[str] = Field(None, description="Official account name")
    nickname: Optional[str] = Field(None, description="User-defined nickname")

    # Account classification
    account_type: AccountType = Field(index=True, description="Account type")
    account_subtype: Optional[AccountSubtype] = Field(None, index=True, description="Account subtype")
    primary_source: AccountSource = Field(index=True, description="Primary data source")

    # External identifiers
    plaid_account_id: Optional[str] = Field(None, index=True, description="Plaid account ID")
    account_number: Optional[str] = Field(None, description="Account number (masked)")
    routing_number: Optional[str] = Field(None, description="Routing number")

    # Account holder and classification
    holder_category: HolderCategory = Field(default=HolderCategory.PERSONAL, index=True)

    # Balance information (current snapshot)
    available_balance: Optional[float] = Field(None, description="Available balance")
    current_balance: Optional[float] = Field(None, description="Current balance")
    limit_balance: Optional[float] = Field(None, description="Credit limit or loan amount")
    iso_currency_code: str = Field(default="USD", description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")

    # Balance metadata
    balance_last_updated: Optional[datetime] = Field(None, description="When balance was last updated")

    # Account status and verification
    status: AccountStatus = Field(default=AccountStatus.ACTIVE, index=True)
    is_closed: bool = Field(default=False, index=True)
    verification_status: Optional[str] = Field(None, description="Verification status")

    # Display preferences
    invert_balance: bool = Field(default=False, description="Invert balance display")
    invert_transactions: bool = Field(default=False, description="Invert transaction amounts display")

    # Integration status
    plaid_enabled: bool = Field(default=False, index=True, description="Connected via Plaid")
    manual_entry_allowed: bool = Field(default=True, description="Allow manual transaction entry")

    # Health and sync tracking
    health_status: str = Field(default="healthy", index=True, description="healthy, degraded, down")
    last_health_check: Optional[datetime] = None
    plaid_sync_errors: int = Field(default=0, description="Count of recent sync errors")
    last_plaid_sync: Optional[datetime] = Field(None, description="Last sync with Plaid data")

    # Metadata
    notes: Optional[str] = Field(None, sa_column=Column(Text), description="Internal notes")
    tags: Optional[str] = Field(None, description="Comma-separated tags for categorization")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Helper properties
    @property
    def tags_list(self) -> List[str]:
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
        return []

    @tags_list.setter
    def tags_list(self, value: List[str]):
        """Set tags from a list"""
        self.tags = ",".join(value) if value else None

    @property
    def balance_display(self) -> str:
        """Get formatted balance for display"""
        balance = self.current_balance if self.current_balance is not None else 0
        if self.invert_balance:
            balance = -balance
        return f"{balance:.2f}"

    @property
    def is_positive_balance(self) -> bool:
        """Check if account has positive balance"""
        if self.current_balance is None:
            return False
        return (self.current_balance > 0) != self.invert_balance


class AccountSourceMapping(SQLModel, table=True):
    """
    Maps accounts to their external source identifiers

    This allows tracking of the same account across multiple data sources
    and prevents duplicate account creation.
    """
    __tablename__ = "account_source_mappings"

    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("accounts.id")

    # Source information
    source: AccountSource = Field(index=True, description="Data source")
    external_id: str = Field(index=True, description="External identifier")
    external_account_id: Optional[str] = Field(None, description="External account identifier")

    # Source metadata
    source_metadata: Optional[str] = Field(None, sa_column=Column(Text), description="JSON metadata from source")

    # Mapping status
    is_active: bool = Field(default=True, index=True)
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class AccountBalanceHistory(SQLModel, table=True):
    """
    Track balance changes for accounts over time

    This provides historical balance information for trend analysis
    and account reconciliation.
    """
    __tablename__ = "account_balance_history"

    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("accounts.id")

    # Balance snapshot
    available_balance: Optional[float] = Field(None, description="Available balance at time")
    current_balance: Optional[float] = Field(None, description="Current balance at time")
    limit_balance: Optional[float] = Field(None, description="Credit limit at time")
    iso_currency_code: str = Field(default="USD", description="Currency at time")

    # Change tracking
    available_change: Optional[float] = Field(None, description="Change in available balance")
    current_change: Optional[float] = Field(None, description="Change in current balance")

    # Source and metadata
    source: str = Field(default="api_sync", description="Source of balance update")
    balance_updated_at: Optional[datetime] = Field(None, description="When balance was updated")

    # Timestamps
    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class AccountStatusHistory(SQLModel, table=True):
    """
    Track status changes for accounts over time

    This provides audit trail for account status changes
    and helps with troubleshooting.
    """
    __tablename__ = "account_status_history"

    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("accounts.id")

    # Status information
    previous_status: Optional[AccountStatus] = Field(None, description="Previous account status")
    new_status: AccountStatus = Field(description="New account status")
    previous_closed: Optional[bool] = Field(None, description="Previous closed status")
    new_closed: bool = Field(description="New closed status")

    # Change metadata
    change_reason: Optional[str] = Field(None, description="Reason for status change")
    source: str = Field(default="system", description="Source of status change")

    # Timestamps
    changed_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
