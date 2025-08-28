"""
Plaid Link Models - Official Plaid API Compliant

Pydantic models based on official Plaid Link Token Create API documentation.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

# ==========================================
# Enums based on official Plaid documentation
# ==========================================

class CountryCode(str, Enum):
    """Supported country codes for Link - ISO-3166-1 alpha-2"""
    US = "US"
    GB = "GB"
    ES = "ES"
    NL = "NL"
    FR = "FR"
    IE = "IE"
    CA = "CA"
    DE = "DE"
    IT = "IT"
    PL = "PL"
    DK = "DK"
    NO = "NO"
    SE = "SE"
    EE = "EE"
    LT = "LT"
    LV = "LV"
    PT = "PT"
    BE = "BE"
    AT = "AT"
    FI = "FI"

class PlaidProduct(str, Enum):
    """Official Plaid products that can be enabled for Link"""
    ASSETS = "assets"
    AUTH = "auth"
    BEACON = "beacon"
    EMPLOYMENT = "employment"
    IDENTITY = "identity"
    INCOME_VERIFICATION = "income_verification"
    IDENTITY_VERIFICATION = "identity_verification"
    INVESTMENTS = "investments"
    LIABILITIES = "liabilities"
    PAYMENT_INITIATION = "payment_initiation"
    STANDING_ORDERS = "standing_orders"
    SIGNAL = "signal"
    STATEMENTS = "statements"
    TRANSACTIONS = "transactions"
    TRANSFER = "transfer"
    CRA_BASE_REPORT = "cra_base_report"
    CRA_INCOME_INSIGHTS = "cra_income_insights"
    CRA_PARTNER_INSIGHTS = "cra_partner_insights"
    CRA_NETWORK_INSIGHTS = "cra_network_insights"
    CRA_CASHFLOW_INSIGHTS = "cra_cashflow_insights"
    CRA_MONITORING = "cra_monitoring"
    LAYER = "layer"
    PROTECT_LINKED_BANK = "protect_linked_bank"

class OptionalProduct(str, Enum):
    """Products that can be added optionally"""
    AUTH = "auth"
    IDENTITY = "identity"
    INVESTMENTS = "investments"
    LIABILITIES = "liabilities"
    SIGNAL = "signal"
    STATEMENTS = "statements"
    TRANSACTIONS = "transactions"

class AccountSubtype(str, Enum):
    """Account subtypes for filtering"""
    # Depository subtypes
    CHECKING = "checking"
    SAVINGS = "savings"
    HSA = "hsa"
    CD = "cd"
    MONEY_MARKET = "money market"
    PAYPAL = "paypal"
    PREPAID = "prepaid"
    CASH_MANAGEMENT = "cash management"
    EBT = "ebt"
    
    # Credit subtypes
    CREDIT_CARD = "credit card"
    
    # Loan subtypes
    AUTO = "auto"
    BUSINESS = "business"
    COMMERCIAL = "commercial"
    CONSTRUCTION = "construction"
    CONSUMER = "consumer"
    HOME_EQUITY = "home equity"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    LINE_OF_CREDIT = "line of credit"
    STUDENT = "student"
    OTHER = "other"
    
    # Investment subtypes (subset - there are many more)
    BROKERAGE = "brokerage"
    IRA = "ira"
    ROTH = "roth"
    RETIREMENT = "retirement"
    
    # Special value
    ALL = "all"

# ==========================================
# User and Address Models
# ==========================================

class LinkUserName(BaseModel):
    """User's full name for Identity Verification product"""
    given_name: str = Field(..., description="Given name with max length of 100 characters")
    family_name: str = Field(..., description="Family name with max length of 100 characters")

class LinkUserAddress(BaseModel):
    """User's address for Identity Verification and Identity Match"""
    street: str = Field(..., description="Primary street portion with max length of 80 characters")
    street2: Optional[str] = Field(None, description="Secondary street info with max length of 50 characters")
    city: str = Field(..., description="City with max length of 100 characters")
    region: str = Field(..., description="ISO 3166-2 subdivision code (state, province, etc.)")
    postal_code: str = Field(..., description="Postal code, 2-10 alphanumeric characters")
    country: str = Field(..., description="Two-letter ISO country code")

