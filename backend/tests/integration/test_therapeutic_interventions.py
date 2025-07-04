"""
Integration Tests for Therapeutic Interventions API

This module contains tests for the Therapeutic Interventions API endpoints.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import required dependencies
try:
    from fastapi.testclient import TestClient
    import uuid
    from backend.main import app
    from backend.schemas.intervention_schema import (
        TherapeuticApproach,
        InterventionCategory,
        ProgressStatus
    )
    from backend.services.therapeutic_interventions import intervention_framework
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)

client = TestClient(app)


@pytest.fixture
def seed_intervention_library():
    """Ensure the intervention library is initialized with test data."""
    # The library is automatically initialized when the framework is created
    return intervention_framework


@pytest.fixture
def sample_plan_id() -> str:
    """Get a sample intervention plan ID."""
    # Create a test plan and return its ID
    response = client.post(
        "/api/interventions/plans",
        params={
            "title": "Test Intervention Plan",
            "user_id": "test_user_123",
            "primary_approach": TherapeuticApproach.CBT,
            "target_categories": [
                InterventionCategory.COMMUNICATION,
                InterventionCategory.EMOTIONAL_REGULATION
            ],
            "description": "Test plan for integration tests",
            "goals": ["Improve communication", "Develop coping strategies"]
        }
    )
    
    assert response.status_code == 201
    return response.json()["plan_id"]


@pytest.fixture
def sample_intervention_id(seed_intervention_library) -> str:
    """Get a sample intervention ID."""
    # Get the first intervention from the library using a category that has
    # interventions
    interventions = intervention_framework.get_interventions_by_category(
        InterventionCategory.EMOTIONAL_REGULATION
    )
    assert len(interventions) > 0
    return interventions[0].id


def test_list_therapeutic_approaches():
    """Test listing all therapeutic approaches."""
    response = client.get("/api/interventions/approaches")
    assert response.status_code == 200
    
    approaches = response.json()
    assert isinstance(approaches, list)
    assert len(approaches) > 0
    
    # Check structure of each approach
    for approach in approaches:
        assert "value" in approach
        assert "name" in approach


def test_list_intervention_categories():
    """Test listing all intervention categories."""
    response = client.get("/api/interventions/categories")
    assert response.status_code == 200
    
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    
    # Check structure of each category
    for category in categories:
        assert "value" in category
        assert "name" in category


def test_get_interventions_by_category():
    """Test getting interventions by category."""
    # Test for each category
    for category in InterventionCategory:
        response = client.get(f"/api/interventions/suggestions/by-category/{category.value}")
        assert response.status_code == 200
        
        interventions = response.json()
        assert isinstance(interventions, list)
        
        # Not all categories may have interventions in the test library
        if interventions:
            # Check that each intervention contains the requested category
            for intervention in interventions:
                assert category.value in [cat for cat in intervention["categories"]]


def test_get_interventions_by_approach():
    """Test getting interventions by therapeutic approach."""
    # Test for each approach
    for approach in TherapeuticApproach:
        response = client.get(f"/api/interventions/suggestions/by-approach/{approach.value}")
        assert response.status_code == 200
        
        interventions = response.json()
        assert isinstance(interventions, list)
        
        # Not all approaches may have interventions in the test library
        if interventions:
            # Check that each intervention uses the requested approach
            for intervention in interventions:
                assert approach.value in [app for app in 
                                         intervention["therapeutic_approaches"]]


def test_recommend_interventions():
    """Test getting personalized intervention recommendations."""
    request_data = {
        "user_id": "test_user_123",
        "focus_categories": [
            InterventionCategory.COMMUNICATION.value,
            InterventionCategory.EMOTIONAL_REGULATION.value
        ],
        "preferred_approaches": [
            TherapeuticApproach.CBT.value,
            TherapeuticApproach.MINDFULNESS.value
        ],
        "difficulty_range": {"min": 1, "max": 3},
        "excluded_intervention_ids": [],
        "context_data": {
            "relationship_status": "married",
            "communication_style": "passive"
        }
    }
    
    response = client.post("/api/interventions/recommend", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "recommended_interventions" in data
    assert "recommendation_rationale" in data


def test_create_intervention_plan():
    """Test creating a new intervention plan."""
    response = client.post(
        "/api/interventions/plans",
        params={
            "title": "New Test Plan",
            "user_id": "test_user_456",
            "primary_approach": TherapeuticApproach.MINDFULNESS,
            "target_categories": [
                InterventionCategory.STRESS_MANAGEMENT,
                InterventionCategory.EMOTIONAL_REGULATION
            ],
            "description": "A plan for stress management",
            "goals": ["Reduce anxiety", "Improve sleep"]
        }
    )
    
    assert response.status_code == 201
    
    plan_data = response.json()
    assert "plan_id" in plan_data
    assert "title" in plan_data
    assert plan_data["title"] == "New Test Plan"
    assert plan_data["primary_approach"] == TherapeuticApproach.MINDFULNESS.value
    assert InterventionCategory.STRESS_MANAGEMENT.value in plan_data["target_categories"]
    assert InterventionCategory.EMOTIONAL_REGULATION.value in plan_data["target_categories"]


def test_get_plan(sample_plan_id):
    """Test getting a specific intervention plan by ID."""
    response = client.get(f"/api/interventions/plans/{sample_plan_id}")
    assert response.status_code == 200
    
    plan = response.json()
    assert plan["id"] == sample_plan_id
    
    # Check plan structure
    assert "user_id" in plan
    assert "primary_approaches" in plan
    assert "focus_areas" in plan
    assert "goals" in plan


def test_get_user_plans():
    """Test getting all intervention plans for a user."""
    user_id = "test_user_123"
    response = client.get(f"/api/interventions/plans/user/{user_id}")
    assert response.status_code == 200
    
    plans = response.json()
    assert isinstance(plans, list)
    
    # Verify all plans belong to the user
    for plan in plans:
        assert plan["user_id"] == user_id


def test_add_intervention_to_plan(sample_plan_id, sample_intervention_id):
    """Test adding an intervention to a plan."""
    response = client.post(f"/api/interventions/plans/{sample_plan_id}/interventions/{sample_intervention_id}")
    assert response.status_code == 200
    
    updated_plan = response.json()
    assert sample_intervention_id in updated_plan["active_interventions"]


def test_update_intervention_progress(sample_plan_id, sample_intervention_id):
    """Test updating the progress of an intervention in a plan."""
    # First, add the intervention to the plan if not already there
    client.post(f"/api/interventions/plans/{sample_plan_id}/interventions/{sample_intervention_id}")
    
    # Now update the progress
    progress_data = {
        "status": ProgressStatus.IN_PROGRESS.value,
        "notes": "Started working on this technique",
        "perceived_effectiveness": 7,
        "challenges_encountered": ["Initial resistance", "Time constraints"],
        "modifications_made": "Adapted for shorter sessions",
        "time_spent": 30
    }
    
    response = client.post(
        f"/api/interventions/plans/{sample_plan_id}/interventions/{sample_intervention_id}/progress",
        json=progress_data
    )
    assert response.status_code == 200
    
    progress_summary = response.json()
    assert "plan_id" in progress_summary
    assert "overall_progress" in progress_summary
    assert "intervention_progress" in progress_summary


def test_get_plan_progress(sample_plan_id):
    """Test getting a summary of progress for all interventions in a plan."""
    response = client.get(f"/api/interventions/plans/{sample_plan_id}/progress")
    assert response.status_code == 200
    
    progress = response.json()
    assert "plan_id" in progress
    assert progress["plan_id"] == sample_plan_id
    assert "overall_progress" in progress
    assert "intervention_progress" in progress


def test_nonexistent_plan():
    """Test behavior when requesting a non-existent plan."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/interventions/plans/{fake_id}")
    assert response.status_code == 404


