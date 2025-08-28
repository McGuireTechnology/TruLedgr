"""
Transactions Schemas

Pydantic schemas for transaction API requests and responses.
Provides validation and serialization for transaction operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

from .models import (
    TransactionType,
    TransactionStatus,
    TransactionSource,
    TransactionCategory,
    TransactionSubcategory,
    RecurrencePattern
)


class TransactionBase(BaseModel):
    """Base transaction schema with common fields"""
    model_config = ConfigDict(from_attributes=True)

    # Core transaction information
    amount: float = Field(..., description="Transaction amount (positive for credits, negative for debits)")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    transaction_date: date = Field(..., description="Transaction date")
    transaction_datetime: Optional[datetime] = Field(None, description="Transaction datetime")

    # Transaction identification and naming
    name: str = Field(..., description="Transaction name/description")
    description: Optional[str] = Field(None, description="Detailed description")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")

    # Categorization
    category: Optional[TransactionCategory] = Field(None, description="High-level category")
    subcategory: Optional[TransactionSubcategory] = Field(None, description="Detailed subcategory")
    custom_category: Optional[str] = Field(None, description="Custom category if not in enum")

    # Status and processing
    status: TransactionStatus = Field(default=TransactionStatus.CLEARED, description="Transaction status")
    source: TransactionSource = Field(..., description="Data source")
    is_pending: bool = Field(default=False, description="Whether transaction is pending")

    # Financial details
    iso_currency_code: str = Field(default="USD", description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    exchange_rate: Optional[float] = Field(None, description="Exchange rate if applicable")

    # Check and payment information
    check_number: Optional[str] = Field(None, description="Check number")
    payment_method: Optional[str] = Field(None, description="Payment method used")

    # Location information
    location: Optional[Dict[str, Any]] = Field(None, description="Location data")

    # Counterparty information
    counterparty_name: Optional[str] = Field(None, description="Counterparty name")
    counterparty_type: Optional[str] = Field(None, description="Counterparty type")

    # Visual and web information
    logo_url: Optional[str] = Field(None, description="Transaction/merchant logo URL")
    website: Optional[str] = Field(None, description="Merchant website")

    # Recurring transaction support
    is_recurring: bool = Field(default=False, description="Whether this is a recurring transaction")
    recurrence_pattern: Optional[RecurrencePattern] = Field(None, description="Recurrence pattern")
    recurrence_id: Optional[str] = Field(None, description="ID linking recurring transactions")

    # Tags and notes
    tags: Optional[List[str]] = Field(None, description="Transaction tags")
    notes: Optional[str] = Field(None, description="Internal notes")

    # Reconciliation
    is_reconciled: bool = Field(default=False, description="Whether transaction is reconciled")


class TransactionCreate(TransactionBase):
    """Schema for creating new transactions"""
    # Required relationships
    account_id: str = Field(..., description="Account ID")
    institution_id: str = Field(..., description="Institution ID")
    user_id: str = Field(..., description="User ID")

    # Optional external identifiers
    plaid_transaction_id: Optional[str] = Field(None, description="Plaid transaction ID")
    external_transaction_id: Optional[str] = Field(None, description="External system transaction ID")


class TransactionUpdate(BaseModel):
    """Schema for updating existing transactions"""
    model_config = ConfigDict(from_attributes=True)

    # Core transaction information
    amount: Optional[float] = Field(None, description="Transaction amount")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type")
    transaction_date: Optional[date] = Field(None, description="Transaction date")
    transaction_datetime: Optional[datetime] = Field(None, description="Transaction datetime")

    # Transaction identification and naming
    name: Optional[str] = Field(None, description="Transaction name/description")
    description: Optional[str] = Field(None, description="Detailed description")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")

    # Categorization
    category: Optional[TransactionCategory] = Field(None, description="High-level category")
    subcategory: Optional[TransactionSubcategory] = Field(None, description="Detailed subcategory")
    custom_category: Optional[str] = Field(None, description="Custom category if not in enum")

    # Status and processing
    status: Optional[TransactionStatus] = Field(None, description="Transaction status")
    is_pending: Optional[bool] = Field(None, description="Whether transaction is pending")

    # Financial details
    iso_currency_code: Optional[str] = Field(None, description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    exchange_rate: Optional[float] = Field(None, description="Exchange rate if applicable")

    # Check and payment information
    check_number: Optional[str] = Field(None, description="Check number")
    payment_method: Optional[str] = Field(None, description="Payment method used")

    # Location information
    location: Optional[Dict[str, Any]] = Field(None, description="Location data")

    # Counterparty information
    counterparty_name: Optional[str] = Field(None, description="Counterparty name")
    counterparty_type: Optional[str] = Field(None, description="Counterparty type")

    # Visual and web information
    logo_url: Optional[str] = Field(None, description="Transaction/merchant logo URL")
    website: Optional[str] = Field(None, description="Merchant website")

    # Recurring transaction support
    is_recurring: Optional[bool] = Field(None, description="Whether this is a recurring transaction")
    recurrence_pattern: Optional[RecurrencePattern] = Field(None, description="Recurrence pattern")
    recurrence_id: Optional[str] = Field(None, description="ID linking recurring transactions")

    # Tags and notes
    tags: Optional[List[str]] = Field(None, description="Transaction tags")
    notes: Optional[str] = Field(None, description="Internal notes")

    # Reconciliation
    is_reconciled: Optional[bool] = Field(None, description="Whether transaction is reconciled")


class TransactionResponse(TransactionBase):
    """Schema for transaction API responses"""
    # Primary identifiers
    id: str = Field(..., description="Transaction ID")

    # Relationships
    account_id: str = Field(..., description="Account ID")
    institution_id: str = Field(..., description="Institution ID")
    user_id: str = Field(..., description="User ID")

    # External identifiers
    plaid_transaction_id: Optional[str] = Field(None, description="Plaid transaction ID")
    external_transaction_id: Optional[str] = Field(None, description="External system transaction ID")

    # Reconciliation details
    reconciled_at: Optional[datetime] = Field(None, description="When transaction was reconciled")
    reconciled_by: Optional[str] = Field(None, description="Who reconciled the transaction")

    # Audit information
    created_by: Optional[str] = Field(None, description="Who created the transaction")
    updated_by: Optional[str] = Field(None, description="Who last updated the transaction")

    # Metadata
    confidence_score: Optional[float] = Field(None, description="Confidence score for categorization (0-1)")
    duplicate_of: Optional[str] = Field(None, description="ID of duplicate transaction if applicable")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")

    # Computed properties
    tags_list: List[str] = Field(default_factory=list, description="Tags as a list")
    absolute_amount: float = Field(..., description="Absolute transaction amount")
    is_debit: bool = Field(..., description="Whether transaction is a debit")
    is_credit: bool = Field(..., description="Whether transaction is a credit")


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list responses"""
    transactions: List[TransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    skip: int = Field(..., description="Number of transactions skipped")
    limit: int = Field(..., description="Maximum number of transactions returned")


class TransactionSearchRequest(BaseModel):
    """Schema for transaction search/filtering requests"""
    # Date filtering
    start_date: Optional[date] = Field(None, description="Start date for filtering")
    end_date: Optional[date] = Field(None, description="End date for filtering")

    # Amount filtering
    min_amount: Optional[float] = Field(None, description="Minimum transaction amount")
    max_amount: Optional[float] = Field(None, description="Maximum transaction amount")

    # Categorization filtering
    category: Optional[TransactionCategory] = Field(None, description="Filter by category")
    subcategory: Optional[TransactionSubcategory] = Field(None, description="Filter by subcategory")
    custom_category: Optional[str] = Field(None, description="Filter by custom category")

    # Status filtering
    status: Optional[TransactionStatus] = Field(None, description="Filter by status")
    is_pending: Optional[bool] = Field(None, description="Filter by pending status")
    is_reconciled: Optional[bool] = Field(None, description="Filter by reconciliation status")

    # Source filtering
    source: Optional[TransactionSource] = Field(None, description="Filter by data source")
    plaid_transaction_id: Optional[str] = Field(None, description="Filter by Plaid transaction ID")

    # Relationship filtering
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    institution_id: Optional[str] = Field(None, description="Filter by institution ID")
    user_id: Optional[str] = Field(None, description="Filter by user ID")

    # Text search
    search_text: Optional[str] = Field(None, description="Search in transaction name/description")

    # Merchant filtering
    merchant_name: Optional[str] = Field(None, description="Filter by merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Filter by merchant entity ID")

    # Recurring filtering
    is_recurring: Optional[bool] = Field(None, description="Filter by recurring status")
    recurrence_id: Optional[str] = Field(None, description="Filter by recurrence ID")

    # Tag filtering
    tags: Optional[str] = Field(None, description="Filter by tags (comma-separated)")

    # Sorting
    sort_by: Optional[str] = Field("transaction_date", description="Field to sort by")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc/desc)")


