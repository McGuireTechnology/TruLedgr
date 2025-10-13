"""Integration tests for user repository."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.repositories.models import Base, UserModel
from api.repositories.repositories import SqlAlchemyUserRepository
from api.repositories.mappers import UserMapper
from api.entities import User
from api.value_objects import UserId, EmailAddress


@pytest.fixture
def db_session():
    """Create test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.mark.asyncio
async def test_user_repository_create_and_get(db_session):
    """Test creating and retrieving a user."""
    repo = SqlAlchemyUserRepository(db_session)
    
    # Create user entity
    user = User(
        id=UserId("test-123"),
        email=EmailAddress("test@example.com"),
        first_name="Test",
        last_name="User"
    )
    
    # Save via repository
    created_user = await repo.create(user)
    
    # Retrieve via repository
    retrieved_user = await repo.get_by_id(UserId("test-123"))
    
    # Verify
    assert retrieved_user is not None
    assert str(retrieved_user.id) == "test-123"
    assert str(retrieved_user.email) == "test@example.com"
    assert retrieved_user.first_name == "Test"


@pytest.mark.asyncio
async def test_user_repository_get_by_email(db_session):
    """Test retrieving user by email."""
    repo = SqlAlchemyUserRepository(db_session)
    
    # Create user
    user = User(
        id=UserId("test-456"),
        email=EmailAddress("test2@example.com"),
        first_name="Test",
        last_name="User2"
    )
    await repo.create(user)
    
    # Retrieve by email
    found_user = await repo.get_by_email(EmailAddress("test2@example.com"))
    
    # Verify
    assert found_user is not None
    assert str(found_user.id) == "test-456"


# Add more integration tests as needed
