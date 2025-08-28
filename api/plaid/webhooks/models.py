"""
Plaid Webhooks Models

Pydantic models for webhook verification and handling.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

# Base Webhook Models

class WebhookVerificationRequest(BaseModel):
    """Request model for webhook verification"""
    webhook_type: str = Field(..., description="Type of webhook (TRANSACTIONS, ITEM, etc.)")
    webhook_code: str = Field(..., description="Specific webhook code")
    item_id: str = Field(..., description="Plaid item ID")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if applicable")
    new_transactions: Optional[int] = Field(None, description="Number of new transactions")
    removed_transactions: Optional[List[str]] = Field(None, description="IDs of removed transactions")
    consent_expiration_time: Optional[str] = Field(None, description="ISO timestamp of consent expiration")
    account_id: Optional[str] = Field(None, description="Account ID for account-specific webhooks")
    new_webhook_url: Optional[str] = Field(None, description="New webhook URL if updated")
    environment: Optional[str] = Field("production", description="Plaid environment")

class WebhookResponse(BaseModel):
    """Response model for webhook processing"""
    status: str = Field(..., description="Processing status: processed, error, unhandled")
    action: Optional[str] = Field(None, description="Action taken in response to webhook")
    item_id: Optional[str] = Field(None, description="Plaid item ID")
    message: str = Field(..., description="Human-readable processing result")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the processing")

class WebhookEventLog(BaseModel):
    """Model for logging webhook events"""
    webhook_type: str
    webhook_code: str
    item_id: str
    processed_at: datetime
    status: str
    response: Dict[str, Any]
    raw_payload: Optional[Dict[str, Any]] = None

class WebhookStatusResponse(BaseModel):
    """Response model for webhook status and configuration"""
    webhook_configured: bool = Field(..., description="Whether webhooks are configured")
    webhook_secret_set: bool = Field(..., description="Whether webhook secret is configured")
    supported_webhook_types: List[str] = Field(..., description="List of supported webhook types")
    webhook_codes_by_type: Dict[str, List[str]] = Field(..., description="Supported codes for each webhook type")
    last_webhook_received: Optional[datetime] = Field(None, description="Timestamp of last webhook received")
    total_webhooks_processed: Optional[int] = Field(None, description="Total number of webhooks processed")

# Specific Webhook Type Models

class ItemWebhookRequest(BaseModel):
    """Specific model for ITEM webhook requests"""
    webhook_type: str = Field("ITEM", description="Always 'ITEM' for this webhook")
    webhook_code: str = Field(..., description="ERROR, PENDING_EXPIRATION, USER_PERMISSION_REVOKED, etc.")
    item_id: str = Field(..., description="Plaid item ID")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details for ERROR webhook")
    consent_expiration_time: Optional[str] = Field(None, description="Consent expiration timestamp")
    new_webhook_url: Optional[str] = Field(None, description="New webhook URL")
    environment: str = Field("production", description="Plaid environment")

class AuthWebhookRequest(BaseModel):
    """Specific model for AUTH webhook requests"""
    webhook_type: str = Field("AUTH", description="Always 'AUTH' for this webhook")
    webhook_code: str = Field(..., description="AUTOMATICALLY_VERIFIED or VERIFICATION_EXPIRED")
    item_id: str = Field(..., description="Plaid item ID")
    account_id: str = Field(..., description="Account ID that was verified or expired")
    environment: str = Field("production", description="Plaid environment")