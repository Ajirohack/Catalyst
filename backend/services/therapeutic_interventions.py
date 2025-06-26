# -*- coding: utf-8 -*-
"""
Therapeutic Intervention Recommendations Service for Catalyst
Provides AI-powered therapeutic interventions and recommendations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Import schema models
from schemas.intervention_schema import (
    TherapeuticApproach,
    InterventionCategory,
    EvidenceLevel,
    ProgressStatus,
    InterventionSuggestion,
    InterventionPlan as SchemaPlan,
    InterventionRecommendationRequest,
    InterventionRecommendationResponse
)

logger = logging.getLogger(__name__)


class InterventionFramework:
    """
    Main intervention framework service that provides therapeutic
    interventions, suggestions, and progress tracking.
    """

    def __init__(self):
        """Initialize the intervention framework with a library of
        interventions."""
        self._intervention_suggestions = (
            self._initialize_intervention_library()
        )
        # Dictionary to store intervention plans by ID
        self._intervention_plans = {}

    def _initialize_intervention_library(self) -> Dict[
            str, InterventionSuggestion]:
        """
        Initialize a comprehensive library of intervention suggestions.

        Returns:
            Dict[str, InterventionSuggestion]: Dictionary of intervention
            suggestions keyed by ID
        """
        interventions = {}

        # Add CBT interventions
        interventions.update(self._create_cbt_interventions())

        # Add DBT interventions
        interventions.update(self._create_dbt_interventions())

        # Add ACT interventions
        interventions.update(self._create_act_interventions())

        # Add Mindfulness interventions
        interventions.update(self._create_mindfulness_interventions())

        # Add Solution-Focused interventions
        interventions.update(self._create_solution_focused_interventions())

        # Add additional intervention types
        interventions.update(self._create_narrative_interventions())
        interventions.update(self._create_psychodynamic_interventions())
        interventions.update(self._create_humanistic_interventions())
        interventions.update(self._create_motivational_interventions())
        interventions.update(self._create_family_systems_interventions())

        return interventions

    def _create_cbt_interventions(self) -> Dict[str, InterventionSuggestion]:
        """Create Cognitive Behavioral Therapy interventions."""
        interventions = {}

        # Thought Record
        thought_record_id = str(uuid.uuid4())
        interventions[thought_record_id] = InterventionSuggestion(
            id=thought_record_id,
            title="Thought Record",
            description=(
                "A structured technique to identify, examine, and "
                "challenge negative or unhelpful thought patterns."
            ),
            therapeutic_approaches=[TherapeuticApproach.CBT],
            categories=[
                InterventionCategory.EMOTIONAL_REGULATION,
                InterventionCategory.STRESS_MANAGEMENT
            ],
            steps=[
                "Identify the triggering situation or event",
                "Notice and record your immediate thoughts",
                "Identify the emotions you're experiencing",
                "Rate the intensity of your emotions (1-10)",
                "Examine the evidence for and against your thoughts",
                "Develop a more balanced, realistic thought",
                "Re-rate your emotional intensity",
                "Plan a helpful behavioral response"
            ],
            estimated_duration="15-30 minutes per session",
            difficulty_level=2,
            evidence={
                "evidence_level": EvidenceLevel.HIGH,
                "research_summary": (
                    "Extensive research supports the effectiveness of "
                    "thought records in reducing anxiety and depression."
                ),
                "effectiveness_rating": 4.5
            },
            contraindications=[
                "Severe cognitive impairment",
                "Active psychosis",
                "Extreme emotional dysregulation"
            ],
            expected_outcomes=[
                "Increased awareness of thought patterns",
                "Reduced emotional reactivity",
                "Improved problem-solving skills",
                "Greater emotional regulation"
            ],
            resources_needed=[
                "Thought record worksheet",
                "Pen or digital device",
                "Quiet space for reflection"
            ],
            related_interventions=[]
        )

        return interventions

    def _create_dbt_interventions(self) -> Dict[str, InterventionSuggestion]:
        """Create Dialectical Behavior Therapy interventions."""
        interventions = {}
        
        # TIPP Skill
        tipp_id = str(uuid.uuid4())
        interventions[tipp_id] = InterventionSuggestion(
            id=tipp_id,
            title="TIPP Skill",
            description="Temperature, Intense exercise, Paced breathing, Paired muscle relaxation for crisis survival.",
            therapeutic_approaches=[TherapeuticApproach.DBT],
            categories=[InterventionCategory.EMOTIONAL_REGULATION, InterventionCategory.STRESS_MANAGEMENT],
            steps=[
                "Use cold water on face or hold ice cubes",
                "Do intense exercise for 10-15 minutes",
                "Practice paced breathing (exhale longer than inhale)",
                "Tense and release muscle groups"
            ],
            estimated_duration="10-20 minutes",
            difficulty_level=3,
            evidence={
                "evidence_level": EvidenceLevel.HIGH,
                "research_summary": "TIPP skills are effective for rapid emotional regulation in crisis situations.",
                "effectiveness_rating": 4.0
            },
            contraindications=["Severe physical health conditions"],
            expected_outcomes=["Rapid emotional regulation", "Reduced crisis intensity"],
            resources_needed=["Cold water or ice", "Space for movement"],
            related_interventions=[]
        )
        
        return interventions

    def _create_act_interventions(self) -> Dict[str, InterventionSuggestion]:
        """Create Acceptance and Commitment Therapy interventions."""
        interventions = {}
        
        # Values Clarification
        values_id = str(uuid.uuid4())
        interventions[values_id] = InterventionSuggestion(
            id=values_id,
            title="Values Clarification Exercise",
            description="An exercise to identify and clarify personal values "
                       "to guide meaningful action.",
            therapeutic_approaches=[TherapeuticApproach.ACT],
            categories=[InterventionCategory.PROBLEM_SOLVING,
                       InterventionCategory.STRESS_MANAGEMENT],
            steps=[
                "Reflect on what matters most to you in life",
                "Write down your top 5-10 values",
                "Rate how well you're currently living each value (1-10)",
                "Identify specific actions that align with your values",
                "Choose one small step to take today"
            ],
            estimated_duration="20-30 minutes",
            difficulty_level=2,
            evidence={
                "evidence_level": EvidenceLevel.HIGH,
                "research_summary": "Values clarification improves psychological flexibility and life satisfaction.",
                "effectiveness_rating": 4.2
            },
            contraindications=["Severe cognitive impairment"],
            expected_outcomes=["Increased clarity of values",
                              "Enhanced motivation", "Better decision-making"],
            resources_needed=["Paper and pen", "Quiet reflection time"],
            related_interventions=[]
        )
        
        return interventions

    def _create_mindfulness_interventions(self) -> Dict[
            str, InterventionSuggestion]:
        """Create Mindfulness-based interventions."""
        interventions = {}
        
        # Body Scan Meditation
        body_scan_id = str(uuid.uuid4())
        interventions[body_scan_id] = InterventionSuggestion(
            id=body_scan_id,
            title="Body Scan Meditation",
            description="A mindfulness practice that involves systematically "
                       "focusing attention on different parts of the body.",
            therapeutic_approaches=[TherapeuticApproach.MINDFULNESS],
            categories=[InterventionCategory.STRESS_MANAGEMENT,
                       InterventionCategory.EMOTIONAL_REGULATION],
            steps=[
                "Find a comfortable lying or sitting position",
                "Close your eyes and take three deep breaths",
                "Start at the top of your head and slowly scan down",
                "Notice sensations in each body part without judgment",
                "Spend 30-60 seconds on each area",
                "End with awareness of the whole body"
            ],
            estimated_duration="15-45 minutes",
            difficulty_level=2,
            evidence={
                "evidence_level": EvidenceLevel.HIGH,
                "research_summary": "Body scan meditation reduces stress and improves body awareness.",
                "effectiveness_rating": 4.5
            },
            contraindications=["Severe dissociation", "Active psychosis"],
            expected_outcomes=["Increased body awareness", "Reduced tension",
                              "Improved relaxation"],
            resources_needed=["Quiet space", "Comfortable surface"],
            related_interventions=[]
        )
        
        return interventions

    def _create_solution_focused_interventions(self) -> Dict[
            str, InterventionSuggestion]:
        """Create Solution-Focused interventions."""
        return {}

    def _create_narrative_interventions(self) -> Dict[
            str, InterventionSuggestion]:
        """Create Narrative Therapy interventions."""
        return {}

    def _create_psychodynamic_interventions(self) -> Dict[
            str, InterventionSuggestion]:
        """Create Psychodynamic interventions."""
        return {}

    def _create_humanistic_interventions(self) -> Dict[
            str, InterventionSuggestion]:
        """Create Humanistic interventions."""
        return {}

    def _create_motivational_interventions(self) -> (
            Dict[str, InterventionSuggestion]):
        """Create Motivational Interviewing interventions."""
        return {}

    def _create_family_systems_interventions(self) -> (
            Dict[str, InterventionSuggestion]):
        """Create Family Systems interventions."""
        return {}

    def get_intervention_recommendations(
        self,
        request: InterventionRecommendationRequest
    ) -> InterventionRecommendationResponse:
        """
        Get personalized intervention recommendations based on user profile
        and preferences.
        """
        try:
            # Filter interventions based on focus categories
            relevant_interventions = []
            for intervention in self._intervention_suggestions.values():
                # Check if intervention matches any focus categories
                if any(cat in intervention.categories
                       for cat in request.focus_categories):
                    relevant_interventions.append(intervention)

            # Filter by preferred approaches if specified
            if request.preferred_approaches:
                filtered_interventions = []
                for intervention in relevant_interventions:
                    if any(approach in intervention.therapeutic_approaches
                           for approach in request.preferred_approaches):
                        filtered_interventions.append(intervention)
                relevant_interventions = filtered_interventions

            # Filter by difficulty range if specified
            if request.difficulty_range:
                min_diff = request.difficulty_range.get('min', 1)
                max_diff = request.difficulty_range.get('max', 5)
                relevant_interventions = [
                    intervention for intervention in relevant_interventions
                    if min_diff <= intervention.difficulty_level <= max_diff
                ]

            # Exclude specified interventions
            if request.excluded_intervention_ids:
                relevant_interventions = [
                    intervention for intervention in relevant_interventions
                    if intervention.id not in request.excluded_intervention_ids
                ]

            # Sort by evidence level and effectiveness
            def sort_key(intervention):
                evidence = intervention.evidence
                effectiveness = evidence.get('effectiveness_rating', 0)
                evidence_level = evidence.get('evidence_level', '')
                level_score = {
                    EvidenceLevel.HIGH: 3,
                    EvidenceLevel.MODERATE: 2,
                    EvidenceLevel.LOW: 1
                }.get(evidence_level, 0)
                return (level_score, effectiveness)

            relevant_interventions.sort(key=sort_key, reverse=True)

            # Limit to top 10 recommendations
            top_interventions = relevant_interventions[:10]

            # Generate rationale
            rationale = {
                "matching_criteria": (
                    f"Found {len(top_interventions)} interventions matching "
                    f"categories: {', '.join(request.focus_categories)}"
                ),
                "filtering_applied": (
                    "Filtered by preferred approaches and difficulty level"
                    if request.preferred_approaches or request.difficulty_range
                    else "No additional filtering applied"
                ),
                "sorting_method": (
                    "Sorted by evidence level and effectiveness rating"
                )
            }

            return InterventionRecommendationResponse(
                recommended_interventions=top_interventions,
                recommendation_rationale=rationale
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return InterventionRecommendationResponse(
                recommended_interventions=[],
                recommendation_rationale={
                    "error": f"Failed to generate recommendations: {str(e)}"
                }
            )

    def get_intervention_by_id(self, intervention_id: str) -> Optional[InterventionSuggestion]:
        """Get a specific intervention by ID."""
        return self._intervention_suggestions.get(intervention_id)

    def get_interventions_by_category(self, category: str) -> List[InterventionSuggestion]:
        """Get interventions filtered by category."""
        # Convert category string to enum if needed
        if isinstance(category, str):
            category_value = category
        else:
            category_value = category.value if hasattr(category, 'value') else str(category)
        
        matching_interventions = []
        for intervention in self._intervention_suggestions.values():
            intervention_categories = []
            if hasattr(intervention, 'categories'):
                intervention_categories = [
                    cat.value if hasattr(cat, 'value') else str(cat)
                    for cat in intervention.categories
                ]
            elif isinstance(intervention, dict) and 'categories' in intervention:
                intervention_categories = intervention['categories']
            
            if category_value in intervention_categories:
                matching_interventions.append(intervention)
        
        return matching_interventions

    def get_interventions_by_approach(
            self, approach: str) -> List[InterventionSuggestion]:
        """Get all interventions for a specific therapeutic approach."""
        # Convert approach string to enum if needed
        if isinstance(approach, str):
            approach_value = approach
        else:
            approach_value = (
                approach.value if hasattr(approach, 'value')
                else str(approach)
            )
        
        matching_interventions = []
        for intervention in self._intervention_suggestions.values():
            intervention_approaches = []
            if hasattr(intervention, 'therapeutic_approaches'):
                intervention_approaches = [
                    app.value if hasattr(app, 'value') else str(app)
                    for app in intervention.therapeutic_approaches
                ]
            elif (isinstance(intervention, dict) and
                  'therapeutic_approaches' in intervention):
                intervention_approaches = intervention[
                    'therapeutic_approaches']
            
            if approach_value in intervention_approaches:
                matching_interventions.append(intervention)
        
        return matching_interventions

    def get_intervention_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific intervention plan by ID."""
        return self._intervention_plans.get(plan_id)

    def get_user_intervention_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all intervention plans for a specific user."""
        plans = [
            plan for plan in self._intervention_plans.values()
            if plan.get("user_id") == user_id
        ]
        # Ensure each plan has the required fields for validation
        for plan in plans:
            if "id" not in plan:
                plan["id"] = plan.get("plan_id", str(uuid.uuid4()))
            if "name" not in plan:
                plan["name"] = plan.get("title", "Unnamed Plan")
        return plans

    def add_intervention_to_plan(self, plan_id: str, intervention_id: str) -> Dict[str, Any]:
        """Add an intervention to an existing plan."""
        plan = self._intervention_plans.get(plan_id)
        if not plan:
            raise KeyError(f"Plan with ID {plan_id} not found")
        
        intervention = self.get_intervention_by_id(intervention_id)
        if not intervention:
            raise KeyError(
                f"Intervention with ID {intervention_id} not found"
            )
        
        if "interventions" not in plan:
            plan["interventions"] = []
        if "active_interventions" not in plan:
            plan["active_interventions"] = []
        
        plan["interventions"].append({
            "intervention_id": intervention_id,
            "added_at": datetime.now().isoformat(),
            "status": "not_started"
        })
        
        # Add to active interventions list
        if intervention_id not in plan["active_interventions"]:
            plan["active_interventions"].append(intervention_id)
        
        return plan

    def update_intervention_progress(
        self,
        plan_id: str,
        intervention_id: str,
        progress_data: Any
    ) -> Dict[str, Any]:
        """Update the progress of an intervention in a plan."""
        plan = self._intervention_plans.get(plan_id)
        if not plan:
            raise KeyError(f"Plan with ID {plan_id} not found")
        
        intervention = self.get_intervention_by_id(intervention_id)
        if not intervention:
            raise KeyError(
                f"Intervention with ID {intervention_id} not found"
            )
        
        # Convert progress_data to dict if it's a Pydantic model
        if hasattr(progress_data, 'model_dump'):
            progress_dict = progress_data.model_dump()
        elif hasattr(progress_data, 'dict'):
            progress_dict = progress_data.model_dump()
        elif isinstance(progress_data, dict):
            progress_dict = progress_data
        else:
            # Fallback: try to access attributes directly
            progress_dict = {
                "status": getattr(progress_data, 'status', 'not_started'),
                "notes": getattr(progress_data, 'notes', ''),
                "perceived_effectiveness": getattr(
                    progress_data, 'perceived_effectiveness', None),
                "challenges_encountered": getattr(
                    progress_data, 'challenges_encountered', []),
                "modifications_made": getattr(
                    progress_data, 'modifications_made', ''),
                "time_spent": getattr(progress_data, 'time_spent', 0)
            }
        
        # Find the intervention in the plan
        interventions = plan.get("interventions", [])
        intervention_found = False
        
        for i, plan_intervention in enumerate(interventions):
            if plan_intervention.get("intervention_id") == intervention_id:
                # Update the intervention progress
                plan_intervention.update({
                    "status": progress_dict.get("status", "not_started"),
                    "notes": progress_dict.get("notes", ""),
                    "perceived_effectiveness": progress_dict.get(
                        "perceived_effectiveness"),
                    "challenges_encountered": progress_dict.get(
                        "challenges_encountered", []),
                    "modifications_made": progress_dict.get(
                        "modifications_made", ""),
                    "time_spent": progress_dict.get("time_spent", 0),
                    "updated_at": datetime.now().isoformat()
                })
                intervention_found = True
                break
        
        if not intervention_found:
            # Add the intervention to the plan if it's not there
            self.add_intervention_to_plan(plan_id, intervention_id)
            # Then update its progress
            return self.update_intervention_progress(
                plan_id, intervention_id, progress_data)
        
        # Return progress summary
        return self.get_intervention_plan_progress(plan_id)

    def get_intervention_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """Get progress summary for an intervention plan."""
        plan = self._intervention_plans.get(plan_id)
        if not plan:
            raise KeyError(f"Plan with ID {plan_id} not found")
        
        interventions = plan.get("interventions", [])
        total_interventions = len(interventions)
        completed_interventions = sum(
            1 for intervention in interventions
            if intervention.get("status") == "completed"
        )
        
        progress_percentage = (
            (completed_interventions / total_interventions * 100)
            if total_interventions > 0 else 0
        )
        
        return {
            "plan_id": plan_id,
            "total_interventions": total_interventions,
            "completed_interventions": completed_interventions,
            "progress_percentage": progress_percentage,
            "overall_progress": progress_percentage,  # Expected by tests
            "intervention_progress": interventions,  # Expected by tests
            "last_updated": datetime.now().isoformat()
        }

    def create_intervention_plan(self, **kwargs) -> Dict[str, Any]:
        """Create and store a new intervention plan."""
        # Provide default values for required parameters
        defaults = {
            'title': kwargs.get('title', 'Personalized Intervention Plan'),
            'primary_approach': kwargs.get(
                'primary_approach', TherapeuticApproach.CBT.value),
            'target_categories': kwargs.get(
                'target_categories',
                [InterventionCategory.EMOTIONAL_REGULATION.value])
        }
        # Merge with provided kwargs
        plan_kwargs = {**defaults, **kwargs}
        plan = create_new_intervention_plan(**plan_kwargs)
        plan_id = plan["id"]
        self._intervention_plans[plan_id] = plan
        return plan


# Create global instance
intervention_framework = InterventionFramework()

# Create alias for backward compatibility
TherapeuticInterventionService = InterventionFramework


def get_intervention_recommendations(
    request: InterventionRecommendationRequest
) -> InterventionRecommendationResponse:
    """Get intervention recommendations based on user profile."""
    return intervention_framework.get_intervention_recommendations(request)


def create_new_intervention_plan(
    user_id: str,
    title: str,
    primary_approach: str,
    target_categories: List[str],
    **kwargs
) -> Dict[str, Any]:
    """Create a new intervention plan for a user."""
    # Placeholder implementation
    plan_id = str(uuid.uuid4())
    
    # Handle enum conversion for primary_approach
    if hasattr(primary_approach, 'value'):
        # If it's an enum, use its value
        approach_value = primary_approach.value
    else:
        # If it's a string, use it directly
        approach_value = primary_approach
    
    # Handle target_categories enum conversion
    processed_categories = []
    for cat in target_categories:
        if hasattr(cat, 'value'):
            # If it's an enum, use its value
            processed_categories.append(cat.value)
        else:
            # If it's a string, use it directly
            processed_categories.append(cat)
    
    return {
        "id": plan_id,
        "plan_id": plan_id,  # Include both for compatibility
        "user_id": user_id,
        "title": title,
        "name": title,  # For compatibility
        "primary_approach": approach_value,  # Return enum value
        "primary_approaches": [approach_value],  # Expected by tests
        "target_categories": processed_categories,
        "focus_areas": processed_categories,  # Expected by tests
        "goals": kwargs.get("goals", []),
        "description": kwargs.get("description", ""),
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "active_interventions": [],
        "interventions": []
    }


def update_intervention_progress(
    plan_id: str,
    intervention_id: str,
    status: ProgressStatus,
    notes: str,
    effectiveness_rating: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Update the progress of an intervention and return the updated plan
    summary."""
    # Placeholder implementation
    return {
        "plan_id": plan_id,
        "intervention_id": intervention_id,
        "status": status,
        "notes": notes,
        "effectiveness_rating": effectiveness_rating,
        "updated_at": datetime.now().isoformat()
    }


