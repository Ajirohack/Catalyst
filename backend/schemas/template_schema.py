"""Template Schema Module

This module defines the schema structures for the message template system,
including template categories, templates, and template usage tracking.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TemplateCategory(str, Enum):
    """Enumeration of supported template categories."""
    GREETING = "greeting"
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"
    QUESTION = "question"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"
    STATUS_UPDATE = "status_update"
    INTRODUCTION = "introduction"
    THANK_YOU = "thank_you"
    APOLOGY = "apology"
    REQUEST = "request"
    REMINDER = "reminder"
    CUSTOM = "custom"


class TemplateContext(str, Enum):
    """Contexts where templates can be used."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    CUSTOMER_SERVICE = "customer_service"
    HEALTHCARE = "healthcare"
    SALES = "sales"
    TECHNICAL = "technical"
    GENERAL = "general"


class TemplateUsageStatus(str, Enum):
    """Status of a template's usage."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class TemplateVariable(BaseModel):
    """Schema for variables that can be used in templates."""
    name: str = Field(..., description="Name of the variable")
    description: str = Field(..., description="Description of what the variable represents")
    default_value: Optional[str] = Field(None, description="Default value if not provided")
    required: bool = Field(default=False, description="Whether this variable is required")
    example: str = Field(..., description="Example value for this variable")


class Template(BaseModel):
    """Schema for a message template."""
    id: str = Field(..., description="Unique identifier for the template")
    title: str = Field(..., description="Title of the template")
    content: str = Field(..., description="Template content with variable placeholders")
    description: str = Field(..., description="Detailed description of the template")
    category: TemplateCategory = Field(..., description="Category this template falls under")
    contexts: List[TemplateContext] = Field(..., description="Contexts where this template is appropriate")
    variables: List[TemplateVariable] = Field(default=[], description="Variables used in this template")
    tags: List[str] = Field(default=[], description="Tags for searching and filtering templates")
    created_at: datetime = Field(default_factory=datetime.now, description="When this template was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this template was last updated")
    created_by: Optional[str] = Field(None, description="ID of the user who created this template")
    is_default: bool = Field(default=False, description="Whether this is a default system template")
    usage_count: int = Field(default=0, description="Number of times this template has been used")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Average user rating from 0-5")
    status: TemplateUsageStatus = Field(default=TemplateUsageStatus.ACTIVE, description="Current status of the template")


class TemplateUsage(BaseModel):
    """Schema for tracking template usage."""
    id: str = Field(..., description="Unique identifier for this usage record")
    template_id: str = Field(..., description="ID of the template used")
    user_id: str = Field(..., description="ID of the user who used the template")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation where the template was used")
    message_id: Optional[str] = Field(None, description="ID of the message that used the template")
    used_at: datetime = Field(default_factory=datetime.now, description="When the template was used")
    variables_used: Dict[str, str] = Field(default={}, description="Variables and values used in this instance")
    modified_content: Optional[str] = Field(None, description="Modified content if the template was customized")
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating of effectiveness (1-5)")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data for this usage")


class TemplateCreateRequest(BaseModel):
    """Schema for creating a new template."""
    title: str = Field(..., description="Title of the template")
    content: str = Field(..., description="Template content with variable placeholders")
    description: str = Field(..., description="Detailed description of the template")
    category: TemplateCategory = Field(..., description="Category this template falls under")
    contexts: List[TemplateContext] = Field(..., description="Contexts where this template is appropriate")
    variables: List[TemplateVariable] = Field(default=[], description="Variables used in this template")
    tags: List[str] = Field(default=[], description="Tags for searching and filtering templates")
    is_default: bool = Field(default=False, description="Whether this is a default system template")


class TemplateUpdateRequest(BaseModel):
    """Schema for updating an existing template."""
    title: Optional[str] = Field(None, description="Title of the template")
    content: Optional[str] = Field(None, description="Template content with variable placeholders")
    description: Optional[str] = Field(None, description="Detailed description of the template")
    category: Optional[TemplateCategory] = Field(None, description="Category this template falls under")
    contexts: Optional[List[TemplateContext]] = Field(None, description="Contexts where this template is appropriate")
    variables: Optional[List[TemplateVariable]] = Field(None, description="Variables used in this template")
    tags: Optional[List[str]] = Field(None, description="Tags for searching and filtering templates")
    status: Optional[TemplateUsageStatus] = Field(None, description="Current status of the template")


class TemplateSearchRequest(BaseModel):
    """Schema for searching templates."""
    query: Optional[str] = Field(None, description="Search query for template content or title")
    categories: Optional[List[TemplateCategory]] = Field(None, description="Filter by categories")
    contexts: Optional[List[TemplateContext]] = Field(None, description="Filter by contexts")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    created_by: Optional[str] = Field(None, description="Filter by creator ID")
    status: Optional[TemplateUsageStatus] = Field(None, description="Filter by status")
    is_default: Optional[bool] = Field(None, description="Filter by default status")
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Minimum rating threshold")


class TemplateSearchResponse(BaseModel):
    """Schema for template search responses."""
    templates: List[Template] = Field(..., description="List of templates matching the search criteria")
    total_count: int = Field(..., description="Total number of templates matching the search criteria")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Number of templates per page")
    search_metadata: Dict[str, Any] = Field(default={}, description="Additional metadata about the search")


class TemplateRenderRequest(BaseModel):
    """Schema for rendering a template with variables."""
    template_id: str = Field(..., description="ID of the template to render")
    variables: Dict[str, str] = Field(default={}, description="Variables and values to use in rendering")
    user_id: str = Field(..., description="ID of the user rendering the template")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation where the template will be used")


class TemplateRenderResponse(BaseModel):
    """Schema for template render responses."""
    rendered_content: str = Field(..., description="Rendered template content with variables replaced")
    template_id: str = Field(..., description="ID of the template that was rendered")
    usage_id: str = Field(..., description="ID of the usage record created")
    missing_variables: List[str] = Field(default=[], description="Variables that were missing and used defaults")
    template_metadata: Dict[str, Any] = Field(default={}, description="Additional metadata about the template")