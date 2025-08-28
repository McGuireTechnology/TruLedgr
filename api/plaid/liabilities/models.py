"""
Plaid Liabilities Models

Pydantic models for credit cards, mortgages, and student loan data.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# Import shared models
from ..models import Account

class APRDetails(BaseModel):
    """Annual Percentage Rate details for credit accounts"""
    apr_percentage: float = Field(..., description="Annual Percentage Rate applied")
    apr_type: str = Field(..., description="Type of balance to which APR applies")
    balance_subject_to_apr: Optional[float] = Field(None, description="Amount subjected to APR if balance carried")
    interest_charge_amount: Optional[float] = Field(None, description="Interest charged due to last statement")

class InterestRate(BaseModel):
    """Interest rate information for mortgages"""
    percentage: Optional[float] = Field(None, description="Interest rate percentage")
    type: Optional[str] = Field(None, description="Interest rate type: fixed or variable")

class PropertyAddress(BaseModel):
    """Property address for mortgage accounts"""
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    postal_code: Optional[str] = Field(None, description="Postal code")
    region: Optional[str] = Field(None, description="Region or state")
    street: Optional[str] = Field(None, description="Full street address")

class ServicerAddress(BaseModel):
    """Student loan servicer address"""
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code") 
    postal_code: Optional[str] = Field(None, description="Postal code")
    region: Optional[str] = Field(None, description="Region or state")
    street: Optional[str] = Field(None, description="Full street address")

class RepaymentPlan(BaseModel):
    """Student loan repayment plan information"""
    description: Optional[str] = Field(None, description="Description of repayment plan")
    type: Optional[str] = Field(None, description="Type of repayment plan")

class PSLFStatus(BaseModel):
    """Public Service Loan Forgiveness status for student loans"""
    estimated_eligibility_date: Optional[str] = Field(None, description="Estimated PSLF eligibility date")
    payments_made: Optional[int] = Field(None, description="Number of qualifying payments made")
    payments_remaining: Optional[int] = Field(None, description="Number of qualifying payments remaining")

class LoanStatus(BaseModel):
    """Student loan status information"""
    end_date: Optional[str] = Field(None, description="End date of current status")
    type: Optional[str] = Field(None, description="Current status type")

class CreditLiability(BaseModel):
    """Credit card liability details"""
    account_id: Optional[str] = Field(None, description="Account ID associated with the liability")
    aprs: List[APRDetails] = Field([], description="Interest rates that apply to the account")
    is_overdue: Optional[bool] = Field(None, description="Whether a payment is currently overdue")
    last_payment_amount: Optional[float] = Field(None, description="Amount of the last payment")
    last_payment_date: Optional[str] = Field(None, description="Date of the last payment (YYYY-MM-DD)")
    last_statement_issue_date: Optional[str] = Field(None, description="Date of the last statement (YYYY-MM-DD)")
    last_statement_balance: Optional[float] = Field(None, description="Total amount owed as of last statement")
    minimum_payment_amount: Optional[float] = Field(None, description="Minimum payment due for next billing cycle")
    next_payment_due_date: Optional[str] = Field(None, description="Due date for next payment (YYYY-MM-DD)")

class MortgageLiability(BaseModel):
    """Mortgage liability details"""
    account_id: str = Field(..., description="Account ID associated with the liability")
    account_number: Optional[str] = Field(None, description="Account number of the mortgage")
    current_late_fee: Optional[float] = Field(None, description="Current late fee amount")
    escrow_balance: Optional[float] = Field(None, description="Escrow account balance")
    has_pmi: Optional[bool] = Field(None, description="Whether borrower has private mortgage insurance")
    has_prepayment_penalty: Optional[bool] = Field(None, description="Whether there's prepayment penalty")
    interest_rate: Optional[InterestRate] = Field(None, description="Interest rate information")
    last_payment_amount: Optional[float] = Field(None, description="Amount of the last payment")
    last_payment_date: Optional[str] = Field(None, description="Date of the last payment (YYYY-MM-DD)")
    loan_term: Optional[str] = Field(None, description="Full duration of mortgage")
    loan_type_description: Optional[str] = Field(None, description="Type of loan description")
    maturity_date: Optional[str] = Field(None, description="Date mortgage is due in full (YYYY-MM-DD)")
    next_monthly_payment: Optional[float] = Field(None, description="Amount of the next payment")
    next_payment_due_date: Optional[str] = Field(None, description="Due date for next payment (YYYY-MM-DD)")
    origination_date: Optional[str] = Field(None, description="Date loan was initially lent (YYYY-MM-DD)")
    origination_principal_amount: Optional[float] = Field(None, description="Original principal balance")
    past_due_amount: Optional[float] = Field(None, description="Past due amount")
    property_address: Optional[PropertyAddress] = Field(None, description="Property address")
    ytd_interest_paid: Optional[float] = Field(None, description="Year-to-date interest paid")
    ytd_principal_paid: Optional[float] = Field(None, description="Year-to-date principal paid")

class StudentLoanLiability(BaseModel):
    """Student loan liability details"""
    account_id: str = Field(..., description="Account ID associated with the liability")
    account_number: Optional[str] = Field(None, description="Account number of the loan")
    disbursement_dates: Optional[List[str]] = Field(None, description="Disbursement dates (YYYY-MM-DD)")
    expected_payoff_date: Optional[str] = Field(None, description="Expected payoff date (YYYY-MM-DD)")
    guarantor: Optional[str] = Field(None, description="Guarantor of the student loan")
    interest_rate_percentage: float = Field(..., description="Interest rate as a percentage")
    is_overdue: Optional[bool] = Field(None, description="Whether a payment is currently overdue")
    last_payment_amount: Optional[float] = Field(None, description="Amount of the last payment")
    last_payment_date: Optional[str] = Field(None, description="Date of the last payment (YYYY-MM-DD)")
    last_statement_balance: Optional[float] = Field(None, description="Total amount owed as of last statement")
    last_statement_issue_date: Optional[str] = Field(None, description="Date of last statement (YYYY-MM-DD)")
    loan_name: Optional[str] = Field(None, description="Name of the loan")
    loan_status: Optional[LoanStatus] = Field(None, description="Current loan status")
    minimum_payment_amount: Optional[float] = Field(None, description="Minimum payment due for next billing cycle")
    next_payment_due_date: Optional[str] = Field(None, description="Due date for next payment (YYYY-MM-DD)")
    origination_date: Optional[str] = Field(None, description="Date loan was initially lent (YYYY-MM-DD)")
    origination_principal_amount: Optional[float] = Field(None, description="Original principal balance")
    outstanding_interest_amount: Optional[float] = Field(None, description="Outstanding interest amount")
    payment_reference_number: Optional[str] = Field(None, description="Payment reference number")
    pslf_status: Optional[PSLFStatus] = Field(None, description="Public Service Loan Forgiveness status")
    repayment_plan: Optional[RepaymentPlan] = Field(None, description="Repayment plan information")
    sequence_number: Optional[str] = Field(None, description="Sequence number of the loan")
    servicer_address: Optional[ServicerAddress] = Field(None, description="Servicer address")
    ytd_interest_paid: Optional[float] = Field(None, description="Year-to-date interest paid")
    ytd_principal_paid: Optional[float] = Field(None, description="Year-to-date principal paid")

class LiabilitiesData(BaseModel):
    """Container for all liability data"""
    credit: Optional[List[CreditLiability]] = Field(None, description="Credit card liabilities")
    mortgage: Optional[List[MortgageLiability]] = Field(None, description="Mortgage liabilities")
    student: Optional[List[StudentLoanLiability]] = Field(None, description="Student loan liabilities")

# Request/Response Models for Liabilities API

class LiabilitiesRequest(BaseModel):
    """Request model for getting liabilities data"""
    access_token: str = Field(..., description="Access token for the connected account")
    account_ids: Optional[List[str]] = Field(None, description="Specific account IDs to retrieve liabilities for")

class LiabilitiesResponse(BaseModel):
    """Response model for liabilities data"""
    accounts: List[Account] = Field(..., description="Accounts with liability data")
    liabilities: LiabilitiesData = Field(..., description="Liabilities data organized by type")
    request_id: str = Field(..., description="Unique request identifier")

# Liabilities Webhook Models

class LiabilitiesWebhookRequest(BaseModel):
    """Model for LIABILITIES webhook requests"""
    webhook_type: str = Field("LIABILITIES", description="Always 'LIABILITIES' for this webhook")
    webhook_code: str = Field("DEFAULT_UPDATE", description="Always 'DEFAULT_UPDATE' for liabilities")
    item_id: str = Field(..., description="Plaid item ID")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if applicable")
    account_ids_with_new_liabilities: List[str] = Field(..., description="Account IDs with new liabilities")
    account_ids_with_updated_liabilities: Dict[str, List[str]] = Field(..., description="Account IDs with updated liability fields")
    environment: str = Field("production", description="Plaid environment")