class TransactionSummaryResponse(BaseModel):
    """Schema for transaction summary/statistics responses"""
    # Count statistics
    total_transactions: int = Field(..., description="Total number of transactions")
    pending_transactions: int = Field(..., description="Number of pending transactions")
    reconciled_transactions: int = Field(..., description="Number of reconciled transactions")
    recurring_transactions: int = Field(..., description="Number of recurring transactions")

    # Amount statistics
    total_debits: float = Field(..., description="Total debit amount")
    total_credits: float = Field(..., description="Total credit amount")
    net_amount: float = Field(..., description="Net transaction amount (credits - debits)")

    # Category breakdown
    transactions_by_category: Dict[str, int] = Field(default_factory=dict, description="Transaction count by category")
    amount_by_category: Dict[str, float] = Field(default_factory=dict, description="Transaction amount by category")

    # Source breakdown
    transactions_by_source: Dict[str, int] = Field(default_factory=dict, description="Transaction count by source")
    amount_by_source: Dict[str, float] = Field(default_factory=dict, description="Transaction amount by source")

    # Date range
    date_range_start: Optional[date] = Field(None, description="Start date of summary period")
    date_range_end: Optional[date] = Field(None, description="End date of summary period")


class TransactionReconciliationRequest(BaseModel):
    """Schema for transaction reconciliation requests"""
    account_id: str = Field(..., description="Account ID to reconcile")
    reconciliation_date: date = Field(..., description="Date of reconciliation")
    statement_balance: float = Field(..., description="Balance according to bank statement")
    notes: Optional[str] = Field(None, description="Reconciliation notes")


