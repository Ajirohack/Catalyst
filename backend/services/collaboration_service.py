"""
Real-time Collaboration Service for Catalyst

This module provides the backend functionality for real-time collaboration
features including shared coaching sessions, multi-user interactions, and
therapist-client communication.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Set, Union, Callable
from datetime import datetime
import uuid
from enum import Enum
from pydantic import BaseModel, Field

# Setup logging
logger = logging.getLogger(__name__)

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


class SessionAction(str, Enum):
    """Types of actions that can occur within a session."""
    JOIN = "join"
    LEAVE = "leave"
    MESSAGE = "message"
    DOCUMENT_EDIT = "document_edit"
    STATUS_CHANGE = "status_change"
    EXERCISE_ASSIGNED = "exercise_assigned"
    EXERCISE_COMPLETED = "exercise_completed"
    INTERVENTION_SHARED = "intervention_shared"
    SCREEN_SHARE = "screen_share"
    RAISE_HAND = "raise_hand"
    TIMER_START = "timer_start"
    TIMER_STOP = "timer_stop"
    BREAKOUT_CREATE = "breakout_create"
    ANNOTATION = "annotation"


class SessionStatus(str, Enum):
    """Status of a collaborative session."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"


class SessionMessage(BaseModel):
    """A message within a collaborative session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    sender_id: str
    sender_name: str
    sender_role: ParticipantRole
    timestamp: datetime = Field(default_factory=datetime.now)
    content: str
    content_type: str = "text"  # "text", "file", "intervention", "exercise", etc.
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class SessionParticipant(BaseModel):
    """A participant in a collaborative session."""
    id: str
    name: str
    email: str
    role: ParticipantRole
    access_level: AccessLevel
    joined_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    last_active: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}


class SessionDocument(BaseModel):
    """A shared document within a collaborative session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    title: str
    content: str
    content_type: str = "text"  # "text", "markdown", "intervention", "notes", etc.
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    last_edited_by: str
    version: int = 1
    edit_history: List[Dict[str, Any]] = []
    shared_with: List[str] = []  # List of participant IDs
    permissions: Dict[str, AccessLevel] = {}


class CollaborativeSession(BaseModel):
    """A collaborative session between multiple participants."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    session_type: SessionType
    created_at: datetime = Field(default_factory=datetime.now)
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: SessionStatus = SessionStatus.SCHEDULED
    participants: List[SessionParticipant] = []
    host_id: str
    recurring: bool = False
    recurring_pattern: Optional[Dict[str, Any]] = None
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
    metadata: Dict[str, Any] = {}
    tags: List[str] = []


class SessionEvent(BaseModel):
    """An event that occurs within a collaborative session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    event_type: SessionAction
    timestamp: datetime = Field(default_factory=datetime.now)
    actor_id: str
    target_id: Optional[str] = None
    details: Dict[str, Any] = {}


