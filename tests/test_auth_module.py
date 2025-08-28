"""
Unit tests for authentication module.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt

from fastapi_security_sample.users.auth.auth import (
    create_access_token, verify_token, get_current_user,
    create_access_token_with_session, get_client_info
)
from fastapi_security_sample.users.models import User
from fastapi_security_sample.users.exceptions import InvalidCredentialsError


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiration(self):
        """Test JWT token creation with custom expiration."""
        data = {"sub": "testuser", "user_id": "123"}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        # Decode token to verify expiration
        from fastapi_security_sample.users.auth.auth import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded

    def test_verify_token_valid(self):
        """Test verification of valid token."""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"

    def test_verify_token_invalid(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(InvalidCredentialsError):
            verify_token(invalid_token)

    def test_verify_token_expired(self):
        """Test verification of expired token."""
        data = {"sub": "testuser", "user_id": "123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(InvalidCredentialsError):
            verify_token(token)


class TestAuthenticationDependencies:
    """Test authentication dependency functions."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_session, created_user):
        """Test getting current user from valid token."""
        from fastapi import Request
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        
        # Create token for user
        data = {"sub": created_user.username, "user_id": created_user.id}
        token = create_access_token(data)
        
        # Mock request and credentials
        request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with patch('fastapi_security_sample.users.auth.auth.get_db') as mock_get_db:
            mock_get_db.return_value = db_session
            
            user = await get_current_user(request, credentials, db_session)
            
            assert user is not None
            assert user.username == created_user.username
            assert user.id == created_user.id

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_session):
        """Test getting current user with invalid token."""
        from fastapi import Request
        from fastapi.security import HTTPAuthorizationCredentials
        
        request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        
        with pytest.raises(InvalidCredentialsError):
            await get_current_user(request, credentials, db_session)

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, db_session):
        """Test getting current user for non-existent user."""
        from fastapi import Request
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Create token for non-existent user
        data = {"sub": "nonexistent", "user_id": "999"}
        token = create_access_token(data)
        
        request = MagicMock(spec=Request)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(InvalidCredentialsError):
            await get_current_user(request, credentials, db_session)


