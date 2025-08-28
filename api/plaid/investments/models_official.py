"""
Plaid Investments Database Models

Comprehensive database models for storing Plaid Investments data including:
- Investment account information and balances
- Investment holdings (securities held in accounts)
- Security metadata (stocks, bonds, ETFs, mutual funds, crypto, etc.)
- Investment transactions (buy, sell, transfer, dividend, etc.)
- Option contract details and fixed income information
- Webhook events for investment updates
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime, Integer, Float, Boolean
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from sqlalchemy import func, Index
import json

from api.common.ulid_utils import ULIDField, ULIDPrimaryKey, ULIDForeignKey


# ==========================================
# Investment Accounts Table
# ==========================================

class PlaidInvestmentAccount(SQLModel, table=True):
    """Investment accounts with balance and metadata"""
    __tablename__ = "plaid_investment_accounts"
    
    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")
    item_id: str = ULIDForeignKey("plaid_items.id")
    account_id: str = Field(index=True, description="Plaid account_id")
    plaid_account_id: str = Field(index=True, description="Original Plaid account identifier")
    
    # Account basic information
    account_name: str = Field(description="Account name")
    account_official_name: Optional[str] = None
    account_mask: Optional[str] = None
    account_type: str = Field(index=True, description="investment, brokerage")
    account_subtype: str = Field(index=True, description="401k, ira, brokerage, 529, etc.")
    
    # Balance information
    available_balance: Optional[float] = Field(description="Cash available to withdraw")
    current_balance: Optional[float] = Field(description="Total value of assets")
    limit_amount: Optional[float] = None
    iso_currency_code: Optional[str] = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Balance metadata
    last_updated_datetime: Optional[datetime] = None
    
    # Account verification status (for Auth)
    verification_status: Optional[str] = None
    verification_name: Optional[str] = None
    
    # Persistent account tracking
    persistent_account_id: Optional[str] = None
    holder_category: Optional[str] = None  # personal, business, unrecognized
    
    # Status and error tracking
    status: str = Field(default="active", index=True)
    sync_status: str = Field(default="active", description="active, error, stale")
    sync_error: Optional[str] = None
    last_synced: Optional[datetime] = None
    
    # Environment and timestamps
    environment: str = Field(default="sandbox", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


# ==========================================
# Securities (Stocks, Bonds, ETFs, etc.)
# ==========================================

class PlaidInvestmentSecurity(SQLModel, table=True):
    """Security metadata for stocks, bonds, ETFs, mutual funds, crypto, etc."""
    __tablename__ = "plaid_investment_securities"
    
    # Primary identifier
    id: Optional[str] = ULIDPrimaryKey()
    security_id: str = Field(unique=True, index=True, description="Plaid security_id")
    
    # Security identifiers
    isin: Optional[str] = Field(description="12-character ISIN")
    cusip: Optional[str] = Field(description="9-character CUSIP")
    sedol: Optional[str] = Field(description="7-character SEDOL")
    institution_security_id: Optional[str] = None
    institution_id: Optional[str] = None
    proxy_security_id: Optional[str] = None
    
    # Basic security information
    name: Optional[str] = Field(description="Descriptive name for security")
    ticker_symbol: Optional[str] = Field(index=True, description="Trading symbol")
    is_cash_equivalent: Optional[bool] = Field(default=False)
    security_type: Optional[str] = Field(index=True, description="cash, equity, etf, mutual fund, etc.")
    
    # Pricing information
    close_price: Optional[float] = Field(description="Latest close price")
    close_price_as_of: Optional[date] = None
    update_datetime: Optional[datetime] = None
    iso_currency_code: Optional[str] = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Market and classification
    market_identifier_code: Optional[str] = Field(description="ISO-10383 Market ID")
    sector: Optional[str] = Field(index=True, description="Finance, Technology, etc.")
    industry: Optional[str] = Field(index=True, description="Biotechnology, Airlines, etc.")
    
    # Environment and timestamps
    environment: str = Field(default="sandbox", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


# ==========================================
# Option Contract Details
# ==========================================

class PlaidInvestmentOptionContract(SQLModel, table=True):
    """Option contract details for derivative securities"""
    __tablename__ = "plaid_investment_option_contracts"
    
    id: Optional[str] = ULIDPrimaryKey()
    security_id: str = ULIDForeignKey("plaid_investment_securities.security_id", unique=True)
    
    # Option contract details
    contract_type: str = Field(description="put or call")
    expiration_date: date = Field(description="Option expiration date")
    strike_price: float = Field(description="Strike price per share")
    underlying_security_ticker: str = Field(description="Underlying security ticker")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# Fixed Income Details
# ==========================================

class PlaidInvestmentFixedIncome(SQLModel, table=True):
    """Fixed income security details (bonds, CDs, etc.)"""
    __tablename__ = "plaid_investment_fixed_income"
    
    id: Optional[str] = ULIDPrimaryKey()
    security_id: str = ULIDForeignKey("plaid_investment_securities.security_id", unique=True)
    
    # Fixed income details
    yield_rate_percentage: Optional[float] = None
    yield_rate_type: Optional[str] = None  # coupon, coupon_equivalent, discount, yield
    maturity_date: Optional[date] = None
    issue_date: Optional[date] = None
    face_value: Optional[float] = Field(description="Face value per unit")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# Investment Holdings
# ==========================================

class PlaidInvestmentHolding(SQLModel, table=True):
    """Holdings of securities in investment accounts"""
    __tablename__ = "plaid_investment_holdings"
    
    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")
    account_id: str = ULIDForeignKey("plaid_investment_accounts.plaid_account_id")
    security_id: str = ULIDForeignKey("plaid_investment_securities.security_id")
    
    # Unique constraint on account + security
    __table_args__ = (
        Index("idx_account_security", "account_id", "security_id", unique=True),
    )
    
    # Pricing and valuation
    institution_price: float = Field(description="Price given by institution")
    institution_price_as_of: Optional[date] = None
    institution_price_datetime: Optional[datetime] = None
    institution_value: float = Field(description="Total holding value")
    
    # Quantity and cost basis
    quantity: float = Field(description="Total quantity held")
    cost_basis: Optional[float] = Field(description="Total cost basis")
    
    # Currency
    iso_currency_code: Optional[str] = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Vesting information (for equities)
    vested_quantity: Optional[float] = None
    vested_value: Optional[float] = None
    
    # Status and sync tracking
    status: str = Field(default="active", index=True)
    last_updated: Optional[datetime] = None
    
    # Environment and timestamps
    environment: str = Field(default="sandbox", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


# ==========================================
# Investment Transactions
# ==========================================

class PlaidInvestmentTransaction(SQLModel, table=True):
    """Investment transactions (buy, sell, dividend, etc.)"""
    __tablename__ = "plaid_investment_transactions"
    
    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")
    investment_transaction_id: str = Field(unique=True, index=True, description="Plaid investment_transaction_id")
    account_id: str = ULIDForeignKey("plaid_investment_accounts.plaid_account_id")
    security_id: Optional[str] = ULIDForeignKey("plaid_investment_securities.security_id")
    
    # Transaction basic information
    transaction_date: date = Field(index=True, description="Transaction date")
    transaction_name: str = Field(description="Institution description")
    transaction_type: str = Field(index=True, description="buy, sell, cancel, cash, fee, transfer")
    transaction_subtype: str = Field(index=True, description="dividend, buy, sell, etc.")
    
    # Financial details
    amount: float = Field(description="Transaction amount (positive = debit, negative = credit)")
    quantity: float = Field(description="Securities quantity (positive = buy, negative = sell)")
    price: float = Field(description="Price per security")
    fees: Optional[float] = Field(description="Combined fees")
    
    # Currency
    iso_currency_code: Optional[str] = Field(default="USD")
    unofficial_currency_code: Optional[str] = None
    
    # Transaction relationships
    cancel_transaction_id: Optional[str] = Field(description="ID of canceled transaction")
    
    # Status and metadata
    status: str = Field(default="posted", index=True)
    last_updated: Optional[datetime] = None
    
    # Environment and timestamps
    environment: str = Field(default="sandbox", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


# ==========================================
# Investment History Tracking
# ==========================================

class PlaidInvestmentHistory(SQLModel, table=True):
    """Track changes to investment data over time"""
    __tablename__ = "plaid_investment_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")
    account_id: Optional[str] = ULIDForeignKey("plaid_investment_accounts.plaid_account_id")
    security_id: Optional[str] = ULIDForeignKey("plaid_investment_securities.security_id")
    holding_id: Optional[str] = ULIDForeignKey("plaid_investment_holdings.id")
    transaction_id: Optional[str] = ULIDForeignKey("plaid_investment_transactions.id")
    
    # Change tracking
    record_type: str = Field(index=True, description="account, holding, security, transaction")
    field_name: str = Field(index=True)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_type: str = Field(default="update")  # create, update, delete
    change_source: str = Field(default="api_sync")  # api_sync, webhook, manual
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# ==========================================
# Investment Webhook Events
# ==========================================

class PlaidInvestmentWebhookEvent(SQLModel, table=True):
    """Track webhook events related to investments"""
    __tablename__ = "plaid_investment_webhook_events"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Webhook details
    webhook_type: str = Field(index=True)  # HOLDINGS, INVESTMENTS_TRANSACTIONS
    webhook_code: str = Field(index=True)  # DEFAULT_UPDATE, HISTORICAL_UPDATE
    webhook_payload: str = Field(sa_column=Column(Text))
    
    # Holdings webhook data
    new_holdings: Optional[int] = None
    updated_holdings: Optional[int] = None
    
    # Investment transactions webhook data
    new_investments_transactions: Optional[int] = None
    canceled_investments_transactions: Optional[int] = None
    
    # Processing status
    processed: bool = Field(default=False, index=True)
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    
    # Environment and timestamps
    environment: str = Field(index=True)
    received_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# ==========================================
# API Response Models
# ==========================================

class InvestmentHoldingResponse(SQLModel):
    """Response model for investment holding"""
    account_id: str
    security_id: str
    institution_price: float
    institution_price_as_of: Optional[str] = None
    institution_price_datetime: Optional[str] = None
    institution_value: float
    cost_basis: Optional[float] = None
    quantity: float
    iso_currency_code: Optional[str] = None
    unofficial_currency_code: Optional[str] = None
    vested_quantity: Optional[float] = None
    vested_value: Optional[float] = None


class InvestmentSecurityResponse(SQLModel):
    """Response model for investment security"""
    security_id: str
    isin: Optional[str] = None
    cusip: Optional[str] = None
    sedol: Optional[str] = None
    institution_security_id: Optional[str] = None
    institution_id: Optional[str] = None
    proxy_security_id: Optional[str] = None
    name: Optional[str] = None
    ticker_symbol: Optional[str] = None
    is_cash_equivalent: Optional[bool] = None
    type: Optional[str] = None
    close_price: Optional[float] = None
    close_price_as_of: Optional[str] = None
    update_datetime: Optional[str] = None
    iso_currency_code: Optional[str] = None
    unofficial_currency_code: Optional[str] = None
    market_identifier_code: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    option_contract: Optional[Dict[str, Any]] = None
    fixed_income: Optional[Dict[str, Any]] = None


class InvestmentTransactionResponse(SQLModel):
    """Response model for investment transaction"""
    investment_transaction_id: str
    account_id: str
    security_id: Optional[str] = None
    date: str
    name: str
    quantity: float
    amount: float
    price: float
    fees: Optional[float] = None
    type: str
    subtype: str
    iso_currency_code: Optional[str] = None
    unofficial_currency_code: Optional[str] = None
    cancel_transaction_id: Optional[str] = None


class InvestmentAccountResponse(SQLModel):
    """Response model for investment account"""
    account_id: str
    balances: Dict[str, Any]
    mask: Optional[str] = None
    name: str
    official_name: Optional[str] = None
    type: str
    subtype: str
    verification_status: Optional[str] = None
    persistent_account_id: Optional[str] = None
    holder_category: Optional[str] = None


class InvestmentHoldingsResponse(SQLModel):
    """Complete investment holdings response"""
    accounts: List[InvestmentAccountResponse] = []
    holdings: List[InvestmentHoldingResponse] = []
    securities: List[InvestmentSecurityResponse] = []


class InvestmentTransactionsResponse(SQLModel):
    """Complete investment transactions response"""
    accounts: List[InvestmentAccountResponse] = []
    investment_transactions: List[InvestmentTransactionResponse] = []
    securities: List[InvestmentSecurityResponse] = []
    total_investment_transactions: int = 0
