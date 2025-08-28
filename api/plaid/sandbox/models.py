"""
Plaid Sandbox Models

Pydantic models for Sandbox testing and simulation operations.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from enum import Enum

class SandboxItemFireWebhookCode(str, Enum):
    """Webhook codes that can be fired in sandbox"""
    INITIAL_UPDATE = "INITIAL_UPDATE"
    HISTORICAL_UPDATE = "HISTORICAL_UPDATE"
    DEFAULT_UPDATE = "DEFAULT_UPDATE"
    TRANSACTIONS_REMOVED = "TRANSACTIONS_REMOVED"

class SandboxItemSetVerificationStatusCode(str, Enum):
    """Verification status codes for sandbox"""
    AUTOMATICALLY_VERIFIED = "automatically_verified"
    PENDING_AUTOMATIC_VERIFICATION = "pending_automatic_verification"
    PENDING_MANUAL_VERIFICATION = "pending_manual_verification"
    MANUALLY_VERIFIED = "manually_verified"
    VERIFICATION_EXPIRED = "verification_expired"
    VERIFICATION_FAILED = "verification_failed"

class SandboxPublicTokenCreateRequest(BaseModel):
    """Request to create a sandbox public token"""
    institution_id: str = Field(..., description="Institution ID")
    initial_products: List[str] = Field(..., description="Initial products to enable")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")

class SandboxPublicTokenCreateResponse(BaseModel):
    """Response for sandbox public token creation"""
    public_token: str = Field(..., description="Public token for testing")
    request_id: str = Field(..., description="Request identifier")

class SandboxItemFireWebhookRequest(BaseModel):
    """Request to fire a webhook in sandbox"""
    access_token: str = Field(..., description="Access token for the Item")
    webhook_code: SandboxItemFireWebhookCode = Field(..., description="Webhook code to fire")

class SandboxItemFireWebhookResponse(BaseModel):
    """Response for firing a webhook"""
    webhook_fired: bool = Field(True, description="Whether webhook was fired")
    request_id: str = Field(..., description="Request identifier")

class SandboxItemSetVerificationStatusRequest(BaseModel):
    """Request to set verification status in sandbox"""
    access_token: str = Field(..., description="Access token for the Item")
    account_id: str = Field(..., description="Account ID")
    verification_status: SandboxItemSetVerificationStatusCode = Field(..., description="Verification status")

class SandboxItemSetVerificationStatusResponse(BaseModel):
    """Response for setting verification status"""
    verification_status_updated: bool = Field(True, description="Whether status was updated")
    request_id: str = Field(..., description="Request identifier")

class SandboxItemResetLoginRequest(BaseModel):
    """Request to reset login for sandbox item"""
    access_token: str = Field(..., description="Access token for the Item")

class SandboxItemResetLoginResponse(BaseModel):
    """Response for resetting login"""
    reset_login: bool = Field(True, description="Whether login was reset")
    request_id: str = Field(..., description="Request identifier")

class SandboxTransactionsRefreshRequest(BaseModel):
    """Request to refresh transactions in sandbox"""
    access_token: str = Field(..., description="Access token for the Item")

class SandboxTransactionsRefreshResponse(BaseModel):
    """Response for refreshing transactions"""
    transactions_refreshed: bool = Field(True, description="Whether transactions were refreshed")
    request_id: str = Field(..., description="Request identifier")
