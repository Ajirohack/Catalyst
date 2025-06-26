"""AI Provider Schemas for Catalyst
Pydantic schemas for AI provider management and responses
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class AIProviderType(str, Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    HUGGINGFACE = "huggingface"

class ModelType(str, Enum):
    """Model types for different use cases"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"

class ProviderStatus(str, Enum):
    """Provider status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"

class ModelInfo(BaseModel):
    """Information about a specific model"""
    name: str
    type: ModelType
    max_tokens: int
    supports_functions: bool = False
    cost_per_1k_tokens: Dict[str, float] = Field(default_factory=dict)
    description: Optional[str] = None
    
class ProviderConfigSchema(BaseModel):
    """Schema for AI provider configuration"""
    provider_type: AIProviderType
    name: str
    enabled: bool = True
    priority: int = 1
    base_url: Optional[str] = None
    default_model: str
    models: Dict[str, Dict[str, Any]]
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    api_key_configured: bool = False  # Don't expose actual key
    
    model_config = {
        "use_enum_values": True
    }

class ProviderStatusSchema(BaseModel):
    """Schema for provider status information"""
    provider_type: AIProviderType
    name: str
    status: ProviderStatus
    available: bool
    last_used: Optional[datetime] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    model_config = {
        "use_enum_values": True
    }

class UsageMetrics(BaseModel):
    """Schema for AI usage metrics"""
    provider_type: AIProviderType
    model: str
    requests_count: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    error_count: int = 0
    last_used: Optional[datetime] = None
    
    model_config = {
        "use_enum_values": True
    }

class CostAnalysis(BaseModel):
    """Schema for cost analysis"""
    provider_type: AIProviderType
    model: str
    cost_per_request: float
    cost_per_token: float
    estimated_monthly_cost: float
    usage_efficiency: float  # 0-1 score
    
    model_config = {
        "use_enum_values": True
    }

class AIRequest(BaseModel):
    """Schema for AI analysis requests"""
    messages: List[Dict[str, str]]
    analysis_type: str
    context: Optional[Dict[str, Any]] = None
    model_preference: Optional[str] = None
    provider_preference: Optional[AIProviderType] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7
    
    @field_validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v
    
    model_config = {
        "use_enum_values": True
    }

class AIResponse(BaseModel):
    """Schema for AI responses"""
    content: str
    provider: AIProviderType
    model: str
    confidence: float = Field(ge=0, le=1)
    analysis_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    usage: Dict[str, int] = Field(default_factory=dict)  # tokens used
    cost: float = 0.0
    response_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    recommendations: Optional[List[str]] = None
    insights: Optional[List[str]] = None
    
    model_config = {
        "use_enum_values": True
    }

class AnalysisResult(BaseModel):
    """Schema for comprehensive analysis results"""
    analysis_id: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    analysis_type: str
    overall_score: float = Field(ge=0, le=1)
    
    # Analysis components
    emotional_analysis: Dict[str, Any] = Field(default_factory=dict)
    communication_patterns: Dict[str, Any] = Field(default_factory=dict)
    relationship_insights: Dict[str, Any] = Field(default_factory=dict)
    
    # Findings
    red_flags: List[str] = Field(default_factory=list)
    positive_indicators: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    therapy_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    ai_responses: List[AIResponse] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0

class ProviderTestRequest(BaseModel):
    """Schema for testing provider connectivity"""
    provider_type: AIProviderType
    test_message: str = "Hello, this is a test message for connection verification."
    
    model_config = {
        "use_enum_values": True
    }

class ProviderTestResponse(BaseModel):
    """Schema for provider test results"""
    provider_type: AIProviderType
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    response_preview: Optional[str] = None
    
    model_config = {
        "use_enum_values": True
    }

class ProviderUpdateRequest(BaseModel):
    """Schema for updating provider configuration"""
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    default_model: Optional[str] = None
    rate_limits: Optional[Dict[str, int]] = None
    
    @field_validator('priority')
    def validate_priority(cls, v):
        if v is not None and v < 1:
            raise ValueError('Priority must be at least 1')
        return v

class SystemUsageReport(BaseModel):
    """Schema for system-wide usage reports"""
    time_period: str  # e.g., "last_24h", "last_week", "last_month"
    total_requests: int
    total_tokens: int
    total_cost: float
    
    # Provider breakdown
    provider_usage: Dict[AIProviderType, UsageMetrics]
    
    # Performance metrics
    average_response_time: float
    error_rate: float
    
    # Top models and analyses
    top_models: List[Dict[str, Any]]
    top_analysis_types: List[Dict[str, Any]]
    
    # Cost efficiency
    cost_per_request: float
    cost_per_token: float
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "use_enum_values": True
    }

class ProviderHealthCheck(BaseModel):
    """Schema for provider health status"""
    provider_type: AIProviderType
    healthy: bool
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_details: Optional[str] = None
    uptime_percentage: float = Field(ge=0, le=100)
    
    model_config = {
        "use_enum_values": True
    }

class AIServiceStatus(BaseModel):
    """Schema for overall AI service status"""
    service_healthy: bool
    active_providers: int
    total_providers: int
    default_provider: AIProviderType
    fallback_enabled: bool
    provider_health: List[ProviderHealthCheck]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "use_enum_values": True
    }

# Request/Response schemas for specific endpoints

class RouteAnalysisRequest(BaseModel):
    """Request schema for routing analysis to best provider"""
    analysis_type: str
    content: str
    context: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None  # specific requirements like speed, accuracy
    
class RouteAnalysisResponse(BaseModel):
    """Response schema for routed analysis"""
    selected_provider: AIProviderType
    selected_model: str
    reason: str
    estimated_cost: float
    estimated_time_ms: float
    
    model_config = {
        "use_enum_values": True
    }

class BulkAnalysisRequest(BaseModel):
    """Request schema for bulk analysis operations"""
    requests: List[AIRequest]
    optimize_for: str = "cost"  # "cost", "speed", "accuracy"
    max_parallel: int = Field(default=5, ge=1, le=20)
    
class BulkAnalysisResponse(BaseModel):
    """Response schema for bulk analysis"""
    results: List[AnalysisResult]
    total_cost: float
    total_time_ms: float
    provider_distribution: Dict[AIProviderType, int]
    
    model_config = {
        "use_enum_values": True
    }
