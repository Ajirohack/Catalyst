"""
Intervention Schema Module

This module defines the schema structures for the therapeutic intervention system,
including intervention approaches, suggestions, and progress tracking.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TherapeuticApproach(str, Enum):
    """Enumeration of supported therapeutic approaches."""
    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    ACT = "acceptance_commitment_therapy"
    MINDFULNESS = "mindfulness_based"
    SOLUTION_FOCUSED = "solution_focused"
    NARRATIVE = "narrative_therapy"
    PSYCHODYNAMIC = "psychodynamic"
    HUMANISTIC = "humanistic"
    MOTIVATIONAL = "motivational_interviewing"
    FAMILY_SYSTEMS = "family_systems"


class InterventionCategory(str, Enum):
    """Categories of interventions that can be suggested."""
    COMMUNICATION = "communication"
    CONFLICT_RESOLUTION = "conflict_resolution"
    EMOTIONAL_REGULATION = "emotional_regulation"
    BOUNDARY_SETTING = "boundary_setting"
    INTIMACY_BUILDING = "intimacy_building"
    TRUST_BUILDING = "trust_building"
    STRESS_MANAGEMENT = "stress_management"
    PROBLEM_SOLVING = "problem_solving"
    TRAUMA_PROCESSING = "trauma_processing"
    ATTACHMENT_WORK = "attachment_work"


class EvidenceLevel(str, Enum):
    """Levels of evidence supporting an intervention."""
    HIGH = "high"
    MODERATE = "moderate"
    PRELIMINARY = "preliminary"
    THEORETICAL = "theoretical"


class ProgressStatus(str, Enum):
    """Status of an intervention's progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class InterventionEvidence(BaseModel):
    """Schema for evidence supporting an intervention."""
    evidence_level: EvidenceLevel = Field(..., description="Level of evidence supporting this intervention")
    research_summary: str = Field(..., description="Brief summary of research supporting this intervention")
    source_citations: List[str] = Field(default=[], description="Academic citations supporting this intervention")
    effectiveness_rating: float = Field(..., ge=0.0, le=5.0, description="Effectiveness rating from 0-5")
    suitable_contexts: List[str] = Field(default=[], description="Contexts where this intervention is most effective")


class InterventionSuggestion(BaseModel):
    """Schema for a specific intervention suggestion."""
    id: str = Field(..., description="Unique identifier for the intervention suggestion")
    title: str = Field(..., description="Title of the intervention")
    description: str = Field(..., description="Detailed description of the intervention")
    therapeutic_approaches: List[TherapeuticApproach] = Field(
        ..., description="Therapeutic approaches this intervention is based on"
    )
    categories: List[InterventionCategory] = Field(..., description="Categories this intervention falls under")
    steps: List[str] = Field(..., description="Step-by-step instructions for implementing the intervention")
    estimated_duration: str = Field(..., description="Estimated time to complete (e.g., '15 minutes', '1 week')")
    difficulty_level: int = Field(..., ge=1, le=5, description="Difficulty level from 1-5")
    evidence: InterventionEvidence = Field(..., description="Evidence supporting this intervention")
    contraindications: List[str] = Field(default=[], description="Situations where this intervention may not be appropriate")
    expected_outcomes: List[str] = Field(..., description="Expected outcomes from successful implementation")
    resources_needed: List[str] = Field(default=[], description="Resources needed to implement this intervention")
    related_interventions: List[str] = Field(default=[], description="IDs of related interventions")


class ProgressUpdate(BaseModel):
    """Schema for tracking progress updates on an intervention."""
    timestamp: datetime = Field(default_factory=datetime.now, description="When this update was recorded")
    status: ProgressStatus = Field(..., description="Current status of the intervention")
    notes: str = Field(default="", description="Notes about the progress")
    perceived_effectiveness: Optional[int] = Field(None, ge=1, le=10, description="User rating of effectiveness (1-10)")
    challenges_encountered: List[str] = Field(default=[], description="Challenges encountered during implementation")
    modifications_made: str = Field(default="", description="Any modifications made to the original intervention")
    time_spent: Optional[int] = Field(None, description="Time spent on this intervention in minutes")


class InterventionProgress(BaseModel):
    """Schema for tracking progress on a specific intervention."""
    intervention_id: str = Field(..., description="ID of the intervention being tracked")
    user_id: str = Field(..., description="ID of the user implementing the intervention")
    start_date: datetime = Field(default_factory=datetime.now, description="When this intervention was started")
    target_completion_date: Optional[datetime] = Field(None, description="Target date to complete this intervention")
    current_status: ProgressStatus = Field(default=ProgressStatus.NOT_STARTED, description="Current status")
    progress_updates: List[ProgressUpdate] = Field(default=[], description="History of progress updates")
    completion_date: Optional[datetime] = Field(None, description="When this intervention was completed")
    overall_effectiveness: Optional[int] = Field(None, ge=1, le=10, description="Overall effectiveness rating (1-10)")
    outcomes_achieved: List[str] = Field(default=[], description="Specific outcomes achieved")


class InterventionPlan(BaseModel):
    """Schema for a complete intervention plan for a user."""
    id: str = Field(..., description="Unique identifier for this intervention plan")
    user_id: str = Field(..., description="ID of the user this plan is for")
    created_at: datetime = Field(default_factory=datetime.now, description="When this plan was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this plan was last updated")
    primary_approaches: List[TherapeuticApproach] = Field(
        ..., description="Primary therapeutic approaches for this user"
    )
    focus_areas: List[InterventionCategory] = Field(..., description="Areas of focus for interventions")
    active_interventions: List[str] = Field(default=[], description="IDs of currently active interventions")
    completed_interventions: List[str] = Field(default=[], description="IDs of completed interventions")
    notes: str = Field(default="", description="Clinical notes about this intervention plan")
    goals: List[str] = Field(..., description="Goals for this intervention plan")
    contraindicated_approaches: List[TherapeuticApproach] = Field(
        default=[], description="Approaches to avoid for this user"
    )


class InterventionRecommendationRequest(BaseModel):
    """Schema for requesting intervention recommendations."""
    user_id: str = Field(..., description="ID of the user requesting recommendations")
    focus_categories: List[InterventionCategory] = Field(
        ..., description="Categories to focus recommendations on"
    )
    preferred_approaches: Optional[List[TherapeuticApproach]] = Field(
        None, description="Preferred therapeutic approaches"
    )
    difficulty_range: Optional[Dict[str, int]] = Field(
        None, description="Desired difficulty range (min, max)"
    )
    excluded_intervention_ids: List[str] = Field(
        default=[], description="IDs of interventions to exclude"
    )
    context_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional context data for more personalized recommendations"
    )


class InterventionRecommendationResponse(BaseModel):
    """Schema for intervention recommendation responses."""
    recommended_interventions: List[InterventionSuggestion] = Field(
        ..., description="List of recommended interventions"
    )
    recommendation_rationale: Dict[str, str] = Field(
        ..., description="Rationale for each recommendation keyed by intervention ID"
    )
