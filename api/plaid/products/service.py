"""
Plaid Products Service

Service layer for managing Plaid products information and status.
"""

from typing import List, Dict, Any, Optional
import logging
from .models import PlaidProductInfo, PlaidProductsResponse, SupportedProductsResponse, PlaidProductResponse

logger = logging.getLogger(__name__)


class ProductsService:
    """Service for managing Plaid products information"""
    
    def __init__(self):
        """Initialize the ProductsService"""
        self._products_data = self._initialize_products_data()
    
    def _initialize_products_data(self) -> List[PlaidProductInfo]:
        """Initialize the static products data"""
        return [
            PlaidProductInfo(
                name="transactions",
                display_name="Transactions",
                description="Access to account transactions and balances",
                features=[
                    "Transaction history",
                    "Account balances", 
                    "Transaction categorization",
                    "Real-time balance updates"
                ],
                use_cases=[
                    "Personal finance management",
                    "Expense tracking",
                    "Budgeting applications", 
                    "Financial analytics"
                ],
                supported=True,
                documentation_url="https://plaid.com/docs/api/products/transactions/"
            ),
            PlaidProductInfo(
                name="auth",
                display_name="Auth",
                description="Account and routing number verification",
                features=[
                    "Account number verification",
                    "Routing number verification",
                    "Account ownership verification",
                    "Real-time account validation"
                ],
                use_cases=[
                    "ACH payments",
                    "Direct deposit setup",
                    "Account verification",
                    "Payment processing"
                ],
                supported=True,
                documentation_url="https://plaid.com/docs/api/products/auth/"
            ),
            PlaidProductInfo(
                name="identity",
                display_name="Identity",
                description="Account holder identity information",
                features=[
                    "Account holder name",
                    "Email addresses",
                    "Phone numbers",
                    "Addresses"
                ],
                use_cases=[
                    "Identity verification",
                    "KYC compliance",
                    "Account onboarding",
                    "Customer data enrichment"
                ],
                supported=True,
                documentation_url="https://plaid.com/docs/api/products/identity/"
            ),
            PlaidProductInfo(
                name="assets",
                display_name="Assets",
                description="Asset and income verification reports",
                features=[
                    "Asset verification",
                    "Income verification",
                    "Employment verification",
                    "Bank statements"
                ],
                use_cases=[
                    "Loan underwriting",
                    "Credit applications",
                    "Employment verification",
                    "Income verification"
                ],
                supported=True,
                documentation_url="https://plaid.com/docs/api/products/assets/"
            ),
            PlaidProductInfo(
                name="investments",
                display_name="Investments",
                description="Investment account data and holdings",
                features=[
                    "Investment holdings",
                    "Account balances",
                    "Transaction history",
                    "Performance data"
                ],
                use_cases=[
                    "Portfolio management",
                    "Investment tracking",
                    "Financial planning",
                    "Wealth management"
                ],
                supported=True,
                documentation_url="https://plaid.com/docs/api/products/investments/"
            ),
            PlaidProductInfo(
                name="liabilities",
                display_name="Liabilities",
                description="Liability account information",
                features=[
                    "Credit card balances",
                    "Loan balances",
                    "Payment history",
                    "Interest rates"
                ],
                use_cases=[
                    "Debt management",
                    "Credit monitoring",
                    "Loan tracking",
                    "Financial planning"
                ],
                supported=True,
                documentation_url="https://plaid.com/docs/api/products/liabilities/"
            ),
            PlaidProductInfo(
                name="payment_initiation",
                display_name="Payment Initiation",
                description="Initiate payments from user accounts",
                features=[
                    "Single payments",
                    "Standing orders",
                    "Payment status tracking",
                    "Payment validation"
                ],
                use_cases=[
                    "Bill payments",
                    "P2P transfers",
                    "Merchant payments",
                    "Subscription payments"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/payment-initiation/"
            ),
            PlaidProductInfo(
                name="deposit_switch",
                display_name="Deposit Switch",
                description="Switch direct deposit to a new account",
                features=[
                    "Employer identification",
                    "Direct deposit switching",
                    "Switch status tracking",
                    "Payroll integration"
                ],
                use_cases=[
                    "Account switching",
                    "Direct deposit setup",
                    "Payroll management",
                    "Banking migration"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/deposit-switch/"
            ),
            PlaidProductInfo(
                name="transfer",
                display_name="Transfer",
                description="Bank-to-bank transfers and ACH processing",
                features=[
                    "ACH transfers",
                    "Same-day ACH",
                    "Transfer status tracking",
                    "Risk assessment"
                ],
                use_cases=[
                    "Money movement",
                    "Account funding",
                    "Payment processing",
                    "Cash management"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/transfer/"
            ),
            PlaidProductInfo(
                name="employment",
                display_name="Employment",
                description="Employment and income verification",
                features=[
                    "Employment verification",
                    "Income verification",
                    "Payroll data",
                    "Employment history"
                ],
                use_cases=[
                    "Background checks",
                    "Loan applications",
                    "Income verification",
                    "Employment screening"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/employment/"
            ),
            PlaidProductInfo(
                name="income_verification",
                display_name="Income Verification",
                description="Automated income and employment verification",
                features=[
                    "Income verification",
                    "Employment verification",
                    "Payroll connectivity",
                    "Real-time verification"
                ],
                use_cases=[
                    "Lending decisions",
                    "Credit underwriting",
                    "Income assessment",
                    "Risk evaluation"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/income-verification/"
            ),
            PlaidProductInfo(
                name="identity_verification",
                display_name="Identity Verification",
                description="Identity verification and document validation",
                features=[
                    "Document verification",
                    "Selfie verification",
                    "Identity matching",
                    "Fraud detection"
                ],
                use_cases=[
                    "Customer onboarding",
                    "KYC compliance",
                    "Identity verification",
                    "Fraud prevention"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/identity-verification/"
            ),
            PlaidProductInfo(
                name="monitor",
                display_name="Monitor",
                description="Ongoing account monitoring and alerts",
                features=[
                    "Transaction monitoring",
                    "Balance alerts",
                    "Account changes",
                    "Risk monitoring"
                ],
                use_cases=[
                    "Account monitoring",
                    "Fraud detection",
                    "Balance tracking",
                    "Risk management"
                ],
                supported=False,
                documentation_url="https://plaid.com/docs/api/products/monitor/"
            )
        ]
    
    def get_all_products(self) -> PlaidProductsResponse:
        """Get all Plaid products"""
        supported_count = sum(1 for p in self._products_data if p.supported)
        
        return PlaidProductsResponse(
            products=self._products_data,
            supported_count=supported_count,
            total_count=len(self._products_data),
            integration_status={
                "basic_banking": "fully_supported",
                "advanced_payments": "planned",
                "verification_services": "partially_supported",
                "monitoring": "planned"
            }
        )
    
    def get_supported_products(self) -> SupportedProductsResponse:
        """Get only supported Plaid products"""
        supported_products = [p for p in self._products_data if p.supported]
        
        return SupportedProductsResponse(
            products=supported_products,
            count=len(supported_products),
            supported_products=[p.name for p in supported_products]
        )
    
    def get_product_by_name(self, product_name: str) -> Optional[PlaidProductInfo]:
        """Get a specific product by name"""
        return next(
            (p for p in self._products_data if p.name == product_name.lower()),
            None
        )
    
    def get_product_details(self, product_name: str) -> Optional[PlaidProductResponse]:
        """Get detailed information for a specific product"""
        product = self.get_product_by_name(product_name)
        if not product:
            return None
        
        return PlaidProductResponse(
            product=product,
            available_in_environments=["sandbox", "production"] if product.supported else [],
            integration_notes={
                "implemented": product.supported,
                "status": "active" if product.supported else "planned",
                "documentation": product.documentation_url
            }
        )
    
    def get_products_by_category(self, category: str) -> List[PlaidProductInfo]:
        """Get products by category (supported/unsupported)"""
        if category.lower() == "supported":
            return [p for p in self._products_data if p.supported]
        elif category.lower() == "unsupported":
            return [p for p in self._products_data if not p.supported]
        else:
            return self._products_data
