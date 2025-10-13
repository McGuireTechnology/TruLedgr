"""Authentication routes for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

from ..schemas.auth import (
    UserRegistrationRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    ErrorResponse
)
from ..dependencies.database import get_uow
from ..dependencies.auth import get_current_user
from ..repositories.uow import SqlAlchemyUnitOfWork
from ..services.auth import (
    AuthenticationService,
    TokenService,
    PasswordService
)
from ..services.auth_exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserInactiveError
)
from ..services.user_exceptions import UserAlreadyExistsError
from ..entities import User
from ..value_objects import UserId, EmailAddress
from ..config.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {
            "model": ErrorResponse,
            "description": "Email already registered"
        }
    }
)
async def register(
    request: UserRegistrationRequest,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> TokenResponse:
    """
    Register a new user account.
    
    Creates a new user with the provided email and password.
    Returns an access token for immediate authentication.
    
    Args:
        request: Registration details (email and password)
        uow: Unit of Work for database operations
        
    Returns:
        Access token for the newly created user
        
    Raises:
        HTTPException: If email is already registered
    """
    try:
        # Check if username or email already exists
        existing_by_username = await uow.users.get_by_username(
            request.username
        )
        if existing_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        email = EmailAddress(request.email)
        existing_by_email = await uow.users.get_by_email(email)
        
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user entity
        user = User(
            id=UserId.generate(),
            username=request.username,
            email=email,
            hashed_password="",  # Will be set by auth service
            is_active=True,
            is_admin=False
        )
        
        # Create user with hashed password
        auth_service = AuthenticationService(uow.users)
        created_user = await auth_service.create_user_with_password(
            user,
            request.password
        )
        
        # Commit transaction
        await uow.commit()
        
        # Generate access token
        token = TokenService.create_access_token(
            data={"sub": str(created_user.id)},
            expires_delta=timedelta(
                minutes=settings.access_token_expire_minutes
            )
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
        
    except ValueError as e:
        # Invalid email format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorResponse,
            "description": "Invalid credentials"
        },
        403: {
            "model": ErrorResponse,
            "description": "Account inactive"
        }
    }
)
async def login(
    request: LoginRequest,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> TokenResponse:
    """
    Authenticate user and return access token.
    
    Validates user credentials and returns a JWT access token
    for authenticated API access.
    
    Args:
        request: Login credentials (email and password)
        uow: Unit of Work for database operations
        
    Returns:
        Access token for the authenticated user
        
    Raises:
        HTTPException: If credentials are invalid or account is inactive
    """
    try:
        # Validate that either username or email is provided
        if not request.username and not request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either username or email must be provided"
            )
        
        # Find user by username or email
        auth_service = AuthenticationService(uow.users)
        user = None
        
        if request.username:
            # Try to authenticate with username
            found_user = await uow.users.get_by_username(request.username)
            if found_user:
                # Verify password using PasswordService
                if PasswordService.verify_password(
                    request.password,
                    found_user.hashed_password
                ):
                    # Check if user is active
                    if not found_user.is_active:
                        raise UserInactiveError("User account is inactive")
                    user = found_user
        elif request.email:
            # Authenticate with email (original flow)
            email = EmailAddress(request.email)
            user = await auth_service.authenticate_user(
                email,
                request.password
            )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Record login time
        user.record_login()
        await uow.users.update(user)
        await uow.commit()
        
        # Generate access token
        token = TokenService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(
                minutes=settings.access_token_expire_minutes
            )
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
        
    except (UserNotFoundError, InvalidCredentialsError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {"description": "Current user information"},
        401: {
            "model": ErrorResponse,
            "description": "Not authenticated"
        }
    }
)
async def get_current_user_info(
    user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Returns the profile information for the currently authenticated user.
    This endpoint serves as a dashboard verification that the user is
    successfully authenticated.
    
    Args:
        user: Current authenticated user (injected by dependency)
        
    Returns:
        Current user's profile information
    """
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=str(user.email),
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Logout successful"},
        401: {
            "model": ErrorResponse,
            "description": "Not authenticated"
        }
    }
)
async def logout(
    user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    Since we're using JWT tokens (stateless), logout is primarily
    a client-side operation (discarding the token). This endpoint
    exists for consistency and can be extended later with token
    blacklisting if needed.
    
    Args:
        user: Current authenticated user (injected by dependency)
        
    Returns:
        No content (204)
    """
    # With JWT, logout is handled client-side by discarding the token
    # This endpoint can be extended to add token to blacklist if needed
    return None
