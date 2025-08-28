"""
Transactions Models

Core transaction models that aggregate data from multiple sources:
- Plaid transactions (via api.plaid.transactions)
- Manual transaction entries
- Other banking integrations

This provides a unified view of all financial transactions.
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime, Boolean, Float, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy import func, Index
from enum import Enum
from decimal import Decimal

from api.common.ulid_utils import ULIDPrimaryKey, ULIDForeignKey


class TransactionType(str, Enum):
    """Transaction type enumeration - extended"""
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    DIVIDEND = "dividend"
    ADJUSTMENT = "adjustment"
    OTHER = "other"


class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    CLEARED = "cleared"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TransactionSource(str, Enum):
    """Source of transaction data"""
    PLAID = "plaid"
    MANUAL = "manual"
    CSV_IMPORT = "csv_import"
    API = "api"
    OTHER = "other"


class SystemTransactionCategory(str, Enum):
    """High-level transaction categories (system-defined)"""
    FOOD_AND_DRINK = "food_and_drink"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    BILLS_AND_UTILITIES = "bills_and_utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    PERSONAL_CARE = "personal_care"
    TRANSPORTATION = "transportation"
    HOME_AND_GARDEN = "home_and_garden"
    BUSINESS_SERVICES = "business_services"
    TAXES = "taxes"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    DIVIDEND = "dividend"
    INCOME = "income"
    OTHER = "other"


class TransactionSubcategory(str, Enum):
    """Detailed transaction subcategories"""
    # Food and Drink
    RESTAURANTS = "restaurants"
    GROCERIES = "groceries"
    BARS = "bars"
    FAST_FOOD = "fast_food"
    COFFEE_SHOPS = "coffee_shops"

    # Travel
    AIRLINES = "airlines"
    HOTELS = "hotels"
    CAR_RENTAL = "car_rental"
    PUBLIC_TRANSPORTATION = "public_transportation"
    TAXI = "taxi"
    RIDESHARE = "rideshare"

    # Shopping
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    HOME_IMPROVEMENT = "home_improvement"
    DEPARTMENT_STORES = "department_stores"
    SUPERMARKETS = "supermarkets"

    # Bills and Utilities
    ELECTRICITY = "electricity"
    GAS = "gas"
    WATER = "water"
    INTERNET = "internet"
    PHONE = "phone"
    INSURANCE = "insurance"

    # Healthcare
    DOCTORS = "doctors"
    PHARMACIES = "pharmacies"
    HOSPITALS = "hospitals"
    DENTAL = "dental"

    # Transportation
    GAS_STATIONS = "gas_stations"
    PARKING = "parking"
    TOLLS = "tolls"

    # Business Services
    ACCOUNTING = "accounting"
    LEGAL = "legal"
    CONSULTING = "consulting"

    # Income
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENTS = "investments"
    REFUNDS = "refunds"

    # Other
    ATM = "atm"
    CASH = "cash"
    CHECK = "check"
    WIRE_TRANSFER = "wire_transfer"
    OTHER = "other"


class RecurrencePattern(str, Enum):
    """Recurring transaction patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"
    ANNUALLY = "annually"
    IRREGULAR = "irregular"


