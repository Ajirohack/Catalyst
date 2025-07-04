"""Collaboration Router Module

This module provides the API endpoints for real-time collaboration features,
including session management, participant handling, and messaging.
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query, Path, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
import json

try:
    from backend.services.collaboration_service import (
        collaboration_service,
        SessionType,
        ParticipantRole,
        AccessLevel,
        SessionStatus
    )
except ImportError:
    # Fallback implementations if service not available
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
            return {"id": "mock_session", "status": "created"}
        
        async def get_session(self, session_id: str):
            return {"id": session_id, "status": "active"}
        
        async def join_session(self, session_id: str, user_data):
            return {"status": "joined"}
        
        async def leave_session(self, session_id: str, user_id: str):
            return {"status": "left"}
        
        async def get_active_sessions(self):
            return []
        
        async def end_session(self, session_id: str):
            return {"status": "ended"}
    
    collaboration_service = MockCollaborationService()

try:
    from schemas.collaboration_schema import (
        CreateCollaborativeSession, CollaborativeSessionResponse,
        CreateSessionParticipant, SessionParticipantResponse,
        CreateSessionMessage, SessionMessageResponse,
        CreateSessionDocument, SessionDocumentResponse,
        SessionEventResponse, SessionStatisticsResponse,
        SessionType, ParticipantRole, AccessLevel, SessionStatus
    )
except ImportError:
    # Fallback schemas if not available
    from pydantic import BaseModel
    from typing import List, Optional
    
    class CreateCollaborativeSession(BaseModel):
        name: str
        session_type: str
    
    class CollaborativeSessionResponse(BaseModel):
        id: str
        name: str
        status: str
    
    class CreateSessionParticipant(BaseModel):
        user_id: str
        role: str
    
    class SessionParticipantResponse(BaseModel):
        id: str
        user_id: str
        role: str
    
    class CreateSessionMessage(BaseModel):
        content: str
        message_type: str = "text"
    
    class SessionMessageResponse(BaseModel):
        id: str
        content: str
        timestamp: str
    
    class CreateSessionDocument(BaseModel):
        name: str
        content: str
    
    class SessionDocumentResponse(BaseModel):
        id: str
        name: str
        url: str
    
    class SessionEventResponse(BaseModel):
        id: str
        event_type: str
        timestamp: str
    
    class SessionStatisticsResponse(BaseModel):
        total_sessions: int
        active_sessions: int

try:
    from services.collaboration_service import (
        CollaborativeSession, SessionParticipant, 
        SessionMessage, SessionDocument, SessionEvent
    )
except ImportError:
    # Mock classes if service not available
    class CollaborativeSession:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 'mock_session')
            self.name = kwargs.get('name', 'Mock Session')
    
    class SessionParticipant:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 'mock_participant')
    
    class SessionMessage:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 'mock_message')
    
    class SessionDocument:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 'mock_document')
    
    class SessionEvent:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 'mock_event')

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

# Helper function to get user ID (replace with actual auth)
async def get_current_user_id():
    # This is a placeholder - in a real app, this would verify JWT tokens
    # For now, we'll just return a test user ID
    return "test-user-123"

# Helper function to check session access
async def check_session_access(session_id: str, user_id: str):
    session = collaboration_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user is host or participant
    if session.host_id != user_id and not any(p.id == user_id for p in session.participants):
        raise HTTPException(status_code=403, detail="You don't have access to this session")
    
    return session

# Session Management Endpoints
@router.post("/sessions", response_model=CollaborativeSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: CreateCollaborativeSession, 
    user_id: str = Depends(get_current_user_id)
):
    """Create a new collaborative session."""
    try:
        session = collaboration_service.create_session(
            title=session_data.title,
            description=session_data.description,
            session_type=session_data.session_type,
            host_id=user_id,
            scheduled_start=session_data.scheduled_start,
            scheduled_end=session_data.scheduled_end,
            max_participants=session_data.max_participants,
            features_enabled=session_data.features_enabled,
            tags=session_data.tags
        )
        return session
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions", response_model=List[CollaborativeSessionResponse])
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
    status: Optional[SessionStatus] = None,
    session_type: Optional[SessionType] = None
):
    """List all sessions for the current user."""
    try:
        sessions = collaboration_service.get_user_sessions(user_id)
        
        # Apply filters if provided
        if status:
            sessions = [s for s in sessions if s.status == status]
        if session_type:
            sessions = [s for s in sessions if s.session_type == session_type]
            
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get("/sessions/{session_id}", response_model=CollaborativeSessionResponse)
async def get_session_details(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get details of a specific session."""
    try:
        session = await check_session_access(session_id, user_id)
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.post("/sessions/{session_id}/start", response_model=CollaborativeSessionResponse)
async def start_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Start a scheduled session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        # Only host can start session
        if session.host_id != user_id:
            raise HTTPException(status_code=403, detail="Only the host can start the session")
        
        if not collaboration_service.start_session(session_id, user_id):
            raise HTTPException(status_code=400, detail="Failed to start session")
        
        # Get updated session
        updated_session = collaboration_service.get_session(session_id)
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "status_change",
                "data": {
                    "status": "active",
                    "session_id": session_id,
                    "started_by": user_id,
                    "started_at": updated_session.actual_start.isoformat()
                }
            })
        
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/sessions/{session_id}/end", response_model=CollaborativeSessionResponse)
async def end_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """End an active session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        # Only host can end session
        if session.host_id != user_id:
            raise HTTPException(status_code=403, detail="Only the host can end the session")
        
        if not collaboration_service.end_session(session_id, user_id):
            raise HTTPException(status_code=400, detail="Failed to end session")
        
        # Get updated session
        updated_session = collaboration_service.get_session(session_id)
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "status_change",
                "data": {
                    "status": "ended",
                    "session_id": session_id,
                    "ended_by": user_id,
                    "ended_at": updated_session.actual_end.isoformat()
                }
            })
        
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

# Participant Management Endpoints
@router.post("/sessions/{session_id}/participants", response_model=SessionParticipantResponse)
async def add_participant(
    session_id: str,
    participant_data: CreateSessionParticipant,
    user_id: str = Depends(get_current_user_id)
):
    """Add a participant to a session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        # Only host or moderators can add participants
        if session.host_id != user_id and not any(p.id == user_id and p.access_level in [AccessLevel.ADMIN, AccessLevel.MODERATOR] for p in session.participants):
            raise HTTPException(status_code=403, detail="You don't have permission to add participants")
        
        # The participant ID will be provided by the client (email or user ID in the system)
        participant_id = participant_data.email  # Using email as ID for simplicity
        
        participant = collaboration_service.add_participant(
            session_id=session_id,
            user_id=participant_id,
            name=participant_data.name,
            email=participant_data.email,
            role=participant_data.role,
            access_level=participant_data.access_level
        )
        
        if not participant:
            raise HTTPException(status_code=400, detail="Failed to add participant")
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "participant_added",
                "data": {
                    "session_id": session_id,
                    "participant_id": participant_id,
                    "participant_name": participant_data.name,
                    "participant_role": participant_data.role.value,
                    "added_by": user_id
                }
            })
        
        return participant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding participant to session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add participant: {str(e)}")