def get_available_categories() -> List[Dict[str, str]]:
    """Get all available intervention categories."""
    return [
        {"value": "communication", "name": "Communication"},
        {"value": "conflict_resolution", "name": "Conflict Resolution"},
        {"value": "emotional_regulation", "name": "Emotional Regulation"},
        {"value": "boundary_setting", "name": "Boundary Setting"},
        {"value": "intimacy_building", "name": "Intimacy Building"},
        {"value": "trust_building", "name": "Trust Building"},
        {"value": "stress_management", "name": "Stress Management"},
        {"value": "problem_solving", "name": "Problem Solving"},
        {"value": "trauma_processing", "name": "Trauma Processing"},
        {"value": "attachment_work", "name": "Attachment Work"}
    ]


def get_available_approaches() -> List[Dict[str, str]]:
    """Get all available therapeutic approaches."""
    return [
        {"value": "cbt", "name": "Cognitive Behavioral Therapy"},
        {"value": "dbt", "name": "Dialectical Behavior Therapy"},
        {"value": "act", "name": "Acceptance and Commitment Therapy"},
        {"value": "mindfulness", "name": "Mindfulness-Based"},
        {"value": "solution_focused", "name": "Solution-Focused"},
        {"value": "narrative", "name": "Narrative Therapy"},
        {"value": "psychodynamic", "name": "Psychodynamic"},
        {"value": "humanistic", "name": "Humanistic"},
        {"value": "motivational", "name": "Motivational Interviewing"},
        {"value": "family_systems", "name": "Family Systems"}
    ]


def generate_intervention_plan(
    user_id: str,
    title: str,
    primary_approach: str,
    target_categories: List[str],
    **kwargs
) -> Dict[str, Any]:
    """Generate a new intervention plan."""
    # Convert string parameters to proper types if needed
    try:
        from backend.schemas.intervention_schema import (
            TherapeuticApproach as SchemaApproach,
            InterventionCategory
        )
        approach = getattr(SchemaApproach, primary_approach.upper(),
                          primary_approach)
        categories = [
            getattr(InterventionCategory, cat.upper(), cat)
            for cat in target_categories
        ]
    except (ImportError, AttributeError):
        # Use fallback approach
        approach = primary_approach
        categories = target_categories

    return create_new_intervention_plan(
        user_id=user_id,
        title=title,
        primary_approach=approach,
        target_categories=categories,
        **kwargs
    )