class Transaction(SQLModel, table=True):
    """
    Core Transaction model - aggregates data from all sources

    This is the single source of truth for transactions in TruLedgr,
    pulling data from Plaid and allowing manual transaction creation.
    """
    __tablename__ = "transactions"  # type: ignore

    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()

    # Relationships
    account_id: str = ULIDForeignKey("accounts.id", description="Reference to root account")
    institution_id: str = ULIDForeignKey("institutions.id", description="Reference to root institution")
    user_id: str = ULIDForeignKey("users.id", description="Transaction owner")

    # External source identifiers
    plaid_transaction_id: Optional[str] = Field(None, index=True, description="Plaid transaction ID")
    external_transaction_id: Optional[str] = Field(None, index=True, description="External system transaction ID")

    # Core transaction information
    amount: float = Field(description="Transaction amount (positive for credits, negative for debits)")
    transaction_type: TransactionType = Field(index=True, description="Transaction type")
    transaction_date: date = Field(index=True, description="Transaction date")
    transaction_datetime: Optional[datetime] = Field(None, description="Transaction datetime")

    # Transaction identification and naming
    name: str = Field(index=True, description="Transaction name/description")
    description: Optional[str] = Field(None, sa_column=Column(Text), description="Detailed description")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")

    # Categorization
    category: Optional[SystemTransactionCategory] = Field(None, index=True, description="High-level category")
    subcategory: Optional[TransactionSubcategory] = Field(None, index=True, description="Detailed subcategory")
    custom_category: Optional[str] = Field(None, description="Custom category if not in enum")
    user_category_id: Optional[str] = Field(None, index=True, description="User-defined category ID")
    group_category_id: Optional[str] = Field(None, index=True, description="Group-defined category ID")

    # Status and processing
    status: TransactionStatus = Field(default=TransactionStatus.CLEARED, index=True)
    source: TransactionSource = Field(index=True, description="Data source")
    is_pending: bool = Field(default=False, index=True, description="Whether transaction is pending")

    # Financial details
    iso_currency_code: str = Field(default="USD", description="ISO currency code")
    unofficial_currency_code: Optional[str] = Field(None, description="Unofficial currency code")
    exchange_rate: Optional[float] = Field(None, description="Exchange rate if applicable")

    # Check and payment information
    check_number: Optional[str] = Field(None, description="Check number")
    payment_method: Optional[str] = Field(None, description="Payment method used")

    # Location information (stored as JSON)
    location_json: Optional[str] = Field(None, sa_column=Column(Text), description="Location data as JSON")

    # Counterparty information
    counterparty_name: Optional[str] = Field(None, description="Counterparty name")
    counterparty_type: Optional[str] = Field(None, description="Counterparty type")

    # Visual and web information
    logo_url: Optional[str] = Field(None, description="Transaction/merchant logo URL")
    website: Optional[str] = Field(None, description="Merchant website")

    # Recurring transaction support
    is_recurring: bool = Field(default=False, index=True, description="Whether this is a recurring transaction")
    recurrence_pattern: Optional[RecurrencePattern] = Field(None, description="Recurrence pattern")
    recurrence_id: Optional[str] = Field(None, index=True, description="ID linking recurring transactions")

    # Tags and notes
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    notes: Optional[str] = Field(None, sa_column=Column(Text), description="Internal notes")

    # Reconciliation and verification
    is_reconciled: bool = Field(default=False, index=True, description="Whether transaction is reconciled")
    reconciled_at: Optional[datetime] = Field(None, description="When transaction was reconciled")
    reconciled_by: Optional[str] = Field(None, description="Who reconciled the transaction")

    # Audit and tracking
    created_by: Optional[str] = Field(None, description="Who created the transaction")
    updated_by: Optional[str] = Field(None, description="Who last updated the transaction")

    # Metadata
    confidence_score: Optional[float] = Field(None, description="Confidence score for categorization (0-1)")
    duplicate_of: Optional[str] = Field(None, description="ID of duplicate transaction if applicable")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")

    # Helper properties
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

    @property
    def location_dict(self) -> Optional[Dict[str, Any]]:
        """Get location as dictionary"""
        if self.location_json:
            import json
            try:
                return json.loads(self.location_json)
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    @location_dict.setter
    def location_dict(self, value: Optional[Dict[str, Any]]):
        """Set location from dictionary"""
        if value is None:
            self.location_json = None
        else:
            import json
            self.location_json = json.dumps(value)

    @property
    def is_debit(self) -> bool:
        """Check if transaction is a debit (negative amount)"""
        return self.amount < 0

    @property
    def is_credit(self) -> bool:
        """Check if transaction is a credit (positive amount)"""
        return self.amount > 0

    @property
    def absolute_amount(self) -> float:
        """Get absolute transaction amount"""
        return abs(self.amount)

    @property
    def category_type(self) -> str:
        """Get the type of category being used"""
        if self.group_category_id:
            return "group"
        elif self.user_category_id:
            return "user"
        else:
            return "system"

    @property
    def effective_category_id(self) -> Optional[str]:
        """Get the effective category ID (group takes precedence over user)"""
        return self.group_category_id or self.user_category_id


