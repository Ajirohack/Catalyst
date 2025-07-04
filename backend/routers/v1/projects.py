"""
Project Router for Catalyst
Handles CRUD operations for projects
"""

try:
    from fastapi import APIRouter, HTTPException, Query, Path, Depends
    from fastapi.responses import JSONResponse
    from typing import List, Optional, Dict, Any
    from pydantic import BaseModel, Field
    from datetime import datetime, timezone
    import uuid
    import logging

    # Import models and schemas
    from models.project import Project, ProjectStatus, ProjectType
    from schemas.project_schema import (
        ProjectCreate,
        ProjectUpdate,
        Project as ProjectResponse,
        ProjectBase
    )
except ImportError:
    pass

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
    - **status**: Filter by project status
    - **project_type**: Filter by project type
    - **search**: Search term for project names and descriptions
    """
    skip, limit = pagination["skip"], pagination["limit"]
    
    # Get all projects and apply filters
    filtered_projects = list(projects_db.values())
    
    # Apply status filter
    if status:
        filtered_projects = [p for p in filtered_projects if p.status == status]
    
    # Apply project_type filter
    if project_type:
        filtered_projects = [p for p in filtered_projects if p.project_type == project_type]
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        filtered_projects = [
            p for p in filtered_projects 
            if search_lower in p.name.lower() or 
               (p.description and search_lower in p.description.lower())
        ]
    
    # Sort by created_at (newest first)
    filtered_projects.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    paginated_projects = filtered_projects[skip:skip + limit]
    
    # Convert to response model
    return [project_to_response(project) for project in paginated_projects]

@router.post("/", response_model=ProjectResponse, status_code=201, summary="Create Project")
async def create_project(project: ProjectCreate):
    """
    Create a new project.
    
    - **name**: Required project name
    - **description**: Optional project description
    - **project_type**: Type of project (e.g., RELATIONSHIP, SELF_IMPROVEMENT)
    - **participants**: List of participant identifiers
    - **goals**: Optional list of project goals
    - **settings**: Optional project settings
    """
    # Generate ID and timestamps
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # Create new project
    new_project = Project(
        id=project_id,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        status=ProjectStatus.ACTIVE,
        participants=project.participants,
        goals=project.goals or [],
        settings=project.settings or {},
        created_at=now,
        updated_at=now,
        analyses=[],
        milestones=[]
    )
    
    # Save to in-memory database
    projects_db[project_id] = new_project
    
    return project_to_response(new_project)
