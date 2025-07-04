import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    import pytest
    import asyncio
    import json
    from fastapi.testclient import TestClient
    from fastapi import WebSocket
    import sys
    import os
    from unittest.mock import patch, MagicMock, AsyncMock
    import tempfile
    from io import BytesIO
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)


# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)

class TestAnalysisRouter:
    """Test suite for Analysis Router endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        # Clear any existing test data
        from routers.analysis import analysis_history, active_sessions
        analysis_history.clear()
        active_sessions.clear()
        
        # Sample data for testing
        self.sample_text = "This is a test conversation about improving communication in relationships."
        self.sample_project_id = "test-project-123"
        self.sample_session_id = "test-session-456"
        
        # Sample file content for upload tests
        self.sample_file_content = b"Sample conversation data for testing"
    
    def test_upload_conversation_data_success(self):
        """Test successful conversation data upload"""
        # Create a temporary file-like object
        file_data = BytesIO(self.sample_file_content)
        
        files = {
            "file": ("test_conversation.txt", file_data, "text/plain")
        }
        data = {
            "project_id": self.sample_project_id,
            "metadata": json.dumps({"source": "test", "date": "2024-01-01"})
        }
        
        response = client.post("/api/analysis/upload", files=files, data=data)
        assert response.status_code == 200
        
        result = response.model_dump_json()
        assert result["status"] == "success"
        assert "file_id" in result
        assert result["project_id"] == self.sample_project_id
        assert "processed_at" in result
    
    def test_upload_conversation_data_no_file(self):
        """Test upload without file"""
        data = {"project_id": self.sample_project_id}
        response = client.post("/api/analysis/upload", data=data)
        assert response.status_code == 422
    
    def test_upload_conversation_data_invalid_project(self):
        """Test upload with invalid project ID"""
        file_data = BytesIO(self.sample_file_content)
        files = {"file": ("test.txt", file_data, "text/plain")}
        data = {"project_id": ""}  # Empty project ID
        
        response = client.post("/api/analysis/upload", files=files, data=data)
        assert response.status_code == 422
    
    def test_analyze_text_content_success(self):
        """Test successful text analysis"""
        analysis_data = {
            "text": self.sample_text,
            "project_id": self.sample_project_id,
            "analysis_type": "sentiment"
        }
        
        response = client.post("/api/analysis/analyze", json=analysis_data)
        assert response.status_code == 200
        
        result = response.model_dump_json()
        assert result["status"] == "success"
        assert "analysis_id" in result
        assert "sentiment" in result
        assert "keywords" in result
        assert "suggestions" in result
        assert result["project_id"] == self.sample_project_id
    
    def test_analyze_text_content_empty_text(self):
        """Test analysis with empty text"""
        analysis_data = {
            "text": "",
            "project_id": self.sample_project_id,
            "analysis_type": "sentiment"
        }
        
        response = client.post("/api/analysis/analyze", json=analysis_data)
        assert response.status_code == 422
    
    def test_analyze_text_content_invalid_type(self):
        """Test analysis with invalid analysis type"""
        analysis_data = {
            "text": self.sample_text,
            "project_id": self.sample_project_id,
            "analysis_type": "invalid_type"
        }
        
        response = client.post("/api/analysis/analyze", json=analysis_data)
        assert response.status_code == 422
    
    def test_get_analysis_history_success(self):
        """Test getting analysis history for a project"""
        # First perform an analysis to create history
        analysis_data = {
            "text": self.sample_text,
            "project_id": self.sample_project_id,
            "analysis_type": "sentiment"
        }
        client.post("/api/analysis/analyze", json=analysis_data)
        
        # Then get the history
        response = client.get(f"/api/analysis/history/{self.sample_project_id}")
        assert response.status_code == 200
        
        result = response.model_dump_json()
        assert "analyses" in result
        assert "total_count" in result
        assert "project_id" in result
        assert result["project_id"] == self.sample_project_id
    
    def test_get_analysis_history_with_pagination(self):
        """Test getting analysis history with pagination"""
        # Create multiple analyses
        for i in range(5):
            analysis_data = {
                "text": f"Test text {i}",
                "project_id": self.sample_project_id,
                "analysis_type": "sentiment"
            }
            client.post("/api/analysis/analyze", json=analysis_data)
        
        # Test pagination
        response = client.get(f"/api/analysis/history/{self.sample_project_id}?skip=2&limit=2")
        assert response.status_code == 200
        
        result = response.model_dump_json()
        assert len(result["analyses"]) <= 2
    
    def test_get_analysis_history_not_found(self):
        """Test getting history for non-existent project"""
        response = client.get("/api/analysis/history/nonexistent-project")
        assert response.status_code == 404
    
    def test_get_active_whisper_sessions(self):
        """Test getting active whisper sessions"""
        response = client.get("/api/analysis/whisper/sessions")
        assert response.status_code == 200
        
        result = response.model_dump_json()
        assert "active_sessions" in result
        assert "total_count" in result
        assert isinstance(result["active_sessions"], list)
    
    def test_broadcast_message_success(self):
        """Test broadcasting message to sessions"""
        broadcast_data = {
            "message": "Test broadcast message",
            "session_ids": [self.sample_session_id],
            "message_type": "info"
        }
        
        response = client.post("/api/analysis/whisper/broadcast", json=broadcast_data)
        assert response.status_code == 200
        
        result = response.model_dump_json()
        assert result["status"] == "success"
        assert "sent_to" in result
        assert "failed_to" in result
    
    def test_broadcast_message_empty_sessions(self):
        """Test broadcasting with empty session list"""
        broadcast_data = {
            "message": "Test message",
            "session_ids": [],
            "message_type": "info"
        }
        
        response = client.post("/api/analysis/whisper/broadcast", json=broadcast_data)
        assert response.status_code == 422
    
    def test_analysis_health_check(self):
        """Test analysis health check endpoint"""
        response = client.get("/api/analysis/health/check")
        assert response.status_code == 200
        
        data = response.model_dump_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "analysis"
        assert "active_sessions" in data
        assert "total_analyses" in data

class TestWebSocketWhisper:
    """Test suite for WebSocket whisper functionality"""
    
    @patch('routers.analysis.whisper_service')
    def test_websocket_connection_success(self, mock_whisper):
        """Test successful WebSocket connection"""
        session_id = "test-session-websocket"
        
        with client.websocket_connect(f"/api/analysis/whisper/{session_id}") as websocket:
            # Test connection establishment
            data = websocket.receive_json()
            assert data["type"] == "connection"
            assert data["status"] == "connected"
            assert data["session_id"] == session_id
    
    def test_websocket_message_handling(self):
        """Test WebSocket message handling"""
        with patch('services.whisper_service.WhisperService.process_message', new_callable=AsyncMock) as mock_process:
            # Configure the mock to return expected response
            mock_process.return_value = {
                "suggestions": ["Consider acknowledging your partner's feelings"],
                "urgency_level": "medium",
                "category": "general",
                "confidence": 0.9,
                "context": {
                    "sender": "test",
                    "platform": "test",
                    "project_id": "test"
                }
            }
            
            session_id = "test-session-messages"
            
            with client.websocket_connect(f"/api/analysis/whisper/{session_id}") as websocket:
                # Receive connection message
                connection_data = websocket.receive_json()
                assert connection_data["type"] == "connection"
                assert connection_data["status"] == "connected"
                
                # Send whisper message
                whisper_message = {
                    "type": "message",
                    "data": {
                        "content": "I'm feeling frustrated with my partner",
                        "sender": "user",
                        "platform": "test",
                        "project_id": "test-project"
                    }
                }
                websocket.send_json(whisper_message)
                
                # Receive response
                response = websocket.receive_json()
                assert response["type"] == "suggestion"
                assert "content" in response
                assert "confidence" in response
                assert "urgency_level" in response
                assert "category" in response
    
    def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong mechanism"""
        session_id = "test-session-ping"
        
        with client.websocket_connect(f"/api/analysis/whisper/{session_id}") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send ping
            ping_message = {"type": "ping"}
            websocket.send_json(ping_message)
            
            # Should receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"
    
    def test_websocket_status_request(self):
        """Test WebSocket status request"""
        session_id = "test-session-status"
        
        with client.websocket_connect(f"/api/analysis/whisper/{session_id}") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send status request
            status_message = {"type": "status"}
            websocket.send_json(status_message)
            
            # Should receive status response
            response = websocket.receive_json()
            assert response["type"] == "status"
            assert "session_id" in response
            assert "connected_at" in response
            assert "message_count" in response
    
    def test_websocket_invalid_message_type(self):
        """Test WebSocket with invalid message type"""
        session_id = "test-session-invalid"
        
        with client.websocket_connect(f"/api/analysis/whisper/{session_id}") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send invalid message
            invalid_message = {"type": "invalid_type"}
            websocket.send_json(invalid_message)
            
            # Should receive error response
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "message" in response

if __name__ == "__main__":
    pytest.main([__file__])