class CollaborationService:
    """
    Service for managing real-time collaboration between users.
    Handles session creation, participant management, and messaging.
    """
    
    def __init__(self):
        """Initialize the collaboration service."""
        self._active_sessions: Dict[str, CollaborativeSession] = {}
        self._session_messages: Dict[str, List[SessionMessage]] = {}
        self._session_documents: Dict[str, Dict[str, SessionDocument]] = {}
        self._session_events: Dict[str, List[SessionEvent]] = {}
        self._session_connections: Dict[str, Set[str]] = {}  # session_id -> set of connection_ids
        self._user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self._event_handlers: Dict[SessionAction, List[Callable]] = {}
        
        # Initialize event handlers for each action type
        for action in SessionAction:
            self._event_handlers[action] = []
    
    def create_session(self, 
                      title: str, 
                      description: str,
                      session_type: SessionType,
                      host_id: str,
                      scheduled_start: Optional[datetime] = None,
                      scheduled_end: Optional[datetime] = None,
                      **kwargs) -> CollaborativeSession:
        """
        Create a new collaborative session.
        
        Args:
            title: Title of the session
            description: Description of the session
            session_type: Type of collaborative session
            host_id: ID of the user hosting the session
            scheduled_start: When the session is scheduled to start
            scheduled_end: When the session is scheduled to end
            **kwargs: Additional session configuration
            
        Returns:
            The created collaborative session
        """
        session = CollaborativeSession(
            title=title,
            description=description,
            session_type=session_type,
            host_id=host_id,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            **kwargs
        )
        
        self._active_sessions[session.id] = session
        self._session_messages[session.id] = []
        self._session_documents[session.id] = {}
        self._session_events[session.id] = []
        self._session_connections[session.id] = set()
        
        # Add host to user sessions
        if host_id not in self._user_sessions:
            self._user_sessions[host_id] = set()
        self._user_sessions[host_id].add(session.id)
        
        logger.info(f"Created new {session_type} session: {session.id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[CollaborativeSession]:
        """
        Get a session by ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session if found, None otherwise
        """
        return self._active_sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[CollaborativeSession]:
        """
        Get all sessions that a user is participating in.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of sessions the user is participating in
        """
        if user_id not in self._user_sessions:
            return []
        
        return [
            self._active_sessions[session_id] 
            for session_id in self._user_sessions[user_id]
            if session_id in self._active_sessions
        ]
    
    def add_participant(self, 
                       session_id: str, 
                       user_id: str,
                       name: str,
                       email: str,
                       role: ParticipantRole,
                       access_level: AccessLevel) -> Optional[SessionParticipant]:
        """
        Add a participant to a session.
        
        Args:
            session_id: The ID of the session
            user_id: The ID of the user to add
            name: The name of the participant
            email: The email of the participant
            role: The role of the participant in the session
            access_level: The access level of the participant
            
        Returns:
            The added participant if successful, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot add participant to non-existent session: {session_id}")
            return None
        
        # Check if user is already a participant
        for participant in session.participants:
            if participant.id == user_id:
                logger.info(f"User {user_id} is already a participant in session {session_id}")
                return participant
        
        # Check if session has reached maximum participants
        if len(session.participants) >= session.max_participants:
            logger.warning(f"Session {session_id} has reached maximum participants")
            return None
        
        # Create new participant
        participant = SessionParticipant(
            id=user_id,
            name=name,
            email=email,
            role=role,
            access_level=access_level
        )
        
        # Add to session
        session.participants.append(participant)
        
        # Add to user sessions
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = set()
        self._user_sessions[user_id].add(session_id)
        
        # Record join event
        self._record_event(
            session_id=session_id,
            event_type=SessionAction.JOIN,
            actor_id=user_id,
            details={"participant_role": role.value, "access_level": access_level.value}
        )
        
        logger.info(f"Added participant {user_id} to session {session_id} with role {role}")
        return participant
    
    def remove_participant(self, session_id: str, user_id: str) -> bool:
        """
        Remove a participant from a session.
        
        Args:
            session_id: The ID of the session
            user_id: The ID of the user to remove
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot remove participant from non-existent session: {session_id}")
            return False
        
        # Find and remove participant
        for i, participant in enumerate(session.participants):
            if participant.id == user_id:
                session.participants.pop(i)
                
                # Remove from user sessions
                if user_id in self._user_sessions:
                    self._user_sessions[user_id].discard(session_id)
                
                # Record leave event
                self._record_event(
                    session_id=session_id,
                    event_type=SessionAction.LEAVE,
                    actor_id=user_id
                )
                
                logger.info(f"Removed participant {user_id} from session {session_id}")
                return True
        
        logger.warning(f"User {user_id} is not a participant in session {session_id}")
        return False
    
    def start_session(self, session_id: str, host_id: str) -> bool:
        """
        Start a scheduled session.
        
        Args:
            session_id: The ID of the session to start
            host_id: The ID of the user starting the session
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot start non-existent session: {session_id}")
            return False
        
        # Verify host is starting the session
        if session.host_id != host_id:
            logger.error(f"Only the host can start session {session_id}")
            return False
        
        # Check current status
        if session.status != SessionStatus.SCHEDULED:
            logger.error(f"Cannot start session {session_id} with status {session.status}")
            return False
        
        # Update session status
        session.status = SessionStatus.ACTIVE
        session.actual_start = datetime.now()
        
        # Record status change event
        self._record_event(
            session_id=session_id,
            event_type=SessionAction.STATUS_CHANGE,
            actor_id=host_id,
            details={"new_status": SessionStatus.ACTIVE.value}
        )
        
        logger.info(f"Started session {session_id}")
        return True
    
    def end_session(self, session_id: str, host_id: str) -> bool:
        """
        End an active session.
        
        Args:
            session_id: The ID of the session to end
            host_id: The ID of the user ending the session
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot end non-existent session: {session_id}")
            return False
        
        # Verify host is ending the session
        if session.host_id != host_id:
            logger.error(f"Only the host can end session {session_id}")
            return False
        
        # Check current status
        if session.status != SessionStatus.ACTIVE and session.status != SessionStatus.PAUSED:
            logger.error(f"Cannot end session {session_id} with status {session.status}")
            return False
        
        # Update session status
        session.status = SessionStatus.ENDED
        session.actual_end = datetime.now()
        
        # Record status change event
        self._record_event(
            session_id=session_id,
            event_type=SessionAction.STATUS_CHANGE,
            actor_id=host_id,
            details={"new_status": SessionStatus.ENDED.value}
        )
        
        logger.info(f"Ended session {session_id}")
        return True
    
    def send_message(self, 
                    session_id: str, 
                    sender_id: str, 
                    content: str,
                    content_type: str = "text",
                    reply_to: Optional[str] = None,
                    attachments: List[Dict[str, Any]] = None,
                    metadata: Dict[str, Any] = None) -> Optional[SessionMessage]:
        """
        Send a message in a session.
        
        Args:
            session_id: The ID of the session
            sender_id: The ID of the message sender
            content: The message content
            content_type: The type of content being sent
            reply_to: Optional ID of message being replied to
            attachments: Optional list of attachments
            metadata: Optional additional metadata
            
        Returns:
            The created message if successful, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot send message to non-existent session: {session_id}")
            return None
        
        # Find sender information
        sender_info = None
        for participant in session.participants:
            if participant.id == sender_id:
                sender_info = participant
                break
        
        if not sender_info:
            logger.error(f"Sender {sender_id} is not a participant in session {session_id}")
            return None
        
        # Create message
        message = SessionMessage(
            session_id=session_id,
            sender_id=sender_id,
            sender_name=sender_info.name,
            sender_role=sender_info.role,
            content=content,
            content_type=content_type,
            reply_to=reply_to,
            attachments=attachments or [],
            metadata=metadata or {}
        )
        
        # Add to session messages
        self._session_messages[session_id].append(message)
        
        # Record message event
        self._record_event(
            session_id=session_id,
            event_type=SessionAction.MESSAGE,
            actor_id=sender_id,
            details={"message_id": message.id, "content_type": content_type}
        )
        
        logger.info(f"Message sent in session {session_id} by {sender_id}")
        return message
    
    def get_session_messages(self, 
                           session_id: str, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           limit: int = 100) -> List[SessionMessage]:
        """
        Get messages from a session, optionally filtered by time.
        
        Args:
            session_id: The ID of the session
            start_time: Optional start time for message filtering
            end_time: Optional end time for message filtering
            limit: Maximum number of messages to return
            
        Returns:
            List of session messages
        """
        if session_id not in self._session_messages:
            return []
        
        messages = self._session_messages[session_id]
        
        # Apply time filters if provided
        if start_time:
            messages = [m for m in messages if m.timestamp >= start_time]
        if end_time:
            messages = [m for m in messages if m.timestamp <= end_time]
        
        # Sort by timestamp (newest first) and apply limit
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return messages[:limit]
    
    def create_document(self,
                       session_id: str,
                       title: str,
                       content: str,
                       content_type: str,
                       creator_id: str) -> Optional[SessionDocument]:
        """
        Create a shared document in a session.
        
        Args:
            session_id: The ID of the session
            title: The document title
            content: The document content
            content_type: The type of content in the document
            creator_id: The ID of the user creating the document
            
        Returns:
            The created document if successful, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot create document in non-existent session: {session_id}")
            return None
        
        # Verify creator is a participant
        creator = None
        for participant in session.participants:
            if participant.id == creator_id:
                creator = participant
                break
        
        if not creator:
            logger.error(f"Creator {creator_id} is not a participant in session {session_id}")
            return None
        
        # Create document
        document = SessionDocument(
            session_id=session_id,
            title=title,
            content=content,
            content_type=content_type,
            created_by=creator_id,
            last_edited_by=creator_id,
            shared_with=[p.id for p in session.participants]
        )
        
        # Add to session documents
        self._session_documents[session_id][document.id] = document
        
        # Record document creation event
        self._record_event(
            session_id=session_id,
            event_type=SessionAction.DOCUMENT_EDIT,
            actor_id=creator_id,
            target_id=document.id,
            details={"action": "create", "title": title, "content_type": content_type}
        )
        
        logger.info(f"Document {document.id} created in session {session_id} by {creator_id}")
        return document
    
    def update_document(self,
                       session_id: str,
                       document_id: str,
                       content: str,
                       editor_id: str) -> Optional[SessionDocument]:
        """
        Update a shared document in a session.
        
        Args:
            session_id: The ID of the session
            document_id: The ID of the document to update
            content: The new document content
            editor_id: The ID of the user editing the document
            
        Returns:
            The updated document if successful, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Cannot update document in non-existent session: {session_id}")
            return None
        
        # Check if document exists
        if session_id not in self._session_documents or document_id not in self._session_documents[session_id]:
            logger.error(f"Document {document_id} does not exist in session {session_id}")
            return None
        
        document = self._session_documents[session_id][document_id]
        
        # Verify editor is a participant with access
        editor = None
        for participant in session.participants:
            if participant.id == editor_id:
                editor = participant
                break
        
        if not editor:
            logger.error(f"Editor {editor_id} is not a participant in session {session_id}")
            return None
        
        if editor_id not in document.shared_with:
            logger.error(f"Editor {editor_id} does not have access to document {document_id}")
            return None
        
        # Save current version to history
        history_entry = {
            "version": document.version,
            "content": document.content,
            "edited_by": document.last_edited_by,
            "timestamp": document.updated_at.isoformat()
        }
        document.edit_history.append(history_entry)
        
        # Update document
        document.content = content
        document.version += 1
        document.last_edited_by = editor_id
        document.updated_at = datetime.now()
        
        # Record document update event
        self._record_event(
            session_id=session_id,
            event_type=SessionAction.DOCUMENT_EDIT,
            actor_id=editor_id,
            target_id=document_id,
            details={"action": "update", "version": document.version}
        )
        
        logger.info(f"Document {document_id} updated in session {session_id} by {editor_id}")
        return document
    
    def get_session_documents(self, session_id: str) -> List[SessionDocument]:
        """
        Get all documents in a session.
        
        Args:
            session_id: The ID of the session
            
        Returns:
            List of session documents
        """
        if session_id not in self._session_documents:
            return []
        
        return list(self._session_documents[session_id].values())
    
    def get_document(self, session_id: str, document_id: str) -> Optional[SessionDocument]:
        """
        Get a specific document from a session.
        
        Args:
            session_id: The ID of the session
            document_id: The ID of the document
            
        Returns:
            The document if found, None otherwise
        """
        if session_id not in self._session_documents or document_id not in self._session_documents[session_id]:
            return None
        
        return self._session_documents[session_id][document_id]
    
    def get_session_events(self,
                         session_id: str,
                         event_types: Optional[List[SessionAction]] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         limit: int = 100) -> List[SessionEvent]:
        """
        Get events from a session, optionally filtered by type and time.
        
        Args:
            session_id: The ID of the session
            event_types: Optional list of event types to include
            start_time: Optional start time for event filtering
            end_time: Optional end time for event filtering
            limit: Maximum number of events to return
            
        Returns:
            List of session events
        """
        if session_id not in self._session_events:
            return []
        
        events = self._session_events[session_id]
        
        # Apply type filter if provided
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        # Apply time filters if provided
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first) and apply limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    def register_event_handler(self, event_type: SessionAction, handler: Callable) -> None:
        """
        Register a handler function for a specific event type.
        
        Args:
            event_type: The type of event to handle
            handler: The handler function to call when the event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type} events")
    
    def _record_event(self,
                     session_id: str,
                     event_type: SessionAction,
                     actor_id: str,
                     target_id: Optional[str] = None,
                     details: Dict[str, Any] = None) -> SessionEvent:
        """
        Record an event in a session.
        
        Args:
            session_id: The ID of the session
            event_type: The type of event
            actor_id: The ID of the user who performed the action
            target_id: Optional ID of the target of the action
            details: Optional additional details about the event
            
        Returns:
            The recorded event
        """
        event = SessionEvent(
            session_id=session_id,
            event_type=event_type,
            actor_id=actor_id,
            target_id=target_id,
            details=details or {}
        )
        
        # Add to session events
        if session_id not in self._session_events:
            self._session_events[session_id] = []
        self._session_events[session_id].append(event)
        
        # Call event handlers
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        
        return event
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics about a session.
        
        Args:
            session_id: The ID of the session
            
        Returns:
            Dictionary of session statistics
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        
        # Count messages by type
        messages = self._session_messages.get(session_id, [])
        message_counts = {}
        for message in messages:
            if message.content_type not in message_counts:
                message_counts[message.content_type] = 0
            message_counts[message.content_type] += 1
        
        # Count events by type
        events = self._session_events.get(session_id, [])
        event_counts = {}
        for event in events:
            if event.event_type not in event_counts:
                event_counts[event.event_type] = 0
            event_counts[event.event_type] += 1
        
        # Calculate participant stats
        participant_count = len(session.participants)
        participant_roles = {}
        for participant in session.participants:
            if participant.role not in participant_roles:
                participant_roles[participant.role] = 0
            participant_roles[participant.role] += 1
        
        # Calculate session duration
        duration = None
        if session.actual_start:
            end_time = session.actual_end or datetime.now()
            duration = (end_time - session.actual_start).total_seconds()
        
        return {
            "session_id": session_id,
            "title": session.title,
            "type": session.session_type,
            "status": session.status,
            "duration_seconds": duration,
            "participant_count": participant_count,
            "participant_roles": participant_roles,
            "message_count": len(messages),
            "message_types": message_counts,
            "document_count": len(self._session_documents.get(session_id, {})),
            "event_count": len(events),
            "event_types": event_counts
        }


# Create singleton instance
collaboration_service = CollaborationService()