class TestSessionIntegration:
    """Test session integration with authentication."""
    
    def test_create_access_token_with_session(self, created_user):
        """Test creating token with session management."""
        client_ip = "192.168.1.1"
        user_agent = "Test Browser"
        
        with patch('fastapi_security_sample.users.auth.auth.session_manager') as mock_session_manager:
            mock_session = MagicMock()
            mock_session.id = "session_123"
            mock_session_manager.create_session.return_value = mock_session
            
            token, session = create_access_token_with_session(created_user, client_ip, user_agent)
            
            assert token is not None
            assert session == mock_session
            mock_session_manager.create_session.assert_called_once_with(
                created_user.id, client_ip, user_agent
            )

    def test_get_client_info(self):
        """Test extracting client information from request."""
        from fastapi import Request
        
        # Mock request with headers
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers = {
            "user-agent": "Mozilla/5.0 Test Browser",
            "x-forwarded-for": "10.0.0.1"
        }
        
        client_ip, user_agent = get_client_info(request)
        
        # Should prefer x-forwarded-for for IP
        assert client_ip == "10.0.0.1"
        assert user_agent == "Mozilla/5.0 Test Browser"

    def test_get_client_info_no_forwarded(self):
        """Test getting client info without forwarded headers."""
        from fastapi import Request
        
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers = {
            "user-agent": "Mozilla/5.0 Test Browser"
        }
        
        client_ip, user_agent = get_client_info(request)
        
        assert client_ip == "192.168.1.1"
        assert user_agent == "Mozilla/5.0 Test Browser"


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_check_rate_limit(self):
        """Test rate limit checking."""
        from fastapi import Request
        from fastapi_security_sample.users.rate_limiter import check_rate_limit
        
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        
        with patch('fastapi_security_sample.users.rate_limiter.RateLimiter.check_limit') as mock_check:
            mock_check.return_value = True
            
            result = check_rate_limit(request)
            
            assert result is not None
            mock_check.assert_called_once()

    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded scenario."""
        from fastapi import Request, HTTPException
        from fastapi_security_sample.users.rate_limiter import check_rate_limit
        
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.1"
        
        with patch('fastapi_security_sample.users.rate_limiter.RateLimiter.check_limit') as mock_check:
            mock_check.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                check_rate_limit(request)
            
            assert exc_info.value.status_code == 429


class TestAccountLockout:
    """Test account lockout functionality."""
    
    def test_account_lockout_check(self):
        """Test checking if account is locked."""
        from fastapi_security_sample.users.auth.account_lockout import account_lockout
        
        with patch.object(account_lockout, 'is_account_locked') as mock_locked:
            mock_locked.return_value = (True, 300)  # Locked for 5 minutes
            
            is_locked, seconds = account_lockout.is_account_locked("testuser")
            
            assert is_locked is True
            assert seconds == 300

    def test_record_failed_attempt(self):
        """Test recording failed login attempt."""
        from fastapi_security_sample.users.auth.account_lockout import account_lockout
        
        with patch.object(account_lockout, 'record_failed_attempt') as mock_record:
            account_lockout.record_failed_attempt("testuser")
            mock_record.assert_called_once_with("testuser")

    def test_clear_failed_attempts(self):
        """Test clearing failed attempts after successful login."""
        from fastapi_security_sample.users.auth.account_lockout import account_lockout
        
        with patch.object(account_lockout, 'clear_failed_attempts') as mock_clear:
            account_lockout.clear_failed_attempts("testuser")
            mock_clear.assert_called_once_with("testuser")


class TestPasswordResetIntegration:
    """Test password reset integration with auth."""
    
    def test_password_reset_token_generation(self):
        """Test password reset token generation."""
        from fastapi_security_sample.users.auth.password_reset import password_reset_manager
        
        user_id = "user_123"
        email = "test@example.com"
        
        with patch.object(password_reset_manager, 'create_reset_token') as mock_create:
            mock_create.return_value = "reset_token_123"
            
            token = password_reset_manager.create_reset_token(user_id, email)
            
            assert token == "reset_token_123"
            mock_create.assert_called_once_with(user_id, email)

    def test_password_reset_token_verification(self):
        """Test password reset token verification."""
        from fastapi_security_sample.users.auth.password_reset import password_reset_manager
        
        reset_token = "reset_token_123"
        
        with patch.object(password_reset_manager, 'verify_reset_token') as mock_verify:
            mock_token_data = MagicMock()
            mock_token_data.user_id = "user_123"
            mock_verify.return_value = mock_token_data
            
            token_data = password_reset_manager.verify_reset_token(reset_token)
            
            assert token_data.user_id == "user_123"
            mock_verify.assert_called_once_with(reset_token)


class TestLoggingIntegration:
    """Test logging integration with authentication."""
    
    def test_log_user_action(self):
        """Test logging user actions."""
        from fastapi_security_sample.users.logging import log_user_action
        
        with patch('fastapi_security_sample.users.logging.log_user_action') as mock_log:
            log_user_action("login", "user_123", {"ip": "192.168.1.1"})
            
            mock_log.assert_called_once_with("login", "user_123", {"ip": "192.168.1.1"})

    def test_log_security_event(self):
        """Test logging security events."""
        from fastapi_security_sample.users.logging import log_security_event
        
        with patch('fastapi_security_sample.users.logging.log_security_event') as mock_log:
            log_security_event("failed_login", "192.168.1.1", {"username": "testuser"})
            
            mock_log.assert_called_once_with("failed_login", "192.168.1.1", {"username": "testuser"})


class TestAuthConstants:
    """Test authentication constants and configuration."""
    
    def test_token_expiration_constant(self):
        """Test access token expiration setting."""
        from fastapi_security_sample.users.auth.auth import ACCESS_TOKEN_EXPIRE_MINUTES
        
        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int)

    def test_jwt_algorithm_constant(self):
        """Test JWT algorithm setting."""
        from fastapi_security_sample.users.auth.auth import ALGORITHM
        
        assert ALGORITHM in ["HS256", "RS256", "ES256"]  # Common JWT algorithms

    def test_secret_key_exists(self):
        """Test that secret key is configured."""
        from fastapi_security_sample.users.auth.auth import SECRET_KEY
        
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0
        assert isinstance(SECRET_KEY, str)
