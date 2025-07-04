"""Project schema definitions for Catalyst backend."""
from pydantic import BaseModel, Field, field_validator
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
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
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
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
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
    
    model_config = {
        "from_attributes": True
    }

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
    PATTERN = "pattern"
    COMMUNICATION = "communication"
    RELATIONSHIP = "relationship"
    COMPREHENSIVE = "comprehensive"

class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=1)
    analysis_type: AnalysisType = Field(default=AnalysisType.SENTIMENT)
    project_id: Optional[str] = None
    include_recommendations: bool = Field(default=True)
    context: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    """Result model for text analysis"""
    analysis_id: str
    text: str
    sentiment: Dict[str, Any]
    patterns: Optional[List[Dict[str, Any]]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    processed_at: datetime

class MessageUrgency(str, Enum):
    """Message urgency enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageFrequency(str, Enum):
    """Message frequency enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class WhisperMessage(BaseModel):
    """Request model for whisper coaching"""
    context: str = Field(..., min_length=1)
    conversation: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    project_id: Optional[str] = None
    platform: Optional[str] = None
    urgency: MessageUrgency = Field(default=MessageUrgency.NORMAL)
    frequency: MessageFrequency = Field(default=MessageFrequency.MEDIUM)
    previous_suggestions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class WhisperResponse(BaseModel):
    """Response model for whisper coaching"""
    text: str
    timestamp: datetime
    project_id: Optional[str] = None
    platform: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

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