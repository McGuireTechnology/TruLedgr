"""User application services."""



from ...domain.entities import User
from ...domain.value_objects import UserId, EmailAddress
from ...domain.exceptions import ValidationError, DuplicateEntity
from ...domain.repositories import UnitOfWork
from ...infrastructure.auth import TokenService, AuthenticationService


class UserRegistrationService:
    """Service for user registration."""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        is_business: bool = False
    ) -> dict:
        """Register a new user."""
        async with self.uow:
            # Validate email format
            try:
                email_vo = EmailAddress(email)
            except ValidationError as e:
                raise ValidationError(f"Invalid email: {e}")
            
            # Check if user already exists
            if await self.uow.users.exists_by_email(email_vo):
                raise DuplicateEntity("User with this email already exists")
            
            # Create user entity
            import uuid
            user = User(
                id=UserId(str(uuid.uuid4())),
                email=email_vo,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                is_business=is_business
            )
            
            # Create user with password through auth service
            session = self.uow.get_session()
            auth_service = AuthenticationService(session)
            created_user = auth_service.create_user_with_password(user, password)
            
            # Create access token
            access_token = TokenService.create_access_token(
                data={"sub": str(created_user.id)}
            )
            
            await self.uow.commit()
            
            return {
                "user": {
                    "id": str(created_user.id),
                    "email": str(created_user.email),
                    "first_name": created_user.first_name,
                    "last_name": created_user.last_name,
                    "is_business": created_user.is_business
                },
                "access_token": access_token,
                "token_type": "bearer"
            }


class UserAuthenticationService:
    """Service for user authentication."""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate user and return token."""
        async with self.uow:
            try:
                email_vo = EmailAddress(email)
            except ValidationError as e:
                raise ValidationError(f"Invalid email: {e}")
            
            session = self.uow.get_session()
            auth_service = AuthenticationService(session)
            
            user = auth_service.authenticate_user(email_vo, password)
            if not user:
                raise ValidationError("Invalid email or password")
            
            # Create access token
            access_token = TokenService.create_access_token(
                data={"sub": str(user.id)}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "email": str(user.email),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_business": user.is_business
                }
            }
    
    async def change_password(
        self,
        user_id: UserId,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password."""
        async with self.uow:
            session = self.uow.get_session()
            auth_service = AuthenticationService(session)
            
            success = auth_service.change_password(user_id, old_password, new_password)
            if success:
                await self.uow.commit()
            
            return success
