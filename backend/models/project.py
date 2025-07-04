from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ProjectType(str, Enum):
    """Project type enumeration"""
    ROMANTIC = "romantic"
    FAMILY = "family"
    FRIENDSHIP = "friendship"
    PROFESSIONAL = "professional"
    OTHER = "other"

class Project(BaseModel):
    """Main Project model for relationship projects"""
    
    id: Optional[str] = Field(None, description="Unique project identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Current project status")
    project_type: Optional[ProjectType] = Field(ProjectType.OTHER, description="Type of relationship")
    
    # Participants
    participants: List[str] = Field(default_factory=list, description="List of participant names")
    
    # Metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Analysis data
    analysis_count: int = Field(0, description="Number of analyses performed")
    last_analysis_date: Optional[datetime] = Field(None, description="Date of last analysis")
    
    # Goals and objectives
    goals: List[str] = Field(default_factory=list, description="Project goals")
    milestones: List[Dict[str, Any]] = Field(default_factory=list, description="Project milestones")
    analyses: List[Dict[str, Any]] = Field(default_factory=list, description="Project analyses")
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project-specific settings")
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        },
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Improving Communication with Partner",
                "description": "A project focused on enhancing daily communication patterns",
                "status": "active",
                "project_type": "romantic",
                "participants": ["Alice", "Bob"],
                "goals": [
                    "Reduce misunderstandings",
                    "Increase quality time together",
                    "Improve conflict resolution"
                ],
                "settings": {
                    "notifications_enabled": True,
                    "analysis_frequency": "weekly"
                }
            }
        }
    }

class ProjectAnalysis(BaseModel):
    """Model for storing project analysis results"""
    
    id: Optional[int] = Field(None, description="Analysis ID")
    project_id: int = Field(..., description="Associated project ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    
    # Analysis results
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment score (-1 to 1)")
    key_insights: List[str] = Field(default_factory=list, description="Key insights from analysis")
    recommendations: List[str] = Field(default_factory=list, description="AI recommendations")
    
    # Metrics
    communication_score: Optional[float] = Field(None, ge=0, le=10, description="Communication quality score")
    relationship_health: Optional[float] = Field(None, ge=0, le=10, description="Overall relationship health score")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    data_source: str = Field(..., description="Source of analyzed data")
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw analysis data")
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class ProjectMilestone(BaseModel):
    """Model for project milestones"""
    
    id: Optional[int] = Field(None, description="Milestone ID")
    project_id: int = Field(..., description="Associated project ID")
    title: str = Field(..., min_length=1, max_length=200, description="Milestone title")
    description: Optional[str] = Field(None, max_length=500, description="Milestone description")
    
    # Status and dates
    completed: bool = Field(False, description="Whether milestone is completed")
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    completed_date: Optional[datetime] = Field(None, description="Actual completion date")
    
    # Progress tracking
    progress_percentage: float = Field(0, ge=0, le=100, description="Progress percentage")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }