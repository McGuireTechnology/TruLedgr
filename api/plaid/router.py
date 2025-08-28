"""
Plaid API routes for TruLedgr - Database Integration
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta

from api.authentication.deps import get_current_user
from api.users.models import User
from .items.models import PlaidEnvironment
from .accounts.models import PlaidAccountResponse
from .transactions.models import PlaidTransactionResponse
from .service import PlaidService, get_plaid_service

# Import sub-module routers
from .institutions.router import router as institutions_router
from .items.router import router as items_router
from .link.router import router as link_router
from .accounts.router import router as accounts_router
from .transactions.router import router as transactions_router
from .liabilities.router import router as liabilities_router
from .investments.router_official import router as investments_router

router = APIRouter(prefix="/plaid")

# Include sub-module routers
router.include_router(accounts_router)
router.include_router(link_router)
router.include_router(institutions_router)
router.include_router(items_router)
router.include_router(transactions_router)
router.include_router(liabilities_router)
router.include_router(investments_router)
