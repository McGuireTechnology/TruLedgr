"""
TOTP Service - Basic Implementation

This module provides TOTP (Time-based One-Time Password) functionality for 2FA.
This is a basic implementation that can be enhanced with external libraries.
"""

import secrets
import hashlib
import hmac
import struct
import time
import base64
from typing import Optional, Dict, Any, List
from sqlmodel.ext.asyncio.session import AsyncSession

from api.users.models import User
from api.settings import get_settings

settings = get_settings()


class TOTPService:
    """
    Service for TOTP/2FA operations.
    
    Provides TOTP functionality including:
    - Secret generation and setup
    - Code verification
    - Backup code management
    """
    
    def __init__(self):
        self.issuer_name = getattr(settings, 'totp_issuer_name', 'FastAPI Security')
        self.backup_codes_count = 10
        self.totp_digits = 6
        self.totp_window = 30  # seconds
        self.totp_tolerance = 1  # allow 1 window before/after
    
    async def setup_totp(
        self,
        session: AsyncSession,
        user: User
    ) -> Dict[str, Any]:
        """
        Setup TOTP for user.
        
        Args:
            session: Database session
            user: User setting up TOTP
            
        Returns:
            Dictionary with TOTP setup data
        """
        if user.totp_enabled:
            return {
                "error": "totp_already_enabled",
                "message": "TOTP is already enabled for this user"
            }
        
        # Generate TOTP secret
        secret = self._generate_secret()
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes()
        
        # Store secret temporarily (not enabled yet)
        user.totp_secret = secret
        user.backup_codes = ','.join(backup_codes)
        
        await session.commit()
        await session.refresh(user)
        
        return {
            "secret": secret,
            "secret_base32": base64.b32encode(secret.encode()).decode(),
            "backup_codes": backup_codes,
            "qr_setup_url": self._generate_setup_url(user, secret)
        }
    
    async def verify_and_enable_totp(
        self,
        session: AsyncSession,
        user: User,
        totp_code: str
    ) -> Dict[str, Any]:
        """
        Verify TOTP code and enable TOTP for user.
        
        Args:
            session: Database session
            user: User enabling TOTP
            totp_code: TOTP verification code
            
        Returns:
            Dictionary with verification results
        """
        if user.totp_enabled:
            return {
                "error": "totp_already_enabled",
                "message": "TOTP is already enabled for this user"
            }
        
        if not user.totp_secret:
            return {
                "error": "totp_setup_required",
                "message": "TOTP setup required first"
            }
        
        # Verify TOTP code
        if not self._verify_totp_code(user.totp_secret, totp_code):
            return {
                "error": "invalid_totp_code",
                "message": "Invalid TOTP code"
            }
        
        # Enable TOTP
        user.totp_enabled = True
        await session.commit()
        await session.refresh(user)
        
        return {
            "success": True,
            "message": "TOTP enabled successfully"
        }
    
    async def disable_totp(
        self,
        session: AsyncSession,
        user: User,
        totp_code: str
    ) -> Dict[str, Any]:
        """
        Disable TOTP for user after verification.
        
        Args:
            session: Database session
            user: User disabling TOTP
            totp_code: TOTP verification code
            
        Returns:
            Dictionary with disable results
        """
        if not user.totp_enabled:
            return {
                "error": "totp_not_enabled",
                "message": "TOTP is not enabled for this user"
            }
        
        if not user.totp_secret:
            return {
                "error": "totp_secret_missing",
                "message": "TOTP secret not found"
            }
        
        # Verify TOTP code
        if not self._verify_totp_code(user.totp_secret, totp_code):
            return {
                "error": "invalid_totp_code",
                "message": "Invalid TOTP code"
            }
        
        # Disable TOTP
        user.totp_enabled = False
        user.totp_secret = None
        user.backup_codes = None
        
        await session.commit()
        await session.refresh(user)
        
        return {
            "success": True,
            "message": "TOTP disabled successfully"
        }
    
    async def verify_totp_code(
        self,
        session: AsyncSession,
        user_id: str,
        totp_code: str
    ) -> bool:
        """
        Verify TOTP code for user authentication.
        
        Args:
            session: Database session
            user_id: User ID
            totp_code: TOTP code to verify
            
        Returns:
            True if code is valid, False otherwise
        """
        # Get user
        user = await session.get(User, user_id)
        if not user or not user.totp_enabled or not user.totp_secret:
            return False
        
        # Try TOTP code first
        if self._verify_totp_code(user.totp_secret, totp_code):
            return True
        
        # Try backup codes
        if user.backup_codes:
            backup_codes = user.backup_codes.split(',')
            if totp_code in backup_codes:
                # Remove used backup code
                backup_codes.remove(totp_code)
                user.backup_codes = ','.join(backup_codes)
                await session.commit()
                return True
        
        return False
    
    def _generate_secret(self) -> str:
        """
        Generate a TOTP secret.
        
        Returns:
            Base32 encoded secret
        """
        # Generate 20 random bytes (160 bits) for the secret
        random_bytes = secrets.token_bytes(20)
        return base64.b32encode(random_bytes).decode().rstrip('=')
    
    def _generate_setup_url(self, user: User, secret: str) -> str:
        """
        Generate setup URL for QR code.
        
        Args:
            user: User setting up TOTP
            secret: TOTP secret
            
        Returns:
            otpauth:// URL for QR code
        """
        account_name = user.email or user.username
        issuer = self.issuer_name
        
        url = (
            f"otpauth://totp/{issuer}:{account_name}"
            f"?secret={secret}"
            f"&issuer={issuer}"
            f"&digits={self.totp_digits}"
            f"&period={self.totp_window}"
        )
        
        return url
    
    def _verify_totp_code(self, secret: str, code: str) -> bool:
        """
        Verify TOTP code against secret.
        
        Args:
            secret: TOTP secret
            code: TOTP code to verify
            
        Returns:
            True if code is valid, False otherwise
        """
        try:
            # Convert code to integer
            code_int = int(code)
            if len(code) != self.totp_digits:
                return False
        except ValueError:
            return False
        
        # Get current time window
        current_time = int(time.time()) // self.totp_window
        
        # Check current window and tolerance windows
        for time_offset in range(-self.totp_tolerance, self.totp_tolerance + 1):
            window_time = current_time + time_offset
            expected_code = self._generate_totp_code(secret, window_time)
            
            if expected_code == code_int:
                return True
        
        return False
    
    def _generate_totp_code(self, secret: str, time_window: int) -> int:
        """
        Generate TOTP code for given secret and time window.
        
        Args:
            secret: TOTP secret
            time_window: Time window
            
        Returns:
            TOTP code as integer
        """
        # Decode secret from base32
        try:
            key = base64.b32decode(secret + '=' * (8 - len(secret) % 8))
        except Exception:
            return 0
        
        # Convert time window to bytes
        time_bytes = struct.pack('>Q', time_window)
        
        # Generate HMAC-SHA1
        hmac_digest = hmac.new(key, time_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_digest[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_digest[offset:offset + 4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate final code
        code = truncated % (10 ** self.totp_digits)
        
        return code
    
    def _generate_backup_codes(self) -> List[str]:
        """
        Generate backup recovery codes.
        
        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(self.backup_codes_count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()
            codes.append(code)
        
        return codes
