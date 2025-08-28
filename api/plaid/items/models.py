"""
Plaid Items Models

Database and API models for Item management operations.
"""

from sqlmodel import SQLModel, Field, Column, String, DateTime
from typing import Optional, List
from datetime import datetime
from sqlalchemy import func
from pydantic import BaseModel
from enum import Enum
import json

from api.common.ulid_utils import ULIDPrimaryKey, ULIDForeignKey


class PlaidEnvironment(str, Enum):
    """Plaid environment enumeration"""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class ItemStatus(str, Enum):
    """Plaid item status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class WebhookEventType(str, Enum):
    """Plaid webhook event types for items"""
    ERROR = "ERROR"
    LOGIN_REPAIRED = "LOGIN_REPAIRED"
    NEW_ACCOUNTS_AVAILABLE = "NEW_ACCOUNTS_AVAILABLE"
    PENDING_DISCONNECT = "PENDING_DISCONNECT"
    PENDING_EXPIRATION = "PENDING_EXPIRATION"
    USER_PERMISSION_REVOKED = "USER_PERMISSION_REVOKED"
    USER_ACCOUNT_REVOKED = "USER_ACCOUNT_REVOKED"
    WEBHOOK_UPDATE_ACKNOWLEDGED = "WEBHOOK_UPDATE_ACKNOWLEDGED"


# Database Model
class PlaidItem(SQLModel, table=True):
    """Plaid Item database model - represents a financial institution connection with ULID"""
    __tablename__ = "plaid_items"
    
    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")
    
    # Plaid identifiers
    item_id: str = Field(unique=True, index=True)
    access_token: str = Field()
    
    # Institution information
    institution_id: str = Field(index=True)
    institution_name: str = Field()
    
    # Environment and status
    environment: str = Field(default="sandbox")
    status: str = Field(default="active")
    
    # Error information (from Plaid Item.error object)
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_display_message: Optional[str] = None
    error_documentation_url: Optional[str] = None
    error_suggested_action: Optional[str] = None
    
    # Product information (stored as JSON strings)
    available_products: Optional[str] = Field(default=None)  # JSON array
    billed_products: Optional[str] = Field(default=None)     # JSON array
    products: Optional[str] = Field(default=None)            # JSON array
    consented_products: Optional[str] = Field(default=None)  # JSON array
    
    # Consent and authorization
    auth_method: Optional[str] = None  # INSTANT_AUTH, INSTANT_MATCH, etc.
    consent_expiration_time: Optional[datetime] = None
    consented_use_cases: Optional[str] = Field(default=None)  # JSON array
    consented_data_scopes: Optional[str] = Field(default=None)  # JSON array
    
    # Update behavior
    update_type: str = Field(default="background")  # background, user_present_required
    
    # Plaid item creation timestamp (from Plaid API)
    plaid_created_at: Optional[datetime] = None
    
    # Timestamps (our system timestamps)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    last_sync: Optional[datetime] = None
    
    # Webhook URL
    webhook_url: Optional[str] = None
    
    @property
    def available_products_list(self) -> List[str]:
        """Get available products as list"""
        if self.available_products:
            try:
                return json.loads(self.available_products)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @available_products_list.setter
    def available_products_list(self, value: List[str]):
        """Set available products from list"""
        self.available_products = json.dumps(value)
    
    @property
    def billed_products_list(self) -> List[str]:
        """Get billed products as list"""
        if self.billed_products:
            try:
                return json.loads(self.billed_products)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @billed_products_list.setter
    def billed_products_list(self, value: List[str]):
        """Set billed products from list"""
        self.billed_products = json.dumps(value)
    
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
    def consented_products_list(self) -> List[str]:
        """Get consented products as list"""
        if self.consented_products:
            try:
                return json.loads(self.consented_products)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @consented_products_list.setter
    def consented_products_list(self, value: List[str]):
        """Set consented products from list"""
        self.consented_products = json.dumps(value)
    
    @property
    def consented_use_cases_list(self) -> List[str]:
        """Get consented use cases as list"""
        if self.consented_use_cases:
            try:
                return json.loads(self.consented_use_cases)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @consented_use_cases_list.setter
    def consented_use_cases_list(self, value: List[str]):
        """Set consented use cases from list"""
        self.consented_use_cases = json.dumps(value)
    
    @property
    def consented_data_scopes_list(self) -> List[str]:
        """Get consented data scopes as list"""
        if self.consented_data_scopes:
            try:
                return json.loads(self.consented_data_scopes)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @consented_data_scopes_list.setter
    def consented_data_scopes_list(self, value: List[str]):
        """Set consented data scopes from list"""
        self.consented_data_scopes = json.dumps(value)


# Related Tables for comprehensive Item management
class PlaidItemStatusHistory(SQLModel, table=True):
    """Track status changes and errors for Plaid Items over time"""
    __tablename__ = "plaid_item_status_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Status information
    status: str = Field()  # active, inactive, error
    previous_status: Optional[str] = None
    
    # Error information (if status is error)
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_display_message: Optional[str] = None
    
    # Change metadata
    change_reason: Optional[str] = None  # webhook, manual_sync, user_action, etc.
    environment: str = Field()
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class PlaidItemWebhookEvent(SQLModel, table=True):
    """Track webhook events received for Plaid Items"""
    __tablename__ = "plaid_item_webhook_events"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Webhook information
    webhook_type: str = Field(default="ITEM")  # Always ITEM for item webhooks
    webhook_code: str = Field()  # ERROR, LOGIN_REPAIRED, etc.
    
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
        self.webhook_payload = json.dumps(value)


class PlaidItemProductHistory(SQLModel, table=True):
    """Track product changes for Plaid Items"""
    __tablename__ = "plaid_item_product_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Product information
    product_name: str = Field()  # transactions, auth, identity, etc.
    action: str = Field()  # added, removed, billed, consented
    
    # Change metadata
    change_reason: Optional[str] = None
    environment: str = Field()
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# API Models
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

class PlaidItemResponse(SQLModel):
    """Response model for Plaid items"""
    id: str  # ULID
    item_id: str
    institution_id: str
    institution_name: str
    environment: PlaidEnvironment
    status: ItemStatus
    
    # Error information
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_display_message: Optional[str] = None
    error_documentation_url: Optional[str] = None
    error_suggested_action: Optional[str] = None
    
    # Product information
    available_products: List[str] = []
    billed_products: List[str] = []
    products: List[str] = []
    consented_products: List[str] = []
    
    # Consent and authorization
    auth_method: Optional[str] = None
    consent_expiration_time: Optional[datetime] = None
    consented_use_cases: List[str] = []
    consented_data_scopes: List[str] = []
    
    # Update behavior
    update_type: str = "background"
    
    # Timestamps
    plaid_created_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    
    # Additional metadata
    accounts_count: int = 0
    webhook_url: Optional[str] = None
