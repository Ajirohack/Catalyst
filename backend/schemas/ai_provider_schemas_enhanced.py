"""
Enhanced Pydantic Schemas for AI Provider Management
Comprehensive validation and serialization for multi-provider AI integration
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

class ProviderType(str, Enum):
    """Supported AI Provider Types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    CUSTOM = "custom"

class ModelType(str, Enum):
    """AI Model Types"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    IMAGE_GENERATION = "image_generation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"

class ProviderStatus(str, Enum):
    """Provider Status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

class AuthType(str, Enum):
    """Authentication Types"""
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    CUSTOM = "custom"

# Base Provider Schemas
class AIProviderBase(BaseModel):
    """Base schema for AI Provider"""
    provider_type: ProviderType
    name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    base_url: str = Field(..., description="Base API URL for the provider")
    
    @validator('display_name', always=True)
    def set_display_name(cls, v, values):
        return v or values.get('name')

class AIProviderCreate(AIProviderBase):
    """Schema for creating a new AI Provider"""
    api_key: str = Field(..., description="API key for the provider")
    api_version: Optional[str] = Field(None, max_length=20)
    
    # Configuration
    enabled: bool = Field(True, description="Whether the provider is enabled")
    priority: int = Field(1, ge=1, le=100, description="Provider priority (1-100)")
    
    # Dynamic model support
    supports_dynamic_models: bool = Field(False, description="Whether the provider supports dynamic model fetching")
    model_list_endpoint: Optional[str] = Field(None, description="API endpoint to fetch available models")
    
    # Authentication
    auth_type: AuthType = Field(AuthType.BEARER, description="Authentication type")
    custom_headers: Optional[Dict[str, str]] = Field(None, description="Custom headers for API requests")
    
    # Model configuration
    default_model: str = Field(..., description="Default model to use")
    available_models: Optional[List[str]] = Field(None, description="List of available models")
    
    # Rate limiting and performance
    rate_limit_rpm: int = Field(60, ge=1, description="Requests per minute limit")
    rate_limit_tpm: int = Field(10000, ge=1, description="Tokens per minute limit")
    timeout_seconds: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    
    # Quality and cost settings
    confidence_score: float = Field(0.8, ge=0.0, le=1.0, description="Confidence score threshold")
    quality_rating: float = Field(0.8, ge=0.0, le=1.0, description="Quality rating")
    cost_per_1k_tokens: float = Field(0.0, ge=0.0, description="Cost per 1000 tokens")
    
    # Health check settings
    health_check_interval: int = Field(300, ge=60, description="Health check interval in seconds")

