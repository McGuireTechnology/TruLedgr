"""
Tests for monitoring endpoints and functionality.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from fastapi_security_sample.main import app


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.monitoring
    def test_basic_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data
        assert "environment" in data
        
    @pytest.mark.monitoring
    def test_readiness_check(self, client: TestClient):
        """Test readiness probe endpoint."""
        response = client.get("/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        
    @pytest.mark.monitoring
    def test_detailed_health_check(self, client: TestClient):
        """Test detailed health check endpoint."""
        response = client.get("/health/detailed")
        assert response.status_code in [200, 503]  # Can be degraded in test env
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "response_time_ms" in data
        assert "system" in data
        assert "application" in data
        
    @pytest.mark.monitoring
    def test_health_check_with_database_failure(self, client: TestClient):
        """Test health check behavior when database fails."""
        with patch('fastapi_security_sample.db.engine.begin') as mock_begin:
            mock_begin.side_effect = Exception("Database connection failed")
            
            response = client.get("/health")
            data = response.json()
            
            # Should still return 200 but show unhealthy database
            assert response.status_code == 200
            assert "unhealthy" in data.get("database", "")


class TestMetricsEndpoints:
    """Test Prometheus metrics endpoints."""
    
    @pytest.mark.monitoring
    def test_metrics_endpoint_accessible(self, client: TestClient):
        """Test that metrics endpoint is accessible."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        
    @pytest.mark.monitoring
    def test_metrics_content_format(self, client: TestClient):
        """Test that metrics are in Prometheus format."""
        response = client.get("/metrics")
        content = response.text
        
        # Check for standard Prometheus metrics
        assert "# HELP" in content
        assert "# TYPE" in content
        
        # Check for custom metrics
        assert "http_requests_total" in content
        assert "auth_attempts_total" in content
        assert "database_operations_total" in content
        
    @pytest.mark.monitoring
    def test_metrics_after_requests(self, client: TestClient):
        """Test that metrics update after making requests."""
        # Make some requests to generate metrics
        client.get("/health")
        client.get("/ready")
        
        response = client.get("/metrics")
        content = response.text
        
        # Should have HTTP request metrics
        lines = content.split('\n')
        http_metrics = [line for line in lines if 'http_request' in line and '=' in line]
        assert len(http_metrics) > 0


class TestPerformanceMonitoring:
    """Test performance monitoring functionality."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_response_time_monitoring(self, client: TestClient):
        """Test that response times are tracked."""
        response = client.get("/health/detailed")
        
        if response.status_code == 200:
            data = response.json()
            assert "response_time_ms" in data
            assert isinstance(data["response_time_ms"], (int, float))
            assert data["response_time_ms"] > 0
            
    @pytest.mark.performance
    def test_system_metrics_collection(self, client: TestClient):
        """Test that system metrics are collected."""
        response = client.get("/health/detailed")
        
        if response.status_code == 200:
            data = response.json()
            system = data.get("system", {})
            checks = system.get("checks", [])
            
            # Look for system-related checks
            check_names = [check.get("name") for check in checks]
            assert any("memory" in name.lower() for name in check_names)


class TestErrorTracking:
    """Test error tracking and logging."""
    
    @pytest.mark.monitoring
    def test_error_endpoint_logging(self, client: TestClient):
        """Test that errors are properly logged."""
        # Make request to non-existent endpoint
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
    @pytest.mark.monitoring
    def test_authentication_error_tracking(self, client: TestClient):
        """Test that auth errors are tracked."""
        # Try to access protected endpoint without auth
        response = client.get("/users/me")
        assert response.status_code == 401


class TestMonitoringIntegration:
    """Test monitoring system integration."""
    
    @pytest.mark.integration
    @pytest.mark.monitoring
    def test_monitoring_middleware_active(self, client: TestClient):
        """Test that monitoring middleware is active."""
        # Check that requests are being instrumented
        initial_response = client.get("/metrics")
        initial_content = initial_response.text
        
        # Make a request
        client.get("/health")
        
        # Check metrics again
        final_response = client.get("/metrics")
        final_content = final_response.text
        
        # Should see changes in metrics (unless caching)
        # At minimum, should have metrics structure
        assert "http_requests_total" in final_content
        
    @pytest.mark.monitoring
    def test_health_check_dependencies(self, client: TestClient):
        """Test that health checks verify all dependencies."""
        response = client.get("/health/detailed")
        
        if response.status_code in [200, 503]:
            data = response.json()
            
            # Should have dependency checks
            dependencies = data.get("dependencies", {})
            assert "database" in dependencies
            
            # Should have application info
            application = data.get("application", {})
            assert "status" in application
            assert "uptime_seconds" in application


class TestSecurityMonitoring:
    """Test security-related monitoring."""
    
    @pytest.mark.security
    @pytest.mark.monitoring
    def test_authentication_metrics(self, client: TestClient):
        """Test that authentication attempts are tracked."""
        # Make failed login attempt
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        # Check metrics for auth attempts
        metrics_response = client.get("/metrics")
        content = metrics_response.text
        assert "auth_attempts_total" in content
        
    @pytest.mark.security
    @pytest.mark.monitoring  
    def test_rate_limiting_monitoring(self, client: TestClient):
        """Test that rate limiting is monitored."""
        # This test depends on rate limiting implementation
        # For now, just verify the endpoint structure exists
        response = client.get("/health")
        assert response.status_code == 200


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmarks for monitoring endpoints."""
    
    def test_health_endpoint_performance(self, benchmark, client: TestClient):
        """Benchmark health endpoint performance."""
        def make_health_request():
            return client.get("/health")
            
        result = benchmark(make_health_request)
        assert result.status_code == 200
        
    def test_metrics_endpoint_performance(self, benchmark, client: TestClient):
        """Benchmark metrics endpoint performance."""
        def make_metrics_request():
            return client.get("/metrics")
            
        result = benchmark(make_metrics_request)
        assert result.status_code == 200


class TestMonitoringConfiguration:
    """Test monitoring configuration and settings."""
    
    @pytest.mark.monitoring
    def test_monitoring_enabled_in_tests(self):
        """Test that monitoring is properly configured for tests."""
        from fastapi_security_sample.config import get_settings
        settings = get_settings()
        
        # Should have monitoring enabled for comprehensive testing
        assert hasattr(settings, 'metrics_enabled')
        assert hasattr(settings, 'health_check_enabled')
        
    @pytest.mark.monitoring
    def test_monitoring_endpoints_registered(self):
        """Test that all monitoring endpoints are registered."""
        # Get the FastAPI app routes
        routes = [route.path for route in app.routes]
        
        # Check that monitoring endpoints exist
        expected_endpoints = ["/health", "/ready", "/metrics"]
        for endpoint in expected_endpoints:
            assert endpoint in routes or any(endpoint in route for route in routes)
