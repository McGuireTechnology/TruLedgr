"""
Accounts Schemas

Pydantic schemas for account data validation and API responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

from .models import AccountType, AccountSubtype, AccountSource, HolderCategory, AccountStatus


# Base schemas
class AccountBase(BaseModel):
    """Base account schema with common fields"""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Account display name")
    official_name: Optional[str] = Field(None, description="Official account name")
    nickname: Optional[str] = Field(None, description="User-defined nickname")

    account_type: AccountType = Field(..., description="Account type")
    account_subtype: Optional[AccountSubtype] = Field(None, description="Account subtype")
    primary_source: AccountSource = Field(..., description="Primary data source")

    plaid_account_id: Optional[str] = Field(None, description="Plaid account ID")
    account_number: Optional[str] = Field(None, description="Account number (masked)")
    routing_number: Optional[str] = Field(None, description="Routing number")

    holder_category: HolderCategory = Field(default=HolderCategory.PERSONAL, description="Account holder category")

    available_balance: Optional[float] = Field(None, description="Available balance")
    current_balance: Optional[float] = Field(None, description="Current balance")
    limit_balance: Optional[float] = Field(None, description="Credit limit or loan amount")
    iso_currency_code: str = Field(default="USD", description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")

    status: AccountStatus = Field(default=AccountStatus.ACTIVE, description="Account status")
    is_closed: bool = Field(default=False, description="Whether account is closed")

    invert_balance: bool = Field(default=False, description="Invert balance display")
    invert_transactions: bool = Field(default=False, description="Invert transaction amounts display")

    plaid_enabled: bool = Field(default=False, description="Connected via Plaid")
    manual_entry_allowed: bool = Field(default=True, description="Allow manual transaction entry")

    notes: Optional[str] = Field(None, description="Internal notes")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


# Request schemas
class AccountCreate(AccountBase):
    """Schema for creating new accounts"""
    institution_id: str = Field(..., description="Institution ID")
    user_id: str = Field(..., description="User ID")


class AccountUpdate(BaseModel):
    """Schema for updating existing accounts"""
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, description="Account display name")
    official_name: Optional[str] = Field(None, description="Official account name")
    nickname: Optional[str] = Field(None, description="User-defined nickname")

    account_type: Optional[AccountType] = Field(None, description="Account type")
    account_subtype: Optional[AccountSubtype] = Field(None, description="Account subtype")

    account_number: Optional[str] = Field(None, description="Account number (masked)")
    routing_number: Optional[str] = Field(None, description="Routing number")

    holder_category: Optional[HolderCategory] = Field(None, description="Account holder category")

    available_balance: Optional[float] = Field(None, description="Available balance")
    current_balance: Optional[float] = Field(None, description="Current balance")
    limit_balance: Optional[float] = Field(None, description="Credit limit or loan amount")
    iso_currency_code: Optional[str] = Field(None, description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")

    status: Optional[AccountStatus] = Field(None, description="Account status")
    is_closed: Optional[bool] = Field(None, description="Whether account is closed")

    invert_balance: Optional[bool] = Field(None, description="Invert balance display")
    invert_transactions: Optional[bool] = Field(None, description="Invert transaction amounts display")

    plaid_enabled: Optional[bool] = Field(None, description="Connected via Plaid")
    manual_entry_allowed: Optional[bool] = Field(None, description="Allow manual transaction entry")

    notes: Optional[str] = Field(None, description="Internal notes")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class AccountSearchRequest(BaseModel):
    """Schema for searching/filtering accounts"""
    name: Optional[str] = Field(None, description="Search by account name")
    account_type: Optional[AccountType] = Field(None, description="Filter by account type")
    account_subtype: Optional[AccountSubtype] = Field(None, description="Filter by account subtype")
    primary_source: Optional[AccountSource] = Field(None, description="Filter by primary source")
    institution_id: Optional[str] = Field(None, description="Filter by institution ID")
    holder_category: Optional[HolderCategory] = Field(None, description="Filter by holder category")
    status: Optional[AccountStatus] = Field(None, description="Filter by account status")
    is_closed: Optional[bool] = Field(None, description="Filter by closed status")
    plaid_enabled: Optional[bool] = Field(None, description="Filter by Plaid enabled status")
    min_balance: Optional[float] = Field(None, description="Minimum current balance")
    max_balance: Optional[float] = Field(None, description="Maximum current balance")
    tags: Optional[str] = Field(None, description="Filter by tags (comma-separated)")


class PlaidAccountSyncRequest(BaseModel):
    """Schema for syncing account data from Plaid"""
    plaid_account_id: str = Field(..., description="Plaid account ID to sync")
    institution_id: str = Field(..., description="TruLedgr institution ID")
    user_id: str = Field(..., description="User ID")


class AccountBalanceUpdate(BaseModel):
    """Schema for updating account balance"""
    available_balance: Optional[float] = Field(None, description="Available balance")
    current_balance: Optional[float] = Field(None, description="Current balance")
    limit_balance: Optional[float] = Field(None, description="Credit limit or loan amount")
    iso_currency_code: Optional[str] = Field(None, description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    source: str = Field(default="manual", description="Source of balance update")


# Response schemas
class AccountResponse(AccountBase):
    """Schema for account API responses"""
    id: str = Field(..., description="Account ID")
    institution_id: str = Field(..., description="Institution ID")
    user_id: str = Field(..., description="User ID")

    balance_last_updated: Optional[datetime] = Field(None, description="When balance was last updated")
    verification_status: Optional[str] = Field(None, description="Verification status")

    health_status: str = Field(default="healthy", description="Account health status")
    last_health_check: Optional[datetime] = Field(None, description="Last health check")
    plaid_sync_errors: int = Field(default=0, description="Count of recent sync errors")
    last_plaid_sync: Optional[datetime] = Field(None, description="Last sync with Plaid data")

    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Account last update timestamp")

    # Computed fields
    tags_list: Optional[List[str]] = Field(None, description="Tags as a list")
    balance_display: Optional[str] = Field(None, description="Formatted balance for display")
    is_positive_balance: Optional[bool] = Field(None, description="Whether balance is positive")


class AccountListResponse(BaseModel):
    """Schema for paginated account list responses"""
    accounts: List[AccountResponse] = Field(..., description="List of accounts")
    total: int = Field(..., description="Total number of accounts")
    skip: int = Field(..., description="Number of accounts skipped")
    limit: int = Field(..., description="Maximum number of accounts returned")


class AccountSummaryResponse(BaseModel):
    """Schema for account summary/statistics"""
    total_accounts: int = Field(..., description="Total number of accounts")
    active_accounts: int = Field(..., description="Number of active accounts")
    total_balance: float = Field(..., description="Sum of all current balances")
    total_available_balance: float = Field(..., description="Sum of all available balances")

    accounts_by_type: Dict[str, int] = Field(..., description="Count of accounts by type")
    accounts_by_source: Dict[str, int] = Field(..., description="Count of accounts by source")
    accounts_by_status: Dict[str, int] = Field(..., description="Count of accounts by status")


class AccountBalanceHistoryResponse(BaseModel):
    """Schema for account balance history responses"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Balance history record ID")
    account_id: str = Field(..., description="Account ID")

    available_balance: Optional[float] = Field(None, description="Available balance at time")
    current_balance: Optional[float] = Field(None, description="Current balance at time")
    limit_balance: Optional[float] = Field(None, description="Credit limit at time")
    iso_currency_code: str = Field(..., description="Currency at time")

    available_change: Optional[float] = Field(None, description="Change in available balance")
    current_change: Optional[float] = Field(None, description="Change in current balance")

    source: str = Field(..., description="Source of balance update")
    balance_updated_at: Optional[datetime] = Field(None, description="When balance was updated")

    recorded_at: datetime = Field(..., description="When record was created")


class AccountStatusHistoryResponse(BaseModel):
    """Schema for account status history responses"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Status history record ID")
    account_id: str = Field(..., description="Account ID")

    previous_status: Optional[AccountStatus] = Field(None, description="Previous account status")
    new_status: AccountStatus = Field(..., description="New account status")
    previous_closed: Optional[bool] = Field(None, description="Previous closed status")
    new_closed: bool = Field(..., description="New closed status")

    change_reason: Optional[str] = Field(None, description="Reason for status change")
    source: str = Field(..., description="Source of status change")

    changed_at: datetime = Field(..., description="When status changed")
