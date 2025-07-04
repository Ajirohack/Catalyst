"""
Unified Configuration Settings for Catalyst Backend
Consolidated configuration management using Pydantic settings
"""

import os
from typing import Dict, List, Any, Optional, Union
from pydantic import Field, field_validator, model_validator, AnyHttpUrl, EmailStr
from pydantic_settings import BaseSettings
from enum import Enum
import json
from pathlib import Path

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

class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Settings(BaseSettings):
    """Unified application settings"""
    
    # Application Settings
    app_name: str = Field(default="Catalyst", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    api_v1_str: str = Field(default="/api/v1")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")
    workers: int = Field(default=1, description="Number of worker processes")
    
    # Security Settings
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-please",
        description="Secret key for JWT and encryption"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=60 * 24 * 8, description="8 days")
    
    # CORS Settings
    backend_cors_origins: List[Union[AnyHttpUrl, str]] = Field(
        default=[
            "http://localhost:3000",    # React dev server
            "http://127.0.0.1:3000",
            "http://localhost:3001",    # Admin dashboard  
            "http://127.0.0.1:3001",
            "chrome-extension://*",     # Chrome extension
            "moz-extension://*"         # Firefox extension
        ],
        description="Allowed CORS origins"
    )
    
    # Database Settings
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE)
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    # PostgreSQL settings (if used)
    postgres_server: str = Field(default="localhost", description="PostgreSQL server")
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    postgres_password: str = Field(default="", description="PostgreSQL password")
    postgres_db: str = Field(default="catalyst", description="PostgreSQL database name")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    
    # SQLite settings (default)
    sqlite_path: str = Field(default="./catalyst.db", description="SQLite database path")
    
    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """Assemble database connection URL if not provided"""
        if v:
            return v
            
        data = info.data if hasattr(info, 'data') else {}
        db_type = data.get("database_type", DatabaseType.SQLITE)
        
        if db_type == DatabaseType.SQLITE:
            sqlite_path = data.get("sqlite_path", "./catalyst.db")
            return f"sqlite:///{sqlite_path}"
        elif db_type == DatabaseType.POSTGRESQL:
            postgres_user = data.get("postgres_user", "postgres")
            postgres_password = data.get("postgres_password", "")
            postgres_server = data.get("postgres_server", "localhost")
            postgres_port = data.get("postgres_port", 5432)
            postgres_db = data.get("postgres_db", "catalyst")
            return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"
        else:
            return "sqlite:///./catalyst.db"  # Fallback
    
    # Redis Settings (for caching and sessions)
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_enabled: bool = Field(default=False, description="Enable Redis for caching")
    
    # File Storage Settings
    upload_dir: str = Field(default="./storage/uploads", description="File upload directory")
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Max file size (100MB)")
    allowed_file_types: List[str] = Field(
        default=["pdf", "txt", "docx", "md", "csv", "json"],
        description="Allowed file extensions"
    )
    
    # AI Provider Settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    mistral_api_key: Optional[str] = Field(default=None, description="Mistral API key")
    huggingface_api_key: Optional[str] = Field(default=None, description="Hugging Face API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    
    # Default AI Provider Settings
    default_ai_provider: str = Field(default="openai", description="Default AI provider")
    default_model: str = Field(default="gpt-3.5-turbo", description="Default AI model")
    max_tokens: int = Field(default=2000, description="Default max tokens for AI responses")
    temperature: float = Field(default=0.7, description="Default temperature for AI responses")
    
    # Email Settings (for notifications)
    smtp_tls: bool = Field(default=True)
    smtp_port: Optional[int] = Field(default=587)
    smtp_host: Optional[str] = Field(default=None)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    emails_from_email: Optional[EmailStr] = Field(default=None)
    emails_from_name: Optional[str] = Field(default=None)
    
    @field_validator("emails_from_name", mode="before")
    @classmethod
    def get_project_name(cls, v: Optional[str], info) -> str:
        if not v:
            data = info.data if hasattr(info, 'data') else {}
            return data.get("app_name", "Catalyst")
        return v
    
    # Admin Settings
    first_superuser: EmailStr = Field(default="admin@catalyst.com")
    first_superuser_password: str = Field(default="changethis")
    
    # Logging Settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_file: Optional[str] = Field(default="./logs/catalyst.log", description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation schedule")
    log_retention: str = Field(default="30 days", description="Log retention period")
    
    # Feature Flags
    enable_real_time_analysis: bool = Field(default=True, description="Enable real-time analysis")
    enable_whisper_suggestions: bool = Field(default=True, description="Enable whisper suggestions")
    enable_file_upload: bool = Field(default=True, description="Enable file upload")
    enable_knowledge_base: bool = Field(default=True, description="Enable knowledge base")
    enable_advanced_analytics: bool = Field(default=True, description="Enable advanced analytics")
    enable_multi_provider: bool = Field(default=True, description="Enable multi-provider AI")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Requests per minute limit")
    rate_limit_burst: int = Field(default=10, description="Burst limit")
    
    # Monitoring and Performance
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, description="Metrics server port")
    slow_query_threshold: float = Field(default=1.0, description="Slow query threshold in seconds")
    
    # Knowledge Base Settings
    vector_db_type: str = Field(default="chroma", description="Vector database type")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model")
    chunk_size: int = Field(default=1000, description="Text chunk size for embeddings")
    chunk_overlap: int = Field(default=100, description="Text chunk overlap")
    
    # Therapeutic Features
    enable_therapeutic_interventions: bool = Field(default=True, description="Enable therapeutic features")
    intervention_confidence_threshold: float = Field(default=0.7, description="Intervention confidence threshold")
    
    # Development Settings
    reload_includes: List[str] = Field(
        default=["*.py"],
        description="File patterns to watch for auto-reload"
    )
    reload_excludes: List[str] = Field(
        default=["tests/*", "*.pyc", "__pycache__/*"],
        description="File patterns to exclude from auto-reload"
    )
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
        
    @model_validator(mode="before")
    @classmethod
    def validate_config(cls, values):
        """Validate configuration values"""
        if isinstance(values, dict):
            # Ensure upload directory exists
            upload_dir = values.get("upload_dir", "./storage/uploads")
            Path(upload_dir).mkdir(parents=True, exist_ok=True)
            
            # Ensure log directory exists
            log_file = values.get("log_file")
            if log_file:
                Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        return values

# Create global settings instance
settings = Settings()

# Export commonly used settings
__all__ = [
    "Settings",
    "Environment", 
    "DatabaseType",
    "LogLevel",
    "settings"
]
