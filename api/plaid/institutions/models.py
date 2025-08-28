"""
Plaid Institutions Models

Database and API models for Institution search and retrieval operations.
"""

from sqlmodel import SQLModel, Field, Column, String, DateTime, Text
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import func
from pydantic import BaseModel
from enum import Enum
import json

from api.common.ulid_utils import ULIDPrimaryKey


class CountryCode(str, Enum):
    """Supported country codes"""
    US = "US"
    GB = "GB"
    ES = "ES"
    NL = "NL"
    FR = "FR"
    IE = "IE"
    CA = "CA"

class PlaidProduct(str, Enum):
    """Plaid products"""
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


# Database Model
class PlaidInstitution(SQLModel, table=True):
    """Plaid Institution database model - represents a financial institution"""
    __tablename__ = "plaid_institutions"
    
    id: Optional[str] = ULIDPrimaryKey()
    
    # Plaid identifiers
    institution_id: str = Field(unique=True, index=True)
    
    # Institution information
    name: str = Field(index=True)
    logo: Optional[str] = None
    primary_color: Optional[str] = None
    url: Optional[str] = None
    
    # Products and country support
    products: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string
    country_codes: Optional[str] = Field(default=None)  # JSON string
    
    # Banking identifiers
    routing_numbers: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON array
    dtc_numbers: Optional[str] = Field(default=None)  # JSON array
    
    # Features and status
    oauth: bool = Field(default=False)
    status: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON object with detailed status
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    @property
    def products_list(self) -> List[str]:
        """Get products as list"""
        if self.products:
            try:
                return json.loads(self.products)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @products_list.setter
    def products_list(self, value: List[str]):
        """Set products from list"""
        self.products = json.dumps(value)
    
    @property
    def country_codes_list(self) -> List[str]:
        """Get country codes as list"""
        if self.country_codes:
            try:
                return json.loads(self.country_codes)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @country_codes_list.setter
    def country_codes_list(self, value: List[str]):
        """Set country codes from list"""
        self.country_codes = json.dumps(value)
    
    @property
    def routing_numbers_list(self) -> List[str]:
        """Get routing numbers as list"""
        if self.routing_numbers:
            try:
                return json.loads(self.routing_numbers)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @routing_numbers_list.setter
    def routing_numbers_list(self, value: List[str]):
        """Set routing numbers from list"""
        self.routing_numbers = json.dumps(value)
    
    @property
    def dtc_numbers_list(self) -> List[str]:
        """Get DTC numbers as list"""
        if self.dtc_numbers:
            try:
                return json.loads(self.dtc_numbers)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @dtc_numbers_list.setter
    def dtc_numbers_list(self, value: List[str]):
        """Set DTC numbers from list"""
        self.dtc_numbers = json.dumps(value)
    
    @property
    def status_dict(self) -> Dict[str, Any]:
        """Get status as dictionary"""
        if self.status:
            try:
                return json.loads(self.status)
            except (json.JSONDecodeError, TypeError):
                pass
        return {}
    
    @status_dict.setter
    def status_dict(self, value: Dict[str, Any]):
        """Set status from dictionary"""
        self.status = json.dumps(value)


# API Models
class StatusBreakdown(BaseModel):
    """Status breakdown information"""
    success: float = Field(..., description="Success rate (0.0 to 1.0)")
    error_plaid: float = Field(..., description="Plaid error rate")
    error_institution: float = Field(..., description="Institution error rate")
    refresh_interval: Optional[str] = Field(None, description="Refresh interval (for updates)")

class ProductStatus(BaseModel):
    """Status for a specific product"""
    status: str = Field(..., description="Status (HEALTHY, DEGRADED, DOWN)")
    last_status_change: str = Field(..., description="ISO 8601 timestamp of last status change")
    breakdown: StatusBreakdown = Field(..., description="Detailed breakdown")

class InvestmentsStatus(BaseModel):
    """Investments status with nested liabilities"""
    status: str = Field(..., description="Status (HEALTHY, DEGRADED, DOWN)")
    last_status_change: str = Field(..., description="ISO 8601 timestamp of last status change")
    breakdown: StatusBreakdown = Field(..., description="Detailed breakdown")
    liabilities: Optional[ProductStatus] = Field(None, description="Nested liabilities status")

class InstitutionStatus(BaseModel):
    """Comprehensive institution status information"""
    item_logins: Optional[ProductStatus] = Field(None, description="Item login status")
    transactions_updates: Optional[ProductStatus] = Field(None, description="Transaction updates status")
    auth: Optional[ProductStatus] = Field(None, description="Auth product status")
    identity: Optional[ProductStatus] = Field(None, description="Identity product status")
    investments: Optional[InvestmentsStatus] = Field(None, description="Investments product status")
    investments_updates: Optional[ProductStatus] = Field(None, description="Investment updates status")
    liabilities_updates: Optional[ProductStatus] = Field(None, description="Liability updates status")

class Institution(BaseModel):
    """Institution information"""
    institution_id: str = Field(..., description="Plaid institution identifier")
    name: str = Field(..., description="Institution name")
    products: List[PlaidProduct] = Field(..., description="Supported products")
    country_codes: List[CountryCode] = Field(..., description="Supported countries")
    url: Optional[str] = Field(None, description="Institution website URL")
    primary_color: Optional[str] = Field(None, description="Primary brand color")
    logo: Optional[str] = Field(None, description="Logo URL")
    routing_numbers: List[str] = Field(default_factory=list, description="Bank routing numbers")
    dtc_numbers: List[str] = Field(default_factory=list, description="DTC numbers for investment accounts")
    oauth: bool = Field(default=False, description="OAuth authentication support")
    status: Optional[InstitutionStatus] = Field(None, description="Institution status information")

class InstitutionsGetRequest(BaseModel):
    """Request to get institutions"""
    count: int = Field(100, description="Number of institutions to retrieve", ge=1, le=500)
    offset: int = Field(0, description="Offset for pagination", ge=0)
    country_codes: List[CountryCode] = Field(..., description="Country codes to filter by")
    products: Optional[List[PlaidProduct]] = Field(None, description="Products to filter by")

class InstitutionsSearchRequest(BaseModel):
    """Request to search institutions"""
    query: str = Field(..., description="Search query")
    products: List[PlaidProduct] = Field(..., description="Products to filter by")
    country_codes: List[CountryCode] = Field(..., description="Country codes to filter by")

class InstitutionsGetByIdRequest(BaseModel):
    """Request to get institution by ID"""
    institution_id: str = Field(..., description="Institution ID")
    country_codes: List[CountryCode] = Field(..., description="Country codes")
    include_optional_metadata: Optional[bool] = Field(False, description="Include optional metadata")
    include_status: Optional[bool] = Field(False, description="Include status information")

class InstitutionsResponse(BaseModel):
    """Response for institutions requests"""
    institutions: List[Institution]
    total: int
    request_id: str

class PlaidInstitutionResponse(SQLModel):
    """Response model for Plaid institutions"""
    id: str  # ULID
    institution_id: str
    name: str
    logo: Optional[str] = None
    primary_color: Optional[str] = None
    url: Optional[str] = None
    products: List[str] = []
    country_codes: List[str] = []
    routing_numbers: List[str] = []
    dtc_numbers: List[str] = []
    oauth: bool = False
    status: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    items_count: int = 0  # Number of items for this institution