class LinkUserIdNumber(BaseModel):
    """User's ID number for Identity Verification"""
    value: str = Field(..., description="Alpha-numeric ID value with formatting stripped")
    type: str = Field(..., description="Globally unique, human readable ID type")

class LinkUser(BaseModel):
    """User information for Link token creation"""
    client_user_id: str = Field(..., min_length=1, description="Unique identifier for the end user")
    legal_name: Optional[str] = Field(None, description="User's full legal name for micro-deposit verification")
    name: Optional[LinkUserName] = Field(None, description="User's full name for Identity Verification")
    phone_number: Optional[str] = Field(None, description="User's phone number in E.164 format")
    email_address: Optional[str] = Field(None, description="User's email address")
    date_of_birth: Optional[date] = Field(None, description="User's date of birth in yyyy-mm-dd format")
    address: Optional[LinkUserAddress] = Field(None, description="User's address")
    id_number: Optional[LinkUserIdNumber] = Field(None, description="User's ID number")

# ==========================================
# Account Filtering Models
# ==========================================

class AccountFilter(BaseModel):
    """Base account filter"""
    account_subtypes: List[AccountSubtype] = Field(..., description="Array of account subtypes to display")

class DepositoryFilter(AccountFilter):
    """Filter for depository accounts"""
    pass

class CreditFilter(AccountFilter):
    """Filter for credit accounts"""
    pass

class LoanFilter(AccountFilter):
    """Filter for loan accounts"""
    pass

class InvestmentFilter(AccountFilter):
    """Filter for investment accounts"""
    pass

class OtherFilter(AccountFilter):
    """Filter for other account types"""
    pass

class AccountFilters(BaseModel):
    """Account filtering configuration"""
    depository: Optional[DepositoryFilter] = None
    credit: Optional[CreditFilter] = None
    loan: Optional[LoanFilter] = None
    investment: Optional[InvestmentFilter] = None
    other: Optional[OtherFilter] = None

# ==========================================
# Product-Specific Configuration Models
# ==========================================

class TransactionsConfig(BaseModel):
    """Configuration for Transactions product"""
    days_requested: Optional[int] = Field(90, ge=1, le=730, description="Days of transaction history to request")

class AuthConfig(BaseModel):
    """Configuration for Auth product"""
    auth_type_select_enabled: Optional[bool] = Field(False, description="Enable Auth Type Select")
    automated_microdeposits_enabled: Optional[bool] = Field(False, description="Enable Automated Micro-deposits")
    instant_match_enabled: Optional[bool] = Field(True, description="Enable Instant Match")
    same_day_microdeposits_enabled: Optional[bool] = Field(False, description="Enable Same Day Micro-deposits")
    instant_microdeposits_enabled: Optional[bool] = Field(False, description="Enable Instant Micro-deposits")
    sms_microdeposits_verification_enabled: Optional[bool] = Field(True, description="Enable SMS micro-deposits verification")

class UpdateConfig(BaseModel):
    """Configuration for update mode"""
    account_selection_enabled: Optional[bool] = Field(False, description="Enable Account Select in update mode")
    reauthorization_enabled: Optional[bool] = Field(None, description="Override reauthorization scheduling logic")

class InstitutionData(BaseModel):
    """Data to highlight specific institutions"""
    routing_number: Optional[str] = Field(None, description="Routing number to highlight in Link")

class HostedLinkConfig(BaseModel):
    """Configuration for Hosted Link"""
    delivery_method: Optional[str] = Field(None, description="Delivery method: sms or email")
    completion_redirect_uri: Optional[str] = Field(None, description="Redirect URI after completion")
    url_lifetime_seconds: Optional[int] = Field(None, description="Link validity duration in seconds")
    is_mobile_app: Optional[bool] = Field(False, description="Whether opening in mobile OOPWV")

# ==========================================
# Main Request Models
# ==========================================

