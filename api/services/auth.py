"""Authentication and authorization services for TruLedgr.

This module provides authentication and authorization services that follow
Clean Architecture principles:
- Services depend on domain entities and repository interfaces
- No direct SQLAlchemy or infrastructure dependencies
- Password and token handling are domain services (not infrastructure)
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt

from ..config.settings import get_settings
from ..entities import User
from ..value_objects import UserId, EmailAddress
from ..repositories import UserRepository
from .auth_exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserInactiveError,
    PasswordHashingError,
    PasswordValidationError,
)

settings = get_settings()


class PasswordService:
    """Domain service for password hashing and verification.
    
    This is a domain service (not infrastructure) because password policies
    and validation are business rules. The implementation uses bcrypt, but
    the service itself is part of the domain layer.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
            
        Raises:
            PasswordHashingError: If hashing fails
        """
        try:
            # Encode password to bytes
            password_bytes = password.encode('utf-8')
            # Truncate to 72 bytes if necessary (bcrypt limitation)
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise PasswordHashingError(f"Failed to hash password: {e}")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to check against
            
        Returns:
            True if password matches, False otherwise
            
        Raises:
            PasswordValidationError: If verification fails unexpectedly
        """
        try:
            # Encode password to bytes
            password_bytes = plain_password.encode('utf-8')
            # Truncate to 72 bytes if necessary (bcrypt limitation)
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            # Verify password
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            raise PasswordValidationError(
                f"Failed to verify password: {e}"
            )


class TokenService:
    """Domain service for JWT token creation and validation.
    
    This is a domain service because token policies (expiration, claims)
    are business rules. While JWT is a technical detail, the service
    itself belongs to the domain layer.
    """
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token.
        
        Args:
            data: Dictionary of claims to include in token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dict if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_and_get_user_id(token: str) -> Optional[UserId]:
        """Extract user ID from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            UserId if token is valid and contains user ID, None otherwise
        """
        payload = TokenService.verify_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                return UserId(user_id)
        return None


class AuthenticationService:
    """Application service for user authentication.
    
    This service follows Clean Architecture principles:
    - Depends on repository interface (UserRepository), not implementation
    - Works with domain entities (User), not infrastructure models
    - Uses domain services (PasswordService) for business logic
    - No SQLAlchemy or infrastructure dependencies
    """
    
    def __init__(self, user_repository: UserRepository):
        """Initialize authentication service.
        
        Args:
            user_repository: Repository interface for user persistence
        """
        self._user_repository = user_repository
    
    async def authenticate_user(
        self,
        email: EmailAddress,
        password: str
    ) -> User:
        """Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            Authenticated user entity
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            UserNotFoundError: If user doesn't exist
            UserInactiveError: If user account is inactive
        """
        # Get user by email
        user = await self._user_repository.get_by_email(email)
        
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        
        # Verify password
        if not PasswordService.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise UserInactiveError("User account is inactive")
        
        return user
    
    async def create_user_with_password(
        self,
        user: User,
        password: str
    ) -> User:
        """Create a new user with hashed password.
        
        Args:
            user: User entity (without hashed password)
            password: Plain text password
            
        Returns:
            Created user entity
            
        Raises:
            PasswordHashingError: If password hashing fails
        """
        # Hash password and add to user entity
        user.hashed_password = PasswordService.hash_password(password)
        
        # Create user via repository
        created_user = await self._user_repository.create(user)
        
        return created_user
    
    async def change_password(
        self,
        user_id: UserId,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidCredentialsError: If old password is incorrect
            PasswordHashingError: If password hashing fails
        """
        # Get user by ID
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        # Verify old password
        if not PasswordService.verify_password(
            old_password,
            user.hashed_password
        ):
            raise InvalidCredentialsError("Current password is incorrect")
        
        # Hash new password
        user.hashed_password = PasswordService.hash_password(new_password)
        
        # Update user via repository
        await self._user_repository.update(user)
        
        return True
    
    async def get_user_by_id(self, user_id: UserId) -> User:
        """Get user by ID for authentication purposes.
        
        Args:
            user_id: User ID
            
        Returns:
            User entity
            
        Raises:
            UserNotFoundError: If user doesn't exist
            UserInactiveError: If user is inactive
        """
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        if not user.is_active:
            raise UserInactiveError("User account is inactive")
        
        return user


class AuthorizationService:
    """Domain service for user authorization and permissions.
    
    This service contains authorization business rules (who can access what).
    It's a stateless domain service that works with entities only.
    No infrastructure dependencies.
    """
    
    @staticmethod
    def user_can_access_account(
        user: User,
        account_user_id: UserId
    ) -> bool:
        """Check if user can access account.
        
        Args:
            user: User requesting access
            account_user_id: User ID who owns the account
            
        Returns:
            True if user can access account
        """
        return user.id == account_user_id
    
    @staticmethod
    def user_can_access_transaction(
        user: User,
        transaction_account_user_id: UserId
    ) -> bool:
        """Check if user can access transaction.
        
        Args:
            user: User requesting access
            transaction_account_user_id: User ID who owns transaction
            
        Returns:
            True if user can access transaction
        """
        return user.id == transaction_account_user_id
    
    @staticmethod
    def user_can_access_category(
        user: User,
        category_user_id: UserId
    ) -> bool:
        """Check if user can access category.
        
        Args:
            user: User requesting access
            category_user_id: User ID who owns category
            
        Returns:
            True if user can access category
        """
        return user.id == category_user_id
    
    @staticmethod
    def user_is_active(user: User) -> bool:
        """Check if user is active.
        
        Args:
            user: User to check
            
        Returns:
            True if user account is active
        """
        return user.is_active
