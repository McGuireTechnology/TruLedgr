"""
Plaid Investments Models

Pydantic models for investment holdings, transactions, and securities.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import date

# Import shared models
from ..models import Account

class OptionContract(BaseModel):
    """Details about option contracts"""
    contract_type: str = Field(..., description="Type of option: 'put' or 'call'")
    expiration_date: str = Field(..., description="Option expiration date in ISO 8601 format")
    strike_price: float = Field(..., description="Strike price per share")
    underlying_security_ticker: str = Field(..., description="Ticker of underlying security")

class FixedIncomeYieldRate(BaseModel):
    """Yield rate details for fixed income securities"""
    percentage: Optional[float] = Field(None, description="Yield rate percentage")
    type: Optional[str] = Field(None, description="Type: coupon, coupon_equivalent, discount, yield")

class FixedIncome(BaseModel):
    """Details about fixed income securities"""
    yield_rate: Optional[FixedIncomeYieldRate] = Field(None, description="Yield rate information")
    maturity_date: Optional[str] = Field(None, description="Maturity date in ISO 8601 format")
    issue_date: Optional[str] = Field(None, description="Issue date in ISO 8601 format") 
    face_value: Optional[float] = Field(None, description="Face value per unit of security")

class Security(BaseModel):
    """Model for investment securities"""
    security_id: str = Field(..., description="Plaid security identifier")
    isin: Optional[str] = Field(None, description="12-character ISIN identifier")
    cusip: Optional[str] = Field(None, description="9-character CUSIP identifier") 
    sedol: Optional[str] = Field(None, description="7-character SEDOL identifier")
    institution_security_id: Optional[str] = Field(None, description="Institution-provided security identifier")
    institution_id: Optional[str] = Field(None, description="Plaid institution ID for the security")
    proxy_security_id: Optional[str] = Field(None, description="ID of similar-performance security")
    name: Optional[str] = Field(None, description="Descriptive name of the security")
    ticker_symbol: Optional[str] = Field(None, description="Trading symbol for publicly traded securities")
    is_cash_equivalent: Optional[bool] = Field(None, description="Whether security is cash equivalent")
    type: Optional[str] = Field(None, description="Security type: cash, cryptocurrency, derivative, equity, etf, fixed income, loan, mutual fund, other")
    close_price: Optional[float] = Field(None, description="Close price of previous trading session")
    close_price_as_of: Optional[str] = Field(None, description="Date for which close_price is accurate") 
    update_datetime: Optional[str] = Field(None, description="ISO timestamp when close_price was last updated")
    iso_currency_code: Optional[str] = Field(None, description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code for non-ISO currencies")
    market_identifier_code: Optional[str] = Field(None, description="ISO-10383 Market Identifier Code")
    sector: Optional[str] = Field(None, description="Sector classification (e.g., Finance, Technology)")
    industry: Optional[str] = Field(None, description="Industry classification (e.g., Biotechnology, Airlines)")
    option_contract: Optional[OptionContract] = Field(None, description="Option contract details")
    fixed_income: Optional[FixedIncome] = Field(None, description="Fixed income security details")

class InvestmentHolding(BaseModel):
    """Model for investment holdings"""
    account_id: str = Field(..., description="Account ID associated with the holding")
    security_id: str = Field(..., description="Security ID associated with the holding")
    institution_price: float = Field(..., description="Last price given by institution")
    institution_price_as_of: Optional[str] = Field(None, description="Date when institution_price was current")
    institution_price_datetime: Optional[str] = Field(None, description="ISO datetime when price was current")
    institution_value: float = Field(..., description="Value of the holding as reported by institution")
    cost_basis: Optional[float] = Field(None, description="Total cost basis of holding")
    quantity: float = Field(..., description="Total quantity of asset held")
    iso_currency_code: Optional[str] = Field(None, description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    vested_quantity: Optional[float] = Field(None, description="Total quantity of vested assets")
    vested_value: Optional[float] = Field(None, description="Value of vested holdings")

class InvestmentTransaction(BaseModel):
    """Model for investment transactions"""
    investment_transaction_id: str = Field(..., description="Unique investment transaction ID")
    account_id: str = Field(..., description="Account ID where transaction occurred")
    security_id: Optional[str] = Field(None, description="Security ID related to transaction")
    date: str = Field(..., description="ISO 8601 posting date")
    name: str = Field(..., description="Institution's description of transaction")
    quantity: float = Field(..., description="Number of security units (positive for buy, negative for sell)")
    amount: float = Field(..., description="Complete transaction value (positive for debits, negative for credits)")
    price: float = Field(..., description="Price per security unit")
    fees: Optional[float] = Field(None, description="Combined value of all fees")
    type: str = Field(..., description="Transaction type: buy, sell, cancel, cash, fee, transfer")
    subtype: str = Field(..., description="Transaction subtype (see Plaid docs for full list)")
    iso_currency_code: Optional[str] = Field(None, description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")

# Request/Response Models for Investments API

class InvestmentsHoldingsRequest(BaseModel):
    """Request model for getting investment holdings"""
    access_token: str = Field(..., description="Access token for the connected account")
    account_ids: Optional[List[str]] = Field(None, description="Specific account IDs to retrieve holdings for")

class InvestmentsHoldingsResponse(BaseModel):
    """Response model for investment holdings"""
    accounts: List[Account] = Field(..., description="Investment accounts")
    holdings: List[InvestmentHolding] = Field(..., description="Investment holdings")
    securities: List[Security] = Field(..., description="Securities information")
    request_id: str = Field(..., description="Unique request identifier")
    is_investments_fallback_item: bool = Field(False, description="Whether portfolio was manually created")

class InvestmentsTransactionsRequest(BaseModel):
    """Request model for getting investment transactions"""
    access_token: str = Field(..., description="Access token for the connected account")
    start_date: date = Field(..., description="Earliest date to fetch transactions (YYYY-MM-DD)")
    end_date: date = Field(..., description="Most recent date to fetch transactions (YYYY-MM-DD)")
    account_ids: Optional[List[str]] = Field(None, description="Specific account IDs to retrieve")
    count: int = Field(100, ge=1, le=500, description="Number of transactions to fetch (1-500)")
    offset: int = Field(0, ge=0, description="Number of transactions to skip for pagination")
    async_update: bool = Field(False, description="Whether to use asynchronous extraction for initial data")

class InvestmentsTransactionsResponse(BaseModel):
    """Response model for investment transactions"""
    accounts: List[Account] = Field(..., description="Investment accounts")
    investment_transactions: List[InvestmentTransaction] = Field(..., description="Investment transactions")
    securities: List[Security] = Field(..., description="Securities information")
    total_investment_transactions: int = Field(..., description="Total transactions available")
    request_id: str = Field(..., description="Unique request identifier")
    is_investments_fallback_item: bool = Field(False, description="Whether portfolio was manually created")

class InvestmentsRefreshRequest(BaseModel):
    """Request model for refreshing investment data"""
    access_token: str = Field(..., description="Access token for the connected account")

class InvestmentsRefreshResponse(BaseModel):
    """Response model for investments refresh"""
    request_id: str = Field(..., description="Unique request identifier")

# Investment Webhook Models

class HoldingsWebhookRequest(BaseModel):
    """Model for HOLDINGS webhook requests"""
    webhook_type: str = Field("HOLDINGS", description="Always 'HOLDINGS' for this webhook")
    webhook_code: str = Field("DEFAULT_UPDATE", description="Always 'DEFAULT_UPDATE' for holdings")
    item_id: str = Field(..., description="Plaid item ID")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if applicable")
    new_holdings: int = Field(..., description="Number of new holdings detected")
    updated_holdings: int = Field(..., description="Number of updated holdings detected")
    environment: str = Field("production", description="Plaid environment")

class InvestmentsTransactionsWebhookRequest(BaseModel):
    """Model for INVESTMENTS_TRANSACTIONS webhook requests"""
    webhook_type: str = Field("INVESTMENTS_TRANSACTIONS", description="Always 'INVESTMENTS_TRANSACTIONS'")
    webhook_code: str = Field(..., description="DEFAULT_UPDATE or HISTORICAL_UPDATE")
    item_id: str = Field(..., description="Plaid item ID")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if applicable")
    new_investments_transactions: int = Field(..., description="Number of new investment transactions")
    canceled_investments_transactions: int = Field(..., description="Number of canceled investment transactions")
    environment: str = Field("production", description="Plaid environment")