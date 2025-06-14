import pytest
import asyncio
from fastapi.testclient import TestClient
import json
import sys
import os
from io import BytesIO
import time
from unittest.mock import patch, AsyncMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)

class TestIntegrationWorkflows:
    """Test suite for integration workflows across multiple endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        # Clear any existing test data
        from routers.projects import projects_db
        from routers.analysis import analysis_history, active_sessions
        projects_db.clear()
        analysis_history.clear()
        active_sessions.clear()
        
        # Sample data for integration tests
        self.sample_project = {
            "name": "Integration Test Project",
            "description": "A project for testing integration workflows",
            "project_type": "romantic",
            "participants": ["Alice", "Bob"],
            "goals": ["Improve communication", "Spend more quality time"],
            "settings": {"notifications": True, "privacy_level": "high"}
        }
        
        self.conversation_text = "Alice: I feel like we don't talk enough. Bob: I agree, we should make more time for each other."
    
    def test_complete_project_lifecycle(self):
        """Test complete project lifecycle from creation to analysis"""
        # 1. Create a new project
        create_response = client.post("/api/projects/", json=self.sample_project)
        assert create_response.status_code == 201
        project_data = create_response.json()
        project_id = project_data["id"]
        
        # 2. Verify project was created
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == self.sample_project["name"]
        
        # 3. Add a goal to the project
        goal_response = client.post(f"/api/projects/{project_id}/goals", 
                                   json={"goal": "Practice active listening"})
        assert goal_response.status_code == 200
        
        # 4. Upload conversation data
        file_data = BytesIO(self.conversation_text.encode())
        files = {"file": ("conversation.txt", file_data, "text/plain")}
        upload_data = {
            "project_id": project_id,
            "metadata": json.dumps({"source": "integration_test", "participants": ["Alice", "Bob"]})
        }
        upload_response = client.post("/api/analysis/upload", files=files, data=upload_data)
        assert upload_response.status_code == 200
        
        # 5. Analyze the conversation
        analysis_data = {
            "text": self.conversation_text,
            "project_id": project_id,
            "analysis_type": "sentiment"
        }
        analysis_response = client.post("/api/analysis/analyze", json=analysis_data)
        assert analysis_response.status_code == 200
        analysis_result = analysis_response.json()
        
        # 6. Get analysis history
        history_response = client.get(f"/api/analysis/history/{project_id}")
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data["analyses"]) > 0
        
        # 7. Get project statistics
        stats_response = client.get(f"/api/projects/{project_id}/stats")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["total_goals"] == 3  # Original 2 + 1 added
        
        # 8. Update project status
        status_response = client.patch(f"/api/projects/{project_id}/status", 
                                     json={"status": "completed"})
        assert status_response.status_code == 200
        
        # 9. Verify final project state
        final_response = client.get(f"/api/projects/{project_id}")
        assert final_response.status_code == 200
        final_data = final_response.json()
        assert final_data["status"] == "completed"
        assert len(final_data["goals"]) == 3
    
    def test_multi_project_analysis_workflow(self):
        """Test workflow with multiple projects and cross-project analysis"""
        project_ids = []
        
        # Create multiple projects
        for i in range(3):
            project = self.sample_project.copy()
            project["name"] = f"Project {i+1}"
            project["description"] = f"Description for project {i+1}"
            
            response = client.post("/api/projects/", json=project)
            assert response.status_code == 201
            project_ids.append(response.json()["id"])
        
        # Analyze conversations for each project
        for i, project_id in enumerate(project_ids):
            analysis_data = {
                "text": f"Conversation {i+1}: {self.conversation_text}",
                "project_id": project_id,
                "analysis_type": "sentiment"
            }
            response = client.post("/api/analysis/analyze", json=analysis_data)
            assert response.status_code == 200
        
        # Verify each project has analysis history
        for project_id in project_ids:
            history_response = client.get(f"/api/analysis/history/{project_id}")
            assert history_response.status_code == 200
            assert len(history_response.json()["analyses"]) > 0
        
        # List all projects and verify they exist
        list_response = client.get("/api/projects/")
        assert list_response.status_code == 200
        projects = list_response.json()
        assert len(projects) == 3
    
    def test_websocket_integration_workflow(self):
        """Test WebSocket integration with project analysis"""
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
        
            # Create a project first
            create_response = client.post("/api/projects/", json=self.sample_project)
            project_id = create_response.json()["id"]
            
            session_id = f"integration-session-{project_id}"
            
            # Test WebSocket connection and messaging
            with client.websocket_connect(f"/api/analysis/whisper/{session_id}") as websocket:
                # Receive connection confirmation
                connection_msg = websocket.receive_json()
                assert connection_msg["type"] == "connection"
                assert connection_msg["session_id"] == session_id
                
                # Send a message for analysis
                message = {
                    "type": "message",
                    "content": self.conversation_text,
                    "project_id": project_id,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
                websocket.send_json(message)
                
                # Receive suggestion
                suggestion = websocket.receive_json()
                assert suggestion["type"] == "suggestion"
                assert "content" in suggestion
                
                # Test status request
                websocket.send_json({"type": "status"})
                status_response = websocket.receive_json()
                assert status_response["type"] == "status"
                assert status_response["session_id"] == session_id
            
            # Verify session was tracked
            sessions_response = client.get("/api/analysis/whisper/sessions")
            assert sessions_response.status_code == 200
    
    def test_error_recovery_workflow(self):
        """Test error recovery across different endpoints"""
        # Try to get non-existent project
        response = client.get("/api/projects/nonexistent")
        assert response.status_code == 404
        
        # Try to analyze for non-existent project
        analysis_data = {
            "text": self.conversation_text,
            "project_id": "nonexistent",
            "analysis_type": "sentiment"
        }
        response = client.post("/api/analysis/analyze", json=analysis_data)
        # Should still work as analysis doesn't validate project existence
        assert response.status_code == 200
        
        # Try to get history for non-existent project
        response = client.get("/api/analysis/history/nonexistent")
        # Analysis history endpoint returns empty list for non-existent projects
        assert response.status_code == 200
        
        # Create a valid project after errors
        response = client.post("/api/projects/", json=self.sample_project)
        assert response.status_code == 201
        
        # Verify system is still functional
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_concurrent_operations_workflow(self):
        """Test concurrent operations across endpoints"""
        import threading
        import time
        
        results = {"projects": [], "analyses": [], "errors": []}
        
        def create_project_and_analyze(index):
            try:
                # Create project
                project = self.sample_project.copy()
                project["name"] = f"Concurrent Project {index}"
                
                response = client.post("/api/projects/", json=project)
                if response.status_code == 201:
                    project_id = response.json()["id"]
                    results["projects"].append(project_id)
                    
                    # Analyze conversation
                    analysis_data = {
                        "text": f"Concurrent analysis {index}: {self.conversation_text}",
                        "project_id": project_id,
                        "analysis_type": "sentiment"
                    }
                    analysis_response = client.post("/api/analysis/analyze", json=analysis_data)
                    if analysis_response.status_code == 200:
                        results["analyses"].append(analysis_response.json()["analysis_id"])
                else:
                    results["errors"].append(f"Project creation failed for {index}")
            except Exception as e:
                results["errors"].append(str(e))
        
        # Create multiple threads for concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_project_and_analyze, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results["projects"]) == 5
        assert len(results["analyses"]) == 5
        assert len(results["errors"]) == 0
        
        # Verify all projects exist
        list_response = client.get("/api/projects/")
        assert len(list_response.json()) == 5
    
    def test_data_consistency_workflow(self):
        """Test data consistency across operations"""
        # Create project
        response = client.post("/api/projects/", json=self.sample_project)
        project_id = response.json()["id"]
        
        # Perform multiple analyses
        analysis_ids = []
        for i in range(3):
            analysis_data = {
                "text": f"Analysis {i}: {self.conversation_text}",
                "project_id": project_id,
                "analysis_type": "sentiment"
            }
            response = client.post("/api/analysis/analyze", json=analysis_data)
            analysis_ids.append(response.json()["analysis_id"])
        
        # Update project multiple times
        for i in range(3):
            update_data = {
                "name": f"Updated Project {i}",
                "description": f"Updated description {i}"
            }
            response = client.put(f"/api/projects/{project_id}", json=update_data)
            assert response.status_code == 200
        
        # Verify final state consistency
        project_response = client.get(f"/api/projects/{project_id}")
        project_data = project_response.json()
        assert project_data["name"] == "Updated Project 2"
        
        history_response = client.get(f"/api/analysis/history/{project_id}")
        history_data = history_response.json()
        assert len(history_data["analyses"]) == 3
        
        stats_response = client.get(f"/api/projects/{project_id}/stats")
        stats_data = stats_response.json()
        assert stats_data["total_goals"] == len(self.sample_project["goals"])
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        import time
        
        start_time = time.time()
        
        # Create multiple projects rapidly
        for i in range(10):
            project = self.sample_project.copy()
            project["name"] = f"Load Test Project {i}"
            response = client.post("/api/projects/", json=project)
            assert response.status_code == 201
        
        # Perform multiple analyses
        for i in range(10):
            analysis_data = {
                "text": f"Load test analysis {i}: {self.conversation_text}",
                "project_id": f"load-test-{i}",
                "analysis_type": "sentiment"
            }
            response = client.post("/api/analysis/analyze", json=analysis_data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert total_time < 10.0  # 10 seconds for 20 operations
        
        # Verify system health after load
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__])