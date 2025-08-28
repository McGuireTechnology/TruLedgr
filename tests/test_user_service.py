"""
Unit tests for user CRUD operations.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from fastapi_security_sample.users import service
from fastapi_security_sample.users.models import User
from fastapi_security_sample.users.exceptions import UserNotFoundError, UserAlreadyExistsError


class TestUserService:
    """Test the user service layer."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session, sample_user_data):
        """Test successful user creation."""
        from fastapi_security_sample.users.utils import get_password_hash
        
        user = User(
            id="test-id",
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            hashed_password=get_password_hash(sample_user_data["password"])
        )
        
        created_user = await service.create_user(db_session, user)
        
        assert created_user.username == sample_user_data["username"]
        assert created_user.email == sample_user_data["email"]
        assert created_user.hashed_password != sample_user_data["password"]  # Should be hashed
        assert created_user.id == "test-id"

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session, created_user):
        """Test retrieving user by username."""
        user = await service.get_user_by_username(db_session, created_user.username)
        
        assert user is not None
        assert user.username == created_user.username
        assert user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session):
        """Test retrieving non-existent user."""
        user = await service.get_user_by_username(db_session, "nonexistent")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, db_session, created_user):
        """Test retrieving user by email."""
        user = await service.get_user_by_email(db_session, created_user.email)
        
        assert user is not None
        assert user.username == created_user.username
        assert user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session):
        """Test retrieving user by non-existent email."""
        user = await service.get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_list_users(self, db_session, created_user):
        """Test listing all users."""
        users = await service.list_users(db_session)
        
        assert len(users) >= 1
        assert any(user.username == created_user.username for user in users)

    @pytest.mark.asyncio
    async def test_update_user_success(self, db_session, created_user):
        """Test updating user information."""
        new_email = "updated@example.com"
        updates = {"email": new_email}
        
        updated_user = await service.update_user(db_session, created_user.username, updates)
        
        assert updated_user is not None
        assert updated_user.email == new_email
        assert updated_user.username == created_user.username

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, db_session):
        """Test updating non-existent user."""
        updates = {"email": "new@example.com"}
        
        updated_user = await service.update_user(db_session, "nonexistent", updates)
        assert updated_user is None

    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session, created_user):
        """Test soft deleting a user."""
        result = await service.delete_user(db_session, created_user.username)
        
        assert result is True
        
        # Verify user is soft deleted
        user = await service.get_user_by_username(db_session, created_user.username)
        assert user is None or user.is_deleted

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, db_session):
        """Test deleting non-existent user."""
        result = await service.delete_user(db_session, "nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session, created_user, sample_user_data):
        """Test successful user authentication."""
        user = await service.authenticate_user(
            db_session, 
            created_user.username, 
            sample_user_data["password"]
        )
        
        assert user is not None
        assert user.username == created_user.username

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session, created_user):
        """Test authentication with wrong password."""
        user = await service.authenticate_user(
            db_session, 
            created_user.username, 
            "wrongpassword"
        )
        
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, db_session):
        """Test authentication with non-existent user."""
        user = await service.authenticate_user(
            db_session, 
            "nonexistent", 
            "password"
        )
        
        assert user is None


class TestUserValidation:
    """Test user data validation."""
    
    def test_user_create_request_valid(self):
        """Test valid user creation request."""
        from fastapi_security_sample.users.models import UserCreateRequest
        
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        
        request = UserCreateRequest(**data)
        assert request.username == "testuser"
        assert request.email == "test@example.com"
        assert request.password == "SecurePassword123!"

    def test_user_create_request_invalid_username(self):
        """Test invalid username validation."""
        from fastapi_security_sample.users.models import UserCreateRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            UserCreateRequest(
                username="invalid@username",  # Contains invalid character
                email="test@example.com",
                password="SecurePassword123!"
            )

    def test_user_create_request_short_password(self):
        """Test password length validation."""
        from fastapi_security_sample.users.models import UserCreateRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            UserCreateRequest(
                username="testuser",
                email="test@example.com",
                password="short"  # Too short
            )

    def test_user_create_request_invalid_email(self):
        """Test email validation."""
        from fastapi_security_sample.users.models import UserCreateRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            UserCreateRequest(
                username="testuser",
                email="invalid-email",  # Invalid email format
                password="SecurePassword123!"
            )


class TestPasswordUtils:
    """Test password utility functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        from fastapi_security_sample.users.utils import get_password_hash, verify_password
        
        password = "SecureP@ssw0rd2024!"  # Strong password
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        from fastapi_security_sample.users.utils import get_password_hash
        
        password = "SecureP@ssw0rd2024!"  # Strong password
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Should have different salts


class TestTOTPUtils:
    """Test TOTP utility functions."""
    
    def test_generate_totp_secret(self):
        """Test TOTP secret generation."""
        from fastapi_security_sample.users.utils import generate_totp_secret
        
        secret = generate_totp_secret()
        
        assert secret is not None
        assert len(secret) > 0
        assert isinstance(secret, str)

    def test_get_provisioning_uri(self):
        """Test TOTP provisioning URI generation."""
        from fastapi_security_sample.users.utils import get_provisioning_uri
        
        username = "testuser"
        secret = "ABCDEFGHIJKLMNOP"
        
        uri = get_provisioning_uri(username, secret)
        
        assert uri.startswith("otpauth://totp/")
        assert username in uri
        assert secret in uri

    @patch('fastapi_security_sample.users.utils.pyotp.TOTP.verify')
    def test_verify_totp_success(self, mock_verify):
        """Test TOTP verification success."""
        from fastapi_security_sample.users.utils import verify_totp
        
        mock_verify.return_value = True
        
        result = verify_totp("123456", "ABCDEFGHIJKLMNOP")
        assert result is True

    @patch('fastapi_security_sample.users.utils.pyotp.TOTP.verify')
    def test_verify_totp_failure(self, mock_verify):
        """Test TOTP verification failure."""
        from fastapi_security_sample.users.utils import verify_totp
        
        mock_verify.return_value = False
        
        result = verify_totp("123456", "ABCDEFGHIJKLMNOP")
        assert result is False


class TestUserExceptions:
    """Test custom user exceptions."""
    
    def test_user_not_found_error(self):
        """Test UserNotFoundError exception."""
        username = "testuser"
        error = UserNotFoundError(username)
        
        assert error.status_code == 404
        assert username in str(error.detail)

    def test_user_already_exists_error(self):
        """Test UserAlreadyExistsError exception."""
        field = "username"
        value = "testuser"
        error = UserAlreadyExistsError(field, value)
        
        assert error.status_code == 400
        assert field in str(error.detail)
        assert value in str(error.detail)
