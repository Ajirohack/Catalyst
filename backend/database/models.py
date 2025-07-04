"""
Unified Database Models for Catalyst Backend
Consolidated models for AI providers, projects, and core functionality
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json

Base = declarative_base()

# Enums

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
    DEEPSEEK = "deepseek"
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

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"

class ProjectType(str, Enum):
    """Project type enumeration"""
    ROMANTIC = "romantic"
    FAMILY = "family"
    FRIENDSHIP = "friendship"
    PROFESSIONAL = "professional"
    THERAPY = "therapy"
    COACHING = "coaching"
    OTHER = "other"

class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    PREMIUM = "premium"
    THERAPIST = "therapist"
    COACH = "coach"
    ADMIN = "admin"

# Core Models

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    analyses = relationship("Analysis", back_populates="user")

class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String, default=ProjectType.OTHER.value)
    status = Column(String, default=ProjectStatus.ACTIVE.value)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    analyses = relationship("Analysis", back_populates="project")

class Analysis(Base):
    """Analysis model"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    analysis_result = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    model_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    project = relationship("Project", back_populates="analyses")
    provider = relationship("AIProvider")

# AI Provider Models

class AIProvider(Base):
    """AI Provider model"""
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    base_url = Column(String, nullable=True)
    api_version = Column(String, nullable=True)
    supports_dynamic_models = Column(Boolean, default=False)
    auth_type = Column(String, default="bearer")
    default_model = Column(String, nullable=True)
    
    # Configuration and credentials (encrypted)
    config = Column(JSON, nullable=True)
    credentials = Column(Text, nullable=True)  # Encrypted
    
    # Status and monitoring
    status = Column(String, default=ProviderStatus.ACTIVE.value)
    last_tested = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    models = relationship("AIProviderModel", back_populates="provider", cascade="all, delete-orphan")
    usage_logs = relationship("AIUsageLog", back_populates="provider", cascade="all, delete-orphan")

class AIProviderModel(Base):
    """AI Provider Model"""
    __tablename__ = "ai_provider_models"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    model_id = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    model_type = Column(String, default=ModelType.CHAT.value)
    description = Column(Text, nullable=True)
    
    # Model capabilities
    supports_system_messages = Column(Boolean, default=True)
    supports_function_calling = Column(Boolean, default=False)
    supports_streaming = Column(Boolean, default=True)
    supports_vision = Column(Boolean, default=False)
    
    # Pricing information
    input_cost_per_token = Column(Float, nullable=True)
    output_cost_per_token = Column(Float, nullable=True)
    
    # Context limits
    max_tokens = Column(Integer, nullable=True)
    context_window = Column(Integer, nullable=True)
    
    # Status
    is_available = Column(Boolean, default=True)
    last_verified = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("AIProvider", back_populates="models")

class AIUsageLog(Base):
    """AI Usage Log"""
    __tablename__ = "ai_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    
    # Request details
    model_name = Column(String, nullable=False)
    request_type = Column(String, nullable=False)  # chat, completion, embedding, etc.
    
    # Usage metrics
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost calculation
    input_cost = Column(Float, default=0.0)
    output_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Performance metrics
    response_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Request/response data (optional, for debugging)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provider = relationship("AIProvider", back_populates="usage_logs")

# Knowledge Base Models

class KnowledgeBase(Base):
    """Knowledge Base model"""
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")

class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    document_metadata = Column(JSON, nullable=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

# Export all models
__all__ = [
    "Base",
    "User", "Project", "Analysis",
    "AIProvider", "AIProviderModel", "AIUsageLog",
    "KnowledgeBase", "Document",
    "ProviderType", "ModelType", "ProviderStatus",
    "ProjectStatus", "ProjectType", "UserRole"
]