def test_nonexistent_intervention():
    """Test behavior when requesting a non-existent intervention."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/interventions/suggestions/{fake_id}")
    assert response.status_code == 404


def test_user_therapeutic_approaches():
    """Test getting recommended therapeutic approaches for a user."""
    user_id = "test_user_123"
    response = client.get(f"/api/interventions/user-approaches/{user_id}")
    assert response.status_code == 200
    
    approaches = response.json()
    assert isinstance(approaches, list)
    assert len(approaches) > 0
    
    # Check structure of each approach
    for approach in approaches:
        assert "value" in approach
        assert "name" in approach


def test_get_interventions_by_category(sample_intervention_id):
    """Test retrieving interventions by category."""
    # Get interventions for a specific category
    response = client.get(
        f"/api/interventions/by-category/{InterventionCategory.EMOTIONAL_REGULATION}"
    )
    assert response.status_code == 200
    
    interventions = response.json()
    assert isinstance(interventions, list)
    assert len(interventions) > 0
    
    # Check structure of interventions
    for intervention in interventions:
        assert "id" in intervention
        assert "title" in intervention
        assert "description" in intervention
        assert "category" in intervention


@pytest.mark.asyncio
async def test_get_interventions_by_approach():
    """Test retrieving interventions by therapeutic approach."""
    # Get interventions for a specific approach
    response = client.get(
        f"/api/interventions/by-approach/{TherapeuticApproach.CBT}"
    )
    assert response.status_code == 200
    
    interventions = response.json()
    assert isinstance(interventions, list)
    
    # Check structure of interventions
    for intervention in interventions:
        assert "id" in intervention
        assert "title" in intervention
        assert "description" in intervention
        assert "therapeutic_approach" in intervention


@pytest.mark.asyncio
async def test_get_intervention_details(sample_intervention_id):
    """Test retrieving details of a specific intervention."""
    # Get details for a specific intervention
    response = client.get(f"/api/interventions/{sample_intervention_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "category" in data
    assert "therapeutic_approach" in data


@pytest.mark.asyncio
async def test_create_intervention_plan(sample_intervention_id):
    """Test creating a new intervention plan."""
    # Create a new plan
    response = client.post(
        "/api/interventions/plans",
        params={
            "title": "Test Plan",
            "user_id": "test_user_456",
            "primary_approach": TherapeuticApproach.CBT,
            "target_categories": [InterventionCategory.EMOTIONAL_REGULATION],
            "description": "Test plan creation",
            "goals": ["Goal 1", "Goal 2"]
        }
    )
    assert response.status_code == 201
    
    plan_data = response.json()
    assert "plan_id" in plan_data


@pytest.mark.asyncio
async def test_get_intervention_plan(sample_plan_id):
    """Test retrieving an intervention plan."""
    # Get the plan details
    response = client.get(f"/api/interventions/plans/{sample_plan_id}")
    assert response.status_code == 200
    
    plan = response.json()
    assert plan["id"] == sample_plan_id
    assert "title" in plan
    assert "user_id" in plan
    assert "primary_approach" in plan


@pytest.mark.asyncio
async def test_list_intervention_plans():
    """Test listing all intervention plans."""
    # List all plans
    response = client.get("/api/interventions/plans")
    assert response.status_code == 200
    
    plans = response.json()
    assert isinstance(plans, list)
    assert len(plans) > 0
    
    # Check structure of plans
    for plan in plans:
        assert "id" in plan
        assert "title" in plan
        assert "user_id" in plan


@pytest.mark.asyncio
async def test_update_intervention_plan(sample_plan_id):
    """Test updating an intervention plan."""
    # Update the plan
    response = client.put(
        f"/api/interventions/plans/{sample_plan_id}",
        json={
            "title": "Updated Test Plan",
            "description": "Updated test description"
        }
    )
    assert response.status_code == 200
    
    updated_plan = response.json()
    assert updated_plan["id"] == sample_plan_id
    assert updated_plan["title"] == "Updated Test Plan"
    assert updated_plan["description"] == "Updated test description"


@pytest.mark.asyncio
async def test_record_intervention_progress(sample_plan_id, sample_intervention_id):
    """Test recording progress for an intervention."""
    # Record progress
    response = client.post(
        f"/api/interventions/progress/{sample_plan_id}/{sample_intervention_id}",
        json={
            "status": ProgressStatus.IN_PROGRESS,
            "notes": "Making good progress",
            "date": "2025-07-03"
        }
    )
    assert response.status_code == 200
    
    progress_summary = response.json()
    assert "intervention_id" in progress_summary
    assert "status" in progress_summary
    assert progress_summary["status"] == ProgressStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_get_intervention_progress(sample_plan_id, sample_intervention_id):
    """Test retrieving progress for an intervention."""
    # Get progress
    response = client.get(
        f"/api/interventions/progress/{sample_plan_id}/{sample_intervention_id}"
    )
    assert response.status_code == 200
    
    progress = response.json()
    assert isinstance(progress, dict)
    assert "intervention_id" in progress
    assert "status" in progress


@pytest.mark.asyncio
async def test_delete_intervention_plan(sample_plan_id):
    """Test deleting an intervention plan."""
    # Delete the plan
    response = client.delete(f"/api/interventions/plans/{sample_plan_id}")
    assert response.status_code == 204
    
    # Verify plan is deleted
    response = client.get(f"/api/interventions/plans/{sample_plan_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_interventions_by_approach_and_category():
    """Test filtering interventions by both approach and category."""
    # Filter interventions
    response = client.get(
        "/api/interventions/filter",
        params={
            "approach": TherapeuticApproach.CBT,
            "category": InterventionCategory.EMOTIONAL_REGULATION
        }
    )
    assert response.status_code == 200
    
    approaches = response.json()
    assert isinstance(approaches, list)
    
    # Check filtered results
    for intervention in approaches:
        assert intervention["therapeutic_approach"] == TherapeuticApproach.CBT
        assert intervention["category"] == InterventionCategory.EMOTIONAL_REGULATION