class TransactionSourceMapping(SQLModel, table=True):
    """
    Maps transactions to their external source identifiers

    This allows tracking of the same transaction across multiple data sources
    and prevents duplicate transaction creation.
    """
    __tablename__ = "transaction_source_mappings"  # type: ignore

    id: Optional[str] = ULIDPrimaryKey()
    transaction_id: str = ULIDForeignKey("transactions.id")

    # Source information
    source: TransactionSource = Field(index=True, description="Data source")
    external_id: str = Field(index=True, description="External identifier")
    external_transaction_id: Optional[str] = Field(None, description="External transaction identifier")

    # Source metadata
    source_metadata: Optional[str] = Field(None, sa_column=Column(Text), description="JSON metadata from source")

    # Mapping status
    is_active: bool = Field(default=True, index=True)
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class TransactionModificationHistory(SQLModel, table=True):
    """
    Track transaction modifications over time

    This provides audit trail for transaction changes
    and helps with troubleshooting and reconciliation.
    """
    __tablename__ = "transaction_modification_history"  # type: ignore

    id: Optional[str] = ULIDPrimaryKey()
    transaction_id: str = ULIDForeignKey("transactions.id")

    # Modification details
    modification_type: str = Field(description="Type of modification (create, update, delete, reconcile)")
    field_changed: Optional[str] = Field(None, description="Field that was changed")
    previous_value: Optional[str] = Field(None, sa_column=Column(Text), description="Previous value")
    new_value: Optional[str] = Field(None, sa_column=Column(Text), description="New value")

    # Change context
    change_reason: Optional[str] = Field(None, description="Reason for the change")
    changed_by: Optional[str] = Field(None, description="Who made the change")
    source: str = Field(default="system", description="Source of the change")

    # Timestamps
    changed_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class RecurringTransaction(SQLModel, table=True):
    """
    Track recurring transaction patterns

    This helps identify and predict recurring transactions
    for budgeting and financial planning.
    """
    __tablename__ = "recurring_transactions"  # type: ignore

    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")

    # Recurring pattern information
    name: str = Field(description="Name of the recurring transaction")
    description: Optional[str] = Field(None, description="Description of the recurring transaction")

    # Pattern details
    recurrence_pattern: RecurrencePattern = Field(description="How often this recurs")
    estimated_amount: float = Field(description="Estimated transaction amount")
    category: Optional[SystemTransactionCategory] = Field(None, description="Transaction category")
    subcategory: Optional[TransactionSubcategory] = Field(None, description="Transaction subcategory")

    # Merchant information
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_entity_id: Optional[str] = Field(None, description="Merchant entity ID")

    # Status and tracking
    is_active: bool = Field(default=True, index=True, description="Whether this pattern is still active")
    confidence_score: float = Field(description="Confidence that this is truly recurring (0-1)")

    # Date tracking
    first_seen: date = Field(description="Date of first occurrence")
    last_seen: date = Field(description="Date of most recent occurrence")
    next_expected: Optional[date] = Field(None, description="Next expected occurrence")

    # Transaction count
    occurrence_count: int = Field(default=1, description="Number of times this has occurred")

    # Metadata
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    notes: Optional[str] = Field(None, sa_column=Column(Text), description="Internal notes")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Helper properties
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


