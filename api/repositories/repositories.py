"""Repository implementations for TruLedgr infrastructure layer."""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy import and_, func

from ..entities import (
    User, Account, Transaction, Category, Tenant, Person,
    ResourceGroup, Subscription, Invitation, Session
)
from ..value_objects import (
    UserId, AccountId, TransactionId, CategoryId, TenantId, PersonId,
    SubscriptionId, ResourceGroupId, InvitationId, SessionId, EmailAddress, Money,
    Currency, PersonRole, SessionStatus
)
from . import (
    UserRepository, AccountRepository, TransactionRepository, CategoryRepository,
    TenantRepository, PersonRepository, ResourceGroupRepository,
    SubscriptionRepository, InvitationRepository, SessionRepository
)
from .models import (
    UserModel, AccountModel, TransactionModel, CategoryModel,
    TenantModel, PersonModel, ResourceGroupModel, SubscriptionModel, InvitationModel, SessionModel
)
from .mappers import (
    UserMapper, AccountMapper, TransactionMapper, CategoryMapper,
    TenantMapper, PersonMapper, ResourceGroupMapper, SubscriptionMapper, InvitationMapper, SessionMapper
)


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        user_model = UserMapper.to_model(user)
        self._session.add(user_model)
        self._session.flush()  # Get the ID without committing
        return UserMapper.to_entity(user_model)
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        user_model = self._session.query(UserModel).filter(
            UserModel.id == str(user_id)
        ).first()
        return UserMapper.to_entity(user_model) if user_model else None
    
    async def get_by_email(self, email: EmailAddress) -> Optional[User]:
        """Get user by email address."""
        user_model = self._session.query(UserModel).filter(
            UserModel.email == str(email)
        ).first()
        return UserMapper.to_entity(user_model) if user_model else None
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        user_model = self._session.query(UserModel).filter(
            UserModel.id == str(user.id)
        ).first()
        
        if not user_model:
            raise ValueError(f"User with id {user.id} not found")
        
        # Update fields
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.is_active = user.is_active
        user_model.is_business = user.is_business
        user_model.timezone = user.timezone
        user_model.updated_at = user.updated_at
        
        self._session.flush()
        return UserMapper.to_entity(user_model)
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        result = self._session.query(UserModel).filter(
            UserModel.id == str(user_id)
        ).delete()
        return result > 0
    
    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email."""
        return self._session.query(UserModel).filter(
            UserModel.email == str(email)
        ).first() is not None


class SqlAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy implementation of AccountRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, account: Account) -> Account:
        """Create a new account."""
        account_model = AccountMapper.to_model(account)
        self._session.add(account_model)
        self._session.flush()
        return AccountMapper.to_entity(account_model)
    
    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        """Get account by ID."""
        account_model = self._session.query(AccountModel).filter(
            AccountModel.id == str(account_id)
        ).first()
        return AccountMapper.to_entity(account_model) if account_model else None
    
    async def get_by_user_id(self, user_id: UserId) -> List[Account]:
        """Get all accounts for a user."""
        account_models = self._session.query(AccountModel).filter(
            AccountModel.user_id == str(user_id)
        ).all()
        return [AccountMapper.to_entity(model) for model in account_models]
    
    async def update(self, account: Account) -> Account:
        """Update existing account."""
        account_model = self._session.query(AccountModel).filter(
            AccountModel.id == str(account.id)
        ).first()
        
        if not account_model:
            raise ValueError(f"Account with id {account.id} not found")
        
        # Update fields
        account_model.name = account.name
        account_model.balance_amount = account.balance.amount
        account_model.balance_currency = account.balance.currency.value
        account_model.is_active = account.is_active
        account_model.institution_name = account.institution_name
        account_model.account_number_last_four = account.account_number_last_four
        account_model.updated_at = account.updated_at
        
        self._session.flush()
        return AccountMapper.to_entity(account_model)
    
    async def delete(self, account_id: AccountId) -> bool:
        """Delete account by ID."""
        result = self._session.query(AccountModel).filter(
            AccountModel.id == str(account_id)
        ).delete()
        return result > 0


class SqlAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        transaction_model = TransactionMapper.to_model(transaction)
        self._session.add(transaction_model)
        self._session.flush()
        return TransactionMapper.to_entity(transaction_model)
    
    async def get_by_id(self, transaction_id: TransactionId) -> Optional[Transaction]:
        """Get transaction by ID."""
        transaction_model = self._session.query(TransactionModel).filter(
            TransactionModel.id == str(transaction_id)
        ).first()
        return TransactionMapper.to_entity(transaction_model) if transaction_model else None
    
    async def get_by_account_id(
        self,
        account_id: AccountId,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transactions for an account with pagination."""
        transaction_models = self._session.query(TransactionModel).filter(
            TransactionModel.account_id == str(account_id)
        ).order_by(TransactionModel.transaction_date.desc()).limit(limit).offset(offset).all()
        return [TransactionMapper.to_entity(model) for model in transaction_models]
    
    async def get_by_date_range(
        self,
        account_id: AccountId,
        start_date: datetime,
        end_date: datetime
    ) -> List[Transaction]:
        """Get transactions within date range."""
        transaction_models = self._session.query(TransactionModel).filter(
            and_(
                TransactionModel.account_id == str(account_id),
                TransactionModel.transaction_date >= start_date,
                TransactionModel.transaction_date <= end_date
            )
        ).order_by(TransactionModel.transaction_date.desc()).all()
        return [TransactionMapper.to_entity(model) for model in transaction_models]
    
    async def get_by_category(
        self,
        category_id: CategoryId,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get transactions by category with optional date filter."""
        query = self._session.query(TransactionModel).filter(
            TransactionModel.category_id == str(category_id)
        )
        
        if start_date:
            query = query.filter(TransactionModel.transaction_date >= start_date)
        if end_date:
            query = query.filter(TransactionModel.transaction_date <= end_date)
        
        transaction_models = query.order_by(TransactionModel.transaction_date.desc()).all()
        return [TransactionMapper.to_entity(model) for model in transaction_models]
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Update existing transaction."""
        transaction_model = self._session.query(TransactionModel).filter(
            TransactionModel.id == str(transaction.id)
        ).first()
        
        if not transaction_model:
            raise ValueError(f"Transaction with id {transaction.id} not found")
        
        # Update fields
        transaction_model.amount_value = transaction.amount.amount
        transaction_model.amount_currency = transaction.amount.currency.value
        transaction_model.description = transaction.description
        transaction_model.category_id = str(transaction.category_id) if transaction.category_id else None
        transaction_model.is_reconciled = transaction.is_reconciled
        transaction_model.updated_at = transaction.updated_at
        
        self._session.flush()
        return TransactionMapper.to_entity(transaction_model)
    
    async def delete(self, transaction_id: TransactionId) -> bool:
        """Delete transaction by ID."""
        result = self._session.query(TransactionModel).filter(
            TransactionModel.id == str(transaction_id)
        ).delete()
        return result > 0
    
    async def get_balance_summary(self, account_id: AccountId) -> Money:
        """Calculate account balance from transactions."""
        result = self._session.query(
            func.sum(TransactionModel.amount_value).label('total'),
            TransactionModel.amount_currency
        ).filter(
            TransactionModel.account_id == str(account_id)
        ).group_by(TransactionModel.amount_currency).first()
        
        if result:
            return Money(Decimal(str(result.total)), Currency(result.amount_currency))
        return Money(Decimal('0'), Currency.USD)


class SqlAlchemyCategoryRepository(CategoryRepository):
    """SQLAlchemy implementation of CategoryRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, category: Category) -> Category:
        """Create a new category."""
        category_model = CategoryMapper.to_model(category)
        self._session.add(category_model)
        self._session.flush()
        return CategoryMapper.to_entity(category_model)
    
    async def get_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """Get category by ID."""
        category_model = self._session.query(CategoryModel).filter(
            CategoryModel.id == str(category_id)
        ).first()
        return CategoryMapper.to_entity(category_model) if category_model else None
    
    async def get_by_user_id(self, user_id: UserId) -> List[Category]:
        """Get all categories for a user."""
        category_models = self._session.query(CategoryModel).filter(
            CategoryModel.user_id == str(user_id)
        ).all()
        return [CategoryMapper.to_entity(model) for model in category_models]
    
    async def get_subcategories(self, parent_id: CategoryId) -> List[Category]:
        """Get subcategories of a parent category."""
        category_models = self._session.query(CategoryModel).filter(
            CategoryModel.parent_id == str(parent_id)
        ).all()
        return [CategoryMapper.to_entity(model) for model in category_models]
    
    async def update(self, category: Category) -> Category:
        """Update existing category."""
        category_model = self._session.query(CategoryModel).filter(
            CategoryModel.id == str(category.id)
        ).first()
        
        if not category_model:
            raise ValueError(f"Category with id {category.id} not found")
        
        # Update fields
        category_model.name = category.name
        category_model.parent_id = str(category.parent_id) if category.parent_id else None
        category_model.is_income = category.is_income
        category_model.is_active = category.is_active
        category_model.updated_at = category.updated_at
        
        self._session.flush()
        return CategoryMapper.to_entity(category_model)
    
    async def delete(self, category_id: CategoryId) -> bool:
        """Delete category by ID."""
        result = self._session.query(CategoryModel).filter(
            CategoryModel.id == str(category_id)
        ).delete()
        return result > 0


class SqlAlchemyTenantRepository(TenantRepository):
    """SQLAlchemy implementation of TenantRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        tenant_model = TenantMapper.to_model(tenant)
        self._session.add(tenant_model)
        self._session.flush()
        return TenantMapper.to_entity(tenant_model)
    
    async def get_by_id(self, tenant_id: TenantId) -> Optional[Tenant]:
        """Get tenant by ID."""
        tenant_model = self._session.query(TenantModel).filter(
            TenantModel.id == str(tenant_id)
        ).first()
        return TenantMapper.to_entity(tenant_model) if tenant_model else None
    
    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        tenant_model = self._session.query(TenantModel).filter(
            TenantModel.name == name
        ).first()
        return TenantMapper.to_entity(tenant_model) if tenant_model else None
    
    async def update(self, tenant: Tenant) -> Tenant:
        """Update existing tenant."""
        tenant_model = self._session.query(TenantModel).filter(
            TenantModel.id == str(tenant.id)
        ).first()
        
        if not tenant_model:
            raise ValueError(f"Tenant {tenant.id} not found")
        
        # Update fields
        tenant_model.name = tenant.name
        tenant_model.display_name = tenant.display_name
        tenant_model.description = tenant.description
        tenant_model.is_active = tenant.is_active
        tenant_model.max_users = str(tenant.max_users)
        tenant_model.updated_at = tenant.updated_at
        
        return TenantMapper.to_entity(tenant_model)
    
    async def delete(self, tenant_id: TenantId) -> bool:
        """Delete tenant by ID."""
        deleted = self._session.query(TenantModel).filter(
            TenantModel.id == str(tenant_id)
        ).delete()
        return deleted > 0
    
    async def exists_by_name(self, name: str) -> bool:
        """Check if tenant exists by name."""
        count = self._session.query(TenantModel).filter(
            TenantModel.name == name
        ).count()
        return count > 0


class SqlAlchemyPersonRepository(PersonRepository):
    """SQLAlchemy implementation of PersonRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, person: Person) -> Person:
        """Create a new person."""
        person_model = PersonMapper.to_model(person)
        self._session.add(person_model)
        self._session.flush()
        return PersonMapper.to_entity(person_model)
    
    async def get_by_id(self, person_id: PersonId) -> Optional[Person]:
        """Get person by ID."""
        person_model = self._session.query(PersonModel).filter(
            PersonModel.id == str(person_id)
        ).first()
        return PersonMapper.to_entity(person_model) if person_model else None
    
    async def get_by_user_and_tenant(self, user_id: UserId, tenant_id: TenantId) -> Optional[Person]:
        """Get person by user and tenant."""
        person_model = self._session.query(PersonModel).filter(
            and_(
                PersonModel.user_id == str(user_id),
                PersonModel.tenant_id == str(tenant_id)
            )
        ).first()
        return PersonMapper.to_entity(person_model) if person_model else None
    
    async def get_by_user_id(self, user_id: UserId) -> List[Person]:
        """Get all persons for a user."""
        person_models = self._session.query(PersonModel).filter(
            PersonModel.user_id == str(user_id)
        ).all()
        return [PersonMapper.to_entity(model) for model in person_models if model]
    
    async def get_by_tenant_id(self, tenant_id: TenantId) -> List[Person]:
        """Get all persons in a tenant."""
        person_models = self._session.query(PersonModel).filter(
            PersonModel.tenant_id == str(tenant_id)
        ).all()
        return [PersonMapper.to_entity(model) for model in person_models if model]
    
    async def get_admins_by_tenant_id(self, tenant_id: TenantId) -> List[Person]:
        """Get all admin persons in a tenant."""
        from .models import PersonRoleEnum
        person_models = self._session.query(PersonModel).filter(
            and_(
                PersonModel.tenant_id == str(tenant_id),
                PersonModel.role == PersonRoleEnum.ADMIN
            )
        ).all()
        return [PersonMapper.to_entity(model) for model in person_models if model]
    
    async def update(self, person: Person) -> Person:
        """Update existing person."""
        person_model = self._session.query(PersonModel).filter(
            PersonModel.id == str(person.id)
        ).first()
        
        if not person_model:
            raise ValueError(f"Person {person.id} not found")
        
        # Update fields
        person_model.role = PersonMapper._domain_to_db_role(person.role)
        person_model.is_active = person.is_active
        person_model.updated_at = person.updated_at
        
        return PersonMapper.to_entity(person_model)
    
    async def delete(self, person_id: PersonId) -> bool:
        """Delete person by ID."""
        deleted = self._session.query(PersonModel).filter(
            PersonModel.id == str(person_id)
        ).delete()
        return deleted > 0


class SqlAlchemyResourceGroupRepository(ResourceGroupRepository):
    """SQLAlchemy implementation of ResourceGroupRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, resource_group: ResourceGroup) -> ResourceGroup:
        """Create a new resource group."""
        resource_group_model = ResourceGroupMapper.to_model(resource_group)
        self._session.add(resource_group_model)
        self._session.flush()
        return ResourceGroupMapper.to_entity(resource_group_model)
    
    async def get_by_id(self, resource_group_id: ResourceGroupId) -> Optional[ResourceGroup]:
        """Get resource group by ID."""
        resource_group_model = self._session.query(ResourceGroupModel).filter(
            ResourceGroupModel.id == str(resource_group_id)
        ).first()
        return ResourceGroupMapper.to_entity(resource_group_model) if resource_group_model else None
    
    async def get_by_tenant_id(self, tenant_id: TenantId) -> List[ResourceGroup]:
        """Get all resource groups for a tenant."""
        resource_group_models = self._session.query(ResourceGroupModel).filter(
            ResourceGroupModel.tenant_id == str(tenant_id)
        ).all()
        return [ResourceGroupMapper.to_entity(model) for model in resource_group_models if model]
    
    async def update(self, resource_group: ResourceGroup) -> ResourceGroup:
        """Update existing resource group."""
        resource_group_model = self._session.query(ResourceGroupModel).filter(
            ResourceGroupModel.id == str(resource_group.id)
        ).first()
        
        if not resource_group_model:
            raise ValueError(f"ResourceGroup {resource_group.id} not found")
        
        # Update fields
        resource_group_model.name = resource_group.name
        resource_group_model.description = resource_group.description
        resource_group_model.is_active = resource_group.is_active
        resource_group_model.updated_at = resource_group.updated_at
        
        return ResourceGroupMapper.to_entity(resource_group_model)
    
    async def delete(self, resource_group_id: ResourceGroupId) -> bool:
        """Delete resource group by ID."""
        deleted = self._session.query(ResourceGroupModel).filter(
            ResourceGroupModel.id == str(resource_group_id)
        ).delete()
        return deleted > 0


