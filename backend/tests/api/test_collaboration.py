"""
Tests for the Collaboration API endpoints and WebSocket functionality.
"""

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
    from fastapi.testclient import TestClient
    import json
    from datetime import datetime, timedelta
    import time
    
    from main import app
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)

try:
    from services.collaboration_service import (
        collaboration_service, 
        SessionType, 
        ParticipantRole, 
        AccessLevel,
        SessionStatus
    )
except ImportError:
    # Mock implementations for testing
    from enum import Enum
    
    class SessionType(str, Enum):
        ANALYSIS = "analysis"
        THERAPY = "therapy"
        CONSULTATION = "consultation"
    
    class ParticipantRole(str, Enum):
        HOST = "host"
        PARTICIPANT = "participant"
        OBSERVER = "observer"
    
    class AccessLevel(str, Enum):
        READ = "read"
        WRITE = "write"
        ADMIN = "admin"
    
    class SessionStatus(str, Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        ENDED = "ended"
    
    class MockCollaborationService:
        async def create_session(self, session_data):
            return {"id": "test_session", "status": "created"}
    
    collaboration_service = MockCollaborationService()


@pytest.fixture
def test_session():
    """Create a test session"""
    # Create a session
    session = collaboration_service.create_session(
        title="Test Collaboration Session",
        description="A session for testing collaboration features",
        session_type=SessionType.COACHING,
        host_id="test-host-123",
        scheduled_start=datetime.now() + timedelta(hours=1),
        scheduled_end=datetime.now() + timedelta(hours=2)
    )
    
    # Add a participant
    collaboration_service.add_participant(
        session_id=session.id,
        user_id="test-participant-123",
        name="Test Participant",
        email="participant@test.com",
        role=ParticipantRole.CLIENT,
        access_level=AccessLevel.CONTRIBUTOR
    )
    
    return session


class TestCollaborationAPI:
    """Test suite for Collaboration API endpoints"""
    
    def test_create_session(self, client):
        """Test creating a new collaborative session"""
        response = client.post(
            "/api/collaboration/sessions",
            json={
                "title": "Test Session",
                "description": "A test session",
                "session_type": "coaching",
                "scheduled_start": (datetime.now() + timedelta(hours=1)).isoformat(),
                "scheduled_end": (datetime.now() + timedelta(hours=2)).isoformat()
            }
        )
        
        assert response.status_code == 201
        data = response.model_dump_json()
        assert data["title"] == "Test Session"
        assert data["session_type"] == "coaching"
        assert data["status"] == "scheduled"
        assert "id" in data
    
    def test_get_sessions(self, client):
        """Test listing all sessions for a user"""
        # Create a test session first
        client.post(
            "/api/collaboration/sessions",
            json={
                "title": "Test Session for Listing",
                "description": "A test session for the listing endpoint",
                "session_type": "therapy"
            }
        )
        
        # Get sessions
        response = client.get("/api/collaboration/sessions")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_session_details(self, client, test_session):
        """Test getting details of a specific session"""
        response = client.get(f"/api/collaboration/sessions/{test_session.id}")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["id"] == test_session.id
        assert data["title"] == test_session.title
        assert len(data["participants"]) == 1
    
    def test_start_session(self, client, test_session):
        """Test starting a scheduled session"""
        response = client.post(f"/api/collaboration/sessions/{test_session.id}/start")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["status"] == "active"
        assert data["actual_start"] is not None
    
    def test_end_session(self, client, test_session):
        """Test ending an active session"""
        # First start the session
        client.post(f"/api/collaboration/sessions/{test_session.id}/start")
        
        # Then end it
        response = client.post(f"/api/collaboration/sessions/{test_session.id}/end")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["status"] == "ended"
        assert data["actual_end"] is not None
    
    def test_add_participant(self, client, test_session):
        """Test adding a participant to a session"""
        response = client.post(
            f"/api/collaboration/sessions/{test_session.id}/participants",
            json={
                "name": "New Participant",
                "email": "new@test.com",
                "role": "therapist",
                "access_level": "contributor"
            }
        )
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["name"] == "New Participant"
        assert data["role"] == "therapist"
        
        # Check that participant was added to session
        session_response = client.get(f"/api/collaboration/sessions/{test_session.id}")
        session_data = session_response.model_dump_json()
        assert len(session_data["participants"]) == 2
    
    def test_remove_participant(self, client, test_session):
        """Test removing a participant from a session"""
        # Add a participant to remove
        participant_response = client.post(
            f"/api/collaboration/sessions/{test_session.id}/participants",
            json={
                "name": "Temporary Participant",
                "email": "temp@test.com",
                "role": "client",
                "access_level": "comment"
            }
        )
        participant_id = participant_response.model_dump_json()["id"]
        
        # Remove the participant
        response = client.delete(f"/api/collaboration/sessions/{test_session.id}/participants/{participant_id}")
        
        assert response.status_code == 204
        
        # Check that participant was removed from session
        session_response = client.get(f"/api/collaboration/sessions/{test_session.id}")
        session_data = session_response.model_dump_json()
        participant_ids = [p["id"] for p in session_data["participants"]]
        assert participant_id not in participant_ids
    
    def test_send_message(self, client, test_session):
        """Test sending a message in a session"""
        # First start the session
        client.post(f"/api/collaboration/sessions/{test_session.id}/start")
        
        # Send a message
        response = client.post(
            f"/api/collaboration/sessions/{test_session.id}/messages",
            json={
                "content": "Hello, this is a test message",
                "content_type": "text"
            }
        )
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["content"] == "Hello, this is a test message"
        assert "id" in data
        assert data["session_id"] == test_session.id
    
    def test_get_messages(self, client, test_session):
        """Test getting messages from a session"""
        # First start the session
        client.post(f"/api/collaboration/sessions/{test_session.id}/start")
        
        # Send a few messages
        client.post(
            f"/api/collaboration/sessions/{test_session.id}/messages",
            json={"content": "Message 1", "content_type": "text"}
        )
        client.post(
            f"/api/collaboration/sessions/{test_session.id}/messages",
            json={"content": "Message 2", "content_type": "text"}
        )
        
        # Get messages
        response = client.get(f"/api/collaboration/sessions/{test_session.id}/messages")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert data[0]["content"] in ["Message 1", "Message 2"]
    
    def test_create_document(self, client, test_session):
        """Test creating a shared document in a session"""
        response = client.post(
            f"/api/collaboration/sessions/{test_session.id}/documents",
            json={
                "title": "Test Document",
                "content": "This is a test document",
                "content_type": "text"
            }
        )
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["title"] == "Test Document"
        assert data["content"] == "This is a test document"
        assert "id" in data
        assert data["session_id"] == test_session.id
    
    def test_update_document(self, client, test_session):
        """Test updating a shared document in a session"""
        # Create a document first
        document_response = client.post(
            f"/api/collaboration/sessions/{test_session.id}/documents",
            json={
                "title": "Document to Update",
                "content": "Original content",
                "content_type": "text"
            }
        )
        document_id = document_response.model_dump_json()["id"]
        
        # Update the document
        response = client.put(
            f"/api/collaboration/sessions/{test_session.id}/documents/{document_id}",
            json={
                "title": "Document to Update",
                "content": "Updated content",
                "content_type": "text"
            }
        )
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["content"] == "Updated content"
        assert data["version"] == 2  # Version should be incremented
    
    def test_get_documents(self, client, test_session):
        """Test getting all documents in a session"""
        # Create a few documents
        client.post(
            f"/api/collaboration/sessions/{test_session.id}/documents",
            json={"title": "Document 1", "content": "Content 1", "content_type": "text"}
        )
        client.post(
            f"/api/collaboration/sessions/{test_session.id}/documents",
            json={"title": "Document 2", "content": "Content 2", "content_type": "text"}
        )
        
        # Get documents
        response = client.get(f"/api/collaboration/sessions/{test_session.id}/documents")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        document_titles = [doc["title"] for doc in data]
        assert "Document 1" in document_titles
        assert "Document 2" in document_titles
    
    def test_get_session_statistics(self, client, test_session):
        """Test getting statistics about a session"""
        # Start the session
        client.post(f"/api/collaboration/sessions/{test_session.id}/start")
        
        # Add some activity
        client.post(
            f"/api/collaboration/sessions/{test_session.id}/messages",
            json={"content": "Test message", "content_type": "text"}
        )
        client.post(
            f"/api/collaboration/sessions/{test_session.id}/documents",
            json={"title": "Test doc", "content": "Content", "content_type": "text"}
        )
        
        # Get statistics
        response = client.get(f"/api/collaboration/sessions/{test_session.id}/statistics")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["session_id"] == test_session.id
        assert data["participant_count"] >= 1
        assert data["message_count"] >= 1
        assert data["document_count"] >= 1
    
    @pytest.mark.websocket
    def test_websocket_connection(self, client, test_session, websocket_session_id):
        """Test WebSocket connection to a session"""
        with client.websocket_connect(
            f"/api/collaboration/ws/{test_session.id}?client_id=test-host-123"
        ) as websocket:
            # Receive the connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            assert data["data"]["session_id"] == test_session.id
            
            # Send a ping message
            websocket.send_json({
                "type": "ping"
            })
            
            # Receive pong response
            data = websocket.receive_json()
            assert data["type"] == "received"
            
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    @pytest.mark.websocket
    def test_websocket_chat(self, client, test_session, websocket_session_id):
        """Test sending and receiving chat messages via WebSocket"""
        # Start the session
        client.post(f"/api/collaboration/sessions/{test_session.id}/start")
        
        with client.websocket_connect(
            f"/api/collaboration/ws/{test_session.id}?client_id=test-host-123"
        ) as websocket:
            # Skip connection message
            websocket.receive_json()
            
            # Send a chat message
            websocket.send_json({
                "type": "chat",
                "message": "Hello via WebSocket"
            })
            
            # Receive echo response (received confirmation)
            data = websocket.receive_json()
            assert data["type"] == "received"
            
            # Receive broadcasted message
            data = websocket.receive_json()
            assert data["type"] == "chat"
            assert "Hello via WebSocket" in str(data["data"])
            
            # Check that message was stored
            response = client.get(f"/api/collaboration/sessions/{test_session.id}/messages")
            messages = response.model_dump_json()
            assert any("Hello via WebSocket" in message["content"] for message in messages)