class TransactionReconciliationResponse(BaseModel):
    """Schema for transaction reconciliation responses"""
    reconciliation_id: str = Field(..., description="Reconciliation ID")
    account_id: str = Field(..., description="Account ID")
    reconciliation_date: date = Field(..., description="Date of reconciliation")
    statement_balance: float = Field(..., description="Balance according to bank statement")
    calculated_balance: float = Field(..., description="Calculated balance from transactions")
    difference: float = Field(..., description="Difference between statement and calculated balance")
    is_balanced: bool = Field(..., description="Whether reconciliation is balanced")
    reconciled_transactions: int = Field(..., description="Number of transactions reconciled")
    outstanding_transactions: int = Field(..., description="Number of outstanding transactions")
    reconciled_by: str = Field(..., description="Who performed the reconciliation")
    notes: Optional[str] = Field(None, description="Reconciliation notes")
    created_at: datetime = Field(..., description="Reconciliation timestamp")


class RecurringTransactionCreate(BaseModel):
    """Schema for creating recurring transaction patterns"""
    name: str = Field(..., description="Name of the recurring transaction")
    description: Optional[str] = Field(None, description="Description")
    recurrence_pattern: RecurrencePattern = Field(..., description="How often this recurs")
    estimated_amount: float = Field(..., description="Estimated transaction amount")
    category: Optional[TransactionCategory] = Field(None, description="Transaction category")
    subcategory: Optional[TransactionSubcategory] = Field(None, description="Transaction subcategory")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")
    user_id: str = Field(..., description="User ID")
    tags: Optional[List[str]] = Field(None, description="Tags")
    notes: Optional[str] = Field(None, description="Notes")