@router.delete("/sessions/{session_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    session_id: str,
    participant_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Remove a participant from a session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        # Check permissions: host, self-removal, or admin/moderator
        is_host = session.host_id == user_id
        is_self = user_id == participant_id
        is_admin_or_moderator = any(p.id == user_id and p.access_level in [AccessLevel.ADMIN, AccessLevel.MODERATOR] for p in session.participants)
        
        if not (is_host or is_self or is_admin_or_moderator):
            raise HTTPException(status_code=403, detail="You don't have permission to remove this participant")
        
        if not collaboration_service.remove_participant(session_id, participant_id):
            raise HTTPException(status_code=404, detail="Participant not found")
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "participant_removed",
                "data": {
                    "session_id": session_id,
                    "participant_id": participant_id,
                    "removed_by": user_id
                }
            })
        
        return JSONResponse(status_code=204, content={})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing participant {participant_id} from session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove participant: {str(e)}")

# Messaging Endpoints
@router.post("/sessions/{session_id}/messages", response_model=SessionMessageResponse)
async def send_message(
    session_id: str,
    message_data: CreateSessionMessage,
    user_id: str = Depends(get_current_user_id)
):
    """Send a message in a session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        # Check if session is active
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Cannot send messages to inactive sessions")
        
        message = collaboration_service.send_message(
            session_id=session_id,
            sender_id=user_id,
            content=message_data.content,
            content_type=message_data.content_type,
            reply_to=message_data.reply_to,
            attachments=message_data.attachments,
            metadata=message_data.metadata
        )
        
        if not message:
            raise HTTPException(status_code=400, detail="Failed to send message")
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "new_message",
                "data": {
                    "session_id": session_id,
                    "message_id": message.id,
                    "sender_id": user_id,
                    "sender_name": message.sender_name,
                    "content": message.content,
                    "content_type": message.content_type,
                    "timestamp": message.timestamp.isoformat()
                }
            })
        
        return message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message to session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/sessions/{session_id}/messages", response_model=List[SessionMessageResponse])
async def get_messages(
    session_id: str,
    limit: int = Query(50, gt=0, le=100),
    user_id: str = Depends(get_current_user_id)
):
    """Get messages from a session."""
    try:
        await check_session_access(session_id, user_id)
        
        messages = collaboration_service.get_session_messages(
            session_id=session_id,
            limit=limit
        )
        
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

# Document Endpoints
@router.post("/sessions/{session_id}/documents", response_model=SessionDocumentResponse)
async def create_document(
    session_id: str,
    document_data: CreateSessionDocument,
    user_id: str = Depends(get_current_user_id)
):
    """Create a shared document in a session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        document = collaboration_service.create_document(
            session_id=session_id,
            title=document_data.title,
            content=document_data.content,
            content_type=document_data.content_type,
            creator_id=user_id
        )
        
        if not document:
            raise HTTPException(status_code=400, detail="Failed to create document")
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "document_created",
                "data": {
                    "session_id": session_id,
                    "document_id": document.id,
                    "title": document.title,
                    "creator_id": user_id,
                    "created_at": document.created_at.isoformat()
                }
            })
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating document in session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@router.put("/sessions/{session_id}/documents/{document_id}", response_model=SessionDocumentResponse)
async def update_document(
    session_id: str,
    document_id: str,
    document_data: CreateSessionDocument,
    user_id: str = Depends(get_current_user_id)
):
    """Update a shared document in a session."""
    try:
        session = await check_session_access(session_id, user_id)
        
        document = collaboration_service.update_document(
            session_id=session_id,
            document_id=document_id,
            content=document_data.content,
            editor_id=user_id
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Notify connected clients
        if session_id in active_connections:
            await broadcast_to_session(session_id, {
                "type": "document_updated",
                "data": {
                    "session_id": session_id,
                    "document_id": document_id,
                    "editor_id": user_id,
                    "updated_at": document.updated_at.isoformat(),
                    "version": document.version
                }
            })
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id} in session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

