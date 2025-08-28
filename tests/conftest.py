"""
Test configuration and fixtures for the FastAPI Security Sample application.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi_security_sample.main import app
from fastapi_security_sample.db import get_db, Base
from fastapi_security_sample.users.models import User, Role, Permission
from fastapi_security_sample.users.utils import get_password_hash
from fastapi_security_sample.users.auth.auth import create_access_token


# Test database URL (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test async engine  
async_engine = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingAsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a clean database for each test."""
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestingAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
    
    # Drop all tables after test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecureP@ssw0rd2024!"
    }


@pytest.fixture
def admin_user_data():
    """Admin user data for testing."""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminP@ssw0rd2024!"
    }


@pytest.fixture
async def created_user(db_session, sample_user_data):
    """Create a user in the database for testing."""
    user = User(
        id="01234567-89ab-cdef-0123-456789abcdef",
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        hashed_password=get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session, admin_user_data):
    """Create an admin user in the database for testing."""
    # Create admin role
    admin_role = Role(
        id="admin",
        name="Administrator",
        description="System administrator with full access"
    )
    db_session.add(admin_role)
    db_session.commit()
    
    # Create admin user
    user = User(
        id="01234567-89ab-cdef-0123-456789abcde0",
        username=admin_user_data["username"],
        email=admin_user_data["email"],
        hashed_password=get_password_hash(admin_user_data["password"]),
        role_id="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(created_user):
    """Generate a JWT token for the test user."""
    return create_access_token(data={"sub": created_user.username, "user_id": created_user.id})


@pytest.fixture
def admin_token(admin_user):
    """Generate a JWT token for the admin user."""
    return create_access_token(data={"sub": admin_user.username, "user_id": admin_user.id})


@pytest.fixture
def auth_headers(user_token):
    """Create authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Create authorization headers for admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_role_data():
    """Sample role data for testing."""
    return {
        "role_id": "test_role",
        "name": "Test Role",
        "description": "A role for testing purposes"
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission data for testing."""
    return {
        "permission_id": "test_permission",
        "name": "Test Permission",
        "resource": "test_resource",
        "action": "read",
        "description": "A permission for testing purposes"
    }


@pytest.fixture
async def created_role(db_session, sample_role_data):
    """Create a role in the database for testing."""
    role = Role(
        id=sample_role_data["role_id"],
        name=sample_role_data["name"],
        description=sample_role_data["description"]
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
async def created_permission(db_session, sample_permission_data):
    """Create a permission in the database for testing."""
    permission = Permission(
        id=sample_permission_data["permission_id"],
        name=sample_permission_data["name"],
        resource=sample_permission_data["resource"],
        action=sample_permission_data["action"],
        description=sample_permission_data["description"]
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)
    return permission
