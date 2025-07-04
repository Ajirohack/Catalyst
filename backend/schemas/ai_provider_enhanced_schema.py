"""
Enhanced AI Provider Schemas
Pydantic schemas for comprehensive AI provider management
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class AIProviderType(str, Enum):
    """Extended supported AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    OPENROUTER = "openrouter" 
    OLLAMA = "ollama"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

class ModelType(str, Enum):
    """Model types for different use cases"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    VISION = "vision"
    CODE = "code"

class ProviderStatus(str, Enum):
    """Provider status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

class SecretType(str, Enum):
    """Types of secrets that can be stored"""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH_TOKEN = "oauth_token"
    CLIENT_SECRET = "client_secret"

# Request Schemas
class AIProviderCreateRequest(BaseModel):
    """Schema for creating a new AI provider"""
    provider_type: AIProviderType
    name: Optional[str] = None
    description: Optional[str] = ""
    enabled: bool = True
    priority: int = Field(default=1, ge=1, le=100)
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    models_config: Dict[str, Any] = Field(default_factory=dict)
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    quality_rating: float = Field(default=0.8, ge=0.0, le=1.0)
    
    model_config = {
        "use_enum_values": True
    }

class AIProviderUpdateRequest(BaseModel):
    """Schema for updating an existing AI provider"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=100)
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    models_config: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, int]] = None
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    model_config = {
        "use_enum_values": True
    }

class AIModelCreateRequest(BaseModel):
    """Schema for creating a new AI model"""
    provider_id: int
    model_name: str
    model_type: ModelType = ModelType.CHAT
    max_tokens: Optional[int] = Field(None, ge=1)
    supports_functions: bool = False
    supports_vision: bool = False
    supports_tools: bool = False
    cost_input_per_1k: float = Field(default=0.0, ge=0.0)
    cost_output_per_1k: float = Field(default=0.0, ge=0.0)
    quality_score: float = Field(default=0.8, ge=0.0, le=1.0)
    speed_score: float = Field(default=0.8, ge=0.0, le=1.0)
    context_window: Optional[int] = Field(None, ge=1)
    enabled: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "use_enum_values": True
    }

class AIModelUpdateRequest(BaseModel):
    """Schema for updating an existing AI model"""
    model_name: Optional[str] = None
    model_type: Optional[ModelType] = None
    max_tokens: Optional[int] = Field(None, ge=1)
    supports_functions: Optional[bool] = None
    supports_vision: Optional[bool] = None
    supports_tools: Optional[bool] = None
    cost_input_per_1k: Optional[float] = Field(None, ge=0.0)
    cost_output_per_1k: Optional[float] = Field(None, ge=0.0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    speed_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    context_window: Optional[int] = Field(None, ge=1)
    enabled: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None
    
    model_config = {
        "use_enum_values": True
    }

class SecretCreateRequest(BaseModel):
    """Schema for creating a provider secret"""
    provider_id: int
    secret_type: SecretType
    secret_name: str
    secret_value: str
    expires_at: Optional[datetime] = None
    
    model_config = {
        "use_enum_values": True
    }

# Response Schemas
class AIModelResponse(BaseModel):
    """Schema for AI model responses"""
    id: int
    provider_id: int
    model_name: str
    model_type: str
    max_tokens: Optional[int]
    supports_functions: bool
    supports_vision: bool
    supports_tools: bool
    cost_input_per_1k: float
    cost_output_per_1k: float
    quality_score: float
    speed_score: float
    context_window: Optional[int]
    total_requests: int
    total_tokens: int
    total_cost: float
    average_response_time: float
    enabled: bool
    parameters: Dict[str, Any]
    created_at: Optional[str]
    updated_at: Optional[str]
    last_used_at: Optional[str]

class SecretResponse(BaseModel):
    """Schema for secret responses (without actual secret value)"""
    id: int
    provider_id: int
    secret_type: str
    secret_name: str
    active: bool
    expires_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    last_used_at: Optional[str]
    has_value: bool

class ProviderUsageStats(BaseModel):
    """Schema for provider usage statistics"""
    total_requests: int
    total_tokens: int
    total_cost: float
    average_response_time_ms: float
    error_count: int
    success_rate: float
    period_days: int

class AIProviderResponse(BaseModel):
    """Schema for comprehensive AI provider responses"""
    id: int
    provider_type: str
    name: str
    description: str
    enabled: bool
    priority: int
    base_url: Optional[str]
    api_version: Optional[str]
    default_model: str
    models_config: Dict[str, Any]
    rate_limits: Dict[str, int]
    timeout_seconds: int
    max_retries: int
    confidence_score: float
    quality_rating: float
    total_requests: int
    total_tokens: int
    total_cost: float
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    last_used_at: Optional[str]
    last_health_check: Optional[str]
    has_api_key: bool
    models: List[AIModelResponse] = Field(default_factory=list)
    secrets: List[SecretResponse] = Field(default_factory=list)
    usage_stats: ProviderUsageStats

class ProviderTestResult(BaseModel):
    """Schema for provider connection test results"""
    provider_id: int
    provider_type: str
    success: bool
    message: str
    response_time_ms: float
    timestamp: str

class SupportedProviderInfo(BaseModel):
    """Schema for supported provider information"""
    provider_type: str
    name: str
    description: str
    website: str
    documentation_url: str
    supported_features: List[str]
    authentication_methods: List[str]
    pricing_model: str
    default_base_url: Optional[str] = None
    auth_type: Optional[str] = None
    default_models: List[str] = Field(default_factory=list)
    capabilities: Dict[str, bool] = Field(default_factory=dict)

class SystemUsageReport(BaseModel):
    """Schema for system-wide usage reports"""
    total_providers: int
    active_providers: int
    total_requests: int
    total_tokens: int
    total_cost: float
    average_response_time_ms: float
    error_rate: float
    top_providers: List[Dict[str, Any]]
    usage_by_type: Dict[str, Any]
    cost_by_provider: Dict[str, float]
    period_start: str
    period_end: str

class ModelListResponse(BaseModel):
    """Schema for dynamic model list responses"""
    provider_id: int
    provider_type: str
    models: List[Dict[str, Any]]
    fetched_at: str
    cache_expires_at: str

class ProviderCapabilitiesResponse(BaseModel):
    """Schema for provider capabilities"""
    provider_type: str
    supports_chat: bool
    supports_completion: bool
    supports_embedding: bool
    supports_function_calling: bool
    supports_vision: bool
    supports_streaming: bool
    max_context_length: Optional[int]
    supported_formats: List[str]

# Enhanced Request/Response Models
class BulkProviderTestRequest(BaseModel):
    """Schema for testing multiple providers"""
    provider_ids: List[int]
    test_message: str = "Hello, this is a test message."
    timeout_seconds: int = Field(default=30, ge=5, le=120)

class BulkProviderTestResponse(BaseModel):
    """Schema for bulk provider test results"""
    results: List[ProviderTestResult]
    summary: Dict[str, Any]
    total_tested: int
    successful: int
    failed: int

class ProviderMigrationRequest(BaseModel):
    """Schema for migrating between providers"""
    source_provider_id: int
    target_provider_id: int
    model_mapping: Dict[str, str]  # source_model -> target_model
    preserve_history: bool = True

class CostOptimizationSuggestion(BaseModel):
    """Schema for cost optimization suggestions"""
    current_cost: float
    potential_savings: float
    suggested_providers: List[Dict[str, Any]]
    optimization_strategies: List[str]
    impact_analysis: Dict[str, Any]

class ProviderHealthStatus(BaseModel):
    """Schema for detailed provider health status"""
    provider_id: int
    status: ProviderStatus
    health_score: float  # 0-1
    last_successful_request: Optional[str]
    consecutive_failures: int
    avg_response_time_24h: float
    uptime_percentage: float
    issues: List[str]
    recommendations: List[str]

# Analytics Schemas
class ProviderAnalytics(BaseModel):
    """Schema for provider analytics"""
    provider_id: int
    provider_type: str
    time_period: str
    request_volume: List[Dict[str, Any]]  # time series data
    cost_trend: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    error_analysis: Dict[str, Any]
    usage_patterns: Dict[str, Any]

class ModelPerformanceMetrics(BaseModel):
    """Schema for model performance metrics"""
    model_id: int
    model_name: str
    provider_type: str
    quality_metrics: Dict[str, float]
    speed_metrics: Dict[str, float]
    cost_efficiency: float
    user_satisfaction: float
    recommendation_score: float
