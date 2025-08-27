"""
TruLedgr - Personal Finance Application

A modern, secure personal finance application built with FastAPI and Vue.js.
"""

__version__ = "0.1.0"
__author__ = "McGuire Technology"
__email__ = "developer@mcguire.technology"

# Main application components
from api.main import app

__all__ = ["app", "__version__"]