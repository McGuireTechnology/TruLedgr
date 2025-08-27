"""
TOTP (Time-based One-Time Password) Submodule

This module handles TOTP/2FA authentication including:
- TOTP secret generation and setup
- TOTP code verification
- Backup code management
- QR code generation for authenticator apps
"""

from .service import TOTPService
from .router import router

__all__ = [
    "TOTPService",
    "router"
]
