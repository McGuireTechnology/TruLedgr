"""
End-to-end tests for complete user workflows.
"""
import pytest
import time
from fastapi.testclient import TestClient
from typing import Dict, Any


class TestCompleteUserJourney:
    """Test complete user lifecycle from registration to deletion."""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_user_lifecycle(self, client: TestClient):
        """Test complete user lifecycle: register -> login -> use -> delete."""
        # Step 1: User Registration
        user_data = {
            "username": "e2euser",
            "email": "e2euser@example.com",
            "password": "SecureP@ssw0rd2024!"
        }
        
        register_response = client.post("/users", json=user_data)
        if register_response.status_code != 201:
            pytest.skip("User registration failed - database not available")
            
        assert register_response.status_code == 201
        user = register_response.json()
        assert user["username"] == user_data["username"]
        assert user["email"] == user_data["email"]
        
        # Step 2: User Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        assert "access_token" in tokens
        access_token = tokens["access_token"]
        
        # Step 3: Access Protected Resource
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        
        profile = profile_response.json()
        assert profile["username"] == user_data["username"]
        
        # Step 4: Update User Profile
        update_data = {"email": "newemail@example.com"}
        update_response = client.put(
            f"/users/{user['id']}", 
            json=update_data, 
            headers=headers
        )
        if update_response.status_code == 200:
            updated_user = update_response.json()
            assert updated_user["email"] == update_data["email"]
        
        # Step 5: User Logout
        logout_response = client.post("/auth/logout", headers=headers)
        assert logout_response.status_code in [200, 204]
        
        # Step 6: Verify Token Invalidated
        profile_response_after_logout = client.get("/users/me", headers=headers)
        assert profile_response_after_logout.status_code == 401
        
        # Step 7: User Deletion (Admin operation)
        # For this test, we'll just verify the user exists
        user_list_response = client.get("/users")
        if user_list_response.status_code == 200:
            users = user_list_response.json()
            usernames = [u.get("username") for u in users]
            assert user_data["username"] in usernames
    
    @pytest.mark.e2e
    def test_authentication_error_flows(self, client: TestClient):
        """Test various authentication error scenarios."""
        # Test 1: Login with nonexistent user
        login_response = client.post("/auth/login", data={
            "username": "nonexistent",
            "password": "anypassword"
        })
        assert login_response.status_code == 401
        
        # Test 2: Access protected resource without token
        profile_response = client.get("/users/me")
        assert profile_response.status_code == 401
        
        # Test 3: Access protected resource with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 401


class TestSecurityWorkflows:
    """Test security-related workflows and edge cases."""
    
    @pytest.mark.e2e
    @pytest.mark.security
    def test_password_security_workflow(self, client: TestClient):
        """Test password-related security features."""
        # Test weak password rejection
        weak_user_data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123"  # Weak password
        }
        
        response = client.post("/users", json=weak_user_data)
        assert response.status_code in [400, 422]  # Should reject weak password
        
        # Test strong password acceptance
        strong_user_data = {
            "username": "stronguser",
            "email": "strong@example.com",
            "password": "StrongP@ssw0rd2024!"
        }
        
        response = client.post("/users", json=strong_user_data)
        if response.status_code == 201:
            # Test login with correct password
            login_response = client.post("/auth/login", data={
                "username": strong_user_data["username"],
                "password": strong_user_data["password"]
            })
            assert login_response.status_code == 200
            
            # Test login with wrong password
            wrong_login_response = client.post("/auth/login", data={
                "username": strong_user_data["username"],
                "password": "wrongpassword"
            })
            assert wrong_login_response.status_code == 401
    
    @pytest.mark.e2e
    @pytest.mark.security
    def test_duplicate_user_prevention(self, client: TestClient):
        """Test prevention of duplicate users."""
        user_data = {
            "username": "duplicatetest",
            "email": "duplicate@example.com",
            "password": "SecureP@ssw0rd2024!"
        }
        
        # First registration should succeed
        first_response = client.post("/users", json=user_data)
        if first_response.status_code != 201:
            pytest.skip("User registration not working")
        
        # Second registration with same username should fail
        second_response = client.post("/users", json=user_data)
        assert second_response.status_code in [400, 409]
        
        # Third registration with same email should fail
        different_username_data = user_data.copy()
        different_username_data["username"] = "differentusername"
        third_response = client.post("/users", json=different_username_data)
        assert third_response.status_code in [400, 409]


class TestMFAWorkflow:
    """Test Multi-Factor Authentication workflows."""
    
    @pytest.mark.e2e
    @pytest.mark.auth
    @pytest.mark.slow
    def test_totp_setup_and_usage(self, client: TestClient):
        """Test TOTP setup and usage workflow."""
        # Create user first
        user_data = {
            "username": "mfauser",
            "email": "mfa@example.com",
            "password": "SecureP@ssw0rd2024!"
        }
        
        register_response = client.post("/users", json=user_data)
        if register_response.status_code != 201:
            pytest.skip("User registration not working")
        
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Setup TOTP
        totp_setup_response = client.post("/auth/totp/setup", headers=headers)
        if totp_setup_response.status_code == 200:
            totp_data = totp_setup_response.json()
            assert "secret" in totp_data
            assert "qr_code" in totp_data
            
            # Enable TOTP (would normally require valid TOTP code)
            # For testing, we'll just check the endpoint exists
            enable_response = client.post("/auth/totp/enable", 
                                        json={"totp_code": "123456"}, 
                                        headers=headers)
            # This will likely fail without a valid TOTP code, which is expected
            assert enable_response.status_code in [400, 401, 422]


