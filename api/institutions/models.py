"""
Institutions Models

Core institution models that aggregate data from multiple sources:
- Plaid institutions (via api.plaid.institutions)
- Manual institution entries
- Other banking integrations

This provides a unified view of all financial institutions.
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime, Boolean
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import func, Index
from enum import Enum

from api.common.ulid_utils import ULIDPrimaryKey, ULIDForeignKey


class InstitutionType(str, Enum):
    """Type of financial institution"""
    BANK = "bank"
    CREDIT_UNION = "credit_union"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    FINTECH = "fintech"
    OTHER = "other"


class InstitutionSource(str, Enum):
    """Source of institution data"""
    PLAID = "plaid"
    MANUAL = "manual"
    YODLEE = "yodlee"  # Future integration
    FINICITY = "finicity"  # Future integration
    OTHER = "other"


class Institution(SQLModel, table=True):
    """
    Core Institution model - aggregates data from all sources
    
    This is the single source of truth for institutions in TruLedgr,
    pulling data from Plaid and allowing manual institution creation.
    """
    __tablename__ = "institutions"
    
    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()
    
    # Core institution information
    name: str = Field(index=True, description="Institution display name")
    official_name: Optional[str] = Field(None, description="Official legal name")
    common_name: Optional[str] = Field(None, description="Commonly used name")
    
    # Institution classification
    institution_type: InstitutionType = Field(default=InstitutionType.BANK, index=True)
    primary_source: InstitutionSource = Field(index=True, description="Primary data source")
    
    # External identifiers
    plaid_institution_id: Optional[str] = Field(None, index=True, description="Plaid institution ID")
    routing_numbers: Optional[str] = Field(None, description="Comma-separated routing numbers")
    swift_code: Optional[str] = Field(None, description="SWIFT/BIC code for international")
    
    # Contact and location information
    website: Optional[str] = None
    phone: Optional[str] = None
    primary_color: Optional[str] = Field(None, description="Brand primary color (hex)")
    logo_url: Optional[str] = None
    
    # Geographic information
    country_codes: Optional[str] = Field(None, description="Comma-separated country codes")
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: str = Field(default="US")
    
    # Supported products and capabilities
    supports_transactions: bool = Field(default=True)
    supports_auth: bool = Field(default=False, description="Account/routing verification")
    supports_identity: bool = Field(default=False)
    supports_investments: bool = Field(default=False)
    supports_liabilities: bool = Field(default=False)
    supports_assets: bool = Field(default=False)
    
    # Integration status
    is_active: bool = Field(default=True, index=True)
    plaid_enabled: bool = Field(default=False, index=True)
    manual_entry_allowed: bool = Field(default=True, description="Allow manual account creation")
    
    # Health and status tracking
    health_status: str = Field(default="healthy", index=True, description="healthy, degraded, down")
    last_health_check: Optional[datetime] = None
    plaid_sync_errors: int = Field(default=0, description="Count of recent sync errors")
    
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
    last_plaid_sync: Optional[datetime] = Field(None, description="Last sync with Plaid data")
    
    # Helper properties
    @property
    def routing_numbers_list(self) -> List[str]:
        """Get routing numbers as a list"""
        if self.routing_numbers:
            return [rn.strip() for rn in self.routing_numbers.split(",") if rn.strip()]
        return []
    
    @routing_numbers_list.setter
    def routing_numbers_list(self, value: List[str]):
        """Set routing numbers from a list"""
        self.routing_numbers = ",".join(value) if value else None
    
    @property
    def country_codes_list(self) -> List[str]:
        """Get country codes as a list"""
        if self.country_codes:
            return [cc.strip().upper() for cc in self.country_codes.split(",") if cc.strip()]
        return ["US"]
    
    @country_codes_list.setter
    def country_codes_list(self, value: List[str]):
        """Set country codes from a list"""
        self.country_codes = ",".join([cc.upper() for cc in value]) if value else None
    
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


class InstitutionSourceMapping(SQLModel, table=True):
    """
    Maps institution data from different sources
    
    Tracks how institution data from various sources (Plaid, manual, etc.)
    maps to the core Institution record.
    """
    __tablename__ = "institution_source_mappings"
    
    id: Optional[str] = ULIDPrimaryKey()
    institution_id: str = ULIDForeignKey("institutions.id")
    
    # Source information
    source: InstitutionSource = Field(index=True)
    source_institution_id: str = Field(index=True, description="ID in the source system")
    source_name: str = Field(description="Name from the source system")
    
    # Mapping metadata
    confidence_score: float = Field(default=1.0, description="Confidence in mapping (0-1)")
    is_primary: bool = Field(default=False, description="Primary source for this institution")
    
    # Source-specific data (JSON)
    source_metadata: Optional[str] = Field(None, sa_column=Column(Text), description="JSON metadata from source")
    
    # Status tracking
    is_active: bool = Field(default=True)
    last_verified: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


# Add database indexes for performance
Institution.__table_args__ = (
    Index('ix_institutions_name_search', 'name'),
    Index('ix_institutions_plaid_id', 'plaid_institution_id'),
    Index('ix_institutions_type_status', 'institution_type', 'is_active'),
    Index('ix_institutions_source_health', 'primary_source', 'health_status'),
)

InstitutionSourceMapping.__table_args__ = (
    Index('ix_source_mappings_lookup', 'source', 'source_institution_id'),
    Index('ix_source_mappings_institution', 'institution_id', 'is_active'),
)


# API Response Models
class InstitutionResponse(SQLModel):
    """API response model for institutions"""
    id: str
    name: str
    official_name: Optional[str] = None
    institution_type: InstitutionType
    primary_source: InstitutionSource
    
    # Integration status
    plaid_enabled: bool
    supports_transactions: bool
    supports_auth: bool
    supports_identity: bool
    supports_investments: bool
    supports_liabilities: bool
    
    # Visual elements
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    website: Optional[str] = None
    
    # Status
    health_status: str
    is_active: bool
    
    # Location
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: str
    
    # Metadata
    created_at: datetime
    updated_at: datetime


class InstitutionSearchResponse(SQLModel):
    """Response model for institution search"""
    institutions: List[InstitutionResponse]
    total_count: int
    has_more: bool
    search_query: Optional[str] = None


class InstitutionCreateRequest(SQLModel):
    """Request model for creating a new institution"""
    name: str = Field(..., min_length=1, max_length=200)
    official_name: Optional[str] = None
    institution_type: InstitutionType = InstitutionType.BANK
    
    # Optional details
    website: Optional[str] = None
    phone: Optional[str] = None
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: str = "US"
    
    # Routing information
    routing_numbers: Optional[List[str]] = None
    swift_code: Optional[str] = None
    
    # Capabilities
    supports_transactions: bool = True
    supports_auth: bool = False
    supports_identity: bool = False
    supports_investments: bool = False
    supports_liabilities: bool = False
    
    # Metadata
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class InstitutionUpdateRequest(SQLModel):
    """Request model for updating an institution"""
    name: Optional[str] = None
    official_name: Optional[str] = None
    institution_type: Optional[InstitutionType] = None
    
    # Optional details
    website: Optional[str] = None
    phone: Optional[str] = None
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    
    # Capabilities
    supports_transactions: Optional[bool] = None
    supports_auth: Optional[bool] = None
    supports_identity: Optional[bool] = None
    supports_investments: Optional[bool] = None
    supports_liabilities: Optional[bool] = None
    
    # Status
    is_active: Optional[bool] = None
    manual_entry_allowed: Optional[bool] = None
    
    # Metadata
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
