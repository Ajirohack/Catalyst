from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from models.project import Project
from schemas.project_schema import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self):
        # In-memory storage for demonstration
        # In production, this would be replaced with database operations
        self.projects: Dict[str, Project] = {}
        self.project_counter = 0
    
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Create a new project.
        
        Args:
            project_data: Project creation data
            
        Returns:
            Created project
        """
        project_id = str(uuid.uuid4())
        
        project = Project(
            id=project_id,
            name=project_data.name,
            description=project_data.description,
            platform=project_data.platform,
            role=project_data.role,
            participants=project_data.participants or [],
            goals=project_data.goals or [],
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=project_data.metadata or {}
        )
        
        self.projects[project_id] = project
        self.project_counter += 1
        
        return project
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project if found, None otherwise
        """
        return self.projects.get(project_id)
    
    async def get_projects(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Project]:
        """
        Get projects with filtering and pagination.
        
        Args:
            skip: Number of projects to skip
            limit: Maximum number of projects to return
            status: Filter by status
            platform: Filter by platform
            search: Search in project name and description
            
        Returns:
            List of projects
        """
        projects = list(self.projects.values())
        
        # Apply filters
        if status:
            projects = [p for p in projects if p.status == status]
        
        if platform:
            projects = [p for p in projects if p.platform.lower() == platform.lower()]
        
        if search:
            search_lower = search.lower()
            projects = [
                p for p in projects 
                if search_lower in p.name.lower() or 
                   (p.description and search_lower in p.description.lower())
            ]
        
        # Sort by updated_at descending
        projects.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Apply pagination
        return projects[skip:skip + limit]
    
    async def update_project(self, project_id: str, project_data: ProjectUpdate) -> Optional[Project]:
        """
        Update a project.
        
        Args:
            project_id: Project ID
            project_data: Project update data
            
        Returns:
            Updated project if found, None otherwise
        """
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # Update fields if provided
        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description
        if project_data.platform is not None:
            project.platform = project_data.platform
        if project_data.role is not None:
            project.role = project_data.role
        if project_data.participants is not None:
            project.participants = project_data.participants
        if project_data.goals is not None:
            project.goals = project_data.goals
        if project_data.status is not None:
            project.status = project_data.status
        if project_data.metadata is not None:
            project.metadata = {**project.metadata, **project_data.metadata}
        
        project.updated_at = datetime.utcnow()
        
        return project
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False
    
    async def update_project_status(self, project_id: str, status: str) -> Optional[Project]:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            status: New status
            
        Returns:
            Updated project if found, None otherwise
        """
        project = self.projects.get(project_id)
        if not project:
            return None
        
        project.status = status
        project.updated_at = datetime.utcnow()
        
        return project
    
    async def add_project_goal(self, project_id: str, goal: str) -> Optional[Project]:
        """
        Add a goal to a project.
        
        Args:
            project_id: Project ID
            goal: Goal to add
            
        Returns:
            Updated project if found, None otherwise
        """
        project = self.projects.get(project_id)
        if not project:
            return None
        
        if goal not in project.goals:
            project.goals.append(goal)
            project.updated_at = datetime.utcnow()
        
        return project
    
    async def remove_project_goal(self, project_id: str, goal: str) -> Optional[Project]:
        """
        Remove a goal from a project.
        
        Args:
            project_id: Project ID
            goal: Goal to remove
            
        Returns:
            Updated project if found, None otherwise
        """
        project = self.projects.get(project_id)
        if not project:
            return None
        
        if goal in project.goals:
            project.goals.remove(goal)
            project.updated_at = datetime.utcnow()
        
        return project
    
    async def get_project_statistics(self) -> Dict[str, Any]:
        """
        Get project statistics.
        
        Returns:
            Dictionary with project statistics
        """
        projects = list(self.projects.values())
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == "active"])
        completed_projects = len([p for p in projects if p.status == "completed"])
        paused_projects = len([p for p in projects if p.status == "paused"])
        archived_projects = len([p for p in projects if p.status == "archived"])
        
        # Platform distribution
        platform_counts = {}
        for project in projects:
            platform = project.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Role distribution
        role_counts = {}
        for project in projects:
            role = project.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Recent activity (projects updated in last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity = len([p for p in projects if p.updated_at >= week_ago])
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "paused_projects": paused_projects,
            "archived_projects": archived_projects,
            "platform_distribution": platform_counts,
            "role_distribution": role_counts,
            "recent_activity": recent_activity,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def search_projects(self, query: str, limit: int = 10) -> List[Project]:
        """
        Search projects by name, description, or participants.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching projects
        """
        if not query:
            return []
        
        query_lower = query.lower()
        projects = list(self.projects.values())
        matching_projects = []
        
        for project in projects:
            # Search in name
            if query_lower in project.name.lower():
                matching_projects.append(project)
                continue
            
            # Search in description
            if project.description and query_lower in project.description.lower():
                matching_projects.append(project)
                continue
            
            # Search in participants
            for participant in project.participants:
                if query_lower in participant.lower():
                    matching_projects.append(project)
                    break
            
            # Search in goals
            for goal in project.goals:
                if query_lower in goal.lower():
                    matching_projects.append(project)
                    break
        
        # Sort by relevance (name matches first, then description, etc.)
        def relevance_score(project):
            score = 0
            if query_lower in project.name.lower():
                score += 10
            if project.description and query_lower in project.description.lower():
                score += 5
            for participant in project.participants:
                if query_lower in participant.lower():
                    score += 3
                    break
            for goal in project.goals:
                if query_lower in goal.lower():
                    score += 2
                    break
            return score
        
        matching_projects.sort(key=relevance_score, reverse=True)
        
        return matching_projects[:limit]
    
    def get_total_projects(self) -> int:
        """
        Get total number of projects.
        
        Returns:
            Total number of projects
        """
        return len(self.projects)
    
    async def bulk_update_status(self, project_ids: List[str], status: str) -> List[str]:
        """
        Update status for multiple projects.
        
        Args:
            project_ids: List of project IDs
            status: New status
            
        Returns:
            List of successfully updated project IDs
        """
        updated_ids = []
        
        for project_id in project_ids:
            project = await self.update_project_status(project_id, status)
            if project:
                updated_ids.append(project_id)
        
        return updated_ids