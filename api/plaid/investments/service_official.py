"""
Plaid Investments Service - Official Implementation

This service handles the complete investments workflow including:
- Holdings data retrieval and storage
- Investment transactions management
- Securities metadata management
- Account balance tracking
- Webhook processing for investment updates
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
    PlaidInvestmentAccount,
    PlaidInvestmentSecurity,
    PlaidInvestmentOptionContract,
    PlaidInvestmentFixedIncome,
    PlaidInvestmentHolding,
    PlaidInvestmentTransaction,
    PlaidInvestmentHistory,
    PlaidInvestmentWebhookEvent,
    InvestmentHoldingsResponse,
    InvestmentTransactionsResponse,
    InvestmentHoldingResponse,
    InvestmentSecurityResponse,
    InvestmentTransactionResponse,
    InvestmentAccountResponse
)

logger = logging.getLogger(__name__)


class InvestmentsService:
    """Service for managing Plaid investments data"""
    
    def __init__(self, plaid_service: PlaidService):
        self.plaid_service = plaid_service

    # ==========================================
    # Holdings Management
    # ==========================================

    async def fetch_holdings_from_plaid(
        self,
        user_id: str,
        item_id: str,
        account_ids: Optional[List[str]] = None,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Fetch investment holdings from Plaid API.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Plaid item ID
            account_ids: Optional list of specific account IDs
            environment: Plaid environment
            
        Returns:
            Raw holdings data from Plaid API
        """
        try:
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
            
            if account_ids:
                request_data["options"] = {
                    "account_ids": account_ids
                }

            # Call Plaid API
            response = self.plaid_service.client.investments_holdings_get(request_data)
            
            if not response:
                logger.warning(f"Empty response from Plaid holdings API for item {item_id}")
                return {}
                
            logger.info(f"Successfully fetched holdings for item {item_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching holdings from Plaid for item {item_id}: {str(e)}")
            raise

    async def sync_holdings_data(
        self,
        user_id: str,
        item_id: str,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Sync holdings data from Plaid API to database.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Plaid item ID
            environment: Plaid environment
            
        Returns:
            Sync results with counts and any errors
        """
        try:
            # Fetch holdings data from Plaid
            plaid_data = await self.fetch_holdings_from_plaid(user_id, item_id, environment=environment)
            
            if not plaid_data:
                return {
                    "success": False,
                    "message": "No holdings data received from Plaid",
                    "accounts_synced": 0,
                    "holdings_synced": 0,
                    "securities_synced": 0,
                    "errors": []
                }

            with get_db() as session:
                accounts = plaid_data.get("accounts", [])
                holdings = plaid_data.get("holdings", [])
                securities = plaid_data.get("securities", [])
                
                sync_results = {
                    "success": True,
                    "message": "Holdings synced successfully",
                    "accounts_synced": 0,
                    "holdings_synced": 0,
                    "securities_synced": 0,
                    "errors": []
                }
                
                # Process investment accounts
                for account_data in accounts:
                    if account_data.get("type") == "investment":
                        try:
                            await self._upsert_investment_account(session, user_id, item_id, account_data, environment)
                            sync_results["accounts_synced"] += 1
                        except Exception as e:
                            error_msg = f"Error processing account {account_data.get('account_id', 'unknown')}: {str(e)}"
                            logger.error(error_msg)
                            sync_results["errors"].append(error_msg)
                
                # Process securities first (holdings reference them)
                for security_data in securities:
                    try:
                        await self._upsert_security(session, security_data, environment)
                        sync_results["securities_synced"] += 1
                    except Exception as e:
                        error_msg = f"Error processing security {security_data.get('security_id', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        sync_results["errors"].append(error_msg)
                
                # Process holdings
                for holding_data in holdings:
                    try:
                        await self._upsert_holding(session, user_id, holding_data, environment)
                        sync_results["holdings_synced"] += 1
                    except Exception as e:
                        error_msg = f"Error processing holding {holding_data.get('account_id', 'unknown')}/{holding_data.get('security_id', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        sync_results["errors"].append(error_msg)
                
                # Commit all changes
                session.commit()
                
                logger.info(f"Successfully synced holdings for user {user_id}: {sync_results}")
                return sync_results
                
        except Exception as e:
            logger.error(f"Error syncing holdings for user {user_id}: {str(e)}")
            raise

    async def get_user_holdings(
        self,
        user_id: str,
        item_id: Optional[str] = None,
        account_ids: Optional[List[str]] = None
    ) -> InvestmentHoldingsResponse:
        """
        Get investment holdings for a user from database.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Optional Plaid item ID filter
            account_ids: Optional account IDs filter
            
        Returns:
            Formatted holdings response
        """
        try:
            with get_db() as session:
                # Build account query
                account_query = select(PlaidInvestmentAccount).where(
                    PlaidInvestmentAccount.user_id == user_id,
                    PlaidInvestmentAccount.status == "active"
                )
                
                if item_id:
                    account_query = account_query.where(PlaidInvestmentAccount.item_id == item_id)
                
                if account_ids:
                    account_query = account_query.where(PlaidInvestmentAccount.plaid_account_id.in_(account_ids))
                
                accounts = session.exec(account_query).all()
                
                # Get holdings for these accounts
                account_plaid_ids = [acc.plaid_account_id for acc in accounts]
                
                if not account_plaid_ids:
                    return InvestmentHoldingsResponse()
                
                holdings_query = select(PlaidInvestmentHolding).where(
                    PlaidInvestmentHolding.user_id == user_id,
                    PlaidInvestmentHolding.account_id.in_(account_plaid_ids),
                    PlaidInvestmentHolding.status == "active"
                )
                
                holdings = session.exec(holdings_query).all()
                
                # Get securities for these holdings
                security_ids = list(set([holding.security_id for holding in holdings]))
                
                securities_query = select(PlaidInvestmentSecurity).where(
                    PlaidInvestmentSecurity.security_id.in_(security_ids)
                )
                
                securities = session.exec(securities_query).all()
                
                # Format response
                account_responses = []
                for account in accounts:
                    account_responses.append(await self._format_investment_account(account))
                
                holding_responses = []
                for holding in holdings:
                    holding_responses.append(await self._format_holding(holding))
                
                security_responses = []
                for security in securities:
                    security_responses.append(await self._format_security(session, security))
                
                return InvestmentHoldingsResponse(
                    accounts=account_responses,
                    holdings=holding_responses,
                    securities=security_responses
                )
                
        except Exception as e:
            logger.error(f"Error getting holdings for user {user_id}: {str(e)}")
            raise

    # ==========================================
    # Transactions Management
    # ==========================================

    async def fetch_transactions_from_plaid(
        self,
        user_id: str,
        item_id: str,
        start_date: str,
        end_date: str,
        account_ids: Optional[List[str]] = None,
        count: int = 100,
        offset: int = 0,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Fetch investment transactions from Plaid API.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Plaid item ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            account_ids: Optional account IDs filter
            count: Number of transactions to fetch
            offset: Number of transactions to skip
            environment: Plaid environment
            
        Returns:
            Raw transaction data from Plaid API
        """
        try:
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
                "access_token": access_token,
                "start_date": start_date,
                "end_date": end_date,
                "options": {
                    "count": count,
                    "offset": offset
                }
            }
            
            if account_ids:
                request_data["options"]["account_ids"] = account_ids

            # Call Plaid API
            response = self.plaid_service.client.investments_transactions_get(request_data)
            
            if not response:
                logger.warning(f"Empty response from Plaid transactions API for item {item_id}")
                return {}
                
            logger.info(f"Successfully fetched investment transactions for item {item_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching investment transactions from Plaid for item {item_id}: {str(e)}")
            raise

    async def sync_transactions_data(
        self,
        user_id: str,
        item_id: str,
        start_date: str,
        end_date: str,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """
        Sync investment transactions from Plaid API to database.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Plaid item ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            environment: Plaid environment
            
        Returns:
            Sync results with counts and any errors
        """
        try:
            all_transactions = []
            all_securities = []
            offset = 0
            count = 500  # Max allowed by Plaid
            
            # Fetch all transactions in pages
            while True:
                plaid_data = await self.fetch_transactions_from_plaid(
                    user_id, item_id, start_date, end_date, 
                    count=count, offset=offset, environment=environment
                )
                
                if not plaid_data:
                    break
                
                transactions = plaid_data.get("investment_transactions", [])
                securities = plaid_data.get("securities", [])
                total_count = plaid_data.get("total_investment_transactions", 0)
                
                all_transactions.extend(transactions)
                all_securities.extend(securities)
                
                # Check if we've fetched all transactions
                if len(transactions) < count or len(all_transactions) >= total_count:
                    break
                    
                offset += count

            with get_db() as session:
                sync_results = {
                    "success": True,
                    "message": "Investment transactions synced successfully",
                    "transactions_synced": 0,
                    "securities_synced": 0,
                    "errors": []
                }
                
                # Process securities first (transactions reference them)
                unique_securities = {sec["security_id"]: sec for sec in all_securities}.values()
                for security_data in unique_securities:
                    try:
                        await self._upsert_security(session, security_data, environment)
                        sync_results["securities_synced"] += 1
                    except Exception as e:
                        error_msg = f"Error processing security {security_data.get('security_id', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        sync_results["errors"].append(error_msg)
                
                # Process transactions
                for transaction_data in all_transactions:
                    try:
                        await self._upsert_transaction(session, user_id, transaction_data, environment)
                        sync_results["transactions_synced"] += 1
                    except Exception as e:
                        error_msg = f"Error processing transaction {transaction_data.get('investment_transaction_id', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        sync_results["errors"].append(error_msg)
                
                # Commit all changes
                session.commit()
                
                logger.info(f"Successfully synced investment transactions for user {user_id}: {sync_results}")
                return sync_results
                
        except Exception as e:
            logger.error(f"Error syncing investment transactions for user {user_id}: {str(e)}")
            raise

    async def get_user_transactions(
        self,
        user_id: str,
        item_id: Optional[str] = None,
        account_ids: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_types: Optional[List[str]] = None,
        count: int = 100,
        offset: int = 0
    ) -> InvestmentTransactionsResponse:
        """
        Get investment transactions for a user from database.
        
        Args:
            user_id: TruLedgr user ID
            item_id: Optional Plaid item ID filter
            account_ids: Optional account IDs filter
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            transaction_types: Optional transaction types filter
            count: Number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            Formatted transactions response
        """
        try:
            with get_db() as session:
                # Build transactions query
                transactions_query = select(PlaidInvestmentTransaction).where(
                    PlaidInvestmentTransaction.user_id == user_id,
                    PlaidInvestmentTransaction.status == "posted"
                )
                
                if account_ids:
                    transactions_query = transactions_query.where(
                        PlaidInvestmentTransaction.account_id.in_(account_ids)
                    )
                
                if start_date:
                    transactions_query = transactions_query.where(
                        PlaidInvestmentTransaction.transaction_date >= start_date
                    )
                
                if end_date:
                    transactions_query = transactions_query.where(
                        PlaidInvestmentTransaction.transaction_date <= end_date
                    )
                
                if transaction_types:
                    transactions_query = transactions_query.where(
                        PlaidInvestmentTransaction.transaction_type.in_(transaction_types)
                    )
                
                # Order by date descending and apply pagination
                transactions_query = transactions_query.order_by(
                    PlaidInvestmentTransaction.transaction_date.desc()
                ).offset(offset).limit(count)
                
                transactions = session.exec(transactions_query).all()
                
                # Get total count for pagination
                count_query = select(PlaidInvestmentTransaction).where(
                    PlaidInvestmentTransaction.user_id == user_id,
                    PlaidInvestmentTransaction.status == "posted"
                )
                
                if account_ids:
                    count_query = count_query.where(
                        PlaidInvestmentTransaction.account_id.in_(account_ids)
                    )
                
                total_count = len(session.exec(count_query).all())
                
                # Get accounts and securities
                account_ids_set = set([txn.account_id for txn in transactions])
                security_ids_set = set([txn.security_id for txn in transactions if txn.security_id])
                
                accounts = []
                if account_ids_set:
                    accounts_query = select(PlaidInvestmentAccount).where(
                        PlaidInvestmentAccount.plaid_account_id.in_(account_ids_set)
                    )
                    accounts = session.exec(accounts_query).all()
                
                securities = []
                if security_ids_set:
                    securities_query = select(PlaidInvestmentSecurity).where(
                        PlaidInvestmentSecurity.security_id.in_(security_ids_set)
                    )
                    securities = session.exec(securities_query).all()
                
                # Format response
                account_responses = [await self._format_investment_account(acc) for acc in accounts]
                transaction_responses = [await self._format_transaction(txn) for txn in transactions]
                security_responses = [await self._format_security(session, sec) for sec in securities]
                
                return InvestmentTransactionsResponse(
                    accounts=account_responses,
                    investment_transactions=transaction_responses,
                    securities=security_responses,
                    total_investment_transactions=total_count
                )
                
        except Exception as e:
            logger.error(f"Error getting investment transactions for user {user_id}: {str(e)}")
            raise

    # ==========================================
    # Webhook Processing
    # ==========================================

    async def process_webhook_event(
        self,
        webhook_type: str,
        webhook_code: str,
        item_id: str,
        webhook_data: Dict[str, Any],
        environment: str = "sandbox"
    ) -> bool:
        """
        Process investment webhook events.
        
        Args:
            webhook_type: HOLDINGS or INVESTMENTS_TRANSACTIONS
            webhook_code: DEFAULT_UPDATE or HISTORICAL_UPDATE
            item_id: Plaid item ID
            webhook_data: Webhook payload data
            environment: Plaid environment
            
        Returns:
            True if processed successfully
        """
        try:
            # Store webhook event
            with get_db() as session:
                webhook_event = PlaidInvestmentWebhookEvent(
                    id=generate_id(),
                    item_id=item_id,
                    webhook_type=webhook_type,
                    webhook_code=webhook_code,
                    webhook_payload=json.dumps(webhook_data),
                    environment=environment
                )
                
                # Extract webhook-specific data
                if webhook_type == "HOLDINGS":
                    webhook_event.new_holdings = webhook_data.get("new_holdings")
                    webhook_event.updated_holdings = webhook_data.get("updated_holdings")
                elif webhook_type == "INVESTMENTS_TRANSACTIONS":
                    webhook_event.new_investments_transactions = webhook_data.get("new_investments_transactions")
                    webhook_event.canceled_investments_transactions = webhook_data.get("canceled_investments_transactions")
                
                session.add(webhook_event)
                session.commit()
                
                # Process the webhook based on type and code
                if webhook_type == "HOLDINGS" and webhook_code == "DEFAULT_UPDATE":
                    await self._handle_holdings_update_webhook(webhook_data)
                elif webhook_type == "INVESTMENTS_TRANSACTIONS":
                    await self._handle_transactions_update_webhook(webhook_data)
                
                # Mark as processed
                webhook_event.processed = True
                webhook_event.processed_at = datetime.utcnow()
                session.add(webhook_event)
                session.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing investment webhook: {str(e)}")
            return False

    # ==========================================
    # Private Helper Methods
    # ==========================================

    async def _upsert_investment_account(
        self,
        session: Session,
        user_id: str,
        item_id: str,
        account_data: Dict[str, Any],
        environment: str
    ) -> PlaidInvestmentAccount:
        """Upsert investment account record"""
        
        account_id = account_data.get("account_id")
        if not account_id:
            raise ValueError("Account ID is required")
        
        # Check if account already exists
        existing = session.exec(
            select(PlaidInvestmentAccount).where(
                PlaidInvestmentAccount.plaid_account_id == account_id,
                PlaidInvestmentAccount.user_id == user_id
            )
        ).first()
        
        balances = account_data.get("balances", {})
        
        if existing:
            # Update existing record
            existing.account_name = account_data.get("name", "")
            existing.account_official_name = account_data.get("official_name")
            existing.account_mask = account_data.get("mask")
            existing.account_type = account_data.get("type", "")
            existing.account_subtype = account_data.get("subtype", "")
            existing.available_balance = balances.get("available")
            existing.current_balance = balances.get("current")
            existing.limit_amount = balances.get("limit")
            existing.iso_currency_code = balances.get("iso_currency_code")
            existing.unofficial_currency_code = balances.get("unofficial_currency_code")
            existing.last_updated_datetime = balances.get("last_updated_datetime")
            existing.verification_status = account_data.get("verification_status")
            existing.verification_name = account_data.get("verification_name")
            existing.persistent_account_id = account_data.get("persistent_account_id")
            existing.holder_category = account_data.get("holder_category")
            existing.last_synced = datetime.utcnow()
            session.add(existing)
            return existing
        else:
            # Create new record
            new_account = PlaidInvestmentAccount(
                id=generate_id(),
                user_id=user_id,
                item_id=item_id,
                account_id=account_id,
                plaid_account_id=account_id,
                account_name=account_data.get("name", ""),
                account_official_name=account_data.get("official_name"),
                account_mask=account_data.get("mask"),
                account_type=account_data.get("type", ""),
                account_subtype=account_data.get("subtype", ""),
                available_balance=balances.get("available"),
                current_balance=balances.get("current"),
                limit_amount=balances.get("limit"),
                iso_currency_code=balances.get("iso_currency_code"),
                unofficial_currency_code=balances.get("unofficial_currency_code"),
                last_updated_datetime=balances.get("last_updated_datetime"),
                verification_status=account_data.get("verification_status"),
                verification_name=account_data.get("verification_name"),
                persistent_account_id=account_data.get("persistent_account_id"),
                holder_category=account_data.get("holder_category"),
                environment=environment
            )
            session.add(new_account)
            session.flush()  # Ensure ID is generated
            return new_account

    async def _upsert_security(
        self,
        session: Session,
        security_data: Dict[str, Any],
        environment: str
    ) -> PlaidInvestmentSecurity:
        """Upsert security record"""
        
        security_id = security_data.get("security_id")
        if not security_id:
            raise ValueError("Security ID is required")
        
        # Check if security already exists
        existing = session.exec(
            select(PlaidInvestmentSecurity).where(
                PlaidInvestmentSecurity.security_id == security_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.isin = security_data.get("isin")
            existing.cusip = security_data.get("cusip")
            existing.sedol = security_data.get("sedol")
            existing.institution_security_id = security_data.get("institution_security_id")
            existing.institution_id = security_data.get("institution_id")
            existing.proxy_security_id = security_data.get("proxy_security_id")
            existing.name = security_data.get("name")
            existing.ticker_symbol = security_data.get("ticker_symbol")
            existing.is_cash_equivalent = security_data.get("is_cash_equivalent")
            existing.security_type = security_data.get("type")
            existing.close_price = security_data.get("close_price")
            existing.close_price_as_of = security_data.get("close_price_as_of")
            existing.update_datetime = security_data.get("update_datetime")
            existing.iso_currency_code = security_data.get("iso_currency_code")
            existing.unofficial_currency_code = security_data.get("unofficial_currency_code")
            existing.market_identifier_code = security_data.get("market_identifier_code")
            existing.sector = security_data.get("sector")
            existing.industry = security_data.get("industry")
            session.add(existing)
            
            # Update option contract details if present
            option_contract = security_data.get("option_contract")
            if option_contract:
                await self._upsert_option_contract(session, security_id, option_contract)
            
            # Update fixed income details if present
            fixed_income = security_data.get("fixed_income")
            if fixed_income:
                await self._upsert_fixed_income(session, security_id, fixed_income)
            
            return existing
        else:
            # Create new record
            new_security = PlaidInvestmentSecurity(
                id=generate_id(),
                security_id=security_id,
                isin=security_data.get("isin"),
                cusip=security_data.get("cusip"),
                sedol=security_data.get("sedol"),
                institution_security_id=security_data.get("institution_security_id"),
                institution_id=security_data.get("institution_id"),
                proxy_security_id=security_data.get("proxy_security_id"),
                name=security_data.get("name"),
                ticker_symbol=security_data.get("ticker_symbol"),
                is_cash_equivalent=security_data.get("is_cash_equivalent"),
                security_type=security_data.get("type"),
                close_price=security_data.get("close_price"),
                close_price_as_of=security_data.get("close_price_as_of"),
                update_datetime=security_data.get("update_datetime"),
                iso_currency_code=security_data.get("iso_currency_code"),
                unofficial_currency_code=security_data.get("unofficial_currency_code"),
                market_identifier_code=security_data.get("market_identifier_code"),
                sector=security_data.get("sector"),
                industry=security_data.get("industry"),
                environment=environment
            )
            session.add(new_security)
            session.flush()
            
            # Add option contract details if present
            option_contract = security_data.get("option_contract")
            if option_contract:
                await self._upsert_option_contract(session, security_id, option_contract)
            
            # Add fixed income details if present
            fixed_income = security_data.get("fixed_income")
            if fixed_income:
                await self._upsert_fixed_income(session, security_id, fixed_income)
            
            return new_security

    async def _upsert_option_contract(
        self,
        session: Session,
        security_id: str,
        option_data: Dict[str, Any]
    ) -> None:
        """Upsert option contract details"""
        
        # Check if option contract already exists
        existing = session.exec(
            select(PlaidInvestmentOptionContract).where(
                PlaidInvestmentOptionContract.security_id == security_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.contract_type = option_data.get("contract_type", "")
            existing.expiration_date = option_data.get("expiration_date")
            existing.strike_price = option_data.get("strike_price", 0.0)
            existing.underlying_security_ticker = option_data.get("underlying_security_ticker", "")
            session.add(existing)
        else:
            # Create new record
            new_option = PlaidInvestmentOptionContract(
                id=generate_id(),
                security_id=security_id,
                contract_type=option_data.get("contract_type", ""),
                expiration_date=option_data.get("expiration_date"),
                strike_price=option_data.get("strike_price", 0.0),
                underlying_security_ticker=option_data.get("underlying_security_ticker", "")
            )
            session.add(new_option)

    async def _upsert_fixed_income(
        self,
        session: Session,
        security_id: str,
        fixed_income_data: Dict[str, Any]
    ) -> None:
        """Upsert fixed income details"""
        
        # Check if fixed income record already exists
        existing = session.exec(
            select(PlaidInvestmentFixedIncome).where(
                PlaidInvestmentFixedIncome.security_id == security_id
            )
        ).first()
        
        yield_rate = fixed_income_data.get("yield_rate", {})
        
        if existing:
            # Update existing record
            existing.yield_rate_percentage = yield_rate.get("percentage")
            existing.yield_rate_type = yield_rate.get("type")
            existing.maturity_date = fixed_income_data.get("maturity_date")
            existing.issue_date = fixed_income_data.get("issue_date")
            existing.face_value = fixed_income_data.get("face_value")
            session.add(existing)
        else:
            # Create new record
            new_fixed_income = PlaidInvestmentFixedIncome(
                id=generate_id(),
                security_id=security_id,
                yield_rate_percentage=yield_rate.get("percentage"),
                yield_rate_type=yield_rate.get("type"),
                maturity_date=fixed_income_data.get("maturity_date"),
                issue_date=fixed_income_data.get("issue_date"),
                face_value=fixed_income_data.get("face_value")
            )
            session.add(new_fixed_income)

    async def _upsert_holding(
        self,
        session: Session,
        user_id: str,
        holding_data: Dict[str, Any],
        environment: str
    ) -> PlaidInvestmentHolding:
        """Upsert holding record"""
        
        account_id = holding_data.get("account_id")
        security_id = holding_data.get("security_id")
        
        if not account_id or not security_id:
            raise ValueError("Account ID and Security ID are required")
        
        # Check if holding already exists
        existing = session.exec(
            select(PlaidInvestmentHolding).where(
                PlaidInvestmentHolding.account_id == account_id,
                PlaidInvestmentHolding.security_id == security_id,
                PlaidInvestmentHolding.user_id == user_id
            )
        ).first()
        
        if existing:
            # Update existing record
            existing.institution_price = holding_data.get("institution_price", 0.0)
            existing.institution_price_as_of = holding_data.get("institution_price_as_of")
            existing.institution_price_datetime = holding_data.get("institution_price_datetime")
            existing.institution_value = holding_data.get("institution_value", 0.0)
            existing.quantity = holding_data.get("quantity", 0.0)
            existing.cost_basis = holding_data.get("cost_basis")
            existing.iso_currency_code = holding_data.get("iso_currency_code")
            existing.unofficial_currency_code = holding_data.get("unofficial_currency_code")
            existing.vested_quantity = holding_data.get("vested_quantity")
            existing.vested_value = holding_data.get("vested_value")
            existing.last_updated = datetime.utcnow()
            session.add(existing)
            return existing
        else:
            # Create new record
            new_holding = PlaidInvestmentHolding(
                id=generate_id(),
                user_id=user_id,
                account_id=account_id,
                security_id=security_id,
                institution_price=holding_data.get("institution_price", 0.0),
                institution_price_as_of=holding_data.get("institution_price_as_of"),
                institution_price_datetime=holding_data.get("institution_price_datetime"),
                institution_value=holding_data.get("institution_value", 0.0),
                quantity=holding_data.get("quantity", 0.0),
                cost_basis=holding_data.get("cost_basis"),
                iso_currency_code=holding_data.get("iso_currency_code"),
                unofficial_currency_code=holding_data.get("unofficial_currency_code"),
                vested_quantity=holding_data.get("vested_quantity"),
                vested_value=holding_data.get("vested_value"),
                environment=environment
            )
            session.add(new_holding)
            session.flush()
            return new_holding

    async def _upsert_transaction(
        self,
        session: Session,
        user_id: str,
        transaction_data: Dict[str, Any],
        environment: str
    ) -> PlaidInvestmentTransaction:
        """Upsert transaction record"""
        
        investment_transaction_id = transaction_data.get("investment_transaction_id")
        if not investment_transaction_id:
            raise ValueError("Investment transaction ID is required")
        
        # Check if transaction already exists
        existing = session.exec(
            select(PlaidInvestmentTransaction).where(
                PlaidInvestmentTransaction.investment_transaction_id == investment_transaction_id,
                PlaidInvestmentTransaction.user_id == user_id
            )
        ).first()
        
        if existing:
            # Update existing record (transactions usually don't change, but update timestamp)
            existing.last_updated = datetime.utcnow()
            session.add(existing)
            return existing
        else:
            # Create new record
            new_transaction = PlaidInvestmentTransaction(
                id=generate_id(),
                user_id=user_id,
                investment_transaction_id=investment_transaction_id,
                account_id=transaction_data.get("account_id", ""),
                security_id=transaction_data.get("security_id"),
                transaction_date=transaction_data.get("date"),
                transaction_name=transaction_data.get("name", ""),
                transaction_type=transaction_data.get("type", ""),
                transaction_subtype=transaction_data.get("subtype", ""),
                amount=transaction_data.get("amount", 0.0),
                quantity=transaction_data.get("quantity", 0.0),
                price=transaction_data.get("price", 0.0),
                fees=transaction_data.get("fees"),
                iso_currency_code=transaction_data.get("iso_currency_code"),
                unofficial_currency_code=transaction_data.get("unofficial_currency_code"),
                cancel_transaction_id=transaction_data.get("cancel_transaction_id"),
                environment=environment
            )
            session.add(new_transaction)
            session.flush()
            return new_transaction

    async def _format_investment_account(self, account: PlaidInvestmentAccount) -> InvestmentAccountResponse:
        """Format investment account for API response"""
        return InvestmentAccountResponse(
            account_id=account.plaid_account_id,
            balances={
                "available": account.available_balance,
                "current": account.current_balance,
                "limit": account.limit_amount,
                "iso_currency_code": account.iso_currency_code,
                "unofficial_currency_code": account.unofficial_currency_code,
                "last_updated_datetime": account.last_updated_datetime.isoformat() if account.last_updated_datetime else None
            },
            mask=account.account_mask,
            name=account.account_name,
            official_name=account.account_official_name,
            type=account.account_type,
            subtype=account.account_subtype,
            verification_status=account.verification_status,
            persistent_account_id=account.persistent_account_id,
            holder_category=account.holder_category
        )

    async def _format_holding(self, holding: PlaidInvestmentHolding) -> InvestmentHoldingResponse:
        """Format holding for API response"""
        return InvestmentHoldingResponse(
            account_id=holding.account_id,
            security_id=holding.security_id,
            institution_price=holding.institution_price,
            institution_price_as_of=holding.institution_price_as_of.isoformat() if holding.institution_price_as_of else None,
            institution_price_datetime=holding.institution_price_datetime.isoformat() if holding.institution_price_datetime else None,
            institution_value=holding.institution_value,
            cost_basis=holding.cost_basis,
            quantity=holding.quantity,
            iso_currency_code=holding.iso_currency_code,
            unofficial_currency_code=holding.unofficial_currency_code,
            vested_quantity=holding.vested_quantity,
            vested_value=holding.vested_value
        )

    async def _format_security(self, session: Session, security: PlaidInvestmentSecurity) -> InvestmentSecurityResponse:
        """Format security for API response"""
        
        # Get option contract details if available
        option_contract = None
        option_record = session.exec(
            select(PlaidInvestmentOptionContract).where(
                PlaidInvestmentOptionContract.security_id == security.security_id
            )
        ).first()
        
        if option_record:
            option_contract = {
                "contract_type": option_record.contract_type,
                "expiration_date": option_record.expiration_date.isoformat() if option_record.expiration_date else None,
                "strike_price": option_record.strike_price,
                "underlying_security_ticker": option_record.underlying_security_ticker
            }
        
        # Get fixed income details if available
        fixed_income = None
        fixed_income_record = session.exec(
            select(PlaidInvestmentFixedIncome).where(
                PlaidInvestmentFixedIncome.security_id == security.security_id
            )
        ).first()
        
        if fixed_income_record:
            fixed_income = {
                "yield_rate": {
                    "percentage": fixed_income_record.yield_rate_percentage,
                    "type": fixed_income_record.yield_rate_type
                } if fixed_income_record.yield_rate_percentage else None,
                "maturity_date": fixed_income_record.maturity_date.isoformat() if fixed_income_record.maturity_date else None,
                "issue_date": fixed_income_record.issue_date.isoformat() if fixed_income_record.issue_date else None,
                "face_value": fixed_income_record.face_value
            }
        
        return InvestmentSecurityResponse(
            security_id=security.security_id,
            isin=security.isin,
            cusip=security.cusip,
            sedol=security.sedol,
            institution_security_id=security.institution_security_id,
            institution_id=security.institution_id,
            proxy_security_id=security.proxy_security_id,
            name=security.name,
            ticker_symbol=security.ticker_symbol,
            is_cash_equivalent=security.is_cash_equivalent,
            type=security.security_type,
            close_price=security.close_price,
            close_price_as_of=security.close_price_as_of.isoformat() if security.close_price_as_of else None,
            update_datetime=security.update_datetime.isoformat() if security.update_datetime else None,
            iso_currency_code=security.iso_currency_code,
            unofficial_currency_code=security.unofficial_currency_code,
            market_identifier_code=security.market_identifier_code,
            sector=security.sector,
            industry=security.industry,
            option_contract=option_contract,
            fixed_income=fixed_income
        )

    async def _format_transaction(self, transaction: PlaidInvestmentTransaction) -> InvestmentTransactionResponse:
        """Format transaction for API response"""
        return InvestmentTransactionResponse(
            investment_transaction_id=transaction.investment_transaction_id,
            account_id=transaction.account_id,
            security_id=transaction.security_id,
            date=transaction.transaction_date.isoformat() if transaction.transaction_date else "",
            name=transaction.transaction_name,
            quantity=transaction.quantity,
            amount=transaction.amount,
            price=transaction.price,
            fees=transaction.fees,
            type=transaction.transaction_type,
            subtype=transaction.transaction_subtype,
            iso_currency_code=transaction.iso_currency_code,
            unofficial_currency_code=transaction.unofficial_currency_code,
            cancel_transaction_id=transaction.cancel_transaction_id
        )

    async def _handle_holdings_update_webhook(self, webhook_data: Dict[str, Any]) -> None:
        """Handle holdings update webhook"""
        # This would trigger a re-sync of holdings data
        logger.info("Handling holdings update webhook")

    async def _handle_transactions_update_webhook(self, webhook_data: Dict[str, Any]) -> None:
        """Handle transactions update webhook"""
        # This would trigger a re-sync of transaction data
        logger.info("Handling transactions update webhook")


# Global service instance
def get_investments_service() -> InvestmentsService:
    """Get or create investments service instance"""
    from ..service import get_plaid_service
    plaid_service = get_plaid_service()
    return InvestmentsService(plaid_service)