@router.get("/sessions/{session_id}/documents", response_model=List[SessionDocumentResponse])
async def get_documents(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get all documents in a session."""
    try:
        await check_session_access(session_id, user_id)
        
        documents = collaboration_service.get_session_documents(session_id)
        
        return documents
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@router.get("/sessions/{session_id}/documents/{document_id}", response_model=SessionDocumentResponse)
async def get_document(
    session_id: str,
    document_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific document from a session."""
    try:
        await check_session_access(session_id, user_id)
        
        document = collaboration_service.get_document(session_id, document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id} from session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

# Statistics Endpoint
@router.get("/sessions/{session_id}/statistics", response_model=SessionStatisticsResponse)
async def get_session_statistics(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get statistics about a session."""
    try:
        await check_session_access(session_id, user_id)
        
        statistics = collaboration_service.get_session_statistics(session_id)
        
        if not statistics:
            raise HTTPException(status_code=404, detail="Session statistics not found")
        
        return statistics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session statistics: {str(e)}")

# WebSocket for real-time collaboration
async def broadcast_to_session(session_id: str, message: Dict[str, Any]):
    """Broadcast a message to all WebSocket connections in a session."""
    if session_id in active_connections:
        for connection in active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    client_id: str = Query(None)
):
    """WebSocket endpoint for real-time collaboration."""
    if not client_id:
        await websocket.close(code=1003, reason="Client ID is required")
        return
    
    # Check if session exists
    session = collaboration_service.get_session(session_id)
    if not session:
        await websocket.close(code=1003, reason="Session not found")
        return
    
    # Check if client is a participant
    is_participant = session.host_id == client_id or any(p.id == client_id for p in session.participants)
    if not is_participant:
        await websocket.close(code=1003, reason="Not a session participant")
        return
    
    await websocket.accept()
    
    # Add to active connections
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)
    
    # Find participant name
    participant_name = "Host" if session.host_id == client_id else next((p.name for p in session.participants if p.id == client_id), "Unknown")
    
    # Notify other participants of connection
    await broadcast_to_session(session_id, {
        "type": "participant_joined",
        "data": {
            "session_id": session_id,
            "participant_id": client_id,
            "participant_name": participant_name,
            "timestamp": datetime.now().isoformat()
        }
    })
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "session_id": session_id,
                "participant_id": client_id,
                "session_status": session.status,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Process messages
        while True:
            data = await websocket.receive_json()
            
            # Process different message types
            if "type" not in data:
                await websocket.send_json({
                    "type": "error",
                    "data": {
                        "message": "Invalid message format: 'type' field is required",
                        "timestamp": datetime.now().isoformat()
                    }
                })
                continue
            
            message_type = data["type"]
            
            # Echo received message for debugging
            await websocket.send_json({
                "type": "received",
                "data": data
            })
            
            # Broadcast message to all participants if needed
            if message_type in ["chat", "status_update", "document_edit"]:
                # Add sender info
                data["sender_id"] = client_id
                data["sender_name"] = participant_name
                data["timestamp"] = datetime.now().isoformat()
                
                await broadcast_to_session(session_id, {
                    "type": message_type,
                    "data": data
                })
            
            # Handle specific message types
            if message_type == "chat":
                # Store in the database via service
                if "message" in data:
                    collaboration_service.send_message(
                        session_id=session_id,
                        sender_id=client_id,
                        content=data["message"],
                        content_type="text"
                    )
            elif message_type == "document_edit":
                # Update document via service
                if "document_id" in data and "content" in data:
                    collaboration_service.update_document(
                        session_id=session_id,
                        document_id=data["document_id"],
                        content=data["content"],
                        editor_id=client_id
                    )
            elif message_type == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "data": {
                        "timestamp": datetime.now().isoformat()
                    }
                })
    
    except WebSocketDisconnect:
        # Remove from active connections
        if session_id in active_connections:
            active_connections[session_id].remove(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]
        
        # Notify other participants of disconnection
        await broadcast_to_session(session_id, {
            "type": "participant_left",
            "data": {
                "session_id": session_id,
                "participant_id": client_id,
                "participant_name": participant_name,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        # Try to close with error message
        try:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
        except:
            pass
