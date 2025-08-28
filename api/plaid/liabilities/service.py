"""
Plaid Liabilities Service

Service methods for credit cards, mortgages, and student loans.
"""

from typing import List, Dict, Any, Optional
import logging

from plaid.api import plaid_api

logger = logging.getLogger(__name__)

class LiabilitiesService:
    """Service class for liabilities-related operations"""
    
    def __init__(self, plaid_client: plaid_api.PlaidApi):
        self.client = plaid_client
    
    async def get_liabilities(
        self,
        access_token: str,
        account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve liabilities data for an Item.
        
        Returns various details about credit cards, mortgages, and student loans
        including balances, due dates, loan terms, and account details.
        
        Args:
            access_token: Access token for the connected account
            account_ids: Optional list of specific account IDs to retrieve
            
        Returns:
            Dict containing accounts and liabilities data
        """
        try:
            # Import the required model here to avoid import order issues
            from plaid.model.liabilities_get_request import LiabilitiesGetRequest
            from plaid.model.liabilities_get_request_options import LiabilitiesGetRequestOptions
            
            # Build request
            if account_ids:
                options = LiabilitiesGetRequestOptions(account_ids=account_ids)
                request = LiabilitiesGetRequest(access_token=access_token, options=options)
            else:
                request = LiabilitiesGetRequest(access_token=access_token)
            response = self.client.liabilities_get(request)
            
            # Convert response to dictionary format for consistent API
            result = response.to_dict()
            
            return {
                'accounts': [
                    {
                        'account_id': account['account_id'],
                        'name': account['name'],
                        'official_name': account.get('official_name'),
                        'type': account['type'],
                        'subtype': account.get('subtype'),
                        'balances': {
                            'available': account['balances'].get('available'),
                            'current': account['balances'].get('current'),
                            'limit': account['balances'].get('limit'),
                            'iso_currency_code': account['balances'].get('iso_currency_code'),
                            'unofficial_currency_code': account['balances'].get('unofficial_currency_code')
                        },
                        'mask': account.get('mask')
                    }
                    for account in result['accounts']
                ],
                'liabilities': {
                    'credit': [
                        {
                            'account_id': credit.get('account_id'),
                            'aprs': [
                                {
                                    'apr_percentage': apr['apr_percentage'],
                                    'apr_type': apr['apr_type'],
                                    'balance_subject_to_apr': apr.get('balance_subject_to_apr'),
                                    'interest_charge_amount': apr.get('interest_charge_amount')
                                }
                                for apr in credit.get('aprs', [])
                            ],
                            'is_overdue': credit.get('is_overdue'),
                            'last_payment_amount': credit.get('last_payment_amount'),
                            'last_payment_date': credit.get('last_payment_date'),
                            'last_statement_issue_date': credit.get('last_statement_issue_date'),
                            'last_statement_balance': credit.get('last_statement_balance'),
                            'minimum_payment_amount': credit.get('minimum_payment_amount'),
                            'next_payment_due_date': credit.get('next_payment_due_date')
                        }
                        for credit in result['liabilities'].get('credit', [])
                    ] if result['liabilities'].get('credit') else [],
                    'mortgage': [
                        {
                            'account_id': mortgage['account_id'],
                            'account_number': mortgage.get('account_number'),
                            'current_late_fee': mortgage.get('current_late_fee'),
                            'escrow_balance': mortgage.get('escrow_balance'),
                            'has_pmi': mortgage.get('has_pmi'),
                            'has_prepayment_penalty': mortgage.get('has_prepayment_penalty'),
                            'interest_rate': {
                                'percentage': mortgage.get('interest_rate', {}).get('percentage'),
                                'type': mortgage.get('interest_rate', {}).get('type')
                            } if mortgage.get('interest_rate') else None,
                            'last_payment_amount': mortgage.get('last_payment_amount'),
                            'last_payment_date': mortgage.get('last_payment_date'),
                            'loan_term': mortgage.get('loan_term'),
                            'loan_type_description': mortgage.get('loan_type_description'),
                            'maturity_date': mortgage.get('maturity_date'),
                            'next_monthly_payment': mortgage.get('next_monthly_payment'),
                            'next_payment_due_date': mortgage.get('next_payment_due_date'),
                            'origination_date': mortgage.get('origination_date'),
                            'origination_principal_amount': mortgage.get('origination_principal_amount'),
                            'past_due_amount': mortgage.get('past_due_amount'),
                            'property_address': {
                                'city': mortgage.get('property_address', {}).get('city'),
                                'country': mortgage.get('property_address', {}).get('country'),
                                'postal_code': mortgage.get('property_address', {}).get('postal_code'),
                                'region': mortgage.get('property_address', {}).get('region'),
                                'street': mortgage.get('property_address', {}).get('street')
                            } if mortgage.get('property_address') else None,
                            'ytd_interest_paid': mortgage.get('ytd_interest_paid'),
                            'ytd_principal_paid': mortgage.get('ytd_principal_paid')
                        }
                        for mortgage in result['liabilities'].get('mortgage', [])
                    ] if result['liabilities'].get('mortgage') else [],
                    'student': [
                        {
                            'account_id': student['account_id'],
                            'account_number': student.get('account_number'),
                            'disbursement_dates': student.get('disbursement_dates'),
                            'expected_payoff_date': student.get('expected_payoff_date'),
                            'guarantor': student.get('guarantor'),
                            'interest_rate_percentage': student['interest_rate_percentage'],
                            'is_overdue': student.get('is_overdue'),
                            'last_payment_amount': student.get('last_payment_amount'),
                            'last_payment_date': student.get('last_payment_date'),
                            'last_statement_balance': student.get('last_statement_balance'),
                            'last_statement_issue_date': student.get('last_statement_issue_date'),
                            'loan_name': student.get('loan_name'),
                            'loan_status': {
                                'end_date': student.get('loan_status', {}).get('end_date'),
                                'type': student.get('loan_status', {}).get('type')
                            } if student.get('loan_status') else None,
                            'minimum_payment_amount': student.get('minimum_payment_amount'),
                            'next_payment_due_date': student.get('next_payment_due_date'),
                            'origination_date': student.get('origination_date'),
                            'origination_principal_amount': student.get('origination_principal_amount'),
                            'outstanding_interest_amount': student.get('outstanding_interest_amount'),
                            'payment_reference_number': student.get('payment_reference_number'),
                            'pslf_status': {
                                'estimated_eligibility_date': student.get('pslf_status', {}).get('estimated_eligibility_date'),
                                'payments_made': student.get('pslf_status', {}).get('payments_made'),
                                'payments_remaining': student.get('pslf_status', {}).get('payments_remaining')
                            } if student.get('pslf_status') else None,
                            'repayment_plan': {
                                'description': student.get('repayment_plan', {}).get('description'),
                                'type': student.get('repayment_plan', {}).get('type')
                            } if student.get('repayment_plan') else None,
                            'sequence_number': student.get('sequence_number'),
                            'servicer_address': {
                                'city': student.get('servicer_address', {}).get('city'),
                                'country': student.get('servicer_address', {}).get('country'),
                                'postal_code': student.get('servicer_address', {}).get('postal_code'),
                                'region': student.get('servicer_address', {}).get('region'),
                                'street': student.get('servicer_address', {}).get('street')
                            } if student.get('servicer_address') else None,
                            'ytd_interest_paid': student.get('ytd_interest_paid'),
                            'ytd_principal_paid': student.get('ytd_principal_paid')
                        }
                        for student in result['liabilities'].get('student', [])
                    ] if result['liabilities'].get('student') else []
                },
                'request_id': result['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error fetching liabilities: {str(e)}")
            raise
