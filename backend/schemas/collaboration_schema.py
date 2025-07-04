"""
Collaboration Schema Module

This module defines the Pydantic models for the real-time collaboration feature,
including session management, participant handling, and messaging.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid

# Enums
class SessionType(str, Enum):
    """Types of collaborative sessions available in the system."""
    COACHING = "coaching"
    THERAPY = "therapy"
    CONSULTATION = "consultation"
    PEER_SUPPORT = "peer_support"
    MEDIATION = "mediation"
    GROUP_THERAPY = "group_therapy"


class ParticipantRole(str, Enum):
    """Roles that participants can have in a collaborative session."""
    COACH = "coach"
    THERAPIST = "therapist"
    CLIENT = "client"
    OBSERVER = "observer"
    MEDIATOR = "mediator"
    PEER = "peer"
    SUPERVISOR = "supervisor"


class AccessLevel(str, Enum):
    """Access levels for session participants."""
    READ_ONLY = "read_only"
    COMMENT = "comment"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    ADMIN = "admin"


class SessionStatus(str, Enum):
    """Status of a collaborative session."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"


# Base models
class SessionParticipantBase(BaseModel):
    """Base model for session participant."""
    name: str
    email: str
    role: ParticipantRole
    access_level: AccessLevel


class SessionDocumentBase(BaseModel):
    """Base model for session document."""
    title: str
    content: str
    content_type: str = "text"  # "text", "markdown", "intervention", "notes", etc.


class CollaborativeSessionBase(BaseModel):
    """Base model for a collaborative session."""
    title: str
    description: str = ""
    session_type: SessionType
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    max_participants: int = 10
    features_enabled: Dict[str, bool] = {
        "chat": True,
        "video": True,
        "screen_sharing": True,
        "document_collaboration": True,
        "intervention_sharing": True,
        "exercises": True,
        "breakout_rooms": False,
        "recording": False
    }
    tags: List[str] = []


class SessionMessageBase(BaseModel):
    """Base model for a session message."""
    content: str
    content_type: str = "text"  # "text", "file", "intervention", "exercise", etc.
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


# Create models (for POST/PUT requests)
class CreateSessionParticipant(SessionParticipantBase):
    """Model for creating a session participant."""
    pass


class CreateSessionDocument(SessionDocumentBase):
    """Model for creating a session document."""
    pass


class CreateCollaborativeSession(CollaborativeSessionBase):
    """Model for creating a collaborative session."""
    pass


class CreateSessionMessage(SessionMessageBase):
    """Model for creating a session message."""
    pass


# Response models (for GET responses)
class SessionParticipantResponse(SessionParticipantBase):
    """Response model for session participant."""
    id: str
    joined_at: datetime
    is_active: bool
    last_active: datetime
    metadata: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class SessionDocumentResponse(SessionDocumentBase):
    """Response model for session document."""
    id: str
    session_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    last_edited_by: str
    version: int
    shared_with: List[str] = []

    model_config = {"from_attributes": True}


class SessionMessageResponse(SessionMessageBase):
    """Response model for session message."""
    id: str
    session_id: str
    sender_id: str
    sender_name: str
    sender_role: ParticipantRole
    timestamp: datetime

    model_config = {"from_attributes": True}


class CollaborativeSessionResponse(CollaborativeSessionBase):
    """Response model for collaborative session."""
    id: str
    created_at: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: SessionStatus
    host_id: str
    recurring: bool = False
    recurring_pattern: Optional[Dict[str, Any]] = None
    participants: List[SessionParticipantResponse] = []
    metadata: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class SessionEventResponse(BaseModel):
    """Response model for session event."""
    id: str
    session_id: str
    event_type: str
    timestamp: datetime
    actor_id: str
    target_id: Optional[str] = None
    details: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class SessionStatisticsResponse(BaseModel):
    """Response model for session statistics."""
    session_id: str
    title: str
    type: str
    status: str
    duration_seconds: Optional[float] = None
    participant_count: int
    participant_roles: Dict[str, int]
    message_count: int
    message_types: Dict[str, int]
    document_count: int
    event_count: int
    event_types: Dict[str, int]

    model_config = {"from_attributes": True}


# WebSocket message models
class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class WebSocketConnectionMessage(WebSocketMessage):
    """Message for WebSocket connection events."""
    type: str = "connection"
    data: Dict[str, Any]


class WebSocketChatMessage(WebSocketMessage):
    """Message for WebSocket chat events."""
    type: str = "chat"
    data: Dict[str, Any]


class WebSocketDocumentMessage(WebSocketMessage):
    """Message for WebSocket document events."""
    type: str = "document"
    data: Dict[str, Any]


class WebSocketParticipantMessage(WebSocketMessage):
    """Message for WebSocket participant events."""
    type: str = "participant"
    data: Dict[str, Any]


class WebSocketStatusMessage(WebSocketMessage):
    """Message for WebSocket status events."""
    type: str = "status"
    data: Dict[str, Any]


class WebSocketErrorMessage(WebSocketMessage):
    """Message for WebSocket error events."""
    type: str = "error"
    data: Dict[str, Any]
