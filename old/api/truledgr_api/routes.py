from fastapi import APIRouter

from .accounts import accounts_router
from .amazon import amazon_router
from .apple import apple_router
from .audits import audits_router
from .budgets import budgets_router
from .categories import categories_router
from .documents import documents_router
from .entries import entries_router
from .finicity import finicity_router
from .goals import goals_router
from .institutions import institutions_router
from .journals import journals_router
from .ledgers import ledgers_router
from .mx import mx_router
from .payees import payees_router
from .period import period_router
from .plaid import plaid_router
from .stripe import stripe_router
from .tags import tags_router
from .teams import teams_router
from .transactions import transactions_router
from .users import users_router
from .walmart import walmart_router

api_router = APIRouter()

api_router.include_router(accounts_router)
api_router.include_router(amazon_router)
api_router.include_router(apple_router)
api_router.include_router(audits_router)
api_router.include_router(budgets_router)
api_router.include_router(categories_router)
api_router.include_router(documents_router)
api_router.include_router(entries_router)
api_router.include_router(finicity_router)
api_router.include_router(goals_router)
api_router.include_router(institutions_router)
api_router.include_router(journals_router)
api_router.include_router(ledgers_router)
api_router.include_router(mx_router)
api_router.include_router(payees_router)
api_router.include_router(period_router)
api_router.include_router(plaid_router)
api_router.include_router(stripe_router)
api_router.include_router(tags_router)
api_router.include_router(teams_router)
api_router.include_router(transactions_router)
api_router.include_router(users_router)
api_router.include_router(walmart_router)
