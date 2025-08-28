"""
Plaid Items Module

Handles Item management and status operations.
An Item represents a user's connection to a financial institution.
"""

from .models import *
from .service import ItemsService
from .router import router
