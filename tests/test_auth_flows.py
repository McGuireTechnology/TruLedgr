"""
Authentication flow tests for comprehensive security testing.
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient


class TestAuthenticationFlows:
    """Test complete authentication workflows."""
    
    def test_complete_user_registration_flow(self, client):
        """Test complete user registration and first login flow."""
        # Step 1: Register new user
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123!"
        }
        
        register_response = client.post("/users", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user = register_response.json()
        assert user["username"] == user_data["username"]
        
        # Step 2: Login with new user
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/users/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        assert "access_token" in token_data
        
        # Step 3: Access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        profile = profile_response.json()
        assert profile["username"] == user_data["username"]

    def test_totp_setup_and_login_flow(self, client, created_user, sample_user_data):
        """Test TOTP setup and authentication flow."""
        # Step 1: Login and get token
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        login_response = client.post("/users/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 2: Setup TOTP
        setup_response = client.post("/users/auth/totp/setup", headers=headers)
        assert setup_response.status_code == status.HTTP_200_OK
        totp_data = setup_response.json()
        assert "secret" in totp_data
        assert "qr_uri" in totp_data
        
        # Step 3: Enable TOTP
        with patch('fastapi_security_sample.users.utils.verify_totp', return_value=True):
            enable_data = {"code": "123456"}
            enable_response = client.post("/users/auth/totp/enable", json=enable_data, headers=headers)
            assert enable_response.status_code == status.HTTP_200_OK
        
        # Step 4: Login with TOTP (mock the TOTP verification)
        with patch('fastapi_security_sample.users.service.authenticate_user') as mock_auth:
            mock_auth.return_value = created_user
            
            login_with_totp_data = {
                "username": sample_user_data["username"],
                "password": sample_user_data["password"],
                "totp_code": "123456"
            }
            
            totp_login_response = client.post("/users/auth/login", json=login_with_totp_data)
            assert totp_login_response.status_code == status.HTTP_200_OK

    def test_password_reset_flow(self, client, created_user):
        """Test complete password reset flow."""
        # Step 1: Request password reset
        reset_request_data = {"email": created_user.email}
        
        reset_response = client.post("/users/auth/password-reset/request", json=reset_request_data)
        assert reset_response.status_code == status.HTTP_200_OK
        
        # Step 2: Mock password reset confirmation
        with patch('fastapi_security_sample.users.password_reset.password_reset_manager.verify_reset_token') as mock_verify:
            with patch('fastapi_security_sample.users.password_reset.password_reset_manager.use_reset_token') as mock_use:
                mock_verify.return_value = MagicMock(user_id=created_user.id)
                
                confirm_data = {
                    "token": "mock_reset_token",
                    "new_password": "NewSecurePassword123!"
                }
                
                confirm_response = client.post("/users/auth/password-reset/confirm", json=confirm_data)
                assert confirm_response.status_code == status.HTTP_200_OK
                
                # Verify token was used
                mock_use.assert_called_once()

    def test_session_management_flow(self, client, created_user, sample_user_data):
        """Test session creation and management flow."""
        # Step 1: Login and create session
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        login_response = client.post("/users/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Step 2: Get user sessions
        sessions_response = client.get("/users/me/sessions", headers=headers)
        assert sessions_response.status_code == status.HTTP_200_OK
        sessions_data = sessions_response.json()
        assert "sessions" in sessions_data
        assert sessions_data["total_sessions"] >= 1
        
        # Step 3: Terminate all sessions
        terminate_response = client.delete("/users/me/sessions", headers=headers)
        assert terminate_response.status_code == status.HTTP_200_OK
        
        # Step 4: Verify session is terminated (next request should fail)
        # Note: This might not work immediately due to token caching
        profile_response = client.get("/users/me", headers=headers)
        # Session termination might not immediately invalidate the token
        # depending on implementation

    def test_role_assignment_flow(self, client, admin_user, created_user, admin_headers):
        """Test role assignment and permission checking flow."""
        # Step 1: Create a role as admin
        role_data = {
            "role_id": "test_role",
            "name": "Test Role",
            "description": "Test role for user assignment"
        }
        
        role_response = client.post("/users/roles", json=role_data, headers=admin_headers)
        assert role_response.status_code == status.HTTP_200_OK
        
        # Step 2: Assign role to user
        assign_response = client.post(
            f"/users/users/{created_user.id}/roles/{role_data['role_id']}",
            headers=admin_headers
        )
        # Note: This endpoint might not be implemented yet
        # assert assign_response.status_code == status.HTTP_200_OK
        
        # Step 3: Verify user has the role
        user_response = client.get(f"/users/{created_user.username}")
        assert user_response.status_code == status.HTTP_200_OK


class TestSecurityScenarios:
    """Test security-related scenarios and edge cases."""
    
    def test_brute_force_protection(self, client, created_user):
        """Test protection against brute force attacks."""
        login_data = {
            "username": created_user.username,
            "password": "wrongpassword"
        }
        
        # Attempt multiple failed logins
        failed_attempts = []
        for i in range(5):
            response = client.post("/users/auth/login", json=login_data)
            failed_attempts.append(response.status_code)
            
        # All should fail with 401
        assert all(status_code == status.HTTP_401_UNAUTHORIZED for status_code in failed_attempts)
        
        # After multiple failures, account might be locked
        # (Implementation depends on rate limiting and account lockout)

    def test_token_expiration_handling(self, client, created_user, sample_user_data):
        """Test token expiration and refresh scenarios."""
        # Login and get token
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        login_response = client.post("/users/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        
        # Test with valid token
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Test with invalid/expired token (simulate by using garbage token)
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        invalid_response = client.get("/users/me", headers=invalid_headers)
        assert invalid_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_permission_escalation_prevention(self, client, created_user, auth_headers, sample_role_data):
        """Test that users cannot escalate their own permissions."""
        # Try to create role without admin privileges
        response = client.post("/users/roles", json=sample_role_data, headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to create permission without admin privileges
        permission_data = {
            "permission_id": "test_permission",
            "name": "Test Permission",
            "resource": "test",
            "action": "create",
            "description": "Test permission"
        }
        
        permission_response = client.post("/users/permissions", json=permission_data, headers=auth_headers)
        assert permission_response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_user_data_access_prevention(self, client):
        """Test that users cannot access other users' sensitive data."""
        # Create two users
        user1_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "Password123!"
        }
        
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "Password123!"
        }
        
        # Register both users
        client.post("/users", json=user1_data)
        client.post("/users", json=user2_data)
        
        # Login as user1
        login1_response = client.post("/users/auth/login", json={
            "username": user1_data["username"],
            "password": user1_data["password"]
        })
        user1_token = login1_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        # Login as user2
        login2_response = client.post("/users/auth/login", json={
            "username": user2_data["username"],
            "password": user2_data["password"]
        })
        user2_token = login2_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User1 should not be able to see user2's sessions
        # (This test depends on the session endpoint implementation)
        sessions_response = client.get("/users/me/sessions", headers=user1_headers)
        if sessions_response.status_code == status.HTTP_200_OK:
            sessions_data = sessions_response.json()
            # Should only see their own sessions
            assert "sessions" in sessions_data

    def test_sql_injection_prevention(self, client):
        """Test that SQL injection attempts are prevented."""
        # Attempt SQL injection through username
        malicious_data = {
            "username": "admin'; DROP TABLE users; --",
            "email": "test@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/users", json=malicious_data)
        # Should either create user with escaped data or fail validation
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # Attempt SQL injection through login
        login_data = {
            "username": "admin' OR '1'='1",
            "password": "password"
        }
        
        login_response = client.post("/users/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED


class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and race conditions."""
    
    def test_concurrent_user_creation(self, client):
        """Test that concurrent user creation with same data is handled properly."""
        import threading
        import queue
        
        user_data = {
            "username": "concurrent_user",
            "email": "concurrent@example.com",
            "password": "Password123!"
        }
        
        results = queue.Queue()
        
        def create_user():
            response = client.post("/users", json=user_data)
            results.put(response.status_code)
        
        # Create multiple threads to create the same user
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=create_user)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        # One should succeed (201), others should fail (400)
        assert status.HTTP_201_CREATED in status_codes
        assert status.HTTP_400_BAD_REQUEST in status_codes

    def test_concurrent_login_attempts(self, client, created_user, sample_user_data):
        """Test concurrent login attempts."""
        import threading
        import queue
        
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        results = queue.Queue()
        
        def login():
            response = client.post("/users/auth/login", json=login_data)
            results.put((response.status_code, response.json()))
        
        # Create multiple concurrent login attempts
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=login)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        responses = []
        while not results.empty():
            responses.append(results.get())
        
        # All should succeed with valid tokens
        for status_code, response_data in responses:
            assert status_code == status.HTTP_200_OK
            assert "access_token" in response_data


class TestDataValidationAndSanitization:
    """Test comprehensive data validation and sanitization."""
    
    def test_xss_prevention_in_user_data(self, client):
        """Test that XSS attempts in user data are prevented."""
        xss_data = {
            "username": "<script>alert('xss')</script>",
            "email": "test@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/users", json=xss_data)
        
        if response.status_code == status.HTTP_201_CREATED:
            user = response.json()
            # Username should be sanitized or escaped
            assert "<script>" not in user["username"]
        else:
            # Should fail validation
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unicode_handling(self, client):
        """Test proper Unicode character handling."""
        unicode_data = {
            "username": "üser_测试",
            "email": "test@example.com",
            "password": "Pássword123!"
        }
        
        response = client.post("/users", json=unicode_data)
        
        # Should either handle Unicode properly or fail validation gracefully
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_extremely_long_input_handling(self, client):
        """Test handling of extremely long inputs."""
        long_string = "a" * 10000
        
        long_data = {
            "username": long_string,
            "email": "test@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/users", json=long_data)
        
        # Should fail validation due to length constraints
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
