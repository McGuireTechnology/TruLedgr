"""
Plaid Accounts Module

Handles Account information retrieval and balance operations.
Accounts represent individual financial accounts within an Item.
"""

from .models import *
from .service import AccountsService
from .router import router
