"""
Plaid Link Models

Pydantic models for Link token creation and public token exchange.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class CountryCode(str, Enum):
    """Supported country codes for Link"""
    US = "US"
    GB = "GB"
    ES = "ES"
    NL = "NL"
    FR = "FR"
    IE = "IE"
    CA = "CA"

class PlaidProduct(str, Enum):
    """Plaid products that can be enabled for Link"""
    TRANSACTIONS = "transactions"
    AUTH = "auth"
    IDENTITY = "identity"
    ASSETS = "assets"
    INVESTMENTS = "investments"
    LIABILITIES = "liabilities"
    PAYMENT_INITIATION = "payment_initiation"
    DEPOSIT_SWITCH = "deposit_switch"
    STANDING_ORDERS = "standing_orders"
    TRANSFER = "transfer"
    EMPLOYMENT = "employment"
    INCOME_VERIFICATION = "income_verification"
    IDENTITY_VERIFICATION = "identity_verification"
    MONITOR = "monitor"

class LinkUser(BaseModel):
    """User information for Link token creation"""
    client_user_id: str = Field(..., description="Unique identifier for the user")
    legal_name: Optional[str] = Field(None, description="User's legal name")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    phone_number_verified_time: Optional[str] = Field(None, description="Phone verification time")
    email_address: Optional[str] = Field(None, description="User's email address")
    email_address_verified_time: Optional[str] = Field(None, description="Email verification time")

class LinkTokenCreateRequest(BaseModel):
    """Request to create a Link token"""
    client_name: str = Field(..., description="Name of your application")
    country_codes: List[CountryCode] = Field(..., description="List of country codes")
    language: str = Field("en", description="Language for Link UI")
    user: LinkUser = Field(..., description="User information")
    products: List[PlaidProduct] = Field(..., description="List of Plaid products to enable")
    webhook: Optional[str] = Field(None, description="Webhook URL for notifications")
    link_customization_name: Optional[str] = Field(None, description="Link customization name")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")
    android_package_name: Optional[str] = Field(None, description="Android app package name")
    account_filters: Optional[Dict[str, Any]] = Field(None, description="Account type filters")

class LinkTokenCreateResponse(BaseModel):
    """Response from Link token creation"""
    link_token: str = Field(..., description="Link token for initialization")
    expiration: str = Field(..., description="Link token expiration time")
    request_id: str = Field(..., description="Request identifier")

class PublicTokenExchangeRequest(BaseModel):
    """Request to exchange public token for access token"""
    public_token: str = Field(..., description="Public token from Link onSuccess")

class PublicTokenExchangeResponse(BaseModel):
    """Response from public token exchange"""
    access_token: str = Field(..., description="Access token for API requests")
    item_id: str = Field(..., description="Unique identifier for the Item")
    request_id: str = Field(..., description="Request identifier")

class LinkEventRequest(BaseModel):
    """Request for Link event metadata"""
    public_token: Optional[str] = Field(None, description="Public token if available")
    link_session_id: str = Field(..., description="Link session identifier")
    request_id: Optional[str] = Field(None, description="Request identifier")
    
class LinkEventResponse(BaseModel):
    """Response for Link event tracking"""
    success: bool = Field(True, description="Event tracked successfully")
    request_id: str = Field(..., description="Request identifier")
