"""
Plaid Link Module

Handles Link token creation and public token exchange for connecting financial accounts.
"""

from .models import *
from .service import LinkService
from .router import router
