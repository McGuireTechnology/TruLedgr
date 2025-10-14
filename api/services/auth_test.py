"""Unit tests for authentication and authorization services.

These tests are colocated with the service implementation following
The Golden Rule: unit tests are tightly coupled to the component they test.

Tests use mocked repositories to isolate the service layer logic.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import timedelta

from ..entities import User
from ..value_objects import UserId, EmailAddress
from .auth import (
    PasswordService,
    TokenService,
    AuthenticationService,
    AuthorizationService
)
from .auth_exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserInactiveError,
    PasswordHashingError,
    PasswordValidationError,
)


class TestPasswordService:
    """Unit tests for PasswordService."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        hashed = PasswordService.hash_password("test_password")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        """Test that hash_password generates different hashes (salt)."""
        password = "test_password"
        hash1 = PasswordService.hash_password(password)
        hash2 = PasswordService.hash_password(password)
        assert hash1 != hash2  # Different salts
    
    def test_verify_password_correct_password(self):
        """Test verify_password with correct password."""
        password = "test_password"
        hashed = PasswordService.hash_password(password)
        assert PasswordService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test verify_password with incorrect password."""
        password = "test_password"
        hashed = PasswordService.hash_password(password)
        assert PasswordService.verify_password("wrong_password", hashed) is False
    
    def test_hash_password_truncates_long_passwords(self):
        """Test that passwords longer than 72 bytes are truncated."""
        # bcrypt has a 72-byte limit
        long_password = "a" * 100
        hashed = PasswordService.hash_password(long_password)
        # Should not raise exception
        assert isinstance(hashed, str)
    
    def test_hash_password_handles_unicode(self):
        """Test that password service handles unicode characters."""
        unicode_password = "пароль123"  # Russian characters
        hashed = PasswordService.hash_password(unicode_password)
        assert PasswordService.verify_password(unicode_password, hashed) is True


