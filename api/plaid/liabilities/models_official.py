"""
Plaid Liabilities Database Models

Comprehensive database models for storing Plaid Liabilities data including:
- Credit card APR information and payment details
- Mortgage information with interest rates and property data
- Student loan details with servicer and repayment information
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime, Integer, Float, Boolean
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from sqlalchemy import func, Index
import json

from api.common.ulid_utils import ULIDField, ULIDPrimaryKey, ULIDForeignKey


# ==========================================
# Main Liabilities Table
# ==========================================

class PlaidLiability(SQLModel, table=True):
    """Main table for all liability accounts (credit cards, mortgages, student loans)"""
    __tablename__ = "plaid_liabilities"
    
    # Primary identifiers
    id: Optional[str] = ULIDPrimaryKey()
    user_id: str = ULIDForeignKey("users.id")
    item_id: str = ULIDForeignKey("plaid_items.id")
    account_id: str = Field(index=True, description="Plaid account_id")
    plaid_account_id: str = Field(index=True, description="Original Plaid account identifier")
    
    # Account basic information
    account_name: Optional[str] = None
    account_official_name: Optional[str] = None
    account_mask: Optional[str] = None
    account_type: str = Field(index=True, description="credit, loan")
    account_subtype: str = Field(index=True, description="credit card, mortgage, student, paypal")
    
    # Liability type classification
    liability_type: str = Field(index=True, description="credit_card, mortgage, student_loan")
    
    # Current balance information
    current_balance: Optional[float] = None
    available_balance: Optional[float] = None
    limit_amount: Optional[float] = None
    currency_code: str = Field(default="USD")
    
    # Status and error tracking
    status: str = Field(default="active", index=True)
    last_updated: Optional[datetime] = None
    sync_status: str = Field(default="active", description="active, error, stale")
    sync_error: Optional[str] = None
    
    # Environment and timestamps
    environment: str = Field(default="sandbox", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


# ==========================================
# Credit Card Specific Models
# ==========================================

class PlaidCreditCardAPR(SQLModel, table=True):
    """APR information for credit cards"""
    __tablename__ = "plaid_liability_credit_aprs"
    
    id: Optional[str] = ULIDPrimaryKey()
    liability_id: str = ULIDForeignKey("plaid_liabilities.id")
    
    # APR details
    apr_percentage: float = Field(description="Annual percentage rate")
    apr_type: str = Field(description="balance_transfer_apr, cash_apr, purchase_apr, special")
    balance_subject_to_apr: Optional[float] = None
    interest_charge_amount: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlaidCreditCardDetails(SQLModel, table=True):
    """Detailed credit card liability information"""
    __tablename__ = "plaid_liability_credit_details"
    
    id: Optional[str] = ULIDPrimaryKey()
    liability_id: str = ULIDForeignKey("plaid_liabilities.id", unique=True)
    
    # Payment information
    is_overdue: Optional[bool] = None
    last_payment_amount: Optional[float] = None
    last_payment_date: Optional[date] = None
    last_statement_issue_date: Optional[date] = None
    last_statement_balance: Optional[float] = None
    minimum_payment_amount: Optional[float] = None
    next_payment_due_date: Optional[date] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# Mortgage Specific Models
# ==========================================

class PlaidMortgageDetails(SQLModel, table=True):
    """Detailed mortgage liability information"""
    __tablename__ = "plaid_liability_mortgage_details"
    
    id: Optional[str] = ULIDPrimaryKey()
    liability_id: str = ULIDForeignKey("plaid_liabilities.id", unique=True)
    
    # Account information
    account_number: Optional[str] = None
    
    # Mortgage specific fields
    current_late_fee: Optional[float] = None
    escrow_balance: Optional[float] = None
    has_pmi: Optional[bool] = None
    has_prepayment_penalty: Optional[bool] = None
    
    # Interest rate information
    interest_rate_percentage: Optional[float] = None
    interest_rate_type: Optional[str] = None  # fixed, variable
    
    # Payment information
    last_payment_amount: Optional[float] = None
    last_payment_date: Optional[date] = None
    loan_type_description: Optional[str] = None
    loan_term: Optional[str] = None
    maturity_date: Optional[date] = None
    next_monthly_payment: Optional[float] = None
    next_payment_due_date: Optional[date] = None
    
    # Origination information
    origination_date: Optional[date] = None
    origination_principal_amount: Optional[float] = None
    past_due_amount: Optional[float] = None
    
    # Year-to-date information
    ytd_interest_paid: Optional[float] = None
    ytd_principal_paid: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlaidMortgagePropertyAddress(SQLModel, table=True):
    """Property address information for mortgages"""
    __tablename__ = "plaid_liability_mortgage_property_addresses"
    
    id: Optional[str] = ULIDPrimaryKey()
    mortgage_details_id: str = ULIDForeignKey("plaid_liability_mortgage_details.id", unique=True)
    
    # Address components
    street: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = Field(default="US")
    
    # Full address for display
    full_address: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# Student Loan Specific Models
# ==========================================

class PlaidStudentLoanDetails(SQLModel, table=True):
    """Detailed student loan liability information"""
    __tablename__ = "plaid_liability_student_details"
    
    id: Optional[str] = ULIDPrimaryKey()
    liability_id: str = ULIDForeignKey("plaid_liabilities.id", unique=True)
    
    # Account information
    account_number: Optional[str] = None
    loan_name: Optional[str] = None
    
    # Loan details
    disbursement_dates_json: Optional[str] = Field(sa_column=Column(Text))
    expected_payoff_date: Optional[date] = None
    guarantor: Optional[str] = None
    interest_rate_percentage: Optional[float] = None
    
    # Status information
    is_overdue: Optional[bool] = None
    loan_status_type: Optional[str] = None
    loan_status_end_date: Optional[date] = None
    
    # Payment information
    last_payment_amount: Optional[float] = None
    last_payment_date: Optional[date] = None
    last_statement_balance: Optional[float] = None
    last_statement_issue_date: Optional[date] = None
    minimum_payment_amount: Optional[float] = None
    next_payment_due_date: Optional[date] = None
    
    # Origination information
    origination_date: Optional[date] = None
    origination_principal_amount: Optional[float] = None
    outstanding_interest_amount: Optional[float] = None
    
    # Payment reference
    payment_reference_number: Optional[str] = None
    sequence_number: Optional[str] = None
    
    # Year-to-date information
    ytd_interest_paid: Optional[float] = None
    ytd_principal_paid: Optional[float] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def disbursement_dates(self) -> List[str]:
        """Get disbursement dates as list"""
        if self.disbursement_dates_json:
            try:
                return json.loads(self.disbursement_dates_json)
            except (json.JSONDecodeError, TypeError):
                pass
        return []
    
    @disbursement_dates.setter
    def disbursement_dates(self, value: List[str]):
        """Set disbursement dates from list"""
        self.disbursement_dates_json = json.dumps(value) if value else None


class PlaidStudentLoanPSLFStatus(SQLModel, table=True):
    """Public Service Loan Forgiveness status for student loans"""
    __tablename__ = "plaid_liability_student_pslf_status"
    
    id: Optional[str] = ULIDPrimaryKey()
    student_details_id: str = ULIDForeignKey("plaid_liability_student_details.id", unique=True)
    
    # PSLF information
    estimated_eligibility_date: Optional[date] = None
    payments_made: Optional[int] = None
    payments_remaining: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlaidStudentLoanRepaymentPlan(SQLModel, table=True):
    """Repayment plan information for student loans"""
    __tablename__ = "plaid_liability_student_repayment_plans"
    
    id: Optional[str] = ULIDPrimaryKey()
    student_details_id: str = ULIDForeignKey("plaid_liability_student_details.id", unique=True)
    
    # Repayment plan details
    description: Optional[str] = None
    plan_type: Optional[str] = None  # standard, graduated, income-based, etc.
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlaidStudentLoanServicerAddress(SQLModel, table=True):
    """Servicer address information for student loans"""
    __tablename__ = "plaid_liability_student_servicer_addresses"
    
    id: Optional[str] = ULIDPrimaryKey()
    student_details_id: str = ULIDForeignKey("plaid_liability_student_details.id", unique=True)
    
    # Address components
    street: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = Field(default="US")
    
    # Full address for display
    full_address: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# Liability History and Updates
# ==========================================

class PlaidLiabilityHistory(SQLModel, table=True):
    """Track changes to liability data over time"""
    __tablename__ = "plaid_liability_history"
    
    id: Optional[str] = ULIDPrimaryKey()
    liability_id: str = ULIDForeignKey("plaid_liabilities.id")
    
    # Change tracking
    field_name: str = Field(index=True)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_type: str = Field(default="update")  # create, update, delete
    change_source: str = Field(default="api_sync")  # api_sync, webhook, manual
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# ==========================================
# Webhook Event Tracking
# ==========================================

class PlaidLiabilityWebhookEvent(SQLModel, table=True):
    """Track webhook events related to liabilities"""
    __tablename__ = "plaid_liability_webhook_events"
    
    id: Optional[str] = ULIDPrimaryKey()
    item_id: str = ULIDForeignKey("plaid_items.id")
    
    # Webhook details
    webhook_type: str = Field(default="LIABILITIES")
    webhook_code: str = Field(index=True)  # DEFAULT_UPDATE
    webhook_payload: str = Field(sa_column=Column(Text))
    
    # Affected accounts
    account_ids_with_new_liabilities: Optional[str] = Field(sa_column=Column(Text))
    account_ids_with_updated_liabilities: Optional[str] = Field(sa_column=Column(Text))
    
    # Processing status
    processed: bool = Field(default=False, index=True)
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    
    # Environment and timestamps
    environment: str = Field(index=True)
    received_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# ==========================================
# API Response Models
# ==========================================

class LiabilityAPRResponse(SQLModel):
    """Response model for APR information"""
    apr_percentage: float
    apr_type: str
    balance_subject_to_apr: Optional[float] = None
    interest_charge_amount: Optional[float] = None


class CreditCardLiabilityResponse(SQLModel):
    """Response model for credit card liability"""
    account_id: str
    aprs: List[LiabilityAPRResponse]
    is_overdue: Optional[bool] = None
    last_payment_amount: Optional[float] = None
    last_payment_date: Optional[str] = None
    last_statement_issue_date: Optional[str] = None
    last_statement_balance: Optional[float] = None
    minimum_payment_amount: Optional[float] = None
    next_payment_due_date: Optional[str] = None


class MortgageLiabilityResponse(SQLModel):
    """Response model for mortgage liability"""
    account_id: str
    account_number: Optional[str] = None
    current_late_fee: Optional[float] = None
    escrow_balance: Optional[float] = None
    has_pmi: Optional[bool] = None
    has_prepayment_penalty: Optional[bool] = None
    interest_rate: Optional[Dict[str, Any]] = None
    last_payment_amount: Optional[float] = None
    last_payment_date: Optional[str] = None
    loan_term: Optional[str] = None
    loan_type_description: Optional[str] = None
    maturity_date: Optional[str] = None
    next_monthly_payment: Optional[float] = None
    next_payment_due_date: Optional[str] = None
    origination_date: Optional[str] = None
    origination_principal_amount: Optional[float] = None
    past_due_amount: Optional[float] = None
    property_address: Optional[Dict[str, str]] = None
    ytd_interest_paid: Optional[float] = None
    ytd_principal_paid: Optional[float] = None


class StudentLoanLiabilityResponse(SQLModel):
    """Response model for student loan liability"""
    account_id: str
    account_number: Optional[str] = None
    disbursement_dates: Optional[List[str]] = None
    expected_payoff_date: Optional[str] = None
    guarantor: Optional[str] = None
    interest_rate_percentage: Optional[float] = None
    is_overdue: Optional[bool] = None
    last_payment_amount: Optional[float] = None
    last_payment_date: Optional[str] = None
    last_statement_balance: Optional[float] = None
    last_statement_issue_date: Optional[str] = None
    loan_name: Optional[str] = None
    loan_status: Optional[Dict[str, Any]] = None
    minimum_payment_amount: Optional[float] = None
    next_payment_due_date: Optional[str] = None
    origination_date: Optional[str] = None
    origination_principal_amount: Optional[float] = None
    outstanding_interest_amount: Optional[float] = None
    payment_reference_number: Optional[str] = None
    pslf_status: Optional[Dict[str, Any]] = None
    repayment_plan: Optional[Dict[str, str]] = None
    sequence_number: Optional[str] = None
    servicer_address: Optional[Dict[str, str]] = None
    ytd_interest_paid: Optional[float] = None
    ytd_principal_paid: Optional[float] = None


class LiabilitiesResponse(SQLModel):
    """Complete liabilities response"""
    credit: List[CreditCardLiabilityResponse] = []
    mortgage: List[MortgageLiabilityResponse] = []
    student: List[StudentLoanLiabilityResponse] = []