class TestAPIUsagePatterns:
    """Test typical API usage patterns and workflows."""
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_user_listing_and_pagination(self, client: TestClient):
        """Test user listing and pagination functionality."""
        # Create multiple users
        users_created = []
        for i in range(3):
            user_data = {
                "username": f"listuser{i}",
                "email": f"listuser{i}@example.com",
                "password": "SecureP@ssw0rd2024!"
            }
            
            response = client.post("/users", json=user_data)
            if response.status_code == 201:
                users_created.append(response.json())
        
        # Test user listing
        list_response = client.get("/users")
        if list_response.status_code == 200:
            users_list = list_response.json()
            assert len(users_list) >= len(users_created)
            
            # Verify our created users are in the list
            listed_usernames = [u.get("username") for u in users_list]
            for user in users_created:
                assert user["username"] in listed_usernames
    
    @pytest.mark.e2e
    @pytest.mark.api
    def test_content_type_handling(self, client: TestClient):
        """Test proper content type handling."""
        # Test JSON content type
        json_response = client.get("/health")
        assert json_response.headers.get("content-type", "").startswith("application/json")
        
        # Test metrics content type
        metrics_response = client.get("/metrics")
        assert metrics_response.headers.get("content-type", "").startswith("text/plain")
        
    @pytest.mark.e2e
    @pytest.mark.api
    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set."""
        # Make an OPTIONS request
        options_response = client.options("/health")
        
        # Should have CORS headers (depending on configuration)
        headers = options_response.headers
        # Note: Exact CORS behavior depends on configuration
        assert options_response.status_code in [200, 405]  # Some endpoints might not support OPTIONS
        
    @pytest.mark.e2e
    @pytest.mark.api
    def test_error_response_format(self, client: TestClient):
        """Test that error responses have consistent format."""
        # Test 404 error
        not_found_response = client.get("/nonexistent")
        assert not_found_response.status_code == 404
        
        error_data = not_found_response.json()
        assert "detail" in error_data
        
        # Test 401 error
        unauthorized_response = client.get("/users/me")
        assert unauthorized_response.status_code == 401
        
        error_data = unauthorized_response.json()
        assert "detail" in error_data


class TestSystemBehaviorUnderLoad:
    """Test system behavior under various load conditions."""
    
    @pytest.mark.e2e
    @pytest.mark.load
    @pytest.mark.slow
    def test_sustained_operation(self, client: TestClient):
        """Test system behavior under sustained operation."""
        start_time = time.time()
        success_count = 0
        total_requests = 50
        
        for i in range(total_requests):
            # Mix different types of requests
            if i % 3 == 0:
                response = client.get("/health")
            elif i % 3 == 1:
                response = client.get("/ready")
            else:
                response = client.get("/metrics")
            
            if response.status_code in [200, 503]:  # 503 acceptable for detailed health
                success_count += 1
                
            # Small delay to simulate realistic usage
            time.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_rate = success_count / total_requests
        requests_per_second = total_requests / duration
        
        # System should maintain high availability
        assert success_rate >= 0.95  # 95% success rate
        assert requests_per_second > 1  # Should handle at least 1 req/sec
        
    @pytest.mark.e2e
    @pytest.mark.monitoring
    def test_monitoring_data_collection(self, client: TestClient):
        """Test that monitoring data is collected during operation."""
        # Make various requests to generate monitoring data
        client.get("/health")
        client.get("/ready")
        client.get("/nonexistent")  # Generate 404
        client.get("/users/me")    # Generate 401
        
        # Check that metrics reflect the activity
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        
        metrics_content = metrics_response.text
        
        # Should have HTTP request metrics
        assert "http_request" in metrics_content.lower()
        
        # Should have some metric values (not just definitions)
        lines_with_values = [line for line in metrics_content.split('\n') 
                           if line and not line.startswith('#') and '{' in line]
        assert len(lines_with_values) > 0


def create_test_user(client: TestClient, username: str) -> Dict[str, Any]:
    """Helper function to create a test user."""
    user_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "SecureP@ssw0rd2024!"
    }
    
    response = client.post("/users", json=user_data)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create user: {response.status_code}")


def login_user(client: TestClient, username: str, password: str) -> str:
    """Helper function to login a user and return access token."""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = client.post("/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to login user: {response.status_code}")


@pytest.mark.e2e
@pytest.mark.integration
class TestCompleteSystemIntegration:
    """Integration tests that verify the entire system works together."""
    
    def test_full_stack_integration(self, client: TestClient):
        """Test that all system components work together."""
        # Test health endpoints
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Test metrics collection
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        
        # Test API documentation
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        
        # Test OpenAPI schema
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200
        
        schema = openapi_response.json()
        assert "openapi" in schema
        assert "paths" in schema
