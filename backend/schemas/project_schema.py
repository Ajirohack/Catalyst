from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ProjectRole(str, Enum):
    """Project role enumeration"""
    BOYFRIEND = "boyfriend"
    GIRLFRIEND = "girlfriend"
    HUSBAND = "husband"
    WIFE = "wife"
    PARTNER = "partner"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    OTHER = "other"

class Platform(str, Enum):
    """Communication platform enumeration"""
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"
    DISCORD = "discord"
    SLACK = "slack"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    SMS = "sms"
    EMAIL = "email"
    OTHER = "other"

class GoalBase(BaseModel):
    """Base goal model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_date: Optional[datetime] = None
    priority: int = Field(default=1, ge=1, le=5)  # 1 = low, 5 = high

class Goal(GoalBase):
    """Goal model with ID and timestamps"""
    id: str
    completed: bool = False
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ProjectBase(BaseModel):
    """Base project model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    project_type: Optional[str] = Field(None)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()

class ProjectCreate(ProjectBase):
    """Project creation model"""
    participants: Optional[List[str]] = Field(default_factory=list)
    goals: Optional[List[str]] = Field(default_factory=list)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProjectUpdate(BaseModel):
    """Project update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    role: Optional[ProjectRole] = None
    platform: Optional[Platform] = None
    partner_name: Optional[str] = Field(None, max_length=100)
    status: Optional[ProjectStatus] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip() if v else v

class Project(ProjectBase):
    """Complete project model"""
    id: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    participants: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    analysis_count: int = 0
    milestone_count: int = 0
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProjectStats(BaseModel):
    """Project statistics model"""
    total_goals: int
    completed_goals: int
    pending_goals: int
    completion_rate: float = Field(..., ge=0.0, le=100.0)
    days_active: int
    last_activity: Optional[datetime] = None

class ProjectListResponse(BaseModel):
    """Project list response model"""
    projects: List[Project]
    total: int
    page: int
    per_page: int
    total_pages: int

# Analysis related schemas
class MessageData(BaseModel):
    """Message data model for analysis"""
    content: str
    sender: str
    timestamp: datetime
    platform: Optional[Platform] = None
    message_type: Optional[str] = "text"  # text, image, file, etc.

class ConversationData(BaseModel):
    """Conversation data model"""
    project_id: str
    messages: List[MessageData]
    participants: List[str]
    context: Optional[Dict[str, Any]] = {}

class AnalysisType(str, Enum):
    """Analysis type enumeration"""
    SENTIMENT = "sentiment"
    COMMUNICATION_PATTERNS = "communication_patterns"
    RELATIONSHIP_DYNAMICS = "relationship_dynamics"
    FULL = "full"

class AnalysisRequest(BaseModel):
    """Analysis request model"""
    text: str = Field(..., min_length=1)
    analysis_type: AnalysisType = AnalysisType.SENTIMENT
    include_recommendations: bool = False
    project_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class SentimentAnalysis(BaseModel):
    """Sentiment analysis result"""
    polarity: float = Field(..., ge=-1.0, le=1.0)
    subjectivity: float = Field(..., ge=0.0, le=1.0)
    classification: str  # positive, negative, neutral
    confidence: float = Field(..., ge=0.0, le=1.0)

class CommunicationPattern(BaseModel):
    """Communication pattern analysis"""
    message_frequency: Dict[str, int]
    response_time_avg: float
    conversation_balance: float
    engagement_level: str  # high, medium, low
    dominant_topics: List[str]

class RelationshipDynamics(BaseModel):
    """Relationship dynamics analysis"""
    emotional_tone: str
    conflict_indicators: List[str]
    positive_indicators: List[str]
    intimacy_level: str  # high, medium, low
    communication_health: float = Field(..., ge=0.0, le=10.0)

class AnalysisResult(BaseModel):
    """Complete analysis result"""
    id: str
    project_id: Optional[str] = None
    analysis_type: AnalysisType
    sentiment: Optional[SentimentAnalysis] = None
    communication_patterns: Optional[CommunicationPattern] = None
    relationship_dynamics: Optional[RelationshipDynamics] = None
    insights: List[str] = []
    recommendations: List[str] = []
    created_at: datetime
    processing_time: float  # in seconds

class WhisperMessage(BaseModel):
    """Whisper message model for WebSocket"""
    type: str  # message, ping, status_request
    content: Optional[str] = None
    sender: Optional[str] = None
    platform: Optional[str] = None
    project_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    timestamp: Optional[datetime] = None

class WhisperResponse(BaseModel):
    """Whisper response model"""
    type: str  # suggestion, pong, status, error
    content: str
    confidence: Optional[float] = None
    category: Optional[str] = None
    timestamp: datetime

class AnalysisHistoryResponse(BaseModel):
    """Analysis history response model"""
    analyses: List[AnalysisResult]
    total: int
    page: int
    per_page: int
    total_pages: int

# WebSocket management schemas
class WebSocketSession(BaseModel):
    """WebSocket session model"""
    session_id: str
    project_id: Optional[str] = None
    connected_at: datetime
    last_activity: datetime
    user_agent: Optional[str] = None

class WebSocketBroadcast(BaseModel):
    """WebSocket broadcast message model"""
    message: str
    target_sessions: Optional[List[str]] = None  # If None, broadcast to all
    message_type: str = "broadcast"

# Error response schemas
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SuccessResponse(BaseModel):
    """Success response model"""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Health check schemas
class HealthCheck(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    uptime: Optional[float] = None

class APIStatus(BaseModel):
    """API status response model"""
    api_name: str = "Catalyst API"
    version: str = "1.0.0"
    status: str = "operational"
    endpoints: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)