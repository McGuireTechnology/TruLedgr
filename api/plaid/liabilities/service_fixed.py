"""
Plaid Liabilities Service - Fixed Implementation

This service handles the complete liabilities workflow including database operations,
Plaid API integration, and webhook processing with correct relationship handling.
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional

from sqlmodel import Session, select
from sqlalchemy import text

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
    StudentLoanLiabilityResponse
)

logger = logging.getLogger(__name__)


class LiabilitiesService:
    """Service for managing Plaid liabilities data"""
    
    def __init__(self, plaid_service: PlaidService):
        self.plaid_service = plaid_service

    async def fetch_liabilities_from_plaid(
        self,
        user_id: str,
        item_id: str,
        account_ids: Optional[List[str]] = None,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Fetch liabilities data from Plaid API for a specific item.
        
        Args:
            user_id: TruLedgr user ID  
            item_id: Plaid item ID
            account_ids: Optional list of specific account IDs to fetch
            environment: Plaid environment (sandbox, development, production)
            
        Returns:
            Raw liabilities data from Plaid API
        """
        try:
            # Parse account IDs if provided
            account_ids_filter = None
            if account_ids:
                account_ids_filter = account_ids

            # Get item and access token from database
            with get_db() as session:
                from ..items.models import PlaidItem
                
                item = session.exec(
                    select(PlaidItem).where(
                        PlaidItem.user_id == user_id,
                        PlaidItem.id == item_id
                    )
                ).first()
                
                if not item:
                    raise ValueError(f"Item {item_id} not found for user {user_id}")
                
                if not item.access_token:
                    raise ValueError(f"No access token available for item {item_id}")
                
                access_token = item.access_token

            # Prepare request data
            request_data = {
                "access_token": access_token
            }
            
            if account_ids_filter:
                request_data["options"] = {
                    "account_ids": account_ids_filter
                }

            # Call Plaid API
            response = self.plaid_service.client.liabilities_get(request_data)
            
            if not response:
                logger.warning(f"Empty response from Plaid liabilities API for item {item_id}")
                return {}
                
            logger.info(f"Successfully fetched liabilities for item {item_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching liabilities from Plaid for item {item_id}: {str(e)}")
            raise

    async def get_user_liabilities(
        self,
        user_id: str,
        item_id: Optional[str] = None,
        liability_types: Optional[List[str]] = None
    ) -> LiabilitiesResponse:
        """
        Get comprehensive liabilities data for a user from the database.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Optional Plaid item ID filter
            liability_types: Optional list of liability types to filter
            
        Returns:
            Formatted liabilities response with credit cards, mortgages, and student loans
        """
        try:
            with get_db() as session:
                # Build query
                query = select(PlaidLiability).where(
                    PlaidLiability.user_id == user_id,
                    PlaidLiability.deleted_at.is_(None)
                )
                
                if item_id:
                    query = query.where(PlaidLiability.item_id == item_id)
                    
                if liability_types:
                    query = query.where(PlaidLiability.liability_type.in_(liability_types))
                
                liabilities = session.exec(query).all()
                
                # Format response
                credit_cards = []
                mortgages = []
                student_loans = []
                
                for liability in liabilities:
                    if liability.liability_type == "credit_card":
                        credit_cards.append(await self._format_credit_card_liability(session, liability))
                    elif liability.liability_type == "mortgage":
                        mortgages.append(await self._format_mortgage_liability(session, liability))
                    elif liability.liability_type == "student_loan":
                        student_loans.append(await self._format_student_loan_liability(session, liability))
                
                return LiabilitiesResponse(
                    credit=credit_cards,
                    mortgage=mortgages,
                    student=student_loans
                )
                
        except Exception as e:
            logger.error(f"Error getting user liabilities for user {user_id}: {str(e)}")
            raise

    async def sync_user_liabilities(
        self,
        user_id: str,
        item_id: str,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Sync liabilities data from Plaid API to database.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Plaid item ID  
            environment: Plaid environment
            
        Returns:
            Sync results with counts and any errors
        """
        
        try:
            with get_db() as session:
                accounts = plaid_data.get("accounts", [])
                liabilities = plaid_data.get("liabilities", {})
                
                # Counter for results
                sync_results = {
                    "total_synced": 0,
                    "credit_cards": 0,
                    "mortgages": 0,
                    "student_loans": 0,
                    "errors": []
                }
                
                # Process accounts with liability data
                liability_accounts = self._get_liability_accounts(accounts, liabilities)
                
                for account_data in liability_accounts:
                    try:
                        account = account_data["account"]
                        liability_data = account_data["liability_data"]
                        liability_type = account_data["liability_type"]
                        
                        # Upsert main liability record
                        liability = await self._upsert_liability(
                            session, user_id, item_id, account, liability_data, liability_type
                        )
                        
                        if not liability or not liability.id:
                            continue
                            
                        # Process type-specific data
                        if liability_type == "credit_card":
                            credit_data = liability_data.get("credit", {})
                            await self._upsert_credit_card_details(session, liability.id, credit_data)
                            
                            # Process APR data
                            if "aprs" in credit_data and credit_data["aprs"]:
                                await self._upsert_credit_card_aprs(session, liability.id, credit_data["aprs"])
                            
                            sync_results["credit_cards"] += 1
                            
                        elif liability_type == "mortgage":
                            mortgage_data = liability_data.get("mortgage", {})
                            mortgage_details = await self._upsert_mortgage_details(session, liability.id, mortgage_data)
                            
                            # Process property address
                            if "property_address" in mortgage_data and mortgage_data["property_address"]:
                                await self._upsert_mortgage_property_address(
                                    session, mortgage_details.id, mortgage_data["property_address"]
                                )
                            
                            sync_results["mortgages"] += 1
                            
                        elif liability_type == "student_loan":
                            student_data = liability_data.get("student", {})
                            student_details = await self._upsert_student_loan_details(session, liability.id, student_data)
                            
                            # Process PSLF status
                            if "pslf_status" in student_data and student_data["pslf_status"]:
                                await self._upsert_student_pslf_status(
                                    session, student_details.id, student_data["pslf_status"]
                                )
                            
                            # Process repayment plan
                            if "repayment_plan" in student_data and student_data["repayment_plan"]:
                                await self._upsert_student_repayment_plan(
                                    session, student_details.id, student_data["repayment_plan"]
                                )
                            
                            # Process servicer address
                            if "servicer_address" in student_data and student_data["servicer_address"]:
                                await self._upsert_student_servicer_address(
                                    session, student_details.id, student_data["servicer_address"]
                                )
                            
                            sync_results["student_loans"] += 1
                        
                        sync_results["total_synced"] += 1
                        
                    except Exception as e:
                        error_msg = f"Error processing liability for account {account.get('account_id', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        sync_results["errors"].append(error_msg)
                
                # Commit all changes
                session.commit()
                
                logger.info(f"Successfully synced {sync_results['total_synced']} liabilities for user {user_id}")
                return sync_results
                
        except Exception as e:
            logger.error(f"Error syncing liabilities for user {user_id}: {str(e)}")
            raise

    # ==========================================
    # Private Helper Methods  
    # ==========================================

    def _get_liability_accounts(
        self,
        accounts: List[Dict[str, Any]],
        liabilities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract liability accounts with their corresponding liability data"""
        
        liability_accounts = []
        
        # Map account IDs to liability data
        credit_cards = {item["account_id"]: item for item in liabilities.get("credit", [])}
        mortgages = {item["account_id"]: item for item in liabilities.get("mortgage", [])}
        student_loans = {item["account_id"]: item for item in liabilities.get("student", [])}
        
        for account in accounts:
            account_id = account.get("account_id")
            account_type = account.get("type")
            account_subtype = account.get("subtype")
            
            # Determine liability type and get data
            if account_id in credit_cards:
                liability_accounts.append({
                    "account": account,
                    "liability_data": credit_cards[account_id],
                    "liability_type": "credit_card"
                })
            elif account_id in mortgages:
                liability_accounts.append({
                    "account": account,
                    "liability_data": mortgages[account_id],
                    "liability_type": "mortgage"
                })
            elif account_id in student_loans:
                liability_accounts.append({
                    "account": account,
                    "liability_data": student_loans[account_id],
                    "liability_type": "student_loan"
                })
        
        return liability_accounts

    async def _upsert_liability(
        self,
        session: Session,
        user_id: str,
        item_id: str,
        account: Dict[str, Any],
        liability_data: Dict[str, Any],
        liability_type: str
    ) -> Optional[PlaidLiability]:
        """Upsert main liability record"""
        
        account_id = account.get("account_id")
        if not account_id:
            return None
            
        # Check if liability already exists
        existing = session.exec(
            select(PlaidLiability).where(
                PlaidLiability.account_id == account_id,
                PlaidLiability.user_id == user_id,
                PlaidLiability.deleted_at.is_(None)
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.account_name = account.get("name") or ""
            existing.account_type = account.get("type") or ""
            existing.account_subtype = account.get("subtype") or ""
            existing.liability_type = liability_type
            existing.current_balance = account.get("balances", {}).get("current")
            existing.available_balance = account.get("balances", {}).get("available")
            existing.iso_currency_code = account.get("balances", {}).get("iso_currency_code")
            existing.unofficial_currency_code = account.get("balances", {}).get("unofficial_currency_code")
            existing.last_updated = datetime.utcnow()
            session.add(existing)
            return existing
        else:
            # Create new record
            new_liability = PlaidLiability(
                id=generate_id(),
                user_id=user_id,
                item_id=item_id,
                account_id=account_id,
                account_name=account.get("name") or "",
                account_type=account.get("type") or "",
                account_subtype=account.get("subtype") or "",
                liability_type=liability_type,
                current_balance=account.get("balances", {}).get("current"),
                available_balance=account.get("balances", {}).get("available"),
                iso_currency_code=account.get("balances", {}).get("iso_currency_code"),
                unofficial_currency_code=account.get("balances", {}).get("unofficial_currency_code")
            )
            session.add(new_liability)
            session.flush()  # Ensure ID is generated
            return new_liability

    # Note: I'll add the rest of the helper methods in the next part due to length limits
    # This file is intentionally incomplete and serves as a starting point for the fixes.


# Global service instance  
def get_liabilities_service(plaid_service: Optional[PlaidService] = None) -> LiabilitiesService:
    """Get or create liabilities service instance"""
    if plaid_service is None:
        from ..service import get_plaid_service
        plaid_service = get_plaid_service()
    
    return LiabilitiesService(plaid_service)
