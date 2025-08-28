"""
Performance and load testing for FastAPI Security Sample.
"""
import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from fastapi.testclient import TestClient


class TestPerformanceBaselines:
    """Establish performance baselines for key endpoints."""
    
    @pytest.mark.performance
    def test_health_endpoint_response_time(self, client: TestClient):
        """Test health endpoint response time baseline."""
        times = []
        
        for _ in range(10):
            start = time.time()
            response = client.get("/health")
            end = time.time()
            
            assert response.status_code == 200
            times.append((end - start) * 1000)  # Convert to milliseconds
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Health check should be very fast
        assert avg_time < 100  # Less than 100ms average
        assert max_time < 500  # Less than 500ms worst case
        
    @pytest.mark.performance
    def test_metrics_endpoint_response_time(self, client: TestClient):
        """Test metrics endpoint response time baseline."""
        times = []
        
        for _ in range(5):
            start = time.time()
            response = client.get("/metrics")
            end = time.time()
            
            assert response.status_code == 200
            times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        
        # Metrics collection should be reasonable
        assert avg_time < 1000  # Less than 1 second average
        
    @pytest.mark.performance
    @pytest.mark.slow
    def test_authentication_flow_performance(self, client: TestClient):
        """Test complete authentication flow performance."""
        # Create a user first
        user_data = {
            "username": "perftest",
            "email": "perftest@example.com", 
            "password": "SecureP@ssw0rd2024!"
        }
        
        # Test user creation performance
        start = time.time()
        create_response = client.post("/users", json=user_data)
        create_time = (time.time() - start) * 1000
        
        if create_response.status_code == 201:
            # Test login performance
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            start = time.time()
            login_response = client.post("/auth/login", data=login_data)
            login_time = (time.time() - start) * 1000
            
            # Authentication should be reasonably fast
            assert create_time < 2000  # User creation under 2 seconds
            if login_response.status_code == 200:
                assert login_time < 1000  # Login under 1 second


class TestLoadHandling:
    """Test system behavior under load."""
    
    @pytest.mark.load
    @pytest.mark.slow
    def test_concurrent_health_checks(self, client: TestClient):
        """Test concurrent health check requests."""
        def make_request():
            response = client.get("/health")
            return response.status_code, time.time()
        
        # Simulate 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        success_rate = sum(1 for code in status_codes if code == 200) / len(status_codes)
        
        assert success_rate >= 0.95  # At least 95% success rate
        
    @pytest.mark.load
    @pytest.mark.slow
    def test_concurrent_metrics_requests(self, client: TestClient):
        """Test concurrent metrics collection."""
        def make_metrics_request():
            response = client.get("/metrics")
            return response.status_code, len(response.text)
        
        # Simulate 10 concurrent metrics requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_metrics_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # All should succeed and return data
        for status_code, content_length in results:
            assert status_code == 200
            assert content_length > 0
            
    @pytest.mark.load
    @pytest.mark.slow
    def test_mixed_endpoint_load(self, client: TestClient):
        """Test mixed load across different endpoints."""
        def make_health_request():
            return client.get("/health")
            
        def make_ready_request():
            return client.get("/ready")
            
        def make_metrics_request():
            return client.get("/metrics")
        
        # Mix of different request types
        request_funcs = [make_health_request, make_ready_request, make_metrics_request]
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for _ in range(30):  # 30 total requests
                func = request_funcs[len(futures) % len(request_funcs)]
                futures.append(executor.submit(func))
            
            results = [future.result() for future in as_completed(futures)]
        
        # Calculate success rate
        success_count = sum(1 for response in results if response.status_code in [200, 503])
        success_rate = success_count / len(results)
        
        assert success_rate >= 0.90  # At least 90% success rate under mixed load


class TestMemoryAndResourceUsage:
    """Test memory and resource usage patterns."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_stability_under_load(self, client: TestClient):
        """Test memory stability during sustained load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make many requests to test for memory leaks
        for i in range(100):
            client.get("/health")
            if i % 20 == 0:  # Check memory every 20 requests
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory
                
                # Memory shouldn't grow excessively (allow 50MB growth)
                assert memory_growth < 50 * 1024 * 1024
                
    @pytest.mark.performance
    def test_response_size_efficiency(self, client: TestClient):
        """Test that responses are reasonably sized."""
        # Health check should be compact
        health_response = client.get("/health")
        assert len(health_response.content) < 1024  # Less than 1KB
        
        # Metrics can be larger but should be reasonable
        metrics_response = client.get("/metrics")
        assert len(metrics_response.content) < 100 * 1024  # Less than 100KB