class AIProviderUpdate(BaseModel):
    """Schema for updating an AI Provider"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = Field(None, max_length=20)
    
    # Configuration
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=100)
    
    # Dynamic model support
    supports_dynamic_models: Optional[bool] = None
    model_list_endpoint: Optional[str] = None
    
    # Authentication
    auth_type: Optional[AuthType] = None
    custom_headers: Optional[Dict[str, str]] = None
    
    # Model configuration
    default_model: Optional[str] = None
    available_models: Optional[List[str]] = None
    
    # Rate limiting and performance
    rate_limit_rpm: Optional[int] = Field(None, ge=1)
    rate_limit_tpm: Optional[int] = Field(None, ge=1)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    
    # Quality and cost settings
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    cost_per_1k_tokens: Optional[float] = Field(None, ge=0.0)
    
    # Health check settings
    health_check_interval: Optional[int] = Field(None, ge=60)

class AIProviderResponse(AIProviderBase):
    """Schema for AI Provider responses"""
    id: int
    api_version: Optional[str]
    enabled: bool
    priority: int
    supports_dynamic_models: bool
    model_list_endpoint: Optional[str]
    auth_type: AuthType
    custom_headers: Dict[str, str]
    default_model: str
    available_models: List[str]
    rate_limit_rpm: int
    rate_limit_tpm: int
    timeout_seconds: int
    max_retries: int
    confidence_score: float
    quality_rating: float
    cost_per_1k_tokens: float
    
    # Usage statistics
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    average_response_time: float
    success_rate: float
    
    # Status
    status: ProviderStatus
    last_error: Optional[str]
    health_check_interval: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    last_used_at: Optional[datetime]
    last_health_check: Optional[datetime]
    
    # Metadata
    has_api_key: bool
    model_count: int
    
    class Config:
        from_attributes = True

# Model Schemas
class AIProviderModelBase(BaseModel):
    """Base schema for AI Provider Model"""
    model_name: str = Field(..., min_length=1, max_length=100)
    model_id: str = Field(..., min_length=1, max_length=100, description="Actual model ID used in API calls")
    model_type: ModelType = Field(ModelType.CHAT, description="Type of AI model")

class AIProviderModelCreate(AIProviderModelBase):
    """Schema for creating a new AI Provider Model"""
    provider_id: int = Field(..., description="ID of the associated provider")
    
    # Model specifications
    context_length: Optional[int] = Field(None, ge=1, description="Maximum context length")
    max_output_tokens: Optional[int] = Field(None, ge=1, description="Maximum output tokens")
    input_cost_per_1k: float = Field(0.0, ge=0.0, description="Input cost per 1000 tokens")
    output_cost_per_1k: float = Field(0.0, ge=0.0, description="Output cost per 1000 tokens")
    
    # Capabilities
    supports_functions: bool = Field(False, description="Supports function calling")
    supports_vision: bool = Field(False, description="Supports vision/image inputs")
    supports_streaming: bool = Field(True, description="Supports streaming responses")
    
    # Configuration
    enabled: bool = Field(True, description="Whether the model is enabled")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default model parameters")

class AIProviderModelUpdate(BaseModel):
    """Schema for updating an AI Provider Model"""
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    model_id: Optional[str] = Field(None, min_length=1, max_length=100)
    model_type: Optional[ModelType] = None
    
    # Model specifications
    context_length: Optional[int] = Field(None, ge=1)
    max_output_tokens: Optional[int] = Field(None, ge=1)
    input_cost_per_1k: Optional[float] = Field(None, ge=0.0)
    output_cost_per_1k: Optional[float] = Field(None, ge=0.0)
    
    # Capabilities
    supports_functions: Optional[bool] = None
    supports_vision: Optional[bool] = None
    supports_streaming: Optional[bool] = None
    
    # Configuration
    enabled: Optional[bool] = None
    default_parameters: Optional[Dict[str, Any]] = None

class AIProviderModelResponse(AIProviderModelBase):
    """Schema for AI Provider Model responses"""
    id: int
    provider_id: int
    context_length: Optional[int]
    max_output_tokens: Optional[int]
    input_cost_per_1k: float
    output_cost_per_1k: float
    supports_functions: bool
    supports_vision: bool
    supports_streaming: bool
    enabled: bool
    default_parameters: Dict[str, Any]
    
    # Usage statistics
    total_requests: int
    total_tokens: int
    total_cost: float
    
    # Timestamps
    created_at: datetime
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Knowledge Base Schemas
class AIKnowledgeBaseCreate(BaseModel):
    """Schema for creating a new Knowledge Base"""
    provider_id: int = Field(..., description="ID of the associated provider")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    knowledge_type: str = Field("documents", description="Type of knowledge base")
    
    # Configuration
    enabled: bool = Field(True, description="Whether the knowledge base is enabled")
    embedding_model: Optional[str] = Field(None, description="Model used for embeddings")
    chunk_size: int = Field(1000, ge=100, le=8000, description="Text chunk size")
    chunk_overlap: int = Field(200, ge=0, le=1000, description="Chunk overlap size")

class AIKnowledgeBaseResponse(BaseModel):
    """Schema for Knowledge Base responses"""
    id: int
    provider_id: int
    name: str
    description: Optional[str]
    knowledge_type: str
    enabled: bool
    embedding_model: Optional[str]
    chunk_size: int
    chunk_overlap: int
    total_documents: int
    total_chunks: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_updated_documents: Optional[datetime]
    
    class Config:
        from_attributes = True

# Testing and Validation Schemas
class ProviderTestRequest(BaseModel):
    """Schema for testing provider connectivity"""
    provider_id: Optional[int] = None
    test_message: str = Field("Hello, this is a test message.", description="Test message to send")
    max_tokens: int = Field(50, ge=1, le=1000, description="Maximum tokens for test")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for test")

class ProviderTestResult(BaseModel):
    """Schema for provider test results"""
    provider_id: int
    provider_name: str
    success: bool
    response_time_ms: float
    test_message: str
    response_content: Optional[str]
    error_message: Optional[str]
    tokens_used: Optional[int]
    cost: Optional[float]
    timestamp: datetime

class BulkProviderTestRequest(BaseModel):
    """Schema for testing multiple providers"""
    provider_ids: Optional[List[int]] = Field(None, description="Specific provider IDs to test (all if None)")
    test_message: str = Field("Hello, this is a test message.", description="Test message to send")
    max_tokens: int = Field(50, ge=1, le=1000, description="Maximum tokens for test")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for test")

class BulkProviderTestResponse(BaseModel):
    """Schema for bulk provider test results"""
    results: List[ProviderTestResult]
    total_tested: int
    successful: int
    failed: int
    average_response_time: float

# Usage and Analytics Schemas
class UsageMetrics(BaseModel):
    """Schema for usage metrics"""
    provider_id: int
    provider_name: str
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    average_response_time: float
    success_rate: float
    period_start: datetime
    period_end: datetime

class SystemUsageReport(BaseModel):
    """Schema for system-wide usage reports"""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens: int
    total_cost: float
    provider_metrics: List[UsageMetrics]
    top_models: List[Dict[str, Any]]
    cost_breakdown: Dict[str, float]

class ProviderHealthStatus(BaseModel):
    """Schema for provider health status"""
    provider_id: int
    provider_name: str
    status: ProviderStatus
    last_health_check: Optional[datetime]
    response_time_ms: Optional[float]
    error_rate: float
    uptime_percentage: float
    issues: List[str]

class ProviderAnalytics(BaseModel):
    """Schema for provider analytics"""
    provider_id: int
    provider_name: str
    usage_trend: List[Dict[str, Any]]
    cost_trend: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    recommendations: List[str]

class CostOptimizationSuggestion(BaseModel):
    """Schema for cost optimization suggestions"""
    provider_id: int
    provider_name: str
    current_cost: float
    suggested_cost: float
    potential_savings: float
    optimization_type: str
    description: str
    implementation_effort: str

# AI Request and Response Schemas
class AIRequest(BaseModel):
    """Schema for AI requests"""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    provider_preference: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    stream: bool = Field(False, description="Whether to stream the response")
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None
    extra_params: Optional[Dict[str, Any]] = None

class AIResponse(BaseModel):
    """Schema for AI responses"""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    cost: float
    latency: float
    timestamp: datetime
    success: bool = True
    confidence: Optional[float] = None
    analysis_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    response_time_ms: Optional[float] = None
    
    class Config:
        from_attributes = True

# File Upload Schemas
class KnowledgeUploadRequest(BaseModel):
    """Schema for knowledge base file uploads"""
    knowledge_base_id: int
    file_type: str = Field(..., description="Type of file being uploaded")
    chunk_size: Optional[int] = Field(None, ge=100, le=8000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)
    processing_options: Optional[Dict[str, Any]] = None

class KnowledgeUploadResponse(BaseModel):
    """Schema for knowledge upload responses"""
    upload_id: str
    knowledge_base_id: int
    status: str
    total_documents: int
    total_chunks: int
    processing_time_ms: float
    created_at: datetime

# Configuration Schemas
class SupportedProviderInfo(BaseModel):
    """Schema for supported provider information"""
    provider_type: ProviderType
    name: str
    description: str
    documentation_url: str
    supported_models: List[str]
    capabilities: List[str]
    auth_methods: List[AuthType]
    default_base_url: str
    supports_dynamic_models: bool

class ModelListResponse(BaseModel):
    """Schema for model list responses"""
    provider_id: int
    provider_name: str
    models: List[AIProviderModelResponse]
    fetched_at: datetime
    source: str  # "database", "api", "manual"

# Error Schemas
class APIError(BaseModel):
    """Schema for API errors"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationError(BaseModel):
    """Schema for validation errors"""
    field: str
    error: str
    value: Any
