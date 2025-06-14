from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator, root_validator
import re
from datetime import datetime


class ProjectNameValidator(BaseModel):
    """Validator for project names."""
    
    @staticmethod
    def validate_project_name(name: str) -> str:
        """Validate project name format and content."""
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        
        name = name.strip()
        
        if len(name) < 3:
            raise ValueError("Project name must be at least 3 characters long")
        
        if len(name) > 100:
            raise ValueError("Project name cannot exceed 100 characters")
        
        # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            raise ValueError("Project name can only contain letters, numbers, spaces, hyphens, and underscores")
        
        return name


class TextContentValidator(BaseModel):
    """Validator for text content analysis."""
    
    @staticmethod
    def validate_text_content(content: str) -> str:
        """Validate text content for analysis."""
        if not content or not content.strip():
            raise ValueError("Text content cannot be empty")
        
        content = content.strip()
        
        if len(content) < 10:
            raise ValueError("Text content must be at least 10 characters long for meaningful analysis")
        
        if len(content) > 50000:  # 50KB limit
            raise ValueError("Text content cannot exceed 50,000 characters")
        
        return content


class WebSocketMessageValidator(BaseModel):
    """Validator for WebSocket messages."""
    
    @staticmethod
    def validate_message_type(message_type: str) -> str:
        """Validate WebSocket message type."""
        valid_types = {
            "whisper_message", "analysis_request", "project_update", 
            "status_update", "error", "ping", "pong"
        }
        
        if message_type not in valid_types:
            raise ValueError(f"Invalid message type. Must be one of: {', '.join(valid_types)}")
        
        return message_type


class EnhancedProjectCreate(BaseModel):
    """Enhanced project creation model with validation."""
    
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    goals: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        return ProjectNameValidator.validate_project_name(v)
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v
    
    @validator('goals')
    def validate_goals(cls, v):
        if v:
            # Remove empty goals and validate each goal
            validated_goals = []
            for goal in v:
                if isinstance(goal, str) and goal.strip():
                    goal = goal.strip()
                    if len(goal) > 200:
                        raise ValueError("Each goal cannot exceed 200 characters")
                    validated_goals.append(goal)
            return validated_goals
        return []
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v:
            # Ensure metadata values are JSON serializable
            try:
                import json
                json.dumps(v)
            except (TypeError, ValueError):
                raise ValueError("Metadata must contain JSON-serializable values")
            
            # Limit metadata size
            if len(str(v)) > 5000:
                raise ValueError("Metadata cannot exceed 5000 characters when serialized")
        
        return v or {}


class EnhancedTextAnalysisRequest(BaseModel):
    """Enhanced text analysis request model with validation."""
    
    content: str = Field(..., min_length=10, max_length=50000)
    project_id: Optional[str] = Field(None, regex=r'^[a-f0-9-]{36}$')
    analysis_type: Optional[str] = Field("comprehensive", regex=r'^(comprehensive|sentiment|keywords|summary)$')
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        return TextContentValidator.validate_text_content(v)
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v and len(str(v)) > 2000:
            raise ValueError("Analysis metadata cannot exceed 2000 characters when serialized")
        return v or {}


class EnhancedWhisperMessage(BaseModel):
    """Enhanced Whisper message model with validation."""
    
    content: str = Field(..., min_length=1, max_length=10000)
    sender: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., regex=r'^(discord|slack|teams|zoom|generic)$')
    project_id: Optional[str] = Field(None, regex=r'^[a-f0-9-]{36}$')
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message content cannot be empty")
        return v
    
    @validator('sender')
    def validate_sender(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Sender cannot be empty")
        # Basic email or username validation
        if '@' in v:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError("Invalid email format for sender")
        return v
    
    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        if v is None:
            return datetime.now()
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v and len(str(v)) > 1000:
            raise ValueError("Message metadata cannot exceed 1000 characters when serialized")
        return v or {}


class SecurityValidator:
    """Security-focused validation utilities."""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input text to prevent injection attacks."""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '`']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    @staticmethod
    def validate_file_path(path: str) -> str:
        """Validate file path to prevent directory traversal."""
        if not isinstance(path, str):
            raise ValueError("Path must be a string")
        
        # Check for directory traversal attempts
        if '..' in path or path.startswith('/'):
            raise ValueError("Invalid file path")
        
        # Only allow alphanumeric, hyphens, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9._-]+$', path):
            raise ValueError("File path contains invalid characters")
        
        return path
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> str:
        """Validate UUID format."""
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(uuid_pattern, uuid_string.lower()):
            raise ValueError("Invalid UUID format")
        return uuid_string.lower()