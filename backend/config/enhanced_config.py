"""Enhanced Configuration for Unified Catalyst
Manages settings for AI services, database, and therapeutic features
"""

import os
from typing import Dict, List, Any, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from enum import Enum
import json

class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class DatabaseType(str, Enum):
    """Database type options"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

class AIProvider(str, Enum):
    """AI provider options"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE_OPENAI = "azure_openai"

class EnhancedSettings(BaseSettings):
    """Enhanced application settings"""
    
    # Application settings
    app_name: str = Field(default="Enhanced Catalyst", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    
    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    
    # CORS settings
    allowed_origins: List[str] = Field(default=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ])
    allowed_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allowed_headers: List[str] = Field(default=["*"])
    
    # Database settings
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE)
    database_url: str = Field(default="sqlite:///./catalyst_unified.db")
    database_echo: bool = Field(default=False)
    
    # PostgreSQL specific settings (if using PostgreSQL)
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="catalyst")
    postgres_password: str = Field(default="")
    postgres_database: str = Field(default="catalyst_unified")
    
    # AI Service settings
    ai_enabled: bool = Field(default=True)
    default_ai_provider: AIProvider = Field(default=AIProvider.OPENAI)
    ai_fallback_enabled: bool = Field(default=True)
    ai_timeout_seconds: int = Field(default=30)
    ai_max_retries: int = Field(default=3)
    
    # OpenAI settings
    openai_api_key: str = Field(default="", description="OpenAI API key", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4")
    openai_max_tokens: int = Field(default=2000)
    openai_temperature: float = Field(default=0.7)
    
    # Anthropic settings
    anthropic_api_key: str = Field(default="", description="Anthropic API key", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    anthropic_max_tokens: int = Field(default=2000)
    anthropic_temperature: float = Field(default=0.7)
    
    # Azure OpenAI settings
    azure_openai_api_key: str = Field(default="")
    azure_openai_endpoint: str = Field(default="")
    azure_openai_api_version: str = Field(default="2023-12-01-preview")
    azure_openai_deployment_name: str = Field(default="")
    
    # Local AI settings
    local_ai_endpoint: str = Field(default="http://localhost:11434")
    local_ai_model: str = Field(default="llama2")
    
    # Therapy and coaching settings
    therapy_enabled: bool = Field(default=True)
    real_time_coaching_enabled: bool = Field(default=True)
    intervention_auto_delivery: bool = Field(default=False)
    coaching_urgency_threshold: float = Field(default=0.7)
    
    # Analysis settings
    analysis_batch_size: int = Field(default=100)
    analysis_cache_enabled: bool = Field(default=True)
    analysis_cache_ttl_hours: int = Field(default=24)
    sentiment_threshold_positive: float = Field(default=0.1)
    sentiment_threshold_negative: float = Field(default=-0.1)
    
    # File upload settings
    max_file_size_mb: int = Field(default=50)
    allowed_file_types: List[str] = Field(default=[
        "text/plain", "text/csv", "application/json",
        "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ])
    upload_directory: str = Field(default="./uploads")
    
    # WebSocket settings
    websocket_enabled: bool = Field(default=True)
    websocket_heartbeat_interval: int = Field(default=30)
    websocket_max_connections: int = Field(default=100)
    
    # Logging settings
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="catalyst.log")
    log_rotation: str = Field(default="1 day")
    log_retention: str = Field(default="30 days")
    
    # Redis settings (for caching and sessions)
    redis_enabled: bool = Field(default=False)
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="")
    redis_db: int = Field(default=0)
    
    # Email settings (for notifications)
    email_enabled: bool = Field(default=False)
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_username: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_use_tls: bool = Field(default=True)
    
    # Monitoring and metrics
    metrics_enabled: bool = Field(default=True)
    health_check_interval: int = Field(default=60)
    performance_monitoring: bool = Field(default=True)
    
    # Feature flags
    feature_flags: Dict[str, bool] = Field(default_factory=lambda: {
        "advanced_analytics": True,
        "real_time_coaching": True,
        "therapeutic_interventions": True,
        "goal_tracking": True,
        "report_generation": True,
        "multi_user_projects": True,
        "ai_provider_switching": True,
        "conversation_import": True,
        "data_export": True,
        "webhook_notifications": False
    })
    
    # Therapy-specific settings
    therapy_approaches: List[str] = Field(default=[
        "cognitive_behavioral",
        "emotionally_focused",
        "gottman_method",
        "solution_focused",
        "narrative_therapy",
        "systemic_therapy",
        "mindfulness_based"
    ])
    
    intervention_types: List[str] = Field(default=[
        "immediate_response",
        "communication_coaching",
        "conflict_resolution",
        "emotional_regulation",
        "relationship_building",
        "boundary_setting",
        "crisis_intervention"
    ])
    
    # Platform integrations
    supported_platforms: List[str] = Field(default=[
        "whatsapp", "messenger", "discord", "slack", "teams",
        "telegram", "sms", "email", "zoom", "google_meet",
        "instagram", "facebook", "generic"
    ])
    
    @model_validator(mode='before')
    @classmethod
    def build_database_url(cls, values):
        """Build database URL based on type and settings"""
        if isinstance(values, dict) and values.get('database_type') == DatabaseType.POSTGRESQL:
            host = values.get('postgres_host', 'localhost')
            port = values.get('postgres_port', 5432)
            user = values.get('postgres_user', 'catalyst')
            password = values.get('postgres_password', '')
            database = values.get('postgres_database', 'catalyst_unified')
            values['database_url'] = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return values
    
    @field_validator('openai_api_key', 'anthropic_api_key')
    @classmethod
    def validate_api_keys(cls, v, info):
        """Validate API keys are provided when AI is enabled"""
        if not v and info.field_name in ['openai_api_key', 'anthropic_api_key']:
            print(f"Warning: {info.field_name} not provided. AI features may be limited.")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "CATALYST_"
    }

# Global settings instance
settings = EnhancedSettings()

# Configuration utilities
def get_ai_provider_config(provider: AIProvider) -> Dict[str, Any]:
    """Get configuration for specific AI provider"""
    configs = {
        AIProvider.OPENAI: {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "max_tokens": settings.openai_max_tokens,
            "temperature": settings.openai_temperature,
            "timeout": settings.ai_timeout_seconds
        },
        AIProvider.ANTHROPIC: {
            "api_key": settings.anthropic_api_key,
            "model": settings.anthropic_model,
            "max_tokens": settings.anthropic_max_tokens,
            "temperature": settings.anthropic_temperature,
            "timeout": settings.ai_timeout_seconds
        },
        AIProvider.AZURE_OPENAI: {
            "api_key": settings.azure_openai_api_key,
            "endpoint": settings.azure_openai_endpoint,
            "api_version": settings.azure_openai_api_version,
            "deployment_name": settings.azure_openai_deployment_name,
            "timeout": settings.ai_timeout_seconds
        },
        AIProvider.LOCAL: {
            "endpoint": settings.local_ai_endpoint,
            "model": settings.local_ai_model,
            "timeout": settings.ai_timeout_seconds
        }
    }
    return configs.get(provider, {})

def get_database_config() -> Dict[str, Any]:
    """Get database configuration"""
    return {
        "type": settings.database_type,
        "url": settings.database_url,
        "echo": settings.database_echo
    }

def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration"""
    return {
        "allow_origins": settings.allowed_origins,
        "allow_methods": settings.allowed_methods,
        "allow_headers": settings.allowed_headers,
        "allow_credentials": True
    }

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return settings.feature_flags.get(feature, False)

def get_therapy_config() -> Dict[str, Any]:
    """Get therapy-specific configuration"""
    return {
        "enabled": settings.therapy_enabled,
        "real_time_coaching": settings.real_time_coaching_enabled,
        "auto_delivery": settings.intervention_auto_delivery,
        "urgency_threshold": settings.coaching_urgency_threshold,
        "approaches": settings.therapy_approaches,
        "intervention_types": settings.intervention_types
    }

def get_upload_config() -> Dict[str, Any]:
    """Get file upload configuration"""
    return {
        "max_size_mb": settings.max_file_size_mb,
        "allowed_types": settings.allowed_file_types,
        "upload_dir": settings.upload_directory
    }

def validate_configuration() -> Dict[str, Any]:
    """Validate current configuration and return status"""
    validation = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "ai_providers": {},
        "database": {"status": "unknown"},
        "features": settings.feature_flags
    }
    
    # Validate AI providers
    for provider in AIProvider:
        config = get_ai_provider_config(provider)
        if provider == AIProvider.OPENAI:
            validation["ai_providers"][provider.value] = {
                "configured": bool(config.get("api_key")),
                "model": config.get("model")
            }
        elif provider == AIProvider.ANTHROPIC:
            validation["ai_providers"][provider.value] = {
                "configured": bool(config.get("api_key")),
                "model": config.get("model")
            }
        elif provider == AIProvider.LOCAL:
            validation["ai_providers"][provider.value] = {
                "configured": bool(config.get("endpoint")),
                "endpoint": config.get("endpoint")
            }
    
    # Check for missing API keys
    if settings.ai_enabled:
        if not settings.openai_api_key and not settings.anthropic_api_key:
            validation["warnings"].append("No AI provider API keys configured")
    
    # Validate database
    try:
        if settings.database_type == DatabaseType.SQLITE:
            validation["database"]["status"] = "configured"
        elif settings.database_type == DatabaseType.POSTGRESQL:
            if settings.postgres_password:
                validation["database"]["status"] = "configured"
            else:
                validation["warnings"].append("PostgreSQL password not set")
    except Exception as e:
        validation["errors"].append(f"Database configuration error: {e}")
    
    # Check upload directory
    if not os.path.exists(settings.upload_directory):
        validation["warnings"].append(f"Upload directory does not exist: {settings.upload_directory}")
    
    # Set overall validation status
    validation["valid"] = len(validation["errors"]) == 0
    
    return validation

def create_env_template() -> str:
    """Create a template .env file"""
    template = """
# Enhanced Catalyst Configuration
# Copy this file to .env and update the values

# Application Settings
CATALYST_APP_NAME="Enhanced Catalyst"
CATALYST_ENVIRONMENT="development"
CATALYST_DEBUG=true

# Server Settings
CATALYST_HOST="0.0.0.0"
CATALYST_PORT=8000

# Security
CATALYST_SECRET_KEY="your-secret-key-change-in-production"

# Database
CATALYST_DATABASE_TYPE="sqlite"
CATALYST_DATABASE_URL="sqlite:///./catalyst_unified.db"

# PostgreSQL (if using)
# CATALYST_POSTGRES_HOST="localhost"
# CATALYST_POSTGRES_PORT=5432
# CATALYST_POSTGRES_USER="catalyst"
# CATALYST_POSTGRES_PASSWORD="your-password"
# CATALYST_POSTGRES_DATABASE="catalyst_unified"

# AI Providers
CATALYST_AI_ENABLED=true
CATALYST_DEFAULT_AI_PROVIDER="openai"

# OpenAI
OPENAI_API_KEY="your-openai-api-key"
CATALYST_OPENAI_MODEL="gpt-4"

# Anthropic
ANTHROPIC_API_KEY="your-anthropic-api-key"
CATALYST_ANTHROPIC_MODEL="claude-3-sonnet-20240229"

# Azure OpenAI (if using)
# CATALYST_AZURE_OPENAI_API_KEY="your-azure-key"
# CATALYST_AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
# CATALYST_AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"

# Local AI (if using)
# CATALYST_LOCAL_AI_ENDPOINT="http://localhost:11434"
# CATALYST_LOCAL_AI_MODEL="llama2"

# Therapy Features
CATALYST_THERAPY_ENABLED=true
CATALYST_REAL_TIME_COACHING_ENABLED=true

# File Uploads
CATALYST_MAX_FILE_SIZE_MB=50
CATALYST_UPLOAD_DIRECTORY="./uploads"

# Logging
CATALYST_LOG_LEVEL="INFO"
CATALYST_LOG_FILE="catalyst.log"

# Redis (optional)
# CATALYST_REDIS_ENABLED=false
# CATALYST_REDIS_HOST="localhost"
# CATALYST_REDIS_PORT=6379

# Email (optional)
# CATALYST_EMAIL_ENABLED=false
# CATALYST_SMTP_HOST="smtp.gmail.com"
# CATALYST_SMTP_PORT=587
# CATALYST_SMTP_USERNAME="your-email@gmail.com"
# CATALYST_SMTP_PASSWORD="your-app-password"
"""
    return template.strip()

# Export main components
__all__ = [
    "EnhancedSettings",
    "settings",
    "Environment",
    "DatabaseType",
    "AIProvider",
    "get_ai_provider_config",
    "get_database_config",
    "get_cors_config",
    "is_feature_enabled",
    "get_therapy_config",
    "get_upload_config",
    "validate_configuration",
    "create_env_template"
]