"""
Plaid Liabilities Service

Service layer for handling liabilities data including credit cards, mortgages, and student loans.
Manages database operations, API interactions, and webhook processing.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
import json

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from api.db.deps import get_db
from api.common.utils import generate_id
from ..service import PlaidService
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

logger = logging.getLogger(__name__)


class LiabilitiesService:
    """Service for managing Plaid liabilities data"""
    
    def __init__(self, plaid_service: PlaidService):
        self.plaid_service = plaid_service
    
    # ==========================================
    # Main API Operations
    # ==========================================
    
    async def get_liabilities_from_plaid(
        self,
        access_token: str,
        account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch liabilities data from Plaid API
        
        Args:
            access_token: Plaid access token
            account_ids: Optional list of specific account IDs
            
        Returns:
            Raw liabilities data from Plaid
        """
        try:
            if not self.plaid_service.client:
                raise ValueError("Plaid client not configured")
            
            from plaid.model.liabilities_get_request import LiabilitiesGetRequest
            
            # Build request
            request_data = {
                "access_token": access_token
            }
            
            if account_ids:
                request_data["options"] = {
                    "account_ids": account_ids
                }
            
            request = LiabilitiesGetRequest(**request_data)
            response = self.plaid_service.client.liabilities_get(request)
            
            return {
                "accounts": response["accounts"],
                "liabilities": response["liabilities"],
                "item": response["item"],
                "request_id": response["request_id"]
            }
            
        except Exception as e:
            logger.error(f"Error fetching liabilities from Plaid: {str(e)}")
            raise
    
    async def sync_user_liabilities(
        self,
        user_id: str,
        item_id: str,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Sync all liabilities for a user's item from Plaid API
        
        Args:
            user_id: User's ULID
            item_id: Item's ULID  
            environment: Plaid environment
            
        Returns:
            Sync results with counts and status
        """
        try:
            logger.info(f"Syncing liabilities for user {user_id} item {item_id}")
            
            # Get item and access token from database
            with get_db() as session:
                from ..items.models import PlaidItem
                
                item = session.exec(
                    select(PlaidItem).where(
                        PlaidItem.id == item_id,
                        PlaidItem.user_id == user_id
                    )
                ).first()
                
                if not item:
                    raise ValueError(f"Item {item_id} not found for user {user_id}")
                
                access_token = item.access_token
            
            # Fetch liabilities from Plaid
            plaid_data = await self.get_liabilities_from_plaid(access_token)
            
            # Process and store the data
            sync_results = await self._process_liabilities_data(
                user_id=user_id,
                item_id=item_id,
                plaid_data=plaid_data,
                environment=environment
            )
            
            logger.info(f"Successfully synced {sync_results['total_synced']} liabilities for user {user_id}")
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing liabilities for user {user_id}: {str(e)}")
            raise
    
    async def get_user_liabilities(
        self,
        user_id: str,
        item_id: Optional[str] = None,
        liability_types: Optional[List[str]] = None
    ) -> LiabilitiesResponse:
        """
        Get user's liabilities from database
        
        Args:
            user_id: User's ULID
            item_id: Optional specific item ULID
            liability_types: Optional filter by types (credit_card, mortgage, student_loan)
            
        Returns:
            Formatted liabilities response
        """
        try:
            with get_db() as session:
                # Build query
                query = select(PlaidLiability).where(
                    PlaidLiability.user_id == user_id,
                    PlaidLiability.status == "active"
                )
                
                if item_id:
                    query = query.where(PlaidLiability.item_id == item_id)
                
                if liability_types:
                    query = query.where(PlaidLiability.liability_type.in_(liability_types))
                
                liabilities = session.exec(query).all()
                
                # Format response by type
                response = LiabilitiesResponse()
                
                for liability in liabilities:
                    if liability.liability_type == "credit_card":
                        credit_data = await self._format_credit_card_liability(session, liability)
                        response.credit.append(credit_data)
                    elif liability.liability_type == "mortgage":
                        mortgage_data = await self._format_mortgage_liability(session, liability)
                        response.mortgage.append(mortgage_data)
                    elif liability.liability_type == "student_loan":
                        student_data = await self._format_student_loan_liability(session, liability)
                        response.student.append(student_data)
                
                return response
            
        except Exception as e:
            logger.error(f"Error getting user liabilities: {str(e)}")
            raise
    
    # ==========================================
    # Data Processing Methods
    # ==========================================
    
    async def _process_liabilities_data(
        self,
        user_id: str,
        item_id: str,
        plaid_data: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Process and store liabilities data from Plaid API"""
        
        sync_results = {
            "total_synced": 0,
            "credit_cards": 0,
            "mortgages": 0,
            "student_loans": 0,
            "errors": []
        }
        
        try:
            with get_db() as session:
                accounts = plaid_data.get("accounts", [])
                liabilities = plaid_data.get("liabilities", {})
                
                # Process each account type
                if "credit" in liabilities:
                    count = await self._process_credit_cards(
                        session, user_id, item_id, accounts, liabilities["credit"], environment
                    )
                    sync_results["credit_cards"] = count
                    sync_results["total_synced"] += count
                
                if "mortgage" in liabilities:
                    count = await self._process_mortgages(
                        session, user_id, item_id, accounts, liabilities["mortgage"], environment
                    )
                    sync_results["mortgages"] = count
                    sync_results["total_synced"] += count
                
                if "student" in liabilities:
                    count = await self._process_student_loans(
                        session, user_id, item_id, accounts, liabilities["student"], environment
                    )
                    sync_results["student_loans"] = count
                    sync_results["total_synced"] += count
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Error processing liabilities data: {str(e)}")
            sync_results["errors"].append(str(e))
            raise
        
        return sync_results
    
    async def _process_credit_cards(
        self,
        session: Session,
        user_id: str,
        item_id: str,
        accounts: List[Dict],
        credit_liabilities: List[Dict],
        environment: str
    ) -> int:
        """Process credit card liabilities"""
        
        count = 0
        
        for credit_data in credit_liabilities:
            try:
                account_id = credit_data["account_id"]
                
                # Find corresponding account
                account = next((acc for acc in accounts if acc["account_id"] == account_id), None)
                if not account:
                    continue
                
                # Create or update liability record
                liability = await self._upsert_liability(
                    session, user_id, item_id, account, "credit_card", environment
                )
                
                # Create or update credit card details
                await self._upsert_credit_card_details(session, liability.id, credit_data)
                
                # Process APRs
                if "aprs" in credit_data:
                    await self._upsert_credit_card_aprs(session, liability.id, credit_data["aprs"])
                
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing credit card {credit_data.get('account_id')}: {str(e)}")
                continue
        
        return count
    
    async def _process_mortgages(
        self,
        session: Session,
        user_id: str,
        item_id: str,
        accounts: List[Dict],
        mortgage_liabilities: List[Dict],
        environment: str
    ) -> int:
        """Process mortgage liabilities"""
        
        count = 0
        
        for mortgage_data in mortgage_liabilities:
            try:
                account_id = mortgage_data["account_id"]
                
                # Find corresponding account
                account = next((acc for acc in accounts if acc["account_id"] == account_id), None)
                if not account:
                    continue
                
                # Create or update liability record
                liability = await self._upsert_liability(
                    session, user_id, item_id, account, "mortgage", environment
                )
                
                # Create or update mortgage details
                await self._upsert_mortgage_details(session, liability.id, mortgage_data)
                
                # Process property address if present
                if "property_address" in mortgage_data:
                    await self._upsert_mortgage_property_address(
                        session, liability.id, mortgage_data["property_address"]
                    )
                
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing mortgage {mortgage_data.get('account_id')}: {str(e)}")
                continue
        
        return count
    
    async def _process_student_loans(
        self,
        session: Session,
        user_id: str,
        item_id: str,
        accounts: List[Dict],
        student_liabilities: List[Dict],
        environment: str
    ) -> int:
        """Process student loan liabilities"""
        
        count = 0
        
        for student_data in student_liabilities:
            try:
                account_id = student_data["account_id"]
                
                # Find corresponding account
                account = next((acc for acc in accounts if acc["account_id"] == account_id), None)
                if not account:
                    continue
                
                # Create or update liability record
                liability = await self._upsert_liability(
                    session, user_id, item_id, account, "student_loan", environment
                )
                
                # Create or update student loan details
                await self._upsert_student_loan_details(session, liability.id, student_data)
                
                # Process PSLF status if present
                if "pslf_status" in student_data:
                    await self._upsert_student_pslf_status(
                        session, liability.id, student_data["pslf_status"]
                    )
                
                # Process repayment plan if present
                if "repayment_plan" in student_data:
                    await self._upsert_student_repayment_plan(
                        session, liability.id, student_data["repayment_plan"]
                    )
                
                # Process servicer address if present
                if "servicer_address" in student_data:
                    await self._upsert_student_servicer_address(
                        session, liability.id, student_data["servicer_address"]
                    )
                
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing student loan {student_data.get('account_id')}: {str(e)}")
                continue
        
        return count
    
    # ==========================================
    # Database Operations
    # ==========================================
    
    async def _upsert_liability(
        self,
        session: Session,
        user_id: str,
        item_id: str,
        account: Dict[str, Any],
        liability_type: str,
        environment: str
    ) -> PlaidLiability:
        """Create or update a liability record"""
        
        account_id = account["account_id"]
        
        # Check if liability exists
        existing = session.exec(
            select(PlaidLiability).where(
                PlaidLiability.user_id == user_id,
                PlaidLiability.plaid_account_id == account_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.account_name = account.get("name")
            existing.account_official_name = account.get("official_name")
            existing.account_mask = account.get("mask")
            existing.account_type = account.get("type")
            existing.account_subtype = account.get("subtype")
            existing.current_balance = account.get("balances", {}).get("current")
            existing.available_balance = account.get("balances", {}).get("available")
            existing.limit_amount = account.get("balances", {}).get("limit")
            existing.currency_code = account.get("balances", {}).get("iso_currency_code", "USD")
            existing.last_updated = datetime.utcnow()
            existing.sync_status = "active"
            existing.sync_error = None
            existing.updated_at = datetime.utcnow()
            
            session.add(existing)
            return existing
        
        else:
            # Create new record
            liability = PlaidLiability(
                id=generate_id(),
                user_id=user_id,
                item_id=item_id,
                account_id=generate_id(),  # Internal account ID
                plaid_account_id=account_id,
                account_name=account.get("name"),
                account_official_name=account.get("official_name"),
                account_mask=account.get("mask"),
                account_type=account.get("type"),
                account_subtype=account.get("subtype"),
                liability_type=liability_type,
                current_balance=account.get("balances", {}).get("current"),
                available_balance=account.get("balances", {}).get("available"),
                limit_amount=account.get("balances", {}).get("limit"),
                currency_code=account.get("balances", {}).get("iso_currency_code", "USD"),
                last_updated=datetime.utcnow(),
                environment=environment
            )
            
            session.add(liability)
            return liability
    
    async def _upsert_credit_card_details(
        self,
        session: Session,
        liability_id: str,
        credit_data: Dict[str, Any]
    ) -> None:
        """Create or update credit card details"""
        
        # Check if details exist
        existing = session.exec(
            select(PlaidCreditCardDetails).where(
                PlaidCreditCardDetails.liability_id == liability_id
            )
        ).first()
        
        # Parse dates safely
        def parse_date(date_str):
            if date_str:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except:
                    return None
            return None
        
        if existing:
            # Update existing
            existing.is_overdue = credit_data.get("is_overdue")
            existing.last_payment_amount = credit_data.get("last_payment_amount")
            existing.last_payment_date = parse_date(credit_data.get("last_payment_date"))
            existing.last_statement_issue_date = parse_date(credit_data.get("last_statement_issue_date"))
            existing.last_statement_balance = credit_data.get("last_statement_balance")
            existing.minimum_payment_amount = credit_data.get("minimum_payment_amount")
            existing.next_payment_due_date = parse_date(credit_data.get("next_payment_due_date"))
            existing.updated_at = datetime.utcnow()
            
            session.add(existing)
        
        else:
            # Create new
            details = PlaidCreditCardDetails(
                id=generate_id(),
                liability_id=liability_id,
                is_overdue=credit_data.get("is_overdue"),
                last_payment_amount=credit_data.get("last_payment_amount"),
                last_payment_date=parse_date(credit_data.get("last_payment_date")),
                last_statement_issue_date=parse_date(credit_data.get("last_statement_issue_date")),
                last_statement_balance=credit_data.get("last_statement_balance"),
                minimum_payment_amount=credit_data.get("minimum_payment_amount"),
                next_payment_due_date=parse_date(credit_data.get("next_payment_due_date"))
            )
            
            session.add(details)
    
    async def _upsert_credit_card_aprs(
        self,
        session: Session,
        liability_id: str,
        aprs_data: List[Dict[str, Any]]
    ) -> None:
        """Create or update credit card APRs"""
        
        # Delete existing APRs
        existing_aprs = session.exec(
            select(PlaidCreditCardAPR).where(
                PlaidCreditCardAPR.liability_id == liability_id
            )
        ).all()
        
        for apr in existing_aprs:
            session.delete(apr)
        
        # Create new APRs
        for apr_data in aprs_data:
            apr = PlaidCreditCardAPR(
                id=generate_id(),
                liability_id=liability_id,
                apr_percentage=apr_data.get("apr_percentage"),
                apr_type=apr_data.get("apr_type"),
                balance_subject_to_apr=apr_data.get("balance_subject_to_apr"),
                interest_charge_amount=apr_data.get("interest_charge_amount")
            )
            session.add(apr)
    
    # ==========================================
    # Formatting Methods
    # ==========================================
    
    async def _format_credit_card_liability(
        self,
        session: Session,
        liability: PlaidLiability
    ) -> CreditCardLiabilityResponse:
        """Format credit card liability for response"""
        
        # Get details
        details = session.exec(
            select(PlaidCreditCardDetails).where(
                PlaidCreditCardDetails.liability_id == liability.id
            )
        ).first()
        
        # Get APRs
        aprs = session.exec(
            select(PlaidCreditCardAPR).where(
                PlaidCreditCardAPR.liability_id == liability.id
            )
        ).all()
        
        apr_responses = [
            LiabilityAPRResponse(
                apr_percentage=apr.apr_percentage,
                apr_type=apr.apr_type,
                balance_subject_to_apr=apr.balance_subject_to_apr,
                interest_charge_amount=apr.interest_charge_amount
            ) for apr in aprs
        ]
        
        return CreditCardLiabilityResponse(
            account_id=liability.plaid_account_id,
            aprs=apr_responses,
            is_overdue=details.is_overdue if details else None,
            last_payment_amount=details.last_payment_amount if details else None,
            last_payment_date=details.last_payment_date.isoformat() if details and details.last_payment_date else None,
            last_statement_issue_date=details.last_statement_issue_date.isoformat() if details and details.last_statement_issue_date else None,
            last_statement_balance=details.last_statement_balance if details else None,
            minimum_payment_amount=details.minimum_payment_amount if details else None,
            next_payment_due_date=details.next_payment_due_date.isoformat() if details and details.next_payment_due_date else None
        )
    
    # Additional formatting methods would go here for mortgage and student loan data...
    # (Implementing key methods for demonstration, full implementation would include all formatters)
    
    async def _format_mortgage_liability(
        self,
        session: Session,
        liability: PlaidLiability
    ) -> MortgageLiabilityResponse:
        """Format mortgage liability for response"""
        
        # This would include full mortgage details formatting
        # Placeholder for demonstration
        return MortgageLiabilityResponse(account_id=liability.plaid_account_id)
    
    async def _format_student_loan_liability(
        self,
        session: Session,
        liability: PlaidLiability
    ) -> StudentLoanLiabilityResponse:
        """Format student loan liability for response"""
        
        # This would include full student loan details formatting
        # Placeholder for demonstration
        return StudentLoanLiabilityResponse(account_id=liability.plaid_account_id)
    
    # ==========================================
    # Webhook Processing
    # ==========================================
    
    async def process_webhook_event(
        self,
        webhook_data: Dict[str, Any]
    ) -> bool:
        """Process liabilities webhook event"""
        
        try:
            item_id = webhook_data.get("item_id")
            webhook_code = webhook_data.get("webhook_code")
            environment = webhook_data.get("environment", "sandbox")
            
            logger.info(f"Processing liabilities webhook {webhook_code} for item {item_id}")
            
            # Store webhook event
            with get_db() as session:
                webhook_event = PlaidLiabilityWebhookEvent(
                    id=generate_id(),
                    item_id=item_id,
                    webhook_code=webhook_code,
                    webhook_payload=json.dumps(webhook_data),
                    account_ids_with_new_liabilities=json.dumps(
                        webhook_data.get("account_ids_with_new_liabilities", [])
                    ),
                    account_ids_with_updated_liabilities=json.dumps(
                        webhook_data.get("account_ids_with_updated_liabilities", {})
                    ),
                    environment=environment
                )
                
                session.add(webhook_event)
                session.commit()
                
                # Process the webhook based on code
                if webhook_code == "DEFAULT_UPDATE":
                    await self._handle_default_update_webhook(webhook_data)
                
                # Mark as processed
                webhook_event.processed = True
                webhook_event.processed_at = datetime.utcnow()
                session.add(webhook_event)
                session.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing liabilities webhook: {str(e)}")
            return False
    
    async def _handle_default_update_webhook(
        self,
        webhook_data: Dict[str, Any]
    ) -> None:
        """Handle DEFAULT_UPDATE webhook for liabilities"""
        
        # This would trigger a re-sync of liability data
        # Implementation would depend on business requirements
        logger.info("Handling DEFAULT_UPDATE webhook for liabilities")

    # ==========================================
    # Missing Helper Methods
    # ==========================================

    async def _upsert_mortgage_details(
        self,
        session: Session,
        liability_id: str,
        mortgage_data: Dict[str, Any]
    ) -> None:
        """Upsert mortgage details for a liability"""
        
        # Check if details already exist
        existing = session.exec(
            select(PlaidMortgageDetails).where(
                PlaidMortgageDetails.liability_id == liability_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.account_number = mortgage_data.get("account_number")
            existing.current_late_fee = mortgage_data.get("current_late_fee")
            existing.escrow_balance = mortgage_data.get("escrow_balance")
            existing.has_pmi = mortgage_data.get("has_pmi")
            existing.has_prepayment_penalty = mortgage_data.get("has_prepayment_penalty")
            existing.interest_rate_percentage = mortgage_data.get("interest_rate", {}).get("percentage")
            existing.interest_rate_type = mortgage_data.get("interest_rate", {}).get("type")
            existing.last_payment_amount = mortgage_data.get("last_payment_amount")
            existing.last_payment_date = mortgage_data.get("last_payment_date")
            existing.loan_type_description = mortgage_data.get("loan_type_description")
            existing.loan_term = mortgage_data.get("loan_term")
            existing.maturity_date = mortgage_data.get("maturity_date")
            existing.next_monthly_payment = mortgage_data.get("next_monthly_payment")
            existing.next_payment_due_date = mortgage_data.get("next_payment_due_date")
            existing.origination_date = mortgage_data.get("origination_date")
            existing.origination_principal_amount = mortgage_data.get("origination_principal_amount")
            existing.past_due_amount = mortgage_data.get("past_due_amount")
            existing.ytd_interest_paid = mortgage_data.get("ytd_interest_paid")
            existing.ytd_principal_paid = mortgage_data.get("ytd_principal_paid")
            session.add(existing)
        else:
            # Create new record
            new_details = PlaidMortgageDetails(
                id=generate_id(),
                liability_id=liability_id,
                account_number=mortgage_data.get("account_number"),
                current_late_fee=mortgage_data.get("current_late_fee"),
                escrow_balance=mortgage_data.get("escrow_balance"),
                has_pmi=mortgage_data.get("has_pmi"),
                has_prepayment_penalty=mortgage_data.get("has_prepayment_penalty"),
                interest_rate_percentage=mortgage_data.get("interest_rate", {}).get("percentage"),
                interest_rate_type=mortgage_data.get("interest_rate", {}).get("type"),
                last_payment_amount=mortgage_data.get("last_payment_amount"),
                last_payment_date=mortgage_data.get("last_payment_date"),
                loan_type_description=mortgage_data.get("loan_type_description"),
                loan_term=mortgage_data.get("loan_term"),
                maturity_date=mortgage_data.get("maturity_date"),
                next_monthly_payment=mortgage_data.get("next_monthly_payment"),
                next_payment_due_date=mortgage_data.get("next_payment_due_date"),
                origination_date=mortgage_data.get("origination_date"),
                origination_principal_amount=mortgage_data.get("origination_principal_amount"),
                past_due_amount=mortgage_data.get("past_due_amount"),
                ytd_interest_paid=mortgage_data.get("ytd_interest_paid"),
                ytd_principal_paid=mortgage_data.get("ytd_principal_paid")
            )
            session.add(new_details)

    async def _upsert_mortgage_property_address(
        self,
        session: Session,
        liability_id: str,
        property_address: Dict[str, Any]
    ) -> None:
        """Upsert property address for a mortgage"""
        
        if not property_address:
            return
            
        # Check if address already exists
        existing = session.exec(
            select(PlaidMortgagePropertyAddress).where(
                PlaidMortgagePropertyAddress.liability_id == liability_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.street = property_address.get("street")
            existing.city = property_address.get("city")
            existing.region = property_address.get("region")
            existing.postal_code = property_address.get("postal_code")
            existing.country = property_address.get("country")
            session.add(existing)
        else:
            # Create new record
            new_address = PlaidMortgagePropertyAddress(
                id=generate_id(),
                liability_id=liability_id,
                street=property_address.get("street"),
                city=property_address.get("city"),
                region=property_address.get("region"),
                postal_code=property_address.get("postal_code"),
                country=property_address.get("country")
            )
            session.add(new_address)

    async def _upsert_student_loan_details(
        self,
        session: Session,
        liability_id: str,
        student_data: Dict[str, Any]
    ) -> None:
        """Upsert student loan details for a liability"""
        
        # Check if details already exist
        existing = session.exec(
            select(PlaidStudentLoanDetails).where(
                PlaidStudentLoanDetails.liability_id == liability_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.account_number = student_data.get("account_number")
            existing.disbursement_dates = json.dumps(student_data.get("disbursement_dates", []))
            existing.expected_payoff_date = student_data.get("expected_payoff_date")
            existing.guarantor = student_data.get("guarantor")
            existing.interest_rate_percentage = student_data.get("interest_rate_percentage")
            existing.is_overdue = student_data.get("is_overdue")
            existing.last_payment_amount = student_data.get("last_payment_amount")
            existing.last_payment_date = student_data.get("last_payment_date")
            existing.last_statement_issue_date = student_data.get("last_statement_issue_date")
            existing.loan_name = student_data.get("loan_name")
            existing.loan_status_type = student_data.get("loan_status", {}).get("type")
            existing.loan_status_end_date = student_data.get("loan_status", {}).get("end_date")
            existing.minimum_payment_amount = student_data.get("minimum_payment_amount")
            existing.next_payment_due_date = student_data.get("next_payment_due_date")
            existing.origination_date = student_data.get("origination_date")
            existing.origination_principal_amount = student_data.get("origination_principal_amount")
            existing.outstanding_interest_amount = student_data.get("outstanding_interest_amount")
            existing.payment_reference_number = student_data.get("payment_reference_number")
            existing.sequence_number = student_data.get("sequence_number")
            existing.servicer_name = student_data.get("servicer_name")
            existing.servicer_website = student_data.get("servicer_website")
            existing.ytd_interest_paid = student_data.get("ytd_interest_paid")
            existing.ytd_principal_paid = student_data.get("ytd_principal_paid")
            session.add(existing)
        else:
            # Create new record
            new_details = PlaidStudentLoanDetails(
                id=generate_id(),
                liability_id=liability_id,
                account_number=student_data.get("account_number"),
                disbursement_dates=json.dumps(student_data.get("disbursement_dates", [])),
                expected_payoff_date=student_data.get("expected_payoff_date"),
                guarantor=student_data.get("guarantor"),
                interest_rate_percentage=student_data.get("interest_rate_percentage"),
                is_overdue=student_data.get("is_overdue"),
                last_payment_amount=student_data.get("last_payment_amount"),
                last_payment_date=student_data.get("last_payment_date"),
                last_statement_issue_date=student_data.get("last_statement_issue_date"),
                loan_name=student_data.get("loan_name"),
                loan_status_type=student_data.get("loan_status", {}).get("type"),
                loan_status_end_date=student_data.get("loan_status", {}).get("end_date"),
                minimum_payment_amount=student_data.get("minimum_payment_amount"),
                next_payment_due_date=student_data.get("next_payment_due_date"),
                origination_date=student_data.get("origination_date"),
                origination_principal_amount=student_data.get("origination_principal_amount"),
                outstanding_interest_amount=student_data.get("outstanding_interest_amount"),
                payment_reference_number=student_data.get("payment_reference_number"),
                sequence_number=student_data.get("sequence_number"),
                servicer_name=student_data.get("servicer_name"),
                servicer_website=student_data.get("servicer_website"),
                ytd_interest_paid=student_data.get("ytd_interest_paid"),
                ytd_principal_paid=student_data.get("ytd_principal_paid")
            )
            session.add(new_details)

    async def _upsert_student_pslf_status(
        self,
        session: Session,
        liability_id: str,
        pslf_status: Dict[str, Any]
    ) -> None:
        """Upsert PSLF status for a student loan"""
        
        if not pslf_status:
            return
            
        # Check if PSLF status already exists
        existing = session.exec(
            select(PlaidStudentLoanPSLFStatus).where(
                PlaidStudentLoanPSLFStatus.liability_id == liability_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.estimated_eligibility_date = pslf_status.get("estimated_eligibility_date")
            existing.payments_made = pslf_status.get("payments_made")
            existing.payments_remaining = pslf_status.get("payments_remaining")
            session.add(existing)
        else:
            # Create new record
            new_pslf = PlaidStudentLoanPSLFStatus(
                id=generate_id(),
                liability_id=liability_id,
                estimated_eligibility_date=pslf_status.get("estimated_eligibility_date"),
                payments_made=pslf_status.get("payments_made"),
                payments_remaining=pslf_status.get("payments_remaining")
            )
            session.add(new_pslf)

    async def _upsert_student_repayment_plan(
        self,
        session: Session,
        liability_id: str,
        repayment_plan: Dict[str, Any]
    ) -> None:
        """Upsert repayment plan for a student loan"""
        
        if not repayment_plan:
            return
            
        # Check if repayment plan already exists
        existing = session.exec(
            select(PlaidStudentLoanRepaymentPlan).where(
                PlaidStudentLoanRepaymentPlan.liability_id == liability_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.description = repayment_plan.get("description")
            existing.type = repayment_plan.get("type")
            session.add(existing)
        else:
            # Create new record
            new_plan = PlaidStudentLoanRepaymentPlan(
                id=generate_id(),
                liability_id=liability_id,
                description=repayment_plan.get("description"),
                type=repayment_plan.get("type")
            )
            session.add(new_plan)

    async def _upsert_student_servicer_address(
        self,
        session: Session,
        liability_id: str,
        servicer_address: Dict[str, Any]
    ) -> None:
        """Upsert servicer address for a student loan"""
        
        if not servicer_address:
            return
            
        # Check if servicer address already exists
        existing = session.exec(
            select(PlaidStudentLoanServicerAddress).where(
                PlaidStudentLoanServicerAddress.liability_id == liability_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.street = servicer_address.get("street")
            existing.city = servicer_address.get("city")
            existing.region = servicer_address.get("region")
            existing.postal_code = servicer_address.get("postal_code")
            existing.country = servicer_address.get("country")
            session.add(existing)
        else:
            # Create new record
            new_address = PlaidStudentLoanServicerAddress(
                id=generate_id(),
                liability_id=liability_id,
                street=servicer_address.get("street"),
                city=servicer_address.get("city"),
                region=servicer_address.get("region"),
                postal_code=servicer_address.get("postal_code"),
                country=servicer_address.get("country")
            )
            session.add(new_address)


# Global service instance
def get_liabilities_service(plaid_service: Optional[PlaidService] = None) -> LiabilitiesService:
    """Get or create liabilities service instance"""
    if plaid_service is None:
        from ..service import get_plaid_service
        plaid_service = get_plaid_service()
    
    return LiabilitiesService(plaid_service)
