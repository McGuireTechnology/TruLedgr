import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "TruLedgr API is running"
    assert data["version"] == "1.0.0"

def test_health_endpoint():
    """Test the detailed health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "All systems operational"
    assert data["version"] == "1.0.0"

def test_mobile_config_endpoint():
    """Test the mobile configuration endpoint"""
    response = client.get("/api/v1/mobile/config")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert "min_app_version" in data
    assert "features" in data
    assert "biometric_auth" in data["features"]

def test_user_registration():
    """Test user registration endpoint"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] == True

def test_user_login():
    """Test user login endpoint"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user():
    """Test get current user endpoint (with mock auth)"""
    # This would normally require a valid JWT token
    # For now, we'll test the endpoint structure
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer mock_token"})
    # This will return a mock response from our current implementation
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "is_active" in data

def test_openapi_docs():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_openapi_json():
    """Test OpenAPI JSON schema"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "TruLedgr API"