class TransactionReconciliation(SQLModel, table=True):
    """
    Track transaction reconciliation activities

    This helps maintain accurate financial records
    and provides audit trails for reconciliation processes.
    """
    __tablename__ = "transaction_reconciliations"  # type: ignore

    id: Optional[str] = ULIDPrimaryKey()
    account_id: str = ULIDForeignKey("accounts.id")

    # Reconciliation details
    reconciliation_date: date = Field(index=True, description="Date of reconciliation")
    statement_balance: float = Field(description="Balance according to bank statement")
    calculated_balance: float = Field(description="Calculated balance from transactions")

    # Reconciliation results
    difference: float = Field(description="Difference between statement and calculated balance")
    is_balanced: bool = Field(description="Whether reconciliation is balanced")

    # Transaction counts
    reconciled_transactions: int = Field(description="Number of transactions reconciled")
    outstanding_transactions: int = Field(description="Number of outstanding transactions")

    # Reconciliation metadata
    reconciled_by: str = Field(description="Who performed the reconciliation")
    notes: Optional[str] = Field(None, sa_column=Column(Text), description="Reconciliation notes")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class TransactionCategory(SQLModel, table=True):
    """
    User-defined transaction categories with hierarchical support

    This allows users to create their own category hierarchy for organizing transactions.
    Categories can have parent-child relationships to create nested structures.
    Supports both user-level and group-level categories.
    """
    __tablename__ = "transaction_categories"  # type: ignore

    id: Optional[str] = ULIDPrimaryKey()
    user_id: Optional[str] = Field(None, foreign_key="users.id", description="Category owner (null for group categories)")
    group_id: Optional[str] = Field(None, foreign_key="groups.id", description="Group owner (null for user categories)")

    # Category details
    name: str = Field(description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color (hex code)")
    icon: Optional[str] = Field(None, description="Category icon identifier")

    # Hierarchical structure
    parent_id: Optional[str] = Field(None, description="Parent category ID")
    level: int = Field(default=1, description="Category level in hierarchy (1 = root)")
    path: str = Field(description="Full path in hierarchy (e.g., 'Expenses/Housing/Utilities')")

    # Category type
    is_income: bool = Field(default=False, description="Whether this is an income category")
    is_expense: bool = Field(default=True, description="Whether this is an expense category")

    # Budget information
    budget_amount: Optional[float] = Field(None, description="Monthly budget amount")
    budget_period: str = Field(default="monthly", description="Budget period (weekly, monthly, yearly)")

    # Status and ordering
    is_active: bool = Field(default=True, index=True, description="Whether category is active")
    sort_order: int = Field(default=0, description="Display order within parent")

    # Usage tracking
    transaction_count: int = Field(default=0, description="Number of transactions in this category")
    total_amount: float = Field(default=0.0, description="Total amount of transactions in this category")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Relationships
    parent: Optional["TransactionCategory"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "id"}
    )
    children: List["TransactionCategory"] = Relationship(back_populates="parent")

    # Helper properties
    @property
    def is_root(self) -> bool:
        """Check if this is a root category (no parent)"""
        return self.parent_id is None

    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf category (no children)"""
        return len(self.children) == 0

    @property
    def is_user_category(self) -> bool:
        """Check if this is a user-level category"""
        return self.user_id is not None and self.group_id is None

    @property
    def is_group_category(self) -> bool:
        """Check if this is a group-level category"""
        return self.group_id is not None and self.user_id is None

    @property
    def full_path_list(self) -> List[str]:
        """Get the full path as a list of category names"""
        return self.path.split("/") if self.path else [self.name]

    @property
    def depth(self) -> int:
        """Get the depth of this category in the hierarchy"""
        return len(self.full_path_list) - 1


class CategoryRule(SQLModel, table=True):
    """
    Rules for automatically categorizing transactions

    Users can define rules that automatically assign categories to transactions
    based on various criteria like merchant name, amount, description, etc.
    Supports both user-level and group-level rules.
    """
    __tablename__ = "category_rules"  # type: ignore

    id: Optional[str] = ULIDPrimaryKey()
    user_id: Optional[str] = Field(None, foreign_key="users.id", description="Rule owner (null for group rules)")
    group_id: Optional[str] = Field(None, foreign_key="groups.id", description="Group owner (null for user rules)")
    category_id: str = ULIDForeignKey("transaction_categories.id", description="Target category")

    # Rule definition
    name: str = Field(description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")

    # Matching criteria
    merchant_name_pattern: Optional[str] = Field(None, description="Regex pattern for merchant name")
    transaction_name_pattern: Optional[str] = Field(None, description="Regex pattern for transaction name")
    description_pattern: Optional[str] = Field(None, description="Regex pattern for description")
    amount_min: Optional[float] = Field(None, description="Minimum transaction amount")
    amount_max: Optional[float] = Field(None, description="Maximum transaction amount")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type filter")

    # Rule settings
    is_active: bool = Field(default=True, index=True, description="Whether rule is active")
    priority: int = Field(default=0, description="Rule priority (higher = processed first)")
    confidence_threshold: float = Field(default=0.8, description="Minimum confidence to apply rule")

    # Usage tracking
    match_count: int = Field(default=0, description="Number of times rule has matched")
    last_matched: Optional[datetime] = Field(None, description="Last time rule matched")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Helper properties
    @property
    def is_user_rule(self) -> bool:
        """Check if this is a user-level rule"""
        return self.user_id is not None and self.group_id is None

    @property
    def is_group_rule(self) -> bool:
        """Check if this is a group-level rule"""
        return self.group_id is not None and self.user_id is None


# Create indexes for better query performance
# Note: These will be created via database migrations
# Index("idx_transactions_user_date", Transaction.user_id, Transaction.transaction_date)
# Index("idx_transactions_account_date", Transaction.account_id, Transaction.transaction_date)
# Index("idx_transactions_category_date", Transaction.category, Transaction.transaction_date)
# Index("idx_transactions_amount", Transaction.amount)
# Index("idx_transactions_status_date", Transaction.status, Transaction.transaction_date)
# Index("idx_transaction_categories_user_parent", TransactionCategory.user_id, TransactionCategory.parent_id)
# Index("idx_transaction_categories_user_active", TransactionCategory.user_id, TransactionCategory.is_active)
# Index("idx_category_rules_user_active", CategoryRule.user_id, CategoryRule.is_active)