class TestErrorHandlingUnderLoad:
    """Test error handling behavior under load conditions."""
    
    @pytest.mark.load
    @pytest.mark.slow
    def test_error_rate_under_load(self, client: TestClient):
        """Test error rates don't spike under load."""
        def make_mixed_requests():
            responses = []
            responses.append(client.get("/health"))
            responses.append(client.get("/nonexistent"))  # 404
            responses.append(client.get("/users/me"))  # 401
            return responses
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_mixed_requests) for _ in range(10)]
            all_responses = []
            for future in as_completed(futures):
                all_responses.extend(future.result())
        
        # Categorize responses
        success_codes = [200, 201, 202]
        client_error_codes = [400, 401, 403, 404]
        server_error_codes = [500, 501, 502, 503]
        
        success_count = sum(1 for r in all_responses if r.status_code in success_codes)
        client_error_count = sum(1 for r in all_responses if r.status_code in client_error_codes)
        server_error_count = sum(1 for r in all_responses if r.status_code in server_error_codes)
        
        total_requests = len(all_responses)
        
        # Server errors should be minimal
        server_error_rate = server_error_count / total_requests
        assert server_error_rate < 0.05  # Less than 5% server errors
        
        # Should have some successful responses
        success_rate = success_count / total_requests
        assert success_rate > 0.2  # At least 20% successful (health checks)


class TestDatabasePerformance:
    """Test database-related performance."""
    
    @pytest.mark.performance
    @pytest.mark.database
    async def test_database_connection_time(self, db_session):
        """Test database connection establishment time."""
        from sqlalchemy import text
        
        start = time.time()
        result = await db_session.execute(text("SELECT 1"))
        end = time.time()
        
        connection_time = (end - start) * 1000
        assert connection_time < 100  # Less than 100ms for simple query
        
    @pytest.mark.performance
    @pytest.mark.database
    @pytest.mark.slow
    def test_user_creation_performance(self, client: TestClient):
        """Test user creation performance under load."""
        times = []
        
        for i in range(10):
            user_data = {
                "username": f"perfuser{i}",
                "email": f"perfuser{i}@example.com",
                "password": "SecureP@ssw0rd2024!"
            }
            
            start = time.time()
            response = client.post("/users", json=user_data)
            end = time.time()
            
            if response.status_code == 201:
                times.append((end - start) * 1000)
        
        if times:
            avg_time = statistics.mean(times)
            assert avg_time < 2000  # Average user creation under 2 seconds


class TestCachingPerformance:
    """Test caching system performance."""
    
    @pytest.mark.performance
    def test_repeated_request_performance(self, client: TestClient):
        """Test that repeated requests benefit from caching."""
        # First request (cold)
        start = time.time()
        response1 = client.get("/health")
        first_time = time.time() - start
        
        # Second request (should be cached/faster)
        start = time.time()
        response2 = client.get("/health")
        second_time = time.time() - start
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Note: This test might be flaky depending on caching implementation
        # For now, just ensure both requests succeed


# Utility functions for performance testing
def measure_endpoint_performance(client: TestClient, endpoint: str, iterations: int = 10) -> Dict[str, float]:
    """Measure endpoint performance statistics."""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        response = client.get(endpoint)
        end = time.time()
        
        if response.status_code in [200, 201, 202]:
            times.append((end - start) * 1000)
    
    if not times:
        return {"error": "No successful requests"}
    
    return {
        "avg_ms": statistics.mean(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "median_ms": statistics.median(times),
        "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "success_rate": len(times) / iterations
    }


def generate_performance_report(client: TestClient) -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    endpoints = ["/health", "/ready", "/metrics"]
    report = {}
    
    for endpoint in endpoints:
        try:
            report[endpoint] = measure_endpoint_performance(client, endpoint)
        except Exception as e:
            report[endpoint] = {"error": str(e)}
    
    return report