class SqlAlchemySubscriptionRepository(SubscriptionRepository):
    """SQLAlchemy implementation of SubscriptionRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription."""
        subscription_model = SubscriptionMapper.to_model(subscription)
        self._session.add(subscription_model)
        self._session.flush()
        return SubscriptionMapper.to_entity(subscription_model)
    
    async def get_by_id(self, subscription_id: SubscriptionId) -> Optional[Subscription]:
        """Get subscription by ID."""
        subscription_model = self._session.query(SubscriptionModel).filter(
            SubscriptionModel.id == str(subscription_id)
        ).first()
        return SubscriptionMapper.to_entity(subscription_model) if subscription_model else None
    
    async def get_by_tenant_id(self, tenant_id: TenantId) -> List[Subscription]:
        """Get all subscriptions for a tenant."""
        subscription_models = self._session.query(SubscriptionModel).filter(
            SubscriptionModel.tenant_id == str(tenant_id)
        ).all()
        return [SubscriptionMapper.to_entity(model) for model in subscription_models if model]
    
    async def get_by_resource_group_id(self, resource_group_id: ResourceGroupId) -> List[Subscription]:
        """Get all subscriptions for a resource group."""
        subscription_models = self._session.query(SubscriptionModel).filter(
            SubscriptionModel.resource_group_id == str(resource_group_id)
        ).all()
        return [SubscriptionMapper.to_entity(model) for model in subscription_models if model]
    
    async def update(self, subscription: Subscription) -> Subscription:
        """Update existing subscription."""
        subscription_model = self._session.query(SubscriptionModel).filter(
            SubscriptionModel.id == str(subscription.id)
        ).first()
        
        if not subscription_model:
            raise ValueError(f"Subscription {subscription.id} not found")
        
        # Update fields
        subscription_model.name = subscription.name
        subscription_model.status = SubscriptionMapper._domain_to_db_status(subscription.status)
        subscription_model.billing_cycle_days = str(subscription.billing_cycle_days)
        subscription_model.next_billing_date = subscription.next_billing_date
        subscription_model.is_active = subscription.is_active
        subscription_model.updated_at = subscription.updated_at
        
        return SubscriptionMapper.to_entity(subscription_model)
    
    async def delete(self, subscription_id: SubscriptionId) -> bool:
        """Delete subscription by ID."""
        deleted = self._session.query(SubscriptionModel).filter(
            SubscriptionModel.id == str(subscription_id)
        ).delete()
        return deleted > 0