class LinkTokenCreateRequest(BaseModel):
    """Official Plaid Link Token Create request model"""
    client_name: str = Field(..., min_length=1, max_length=30, description="Application name as displayed in Link")
    language: str = Field("en", min_length=1, description="Language for Link UI")
    country_codes: List[CountryCode] = Field(..., description="Supported country codes", min_length=1)
    user: Optional[LinkUser] = Field(None, description="End user information")
    user_id: Optional[str] = Field(None, description="Unique user ID from /user/create")
    products: Optional[List[PlaidProduct]] = Field(None, description="Plaid products to enable")
    required_if_supported_products: Optional[List[OptionalProduct]] = Field(None, description="Products to enable if supported")
    optional_products: Optional[List[OptionalProduct]] = Field(None, description="Best-effort products")
    additional_consented_products: Optional[List[OptionalProduct]] = Field(None, description="Products to collect consent for")
    webhook: Optional[str] = Field(None, description="Webhook URL for notifications")
    access_token: Optional[str] = Field(None, min_length=1, description="Access token for update mode")
    link_customization_name: Optional[str] = Field(None, description="Link customization name")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")
    android_package_name: Optional[str] = Field(None, description="Android package name")
    institution_data: Optional[InstitutionData] = Field(None, description="Institution highlighting data")
    account_filters: Optional[AccountFilters] = Field(None, description="Account filtering configuration")
    auth: Optional[AuthConfig] = Field(None, description="Auth product configuration")
    transactions: Optional[TransactionsConfig] = Field(None, description="Transactions product configuration")
    update: Optional[UpdateConfig] = Field(None, description="Update mode configuration")
    hosted_link: Optional[HostedLinkConfig] = Field(None, description="Hosted Link configuration")

class LinkTokenCreateResponse(BaseModel):
    """Official Plaid Link Token Create response model"""
    link_token: str = Field(..., description="Link token for initialization")
    expiration: str = Field(..., description="Link token expiration time in ISO 8601 format")
    request_id: str = Field(..., description="Request identifier for troubleshooting")
    hosted_link_url: Optional[str] = Field(None, description="Hosted Link URL if enabled")

# ==========================================
# Public Token Exchange Models
# ==========================================

class PublicTokenExchangeRequest(BaseModel):
    """Request to exchange public token for access token"""
    public_token: str = Field(..., description="Public token from Link onSuccess callback")

class PublicTokenExchangeResponse(BaseModel):
    """Response from public token exchange"""
    access_token: str = Field(..., description="Access token for API requests")
    item_id: str = Field(..., description="Unique identifier for the Item")
    request_id: str = Field(..., description="Request identifier for troubleshooting")

# ==========================================
# Simplified Request Models for TruLedgr
# ==========================================

class TruLedgrLinkTokenRequest(BaseModel):
    """Simplified Link token request for TruLedgr users"""
    products: List[PlaidProduct] = Field(default=[PlaidProduct.TRANSACTIONS, PlaidProduct.AUTH, PlaidProduct.IDENTITY], 
                                       description="Products to enable")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for this user's items")
    country_codes: List[CountryCode] = Field(default=[CountryCode.US], description="Supported countries")
    institution_routing_number: Optional[str] = Field(None, description="Routing number to highlight")
    account_filters: Optional[AccountFilters] = Field(None, description="Account type filters")
    transactions_days: Optional[int] = Field(90, ge=30, le=730, description="Days of transaction history")

class TruLedgrPublicTokenExchangeRequest(BaseModel):
    """Public token exchange request for TruLedgr"""
    public_token: str = Field(..., description="Public token from successful Link flow")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for the new item")

# ==========================================
# Response Models
# ==========================================

class TruLedgrLinkTokenResponse(BaseModel):
    """TruLedgr Link token response"""
    link_token: str = Field(..., description="Link token to initialize frontend")
    expiration: str = Field(..., description="Token expiration time")
    products: List[str] = Field(..., description="Enabled products")
    environment: str = Field(..., description="Plaid environment")
    request_id: str = Field(..., description="Request identifier")

class TruLedgrPublicTokenExchangeResponse(BaseModel):
    """TruLedgr public token exchange response"""
    item_id: str = Field(..., description="Created item ULID")
    plaid_item_id: str = Field(..., description="Plaid's item identifier")
    institution_id: str = Field(..., description="Institution identifier")
    institution_name: str = Field(..., description="Institution name")
    products: List[str] = Field(..., description="Initialized products")
    environment: str = Field(..., description="Environment")
    request_id: str = Field(..., description="Request identifier")
