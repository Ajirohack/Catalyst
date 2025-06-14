from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timezone
import uuid

# Import models and schemas
from models.project import Project, ProjectStatus, ProjectType
from schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    Project as ProjectResponse,
    ProjectBase
)

# Create router
router = APIRouter()

# In-memory storage for development (replace with database in production)
projects_db = {}

# Dependency for pagination
def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return")
):
    return {"skip": skip, "limit": limit}

# Helper function to convert Project model to response
def project_to_response(project: Project) -> ProjectResponse:
    try:
        print(f"Converting project to response: {project}")
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            status=project.status,
            participants=project.participants,
            goals=project.goals,
            settings=project.settings,
            created_at=project.created_at,
            updated_at=project.updated_at,
            analysis_count=len(project.analyses) if hasattr(project, 'analyses') and project.analyses else 0,
            milestone_count=len(project.milestones) if hasattr(project, 'milestones') and project.milestones else 0,
            last_activity=project.updated_at
        )
    except Exception as e:
        print(f"Error in project_to_response: {e}")
        import traceback
        print(traceback.format_exc())
        raise

@router.get("/", response_model=List[ProjectResponse], summary="List Projects")
async def list_projects(
    pagination: dict = Depends(get_pagination_params),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    project_type: Optional[ProjectType] = Query(None, description="Filter by project type"),
    search: Optional[str] = Query(None, description="Search in project names and descriptions")
):
    """
    Retrieve a list of all projects with optional filtering and pagination.
    
    - **skip**: Number of projects to skip (for pagination)
    - **limit**: Maximum number of projects to return
    - **status**: Filter projects by status (active, paused, completed, archived)
    - **project_type**: Filter projects by type (romantic, family, friendship, professional)
    - **search**: Search term to filter projects by name or description
    """
    try:
        # Get all projects
        all_projects = list(projects_db.values())
        
        # Apply filters
        filtered_projects = all_projects
        
        if status:
            filtered_projects = [p for p in filtered_projects if p.status == status]
        
        if project_type:
            try:
                filtered_projects = [p for p in filtered_projects if p.project_type == project_type]
                print(f"Filtered by project_type: {project_type}, found {len(filtered_projects)} projects")
            except Exception as e:
                print(f"Error filtering by project_type: {e}")
                import traceback
                print(traceback.format_exc())
                raise
        
        if search:
            search_lower = search.lower()
            filtered_projects = [
                p for p in filtered_projects 
                if search_lower in p.name.lower() or search_lower in (p.description or "").lower()
            ]
        
        # Sort by updated_at (most recent first)
        filtered_projects.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Apply pagination
        skip = pagination["skip"]
        limit = pagination["limit"]
        paginated_projects = filtered_projects[skip:skip + limit]
        
        # Convert to response format
        response_projects = [project_to_response(project) for project in paginated_projects]
        
        return response_projects
        
    except Exception as e:
        print(f"Error in list_projects: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")

@router.post("/", response_model=ProjectResponse, status_code=201, summary="Create Project")
async def create_project(project_data: ProjectCreate):
    """
    Create a new relationship project.
    
    - **name**: Project name (required)
    - **description**: Project description
    - **project_type**: Type of relationship (romantic, family, friendship, professional)
    - **participants**: List of participants in the relationship
    - **goals**: List of relationship goals
    - **settings**: Project-specific settings and preferences
    """
    try:
        print(f"Creating project with data: {project_data}")
        
        # Generate unique ID
        project_id = str(uuid.uuid4())
        
        # Create project instance
        project = Project(
            id=project_id,
            name=project_data.name,
            description=project_data.description,
            project_type=project_data.project_type,
            status=ProjectStatus.ACTIVE,
            participants=project_data.participants or [],
            goals=project_data.goals or [],
            settings=project_data.settings or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            analyses=[],
            milestones=[]
        )
        
        print(f"Created project: {project}")
        
        # Store in database
        projects_db[project_id] = project
        
        response = project_to_response(project)
        print(f"Project response: {response}")
        
        return response
        
    except Exception as e:
        print(f"Error creating project: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get Project")