class TestTokenService:
    """Unit tests for TokenService."""
    
    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        token = TokenService.create_access_token({"sub": "user123"})
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_custom_expiration(self):
        """Test create_access_token with custom expiration."""
        token = TokenService.create_access_token(
            {"sub": "user123"},
            expires_delta=timedelta(minutes=30)
        )
        assert isinstance(token, str)
    
    def test_verify_token_valid_token(self):
        """Test verify_token with valid token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = TokenService.create_access_token(data)
        
        payload = TokenService.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_token_invalid_token(self):
        """Test verify_token with invalid token."""
        payload = TokenService.verify_token("invalid_token")
        assert payload is None
    
    def test_verify_and_get_user_id_valid_token(self):
        """Test verify_and_get_user_id with valid token."""
        user_id = "user123"
        token = TokenService.create_access_token({"sub": user_id})
        
        result = TokenService.verify_and_get_user_id(token)
        assert result is not None
        assert isinstance(result, UserId)
        assert str(result) == user_id
    
    def test_verify_and_get_user_id_invalid_token(self):
        """Test verify_and_get_user_id with invalid token."""
        result = TokenService.verify_and_get_user_id("invalid_token")
        assert result is None
    
    def test_verify_and_get_user_id_missing_sub(self):
        """Test verify_and_get_user_id when token has no 'sub' claim."""
        token = TokenService.create_access_token({"email": "test@example.com"})
        result = TokenService.verify_and_get_user_id(token)
        assert result is None


@pytest.mark.asyncio
class TestAuthenticationService:
    """Unit tests for AuthenticationService."""
    
    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Create mock user
        user_id = UserId("user123")
        email = EmailAddress("test@example.com")
        hashed_password = PasswordService.hash_password("password123")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.email = email
        mock_user.hashed_password = hashed_password
        mock_user.is_active = True
        
        # Create mock repository
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = mock_user
        
        # Test authentication
        service = AuthenticationService(mock_repo)
        result = await service.authenticate_user(email, "password123")
        
        assert result == mock_user
        mock_repo.get_by_email.assert_called_once_with(email)
    
    async def test_authenticate_user_not_found(self):
        """Test authentication when user doesn't exist."""
        email = EmailAddress("test@example.com")
        
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = None
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.authenticate_user(email, "password123")
    
    async def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password."""
        email = EmailAddress("test@example.com")
        hashed_password = PasswordService.hash_password("correct_password")
        
        mock_user = Mock(spec=User)
        mock_user.hashed_password = hashed_password
        mock_user.is_active = True
        
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = mock_user
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(InvalidCredentialsError):
            await service.authenticate_user(email, "wrong_password")
    
    async def test_authenticate_user_inactive(self):
        """Test authentication when user is inactive."""
        email = EmailAddress("test@example.com")
        hashed_password = PasswordService.hash_password("password123")
        
        mock_user = Mock(spec=User)
        mock_user.hashed_password = hashed_password
        mock_user.is_active = False
        
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = mock_user
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(UserInactiveError):
            await service.authenticate_user(email, "password123")
    
    async def test_create_user_with_password(self):
        """Test creating user with password."""
        user_id = UserId("user123")
        email = EmailAddress("test@example.com")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.email = email
        mock_user.hashed_password = None
        
        created_user = Mock(spec=User)
        created_user.id = user_id
        created_user.email = email
        
        mock_repo = AsyncMock()
        mock_repo.create.return_value = created_user
        
        service = AuthenticationService(mock_repo)
        result = await service.create_user_with_password(
            mock_user,
            "password123"
        )
        
        # Check that password was hashed
        assert mock_user.hashed_password is not None
        assert mock_user.hashed_password != "password123"
        
        # Check that user was created
        mock_repo.create.assert_called_once_with(mock_user)
        assert result == created_user
    
    async def test_change_password_success(self):
        """Test successful password change."""
        user_id = UserId("user123")
        old_password = "old_password"
        new_password = "new_password"
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.hashed_password = PasswordService.hash_password(old_password)
        
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.update.return_value = mock_user
        
        service = AuthenticationService(mock_repo)
        result = await service.change_password(
            user_id,
            old_password,
            new_password
        )
        
        assert result is True
        # Verify new password works
        assert PasswordService.verify_password(
            new_password,
            mock_user.hashed_password
        )
        mock_repo.update.assert_called_once_with(mock_user)
    
    async def test_change_password_user_not_found(self):
        """Test password change when user doesn't exist."""
        user_id = UserId("user123")
        
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.change_password(
                user_id,
                "old_password",
                "new_password"
            )
    
    async def test_change_password_incorrect_old_password(self):
        """Test password change with incorrect old password."""
        user_id = UserId("user123")
        
        mock_user = Mock(spec=User)
        mock_user.hashed_password = PasswordService.hash_password(
            "correct_old_password"
        )
        
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_user
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(InvalidCredentialsError):
            await service.change_password(
                user_id,
                "wrong_old_password",
                "new_password"
            )
    
    async def test_get_user_by_id_success(self):
        """Test getting user by ID."""
        user_id = UserId("user123")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.is_active = True
        
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_user
        
        service = AuthenticationService(mock_repo)
        result = await service.get_user_by_id(user_id)
        
        assert result == mock_user
    
    async def test_get_user_by_id_not_found(self):
        """Test getting user when user doesn't exist."""
        user_id = UserId("user123")
        
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.get_user_by_id(user_id)
    
    async def test_get_user_by_id_inactive(self):
        """Test getting user when user is inactive."""
        user_id = UserId("user123")
        
        mock_user = Mock(spec=User)
        mock_user.is_active = False
        
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_user
        
        service = AuthenticationService(mock_repo)
        
        with pytest.raises(UserInactiveError):
            await service.get_user_by_id(user_id)


class TestAuthorizationService:
    """Unit tests for AuthorizationService."""
    
    def test_user_can_access_account_own_account(self):
        """Test user can access their own account."""
        user_id = UserId("user123")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        assert AuthorizationService.user_can_access_account(
            mock_user,
            user_id
        ) is True
    
    def test_user_can_access_account_different_user(self):
        """Test user cannot access another user's account."""
        user_id = UserId("user123")
        other_user_id = UserId("user456")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        assert AuthorizationService.user_can_access_account(
            mock_user,
            other_user_id
        ) is False
    
    def test_user_can_access_transaction_own_transaction(self):
        """Test user can access their own transaction."""
        user_id = UserId("user123")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        assert AuthorizationService.user_can_access_transaction(
            mock_user,
            user_id
        ) is True
    
    def test_user_can_access_category_own_category(self):
        """Test user can access their own category."""
        user_id = UserId("user123")
        
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        assert AuthorizationService.user_can_access_category(
            mock_user,
            user_id
        ) is True
    
    def test_user_is_active_when_active(self):
        """Test user_is_active returns True for active user."""
        mock_user = Mock(spec=User)
        mock_user.is_active = True
        
        assert AuthorizationService.user_is_active(mock_user) is True
    
    def test_user_is_active_when_inactive(self):
        """Test user_is_active returns False for inactive user."""
        mock_user = Mock(spec=User)
        mock_user.is_active = False
        
        assert AuthorizationService.user_is_active(mock_user) is False
