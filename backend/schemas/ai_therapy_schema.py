from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ConflictLevel(str, Enum):
    """Conflict level enumeration"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

class EmotionalState(str, Enum):
    """Emotional state enumeration"""
    POSITIVE = "positive"
    SLIGHTLY_POSITIVE = "slightly_positive"
    NEUTRAL = "neutral"
    SLIGHTLY_NEGATIVE = "slightly_negative"
    NEGATIVE = "negative"
    DISTRESSED = "distressed"
    UPSET = "upset"
    UNKNOWN = "unknown"

class ConversationTrend(str, Enum):
    """Conversation trend enumeration"""
    ESCALATING = "escalating"
    DE_ESCALATING = "de_escalating"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"
    ERROR = "error"

class TherapyApproach(str, Enum):
    """Therapy approach enumeration"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    EMOTIONALLY_FOCUSED = "emotionally_focused"
    GOTTMAN_METHOD = "gottman_method"
    SOLUTION_FOCUSED = "solution_focused"
    NARRATIVE_THERAPY = "narrative_therapy"

class InterventionType(str, Enum):
    """Intervention type enumeration"""
    PAUSE_AND_BREATHE = "pause_and_breathe"
    ACTIVE_LISTENING = "active_listening"
    EMOTIONAL_VALIDATION = "emotional_validation"
    THOUGHT_REFRAMING = "thought_reframing"
    EMOTION_SHARING = "emotion_sharing"
    CONFLICT_RESOLUTION = "conflict_resolution"
    EMPATHY_BUILDING = "empathy_building"

class UrgencyLevel(str, Enum):
    """Urgency level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EscalationPattern(BaseModel):
    """Escalation pattern model"""
    message_index: int
    type: str = Field(..., description="Type of escalation pattern (dismissive, aggressive, etc.)")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    timestamp: Optional[datetime] = None

class ConflictPatterns(BaseModel):
    """Conflict patterns analysis model"""
    frequency: float = Field(..., ge=0.0, le=1.0, description="Frequency of conflict indicators (0.0 to 1.0)")
    resolution_rate: float = Field(..., ge=0.0, le=1.0, description="Rate of conflict resolution attempts (0.0 to 1.0)")
    escalation_risk: float = Field(..., ge=0.0, le=1.0, description="Risk of escalation (0.0 to 1.0)")
    escalation_patterns: List[EscalationPattern] = Field(default_factory=list)
    total_conflicts: int = Field(default=0, description="Total number of conflict indicators detected")
    resolution_attempts: int = Field(default=0, description="Number of resolution attempts detected")

class ParticipantEmotionalState(BaseModel):
    """Individual participant emotional state"""
    participant_id: str
    state: EmotionalState
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in emotional state assessment")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score (-1.0 to 1.0)")

class EmotionalStateAnalysis(BaseModel):
    """Emotional state analysis model"""
    overall_state: EmotionalState
    participants: Dict[str, str] = Field(default_factory=dict, description="Participant-specific emotional states")
    volatility: float = Field(..., ge=0.0, le=1.0, description="Emotional volatility (0.0 to 1.0)")
    sentiment_trend: str = Field(default="stable", description="Overall sentiment trend")

class ImmediateRecommendation(BaseModel):
    """Immediate intervention recommendation"""
    type: InterventionType
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    urgency: UrgencyLevel
    duration_minutes: int = Field(..., ge=1, le=60, description="Recommended duration in minutes")
    instructions: Optional[List[str]] = Field(default_factory=list)
    expected_outcome: Optional[str] = None

class ConflictDetectionRequest(BaseModel):
    """Request model for conflict detection"""
    messages: List[Dict[str, Any]] = Field(..., min_items=1, description="List of conversation messages")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context information")
    sensitivity: float = Field(default=0.5, ge=0.0, le=1.0, description="Detection sensitivity (0.0 to 1.0)")
    therapy_approach: TherapyApproach = Field(default=TherapyApproach.COGNITIVE_BEHAVIORAL)
    project_id: Optional[str] = None
    user_id: Optional[str] = None

class ConflictDetectionResponse(BaseModel):
    """Response model for conflict detection"""
    conflict_level: float = Field(..., ge=0.0, le=1.0, description="Overall conflict level (0.0 to 1.0)")
    emotional_state: EmotionalStateAnalysis
    conversation_trend: ConversationTrend
    escalation_risk: float = Field(..., ge=0.0, le=1.0, description="Risk of escalation (0.0 to 1.0)")
    conflict_patterns: ConflictPatterns
    immediate_recommendations: List[ImmediateRecommendation] = Field(default_factory=list)
    analysis_timestamp: str = Field(..., description="ISO timestamp of analysis")
    sensitivity_used: float = Field(..., ge=0.0, le=1.0)
    therapy_approach: TherapyApproach
    error: Optional[str] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class RealTimeCoachingRequest(BaseModel):
    """Request model for real-time coaching"""
    message: str = Field(..., min_length=1, description="Current message being analyzed")
    sender: str = Field(..., min_length=1, description="Message sender identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Conversation context")
    project_id: str = Field(..., description="Project identifier")
    user_id: Optional[str] = None
    analysis_type: Optional[str] = Field(default="real_time", description="Type of analysis requested")

class RealTimeCoachingResponse(BaseModel):
    """Response model for real-time coaching"""
    message_id: str
    timestamp: datetime
    sender: str
    sentiment: Dict[str, float] = Field(default_factory=dict)
    detected_issues: List[str] = Field(default_factory=list)
    coaching: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    conflict_indicators: Optional[Dict[str, Any]] = None
    intervention_suggested: bool = False
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type (connect, analysis_update, conflict_detection, coaching_request)")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class AnalysisType(str, Enum):
    """Analysis type enumeration"""
    COMPREHENSIVE = "comprehensive"
    SENTIMENT = "sentiment"
    PATTERN_ANALYSIS = "pattern_analysis"
    RELATIONSHIP_HEALTH = "relationship_health"
    CONFLICT_DETECTION = "conflict_detection"
    REAL_TIME = "real_time"

class TherapeuticInterventionRequest(BaseModel):
    """Request model for therapeutic intervention generation"""
    analysis_results: Dict[str, Any] = Field(..., description="Results from conversation analysis")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    intervention_type: Optional[str] = Field(default="general", description="Type of intervention needed")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM)
    therapy_approach: TherapyApproach = Field(default=TherapyApproach.COGNITIVE_BEHAVIORAL)
    project_id: Optional[str] = None
    user_id: Optional[str] = None

class TherapeuticInterventionResponse(BaseModel):
    """Response model for therapeutic intervention"""
    intervention_id: str
    intervention_type: str
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    exercises: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    follow_up_suggestions: List[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    success_indicators: List[str] = Field(default_factory=list)
    timestamp: datetime
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }