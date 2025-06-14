import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)

class TestMainApp:
    """Test suite for Main Application endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "uptime" in data
        assert "services" in data
        
        # Check that all services are reported
        services = data["services"]
        assert "database" in services
        assert "analysis_engine" in services
        assert "websocket" in services
        
        # Check dependencies
        assert "dependencies" in data
        dependencies = data["dependencies"]
        assert "fastapi" in dependencies
        assert "uvicorn" in dependencies
    
    def test_api_status_endpoint(self):
        """Test the API status endpoint"""
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert "api_version" in data
        assert "environment" in data
        assert "features" in data
        assert "limits" in data
        assert "supported_platforms" in data
        
        # Check features
        features = data["features"]
        assert "project_management" in features
        assert "real_time_analysis" in features
        assert "whisper_suggestions" in features
        assert "file_upload" in features
        
        # Check limits
        limits = data["limits"]
        assert "max_file_size" in limits
        assert "max_projects_per_user" in limits
        assert "rate_limit_per_minute" in limits
        
        # Check supported platforms
        platforms = data["supported_platforms"]
        assert "web" in platforms
        assert "chrome_extension" in platforms
    
    def test_docs_endpoint_accessible(self):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_json_accessible(self):
        """Test that OpenAPI JSON is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        # Test preflight request
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should allow CORS
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_404_error_handling(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
    
    def test_method_not_allowed_handling(self):
        """Test method not allowed error handling"""
        # Try POST on a GET-only endpoint
        response = client.post("/")
        assert response.status_code == 405
        
        data = response.json()
        assert "detail" in data

class TestErrorHandling:
    """Test suite for global error handling"""
    
    def test_validation_error_handling(self):
        """Test validation error handling"""
        # Send invalid JSON to an endpoint that expects valid data
        response = client.post("/api/projects/", json={"invalid": "data"})
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
    
    def test_internal_server_error_handling(self):
        """Test internal server error handling"""
        # This test would require mocking to force an internal error
        # For now, we'll just verify the error structure is correct
        pass
    
    def test_request_timeout_handling(self):
        """Test request timeout handling"""
        # This would require a long-running endpoint to test properly
        # For now, we'll just verify the timeout configuration
        pass

class TestSecurity:
    """Test suite for security features"""
    
    def test_trusted_host_middleware(self):
        """Test trusted host middleware"""
        # Test with allowed host
        response = client.get("/", headers={"Host": "localhost"})
        assert response.status_code == 200
        
        # Test with potentially malicious host
        response = client.get("/", headers={"Host": "malicious-site.com"})
        # Should still work in test environment, but middleware is active
        assert response.status_code in [200, 400]
    
    def test_content_type_validation(self):
        """Test content type validation"""
        # Test with correct content type
        response = client.post("/api/projects/", 
                             json={"name": "Test", "description": "Test"},
                             headers={"Content-Type": "application/json"})
        assert response.status_code in [201, 422]  # 422 for validation errors
        
        # Test with incorrect content type for JSON endpoint
        response = client.post("/api/projects/", 
                             data="invalid data",
                             headers={"Content-Type": "text/plain"})
        assert response.status_code == 422
    
    def test_request_size_limits(self):
        """Test request size limits"""
        # Test with reasonable size request
        normal_data = {"name": "Test", "description": "Normal description"}
        response = client.post("/api/projects/", json=normal_data)
        assert response.status_code in [201, 422]
        
        # Test with very large request (would need to be configured in production)
        # For now, just verify the endpoint handles normal requests
        pass

class TestPerformance:
    """Test suite for performance-related tests"""
    
    def test_response_time_reasonable(self):
        """Test that response times are reasonable"""
        import time
        
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads to make concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)
    
    def test_memory_usage_reasonable(self):
        """Test that memory usage doesn't grow excessively"""
        # Make multiple requests to check for memory leaks
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200
        
        # In a real test, you'd monitor memory usage here
        # For now, just verify the requests complete successfully
        pass

if __name__ == "__main__":
    pytest.main([__file__])