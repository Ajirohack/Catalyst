"""Database models for Catalyst backend.

This module defines the database models for future database integration.
Currently using in-memory storage, but designed for easy migration to SQLAlchemy.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class AnalysisType(str, Enum):
    """Analysis type enumeration."""
    COMPREHENSIVE = "comprehensive"
    SENTIMENT = "sentiment"
    KEYWORDS = "keywords"
    SUMMARY = "summary"
    WHISPER = "whisper"


class MessagePlatform(str, Enum):
    """Message platform enumeration."""
    DISCORD = "discord"
    SLACK = "slack"
    TEAMS = "teams"
    ZOOM = "zoom"
    GENERIC = "generic"


# Future SQLAlchemy models (commented out for now)
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    goals = Column(JSON)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata = Column(JSON)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False)
    sentiment_data = Column(JSON)
    keywords = Column(JSON)
    summary = Column(Text)
    participants = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON)
    
    # Relationships
    project = relationship("Project", back_populates="analyses")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    sender = Column(String(100), nullable=False)
    platform = Column(SQLEnum(MessagePlatform), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False, index=True)
    analysis_result = Column(JSON)
    metadata = Column(JSON)
    
    # Relationships
    project = relationship("Project", back_populates="messages")


class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSON)
"""


# Current in-memory model classes (for compatibility)
class DatabaseProject:
    """In-memory project model for current implementation."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str] = None,
        goals: Optional[List[str]] = None,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.goals = goals or []
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "goals": self.goals,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }


class DatabaseAnalysis:
    """In-memory analysis model for current implementation."""
    
    def __init__(
        self,
        id: str,
        project_id: Optional[str],
        content: str,
        analysis_type: str,
        sentiment_data: Optional[Dict[str, Any]] = None,
        keywords: Optional[List[Dict[str, Any]]] = None,
        summary: Optional[str] = None,
        participants: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.project_id = project_id
        self.content = content
        self.analysis_type = analysis_type
        self.sentiment_data = sentiment_data or {}
        self.keywords = keywords or []
        self.summary = summary
        self.participants = participants or []
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "content": self.content,
            "analysis_type": self.analysis_type,
            "sentiment_data": self.sentiment_data,
            "keywords": self.keywords,
            "summary": self.summary,
            "participants": self.participants,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata
        }


class DatabaseMessage:
    """In-memory message model for current implementation."""
    
    def __init__(
        self,
        id: str,
        project_id: Optional[str],
        content: str,
        sender: str,
        platform: str,
        timestamp: Optional[datetime] = None,
        processed: bool = False,
        analysis_result: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.project_id = project_id
        self.content = content
        self.sender = sender
        self.platform = platform
        self.timestamp = timestamp or datetime.now()
        self.processed = processed
        self.analysis_result = analysis_result or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "content": self.content,
            "sender": self.sender,
            "platform": self.platform,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "processed": self.processed,
            "analysis_result": self.analysis_result,
            "metadata": self.metadata
        }