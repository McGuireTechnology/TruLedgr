"""
Plaid Liabilities Module

Comprehensive credit cards, mortgages, and student loan functionality with
database integration and official Plaid API compliance.
"""

from .models_official import (
    PlaidLiability,
    PlaidCreditCardAPR,
    PlaidCreditCardDetails,
    PlaidMortgageDetails,
    PlaidMortgagePropertyAddress,
    PlaidStudentLoanDetails,
    PlaidStudentLoanPSLFStatus,
    PlaidStudentLoanRepaymentPlan,
    PlaidStudentLoanServicerAddress,
    PlaidLiabilityHistory,
    PlaidLiabilityWebhookEvent,
    LiabilitiesResponse,
    CreditCardLiabilityResponse,
    MortgageLiabilityResponse,
    StudentLoanLiabilityResponse,
    LiabilityAPRResponse
)
from .service_official import get_liabilities_service
from .router import router

__all__ = [
    # Database Models
    "PlaidLiability",
    "PlaidCreditCardAPR",
    "PlaidCreditCardDetails",
    "PlaidMortgageDetails", 
    "PlaidMortgagePropertyAddress",
    "PlaidStudentLoanDetails",
    "PlaidStudentLoanPSLFStatus",
    "PlaidStudentLoanRepaymentPlan",
    "PlaidStudentLoanServicerAddress",
    "PlaidLiabilityHistory",
    "PlaidLiabilityWebhookEvent",
    # Response Models
    "LiabilitiesResponse",
    "CreditCardLiabilityResponse",
    "MortgageLiabilityResponse", 
    "StudentLoanLiabilityResponse",
    "LiabilityAPRResponse",
    # Services
    "get_liabilities_service",
    # Router
    "router"
]