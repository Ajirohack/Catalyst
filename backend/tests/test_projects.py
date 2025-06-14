import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from models.project import ProjectStatus, ProjectType

client = TestClient(app)

class TestProjectsRouter:
    """Test suite for Projects Router endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        # Clear any existing test data
        from routers.projects import projects_db
        projects_db.clear()
        
        # Sample project data for testing
        self.sample_project = {
            "name": "Test Relationship Project",
            "description": "A test project for relationship improvement",
            "project_type": "romantic",
            "participants": ["Alice", "Bob"],
            "goals": ["Better communication", "More quality time"],
            "settings": {"notifications": True, "privacy_level": "high"}
        }
        
        self.update_project = {
            "name": "Updated Project Name",
            "description": "Updated description",
            "goals": ["Updated goal 1", "Updated goal 2"]
        }
    
    def test_list_projects_empty(self):
        """Test listing projects when database is empty"""
        response = client.get("/api/projects/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_project_success(self):
        """Test successful project creation"""
        response = client.post("/api/projects/", json=self.sample_project)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == self.sample_project["name"]
        assert data["description"] == self.sample_project["description"]
        assert data["project_type"] == self.sample_project["project_type"]
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        return data["id"]  # Return project ID for other tests
    
    def test_create_project_invalid_data(self):
        """Test project creation with invalid data"""
        invalid_project = {"name": ""}  # Missing required fields
        response = client.post("/api/projects/", json=invalid_project)
        assert response.status_code == 422
    
    def test_get_project_success(self):
        """Test getting a specific project"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Then get it
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == self.sample_project["name"]
    
    def test_get_project_not_found(self):
        """Test getting a non-existent project"""
        response = client.get("/api/projects/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_project_success(self):
        """Test updating a project"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Then update it
        response = client.put(f"/api/projects/{project_id}", json=self.update_project)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == self.update_project["name"]
        assert data["description"] == self.update_project["description"]
    
    def test_update_project_not_found(self):
        """Test updating a non-existent project"""
        response = client.put("/api/projects/nonexistent-id", json=self.update_project)
        assert response.status_code == 404
    
    def test_delete_project_success(self):
        """Test deleting a project"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Then delete it
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify it's gone
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404
    
    def test_delete_project_not_found(self):
        """Test deleting a non-existent project"""
        response = client.delete("/api/projects/nonexistent-id")
        assert response.status_code == 404
    
    def test_update_project_status(self):
        """Test updating project status"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Update status to paused
        status_update = {"status": "paused"}
        response = client.patch(f"/api/projects/{project_id}/status", json=status_update)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "paused"
    
    def test_add_project_goal(self):
        """Test adding a goal to a project"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Add a new goal
        new_goal = {"goal": "New test goal"}
        response = client.post(f"/api/projects/{project_id}/goals", json=new_goal)
        assert response.status_code == 200
        
        data = response.json()
        assert "New test goal" in data["goals"]
    
    def test_remove_project_goal(self):
        """Test removing a goal from a project"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Remove the first goal (index 0)
        response = client.delete(f"/api/projects/{project_id}/goals/0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["goals"]) == len(self.sample_project["goals"]) - 1
    
    def test_get_project_stats(self):
        """Test getting project statistics"""
        # First create a project
        create_response = client.post("/api/projects/", json=self.sample_project)
        project_id = create_response.json()["id"]
        
        # Get stats
        response = client.get(f"/api/projects/{project_id}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_goals" in data
        assert "completed_goals" in data
        assert "progress_percentage" in data
        assert "days_active" in data
    
    def test_list_projects_with_filters(self):
        """Test listing projects with various filters"""
        # Create multiple projects
        project1 = self.sample_project.copy()
        project1["name"] = "Project 1"
        project1["project_type"] = "romantic"
        
        project2 = self.sample_project.copy()
        project2["name"] = "Project 2"
        project2["project_type"] = "family"
        
        create_resp1 = client.post("/api/projects/", json=project1)
        print(f"Create project 1 response: {create_resp1.status_code}, {create_resp1.text}")
        create_resp2 = client.post("/api/projects/", json=project2)
        print(f"Create project 2 response: {create_resp2.status_code}, {create_resp2.text}")
        
        # Test filtering by type
        response = client.get("/api/projects/?project_type=romantic")
        print(f"Filter response: {response.status_code}, {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["project_type"] == "romantic"
        
        # Test search by name
        response = client.get("/api/projects/?search=Project 1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Project 1" in data[0]["name"]
    
    def test_list_projects_pagination(self):
        """Test project listing with pagination"""
        # Create multiple projects
        for i in range(5):
            project = self.sample_project.copy()
            project["name"] = f"Project {i}"
            client.post("/api/projects/", json=project)
        
        # Test pagination
        response = client.get("/api/projects/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_projects_health_check(self):
        """Test projects health check endpoint"""
        response = client.get("/api/projects/health/check")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "projects"

if __name__ == "__main__":
    pytest.main([__file__])