async def get_project(
    project_id: str = Path(..., description="The ID of the project to retrieve")
):
    """
    Retrieve a specific project by its ID.
    
    - **project_id**: Unique identifier of the project
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        return project_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project: {str(e)}")

@router.put("/{project_id}", response_model=ProjectResponse, summary="Update Project")
async def update_project(
    project_data: ProjectUpdate,
    project_id: str = Path(..., description="The ID of the project to update")
):
    """
    Update an existing project.
    
    - **project_id**: Unique identifier of the project
    - **name**: Updated project name
    - **description**: Updated project description
    - **status**: Updated project status
    - **participants**: Updated list of participants
    - **goals**: Updated list of goals
    - **settings**: Updated project settings
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        # Update fields if provided
        update_data = project_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)
        
        # Update timestamp
        project.updated_at = datetime.utcnow()
        
        return project_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@router.delete("/{project_id}", summary="Delete Project")
async def delete_project(
    project_id: str = Path(..., description="The ID of the project to delete")
):
    """
    Delete a project permanently.
    
    - **project_id**: Unique identifier of the project to delete
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Remove from database
        del projects_db[project_id]
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Project deleted successfully",
                "project_id": project_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

@router.patch("/{project_id}/status", response_model=ProjectResponse, summary="Update Project Status")
async def update_project_status(
    status_update: dict,
    project_id: str = Path(..., description="The ID of the project to update")
):
    """
    Update only the status of a project.
    
    - **project_id**: Unique identifier of the project
    - **status**: New status for the project (active, paused, completed, archived)
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if "status" not in status_update:
            raise HTTPException(status_code=422, detail="Status field is required")
            
        status = status_update["status"]
        
        project = projects_db[project_id]
        project.status = status
        project.updated_at = datetime.utcnow()
        
        return project_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project status: {str(e)}")

@router.post("/{project_id}/goals", response_model=ProjectResponse, summary="Add Project Goal")
async def add_project_goal(
    goal_data: dict,
    project_id: str = Path(..., description="The ID of the project")
):
    """
    Add a new goal to a project.
    
    - **project_id**: Unique identifier of the project
    - **goal_data**: Object containing the new goal to add to the project
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if "goal" not in goal_data:
            raise HTTPException(status_code=422, detail="Goal field is required")
            
        goal = goal_data["goal"]
        
        project = projects_db[project_id]
        project.goals.append(goal)
        project.updated_at = datetime.utcnow()
        
        return project_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add goal: {str(e)}")

@router.delete("/{project_id}/goals/{goal_index}", response_model=ProjectResponse, summary="Remove Project Goal")
async def remove_project_goal(
    project_id: str = Path(..., description="The ID of the project"),
    goal_index: int = Path(..., description="The index of the goal to remove")
):
    """
    Remove a goal from a project by its index.
    
    - **project_id**: Unique identifier of the project
    - **goal_index**: Index of the goal to remove (0-based)
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        if 0 <= goal_index < len(project.goals):
            project.goals.pop(goal_index)
            project.updated_at = datetime.now(timezone.utc)
        else:
            raise HTTPException(status_code=400, detail="Invalid goal index")
        
        return project_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove goal: {str(e)}")

@router.get("/{project_id}/stats", summary="Get Project Statistics")
async def get_project_stats(
    project_id: str = Path(..., description="The ID of the project")
):
    """
    Get detailed statistics for a specific project.
    
    - **project_id**: Unique identifier of the project
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        # Calculate statistics
        total_analyses = len(project.analyses) if project.analyses else 0
        total_milestones = len(project.milestones) if project.milestones else 0
        completed_milestones = sum(1 for m in (project.milestones or []) if m.completed)
        
        # Calculate project duration
        duration_days = (datetime.utcnow() - project.created_at).days
        
        # For now, we don't have a way to mark goals as completed, so we'll assume none are completed
        # In a real implementation, we would track completed goals
        completed_goals = 0
        total_goals = len(project.goals)
        progress_percentage = 0
        if total_goals > 0:
            progress_percentage = (completed_goals / total_goals) * 100
            
        return {
            "project_id": project_id,
            "name": project.name,
            "status": project.status,
            "duration_days": duration_days,
            "days_active": duration_days,  # Alias for test compatibility
            "total_analyses": total_analyses,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "milestone_completion_rate": completed_milestones / total_milestones if total_milestones > 0 else 0,
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "progress_percentage": progress_percentage,
            "participant_count": len(project.participants),
            "last_activity": project.updated_at,
            "created_at": project.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project statistics: {str(e)}")

# Health check for projects router
@router.get("/health/check", summary="Projects Router Health Check")
async def projects_health_check():
    """
    Health check endpoint for the projects router.
    """
    return {
        "status": "healthy",
        "service": "projects",
        "total_projects": len(projects_db),
        "timestamp": datetime.now(timezone.utc)
    }