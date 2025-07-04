"""Therapeutic Interventions Router

This module defines the API endpoints for the therapeutic intervention system,
allowing clients to interact with intervention approaches, suggestions, and progress tracking.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from pydantic import UUID4
import uuid

try:
    from backend.schemas.intervention_schema import (
        TherapeuticApproach,
        InterventionCategory,
        ProgressStatus,
        InterventionSuggestion,
        ProgressUpdate,
        InterventionPlan,
        InterventionRecommendationRequest,
        InterventionRecommendationResponse
    )
except ImportError:
    # Fallback schemas if not available
    from pydantic import BaseModel
    
    class TherapeuticApproach(BaseModel):
        name: str
        description: str
    
    class InterventionCategory(BaseModel):
        name: str
        description: str
    
    class ProgressStatus(BaseModel):
        status: str
    
    class InterventionSuggestion(BaseModel):
        title: str
        description: str
    
    class ProgressUpdate(BaseModel):
        progress: float
    
    class InterventionPlan(BaseModel):
        id: str
        name: str
    
    class InterventionRecommendationRequest(BaseModel):
        user_id: str
    
    class InterventionRecommendationResponse(BaseModel):
        recommendations: List[str]

# Import service functions
from services.therapeutic_interventions import (
    intervention_framework,
    get_available_approaches,
    get_available_categories,
    get_intervention_recommendations
)

# Create router
router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/approaches", response_model=List[Dict[str, str]])
async def list_therapeutic_approaches():
    """Get a list of all supported therapeutic approaches."""
    return get_available_approaches()


@router.get("/categories", response_model=List[Dict[str, str]])
async def list_intervention_categories():
    """Get a list of all intervention categories."""
    return get_available_categories()


@router.get("/suggestions/{intervention_id}", response_model=InterventionSuggestion)
async def get_intervention_suggestion(
    intervention_id: str = Path(..., description="The ID of the intervention to retrieve")
):
    """Get a specific intervention suggestion by ID."""
    suggestion = intervention_framework.get_intervention_by_id(intervention_id)
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervention with ID {intervention_id} not found"
        )
    return suggestion


@router.get("/suggestions/by-category/{category}", response_model=List[InterventionSuggestion])
async def get_interventions_by_category(
    category: str = Path(..., description="The category to filter interventions by")
):
    """Get all intervention suggestions for a specific category."""
    return intervention_framework.get_interventions_by_category(category)


@router.get("/suggestions/by-approach/{approach}", response_model=List[InterventionSuggestion])
async def get_interventions_by_approach(
    approach: str = Path(..., description="The therapeutic approach to filter interventions by")
):
    """Get all intervention suggestions for a specific therapeutic approach."""
    return intervention_framework.get_interventions_by_approach(approach)


@router.post("/recommend", response_model=InterventionRecommendationResponse)
async def recommend_interventions(
    request: InterventionRecommendationRequest
):
    """Get personalized intervention recommendations."""
    return get_intervention_recommendations(request)


@router.get("/user-approaches/{user_id}", response_model=List[Dict[str, str]])
async def get_user_therapeutic_approaches(
    user_id: str = Path(..., description="The ID of the user to get approaches for")
):
    """Get recommended therapeutic approaches for a specific user."""
    return get_available_approaches()


@router.post("/plans", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_intervention_plan(
    title: str = Query(..., description="Title of the intervention plan"),
    user_id: str = Query(..., description="ID of the user this plan is for"),
    primary_approach: str = Query(..., description="Primary therapeutic approach"),
    target_categories: List[str] = Query(..., description="Target intervention categories"),
    description: Optional[str] = Query(None, description="Description of the intervention plan"),
    goals: Optional[List[str]] = Query(None, description="Goals for this intervention plan")
):
    """Create a new intervention plan for a user."""
    # Convert enum string representations to their values
    processed_categories = []
    for cat in target_categories:
        if cat.startswith('InterventionCategory.'):
            # Extract the enum name and convert to value
            enum_name = cat.split('.')[-1]
            try:
                enum_obj = getattr(InterventionCategory, enum_name)
                processed_categories.append(enum_obj.value)
            except AttributeError:
                processed_categories.append(cat)
        else:
            processed_categories.append(cat)
    
    # Handle primary_approach enum conversion
    processed_approach = primary_approach
    if primary_approach.startswith('TherapeuticApproach.'):
        enum_name = primary_approach.split('.')[-1]
        try:
            enum_obj = getattr(TherapeuticApproach, enum_name)
            processed_approach = enum_obj.value
        except AttributeError:
            processed_approach = primary_approach
    
    plan = intervention_framework.create_intervention_plan(
        user_id=user_id,
        title=title,
        primary_approach=processed_approach,
        target_categories=processed_categories,
        description=description,
        goals=goals
    )
    # Ensure plan_id is in the response
    if "plan_id" not in plan and "id" in plan:
        plan["plan_id"] = plan["id"]
    return plan


@router.get("/plans/{plan_id}", response_model=InterventionPlan)
async def get_plan(
    plan_id: str = Path(..., description="The ID of the intervention plan to retrieve")
):
    """Get a specific intervention plan by ID."""
    plan = intervention_framework.get_intervention_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervention plan with ID {plan_id} not found"
        )
    return plan


@router.get("/plans/user/{user_id}", response_model=List[InterventionPlan])
async def get_user_plans(
    user_id: str = Path(..., description="The ID of the user to get plans for")
):
    """Get all intervention plans for a specific user."""
    return intervention_framework.get_user_intervention_plans(user_id)


@router.post("/plans/{plan_id}/interventions/{intervention_id}", response_model=Dict[str, Any])
async def add_intervention_to_plan(
    plan_id: str = Path(..., description="The ID of the intervention plan"),
    intervention_id: str = Path(..., description="The ID of the intervention to add")
):
    """Add an intervention to an existing plan."""
    try:
        return intervention_framework.add_intervention_to_plan(plan_id, intervention_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/plans/{plan_id}/interventions/{intervention_id}/progress", response_model=Dict[str, Any])
async def update_progress(
    plan_id: str = Path(..., description="The ID of the intervention plan"),
    intervention_id: str = Path(..., description="The ID of the intervention"),
    progress: ProgressUpdate = None
):
    """Update the progress of an intervention in a plan."""
    try:
        return intervention_framework.update_intervention_progress(
            plan_id=plan_id,
            intervention_id=intervention_id,
            progress_data=progress
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/plans/{plan_id}/progress", response_model=Dict[str, Any])
async def get_plan_progress(
    plan_id: str = Path(..., description="The ID of the intervention plan to get progress for")
):
    """Get a summary of progress for all interventions in a plan."""
    try:
        return intervention_framework.get_intervention_plan_progress(plan_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