class RecurringTransactionResponse(BaseModel):
    """Schema for recurring transaction responses"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Recurring transaction ID")
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="Name of the recurring transaction")
    description: Optional[str] = Field(None, description="Description")
    recurrence_pattern: RecurrencePattern = Field(..., description="How often this recurs")
    estimated_amount: float = Field(..., description="Estimated transaction amount")
    category: Optional[TransactionCategory] = Field(None, description="Transaction category")
    subcategory: Optional[TransactionSubcategory] = Field(None, description="Transaction subcategory")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")
    is_active: bool = Field(..., description="Whether this pattern is still active")
    confidence_score: float = Field(..., description="Confidence that this is truly recurring (0-1)")
    first_seen: date = Field(..., description="Date of first occurrence")
    last_seen: date = Field(..., description="Date of most recent occurrence")
    next_expected: Optional[date] = Field(None, description="Next expected occurrence")
    occurrence_count: int = Field(..., description="Number of times this has occurred")
    tags: Optional[List[str]] = Field(None, description="Tags")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Computed properties
    tags_list: List[str] = Field(default_factory=list, description="Tags as a list")


class PlaidTransactionSyncRequest(BaseModel):
    """Schema for syncing transactions from Plaid"""
    plaid_access_token: str = Field(..., description="Plaid access token")
    account_id: str = Field(..., description="Account ID to sync transactions for")
    start_date: Optional[date] = Field(None, description="Start date for transaction sync")
    end_date: Optional[date] = Field(None, description="End date for transaction sync")
    force_update: bool = Field(default=False, description="Force update even if recently synced")


class BulkTransactionUpdateRequest(BaseModel):
    """Schema for bulk transaction updates"""
    transaction_ids: List[str] = Field(..., description="List of transaction IDs to update")
    updates: TransactionUpdate = Field(..., description="Updates to apply to all transactions")


class TransactionDuplicateCheckRequest(BaseModel):
    """Schema for checking duplicate transactions"""
    account_id: str = Field(..., description="Account ID")
    amount: float = Field(..., description="Transaction amount")
    transaction_date: date = Field(..., description="Transaction date")
    name: str = Field(..., description="Transaction name")
    merchant_name: Optional[str] = Field(None, description="Merchant name")


class TransactionDuplicateResponse(BaseModel):
    """Schema for duplicate transaction check responses"""
    is_duplicate: bool = Field(..., description="Whether transaction appears to be a duplicate")
    duplicate_of: Optional[str] = Field(None, description="ID of existing transaction if duplicate")
    confidence_score: float = Field(..., description="Confidence score for duplicate detection (0-1)")
    similar_transactions: List[TransactionResponse] = Field(default_factory=list, description="Similar transactions found")


# Transaction Category Schemas

class TransactionCategoryBase(BaseModel):
    """Base transaction category schema with common fields"""
    model_config = ConfigDict(from_attributes=True)

    # Category details
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color (hex code)")
    icon: Optional[str] = Field(None, description="Category icon identifier")

    # Hierarchical structure
    parent_id: Optional[str] = Field(None, description="Parent category ID")

    # Category type
    is_income: bool = Field(default=False, description="Whether this is an income category")
    is_expense: bool = Field(default=True, description="Whether this is an expense category")

    # Budget information
    budget_amount: Optional[float] = Field(None, description="Monthly budget amount")
    budget_period: str = Field(default="monthly", description="Budget period (weekly, monthly, yearly)")

    # Status and ordering
    is_active: bool = Field(default=True, description="Whether category is active")
    sort_order: int = Field(default=0, description="Display order within parent")


class TransactionCategoryCreate(TransactionCategoryBase):
    """Schema for creating new transaction categories"""
    user_id: Optional[str] = Field(None, description="User ID (category owner, null for group categories)")
    group_id: Optional[str] = Field(None, description="Group ID (group owner, null for user categories)")


class TransactionCategoryUpdate(BaseModel):
    """Schema for updating existing transaction categories"""
    model_config = ConfigDict(from_attributes=True)

    # Category details
    name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color (hex code)")
    icon: Optional[str] = Field(None, description="Category icon identifier")

    # Hierarchical structure
    parent_id: Optional[str] = Field(None, description="Parent category ID")

    # Category type
    is_income: Optional[bool] = Field(None, description="Whether this is an income category")
    is_expense: Optional[bool] = Field(None, description="Whether this is an expense category")

    # Budget information
    budget_amount: Optional[float] = Field(None, description="Monthly budget amount")
    budget_period: Optional[str] = Field(None, description="Budget period (weekly, monthly, yearly)")

    # Status and ordering
    is_active: Optional[bool] = Field(None, description="Whether category is active")
    sort_order: Optional[int] = Field(None, description="Display order within parent")


class TransactionCategoryResponse(TransactionCategoryBase):
    """Schema for transaction category API responses"""
    # Primary identifiers
    id: str = Field(..., description="Category ID")
    user_id: Optional[str] = Field(None, description="User ID (category owner, null for group categories)")
    group_id: Optional[str] = Field(None, description="Group ID (group owner, null for user categories)")

    # Hierarchical structure
    level: int = Field(..., description="Category level in hierarchy (1 = root)")
    path: str = Field(..., description="Full path in hierarchy (e.g., 'Expenses/Housing/Utilities')")

    # Usage tracking
    transaction_count: int = Field(..., description="Number of transactions in this category")
    total_amount: float = Field(..., description="Total amount of transactions in this category")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Computed properties
    is_root: bool = Field(..., description="Whether this is a root category")
    is_leaf: bool = Field(..., description="Whether this is a leaf category")
    is_user_category: bool = Field(..., description="Whether this is a user-level category")
    is_group_category: bool = Field(..., description="Whether this is a group-level category")
    full_path_list: List[str] = Field(..., description="Full path as a list of category names")
    depth: int = Field(..., description="Depth of this category in the hierarchy")


class TransactionCategoryTreeResponse(BaseModel):
    """Schema for hierarchical transaction category tree responses"""
    category: TransactionCategoryResponse = Field(..., description="Category information")
    children: List["TransactionCategoryTreeResponse"] = Field(default_factory=list, description="Child categories")


class TransactionCategoryListResponse(BaseModel):
    """Schema for paginated transaction category list responses"""
    categories: List[TransactionCategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    skip: int = Field(..., description="Number of categories skipped")
    limit: int = Field(..., description="Maximum number of categories returned")


class TransactionCategoryMoveRequest(BaseModel):
    """Schema for moving categories within the hierarchy"""
    new_parent_id: Optional[str] = Field(None, description="New parent category ID (None for root)")
    sort_order: Optional[int] = Field(None, description="New sort order within parent")


class TransactionCategoryBulkDeleteRequest(BaseModel):
    """Schema for bulk category deletion"""
    category_ids: List[str] = Field(..., description="List of category IDs to delete")
    delete_children: bool = Field(default=False, description="Whether to delete child categories")
    reassign_transactions_to: Optional[str] = Field(None, description="Category ID to reassign transactions to")


# Category Rule Schemas

class CategoryRuleBase(BaseModel):
    """Base category rule schema with common fields"""
    model_config = ConfigDict(from_attributes=True)

    # Rule definition
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")

    # Matching criteria
    merchant_name_pattern: Optional[str] = Field(None, description="Regex pattern for merchant name")
    transaction_name_pattern: Optional[str] = Field(None, description="Regex pattern for transaction name")
    description_pattern: Optional[str] = Field(None, description="Regex pattern for description")
    amount_min: Optional[float] = Field(None, description="Minimum transaction amount")
    amount_max: Optional[float] = Field(None, description="Maximum transaction amount")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type filter")

    # Rule settings
    is_active: bool = Field(default=True, description="Whether rule is active")
    priority: int = Field(default=0, description="Rule priority (higher = processed first)")
    confidence_threshold: float = Field(default=0.8, description="Minimum confidence to apply rule")


class CategoryRuleCreate(CategoryRuleBase):
    """Schema for creating new category rules"""
    user_id: str = Field(..., description="User ID (rule owner)")
    category_id: str = Field(..., description="Target category ID")


class CategoryRuleUpdate(BaseModel):
    """Schema for updating existing category rules"""
    model_config = ConfigDict(from_attributes=True)

    # Rule definition
    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")

    # Matching criteria
    merchant_name_pattern: Optional[str] = Field(None, description="Regex pattern for merchant name")
    transaction_name_pattern: Optional[str] = Field(None, description="Regex pattern for transaction name")
    description_pattern: Optional[str] = Field(None, description="Regex pattern for description")
    amount_min: Optional[float] = Field(None, description="Minimum transaction amount")
    amount_max: Optional[float] = Field(None, description="Maximum transaction amount")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type filter")

    # Rule settings
    is_active: Optional[bool] = Field(None, description="Whether rule is active")
    priority: Optional[int] = Field(None, description="Rule priority (higher = processed first)")
    confidence_threshold: Optional[float] = Field(None, description="Minimum confidence to apply rule")


class CategoryRuleResponse(CategoryRuleBase):
    """Schema for category rule API responses"""
    # Primary identifiers
    id: str = Field(..., description="Rule ID")
    user_id: str = Field(..., description="User ID (rule owner)")
    category_id: str = Field(..., description="Target category ID")

    # Usage tracking
    match_count: int = Field(..., description="Number of times rule has matched")
    last_matched: Optional[datetime] = Field(None, description="Last time rule matched")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CategoryRuleListResponse(BaseModel):
    """Schema for paginated category rule list responses"""
    rules: List[CategoryRuleResponse] = Field(..., description="List of rules")
    total: int = Field(..., description="Total number of rules")
    skip: int = Field(..., description="Number of rules skipped")
    limit: int = Field(..., description="Maximum number of rules returned")


class CategoryRuleTestRequest(BaseModel):
    """Schema for testing category rules against transactions"""
    transaction_ids: List[str] = Field(..., description="List of transaction IDs to test rules against")


class CategoryRuleTestResponse(BaseModel):
    """Schema for category rule test responses"""
    rule_id: str = Field(..., description="Rule ID")
    rule_name: str = Field(..., description="Rule name")
    matches: List[str] = Field(..., description="List of matching transaction IDs")
    match_count: int = Field(..., description="Number of matches")
    would_apply: bool = Field(..., description="Whether rule would be applied")


class CategoryRuleBulkActionRequest(BaseModel):
    """Schema for bulk category rule actions"""
    rule_ids: List[str] = Field(..., description="List of rule IDs")
    action: str = Field(..., description="Action to perform (activate, deactivate, delete)")


# Update forward references
TransactionCategoryTreeResponse.model_rebuild()