class SqlAlchemyInvitationRepository(InvitationRepository):
    """SQLAlchemy implementation of InvitationRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, invitation: Invitation) -> Invitation:
        """Create a new invitation."""
        invitation_model = InvitationMapper.to_model(invitation)
        self._session.add(invitation_model)
        self._session.flush()
        return InvitationMapper.to_entity(invitation_model)
    
    async def get_by_id(self, invitation_id: InvitationId) -> Optional[Invitation]:
        """Get invitation by ID."""
        invitation_model = self._session.query(InvitationModel).filter(
            InvitationModel.id == str(invitation_id)
        ).first()
        return InvitationMapper.to_entity(invitation_model) if invitation_model else None
    
    async def get_by_email_and_tenant(self, email: EmailAddress, tenant_id: TenantId) -> Optional[Invitation]:
        """Get invitation by email and tenant."""
        invitation_model = self._session.query(InvitationModel).filter(
            and_(
                InvitationModel.email == str(email),
                InvitationModel.tenant_id == str(tenant_id)
            )
        ).first()
        return InvitationMapper.to_entity(invitation_model) if invitation_model else None
    
    async def get_by_tenant_id(self, tenant_id: TenantId) -> List[Invitation]:
        """Get all invitations for a tenant."""
        invitation_models = self._session.query(InvitationModel).filter(
            InvitationModel.tenant_id == str(tenant_id)
        ).all()
        return [InvitationMapper.to_entity(model) for model in invitation_models if model]
    
    async def get_pending_by_email(self, email: EmailAddress) -> List[Invitation]:
        """Get all pending invitations for an email."""
        from .models import InvitationStatusEnum
        invitation_models = self._session.query(InvitationModel).filter(
            and_(
                InvitationModel.email == str(email),
                InvitationModel.status == InvitationStatusEnum.PENDING
            )
        ).all()
        return [InvitationMapper.to_entity(model) for model in invitation_models if model]
    
    async def update(self, invitation: Invitation) -> Invitation:
        """Update existing invitation."""
        invitation_model = self._session.query(InvitationModel).filter(
            InvitationModel.id == str(invitation.id)
        ).first()
        
        if not invitation_model:
            raise ValueError(f"Invitation {invitation.id} not found")
        
        # Update fields
        invitation_model.status = InvitationMapper._domain_to_db_status(invitation.status)
        invitation_model.accepted_at = invitation.accepted_at
        invitation_model.updated_at = invitation.updated_at
        
        return InvitationMapper.to_entity(invitation_model)
    
    async def delete(self, invitation_id: InvitationId) -> bool:
        """Delete invitation by ID."""
        deleted = self._session.query(InvitationModel).filter(
            InvitationModel.id == str(invitation_id)
        ).delete()
        return deleted > 0


class SqlAlchemySessionRepository(SessionRepository):
    """SQLAlchemy implementation of SessionRepository."""
    
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def create(self, session_entity: Session) -> Session:
        """Create a new session."""
        session_model = SessionMapper.to_model(session_entity)
        self._session.add(session_model)
        self._session.flush()  # Get the ID without committing
        return SessionMapper.to_entity(session_model)
    
    async def get_by_id(self, session_id: SessionId) -> Optional[Session]:
        """Get session by ID."""
        session_model = self._session.query(SessionModel).filter(
            SessionModel.id == str(session_id)
        ).first()
        return SessionMapper.to_entity(session_model) if session_model else None
    
    async def get_by_token_jti(self, token_jti: str) -> Optional[Session]:
        """Get session by JWT token ID."""
        session_model = self._session.query(SessionModel).filter(
            SessionModel.token_jti == token_jti
        ).first()
        return SessionMapper.to_entity(session_model) if session_model else None
    
    async def get_active_sessions_by_user(self, user_id: UserId) -> List[Session]:
        """Get all active sessions for a user."""
        from .models import SessionStatusEnum
        session_models = self._session.query(SessionModel).filter(
            and_(
                SessionModel.user_id == str(user_id),
                SessionModel.status == SessionStatusEnum.ACTIVE,
                SessionModel.expires_at > datetime.now()
            )
        ).all()
        return [SessionMapper.to_entity(model) for model in session_models]
    
    async def update(self, session_entity: Session) -> Session:
        """Update existing session."""
        session_model = self._session.query(SessionModel).filter(
            SessionModel.id == str(session_entity.id)
        ).first()
        
        if not session_model:
            raise ValueError(f"Session {session_entity.id} not found")
        
        # Update fields
        session_model.status = SessionMapper._domain_to_db_status(session_entity.status)
        session_model.last_activity = session_entity.last_activity
        session_model.expires_at = session_entity.expires_at
        session_model.updated_at = session_entity.updated_at
        
        return SessionMapper.to_entity(session_model)
    
    async def delete(self, session_id: SessionId) -> bool:
        """Delete session by ID."""
        deleted = self._session.query(SessionModel).filter(
            SessionModel.id == str(session_id)
        ).delete()
        return deleted > 0
    
    async def invalidate_user_sessions(self, user_id: UserId) -> int:
        """Invalidate all sessions for a user. Returns count of invalidated sessions."""
        from .models import SessionStatusEnum
        updated = self._session.query(SessionModel).filter(
            and_(
                SessionModel.user_id == str(user_id),
                SessionModel.status == SessionStatusEnum.ACTIVE
            )
        ).update({
            'status': SessionStatusEnum.INVALIDATED,
            'updated_at': datetime.now()
        })
        return updated
    
    async def cleanup_expired_sessions(self, cutoff_time: Optional[datetime] = None) -> int:
        """Clean up expired sessions. Returns count of cleaned sessions."""
        from .models import SessionStatusEnum
        
        if cutoff_time is None:
            cutoff_time = datetime.now()
        
        # Mark expired sessions as EXPIRED
        updated = self._session.query(SessionModel).filter(
            and_(
                SessionModel.status == SessionStatusEnum.ACTIVE,
                SessionModel.expires_at <= cutoff_time
            )
        ).update({
            'status': SessionStatusEnum.EXPIRED,
            'updated_at': datetime.now()
        })
        return updated
