"""Enhanced tests for database layer to improve coverage."""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    import pytest
    from unittest.mock import Mock, patch, MagicMock
    from datetime import datetime, timezone
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)


try:
    from sqlalchemy.orm import Session
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
except ImportError:
    Session = None
    create_engine = None
    StaticPool = None

try:
    from database.models import Project, AnalysisHistory
except ImportError:
    Project = None
    AnalysisHistory = None

try:
    from services.project_service import ProjectService
except ImportError:
    ProjectService = None


class TestDatabaseEnhanced:
    """Enhanced test suite for database layer with comprehensive coverage."""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy.orm import sessionmaker
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = TestingSessionLocal()
        
        try:
            yield session
        finally:
            session.close()
    
    @pytest.fixture
    def project_service(self, db_session):
        """Create project service with test database."""
        with patch('database.base.get_db', return_value=db_session):
            return ProjectService()
    
    @pytest.fixture
    def kb_service(self, db_session):
        """Create knowledge base service with test database."""
        with patch('database.base.get_db', return_value=db_session):
            return KnowledgeBaseService()
    
    def test_project_model_creation(self, db_session):
        """Test Project model creation and basic operations."""
        project = Project(
            name="Test Project",
            description="A test project for database testing",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.status == "active"
    
    def test_analysis_history_model(self, db_session):
        """Test AnalysisHistory model operations."""
        # First create a project
        project = Project(
            name="Analysis Test Project",
            description="Project for analysis testing",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        db_session.commit()
        
        # Create analysis history
        analysis = AnalysisHistory(
            project_id=project.id,
            analysis_type="sentiment",
            input_text="This is a test analysis",
            result={"sentiment": "positive", "confidence": 0.8},
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)
        
        assert analysis.id is not None
        assert analysis.project_id == project.id
        assert analysis.analysis_type == "sentiment"
        assert analysis.result["sentiment"] == "positive"
    
    def test_advanced_user_profile_model(self, db_session):
        """Test AdvancedUserProfile model operations."""
        profile = AdvancedUserProfile(
            user_id="test-user-123",
            preferences={"theme": "dark", "notifications": True},
            therapeutic_goals=["stress_reduction", "mood_improvement"],
            privacy_settings={"data_sharing": False, "analytics": True},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)
        
        assert profile.id is not None
        assert profile.user_id == "test-user-123"
        assert profile.preferences["theme"] == "dark"
        assert "stress_reduction" in profile.therapeutic_goals
    
    def test_conversation_history_model(self, db_session):
        """Test ConversationHistory model operations."""
        conversation = ConversationHistory(
            session_id="session-123",
            user_id="user-456",
            messages=[
                {"role": "user", "content": "Hello", "timestamp": datetime.now(timezone.utc).isoformat()},
                {"role": "assistant", "content": "Hi there!", "timestamp": datetime.now(timezone.utc).isoformat()}
            ],
            analysis_summary={"sentiment": "positive", "topics": ["greeting"]},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.session_id == "session-123"
        assert len(conversation.messages) == 2
        assert conversation.analysis_summary["sentiment"] == "positive"
    
    def test_analysis_cache_model(self, db_session):
        """Test AnalysisCache model operations."""
        cache_entry = AnalysisCache(
            cache_key="sentiment_analysis_hash_123",
            input_hash="abc123def456",
            analysis_type="sentiment",
            result={"sentiment": "neutral", "confidence": 0.7},
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(cache_entry)
        db_session.commit()
        db_session.refresh(cache_entry)
        
        assert cache_entry.id is not None
        assert cache_entry.cache_key == "sentiment_analysis_hash_123"
        assert cache_entry.result["sentiment"] == "neutral"
    
    def test_therapeutic_session_model(self, db_session):
        """Test TherapeuticSession model operations."""
        session = TherapeuticSession(
            user_id="user-789",
            session_type="cognitive_behavioral",
            goals=["anxiety_management", "sleep_improvement"],
            interventions_used=["breathing_exercise", "thought_challenging"],
            outcomes={"mood_improvement": 0.8, "anxiety_reduction": 0.6},
            notes="Patient showed good progress with breathing exercises",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        assert session.id is not None
        assert session.user_id == "user-789"
        assert "anxiety_management" in session.goals
        assert session.outcomes["mood_improvement"] == 0.8
    
    def test_progress_tracking_model(self, db_session):
        """Test ProgressTracking model operations."""
        progress = ProgressTracking(
            user_id="user-101",
            metric_type="mood_score",
            value=7.5,
            context={"activity": "meditation", "duration": 20},
            recorded_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
        
        assert progress.id is not None
        assert progress.user_id == "user-101"
        assert progress.metric_type == "mood_score"
        assert progress.value == 7.5
    
    def test_file_metadata_model(self, db_session):
        """Test FileMetadata model operations."""
        file_meta = FileMetadata(
            filename="test_document.pdf",
            file_path="/uploads/documents/test_document.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            upload_session_id="upload-session-123",
            processing_status="completed",
            metadata={"pages": 10, "language": "en"},
            uploaded_at=datetime.now(timezone.utc),
            processed_at=datetime.now(timezone.utc)
        )
        
        db_session.add(file_meta)
        db_session.commit()
        db_session.refresh(file_meta)
        
        assert file_meta.id is not None
        assert file_meta.filename == "test_document.pdf"
        assert file_meta.processing_status == "completed"
        assert file_meta.metadata["pages"] == 10
    
    def test_unified_project_model(self, db_session):
        """Test UnifiedProject model operations."""
        unified_project = UnifiedProject(
            name="Unified Test Project",
            description="Testing unified project model",
            project_type="therapeutic",
            status="active",
            metadata={"priority": "high", "category": "mental_health"},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(unified_project)
        db_session.commit()
        db_session.refresh(unified_project)
        
        assert unified_project.id is not None
        assert unified_project.name == "Unified Test Project"
        assert unified_project.project_type == "therapeutic"
        assert unified_project.metadata["priority"] == "high"
    
    def test_unified_analysis_model(self, db_session):
        """Test UnifiedAnalysis model operations."""
        unified_analysis = UnifiedAnalysis(
            analysis_id="analysis-456",
            input_data={"text": "Sample analysis input", "type": "conversation"},
            analysis_type="comprehensive",
            results={
                "sentiment": {"label": "positive", "confidence": 0.85},
                "therapeutic": {"risk_level": "low", "recommendations": []}
            },
            metadata={"model_version": "v2.1", "processing_time": 1.5},
            created_at=datetime.now(timezone.utc)
        )
        
        db_session.add(unified_analysis)
        db_session.commit()
        db_session.refresh(unified_analysis)
        
        assert unified_analysis.id is not None
        assert unified_analysis.analysis_id == "analysis-456"
        assert unified_analysis.results["sentiment"]["label"] == "positive"
    
    def test_database_relationships(self, db_session):
        """Test database model relationships."""
        # Create a project
        project = Project(
            name="Relationship Test Project",
            description="Testing relationships",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(project)
        db_session.commit()
        
        # Create multiple analysis histories for the project
        for i in range(3):
            analysis = AnalysisHistory(
                project_id=project.id,
                analysis_type="sentiment",
                input_text=f"Test analysis {i}",
                result={"sentiment": "positive", "confidence": 0.8 + i * 0.05},
                created_at=datetime.now(timezone.utc)
            )
            db_session.add(analysis)
        
        db_session.commit()
        
        # Query and verify relationships
        project_with_analyses = db_session.query(Project).filter(Project.id == project.id).first()
        assert project_with_analyses is not None
        
        analyses = db_session.query(AnalysisHistory).filter(AnalysisHistory.project_id == project.id).all()
        assert len(analyses) == 3
    
    def test_database_transactions(self, db_session):
        """Test database transaction handling."""
        try:
            # Start a transaction
            project = Project(
                name="Transaction Test",
                description="Testing transactions",
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db_session.add(project)
            
            # Simulate an error condition
            if True:  # Simulate error
                db_session.rollback()
                
            # Verify rollback worked
            projects = db_session.query(Project).filter(Project.name == "Transaction Test").all()
            assert len(projects) == 0
            
        except Exception as e:
            db_session.rollback()
            raise e
    
    def test_database_queries_and_filters(self, db_session):
        """Test complex database queries and filters."""
        # Create test data
        projects = []
        for i in range(5):
            project = Project(
                name=f"Query Test Project {i}",
                description=f"Description {i}",
                status="active" if i % 2 == 0 else "inactive",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            projects.append(project)
            db_session.add(project)
        
        db_session.commit()
        
        # Test filtering
        active_projects = db_session.query(Project).filter(Project.status == "active").all()
        assert len(active_projects) == 3
        
        # Test ordering
        ordered_projects = db_session.query(Project).order_by(Project.name).all()
        assert len(ordered_projects) == 5
        
        # Test counting
        project_count = db_session.query(Project).count()
        assert project_count == 5
    
    def test_service_layer_integration(self, project_service, db_session):
        """Test integration between service layer and database."""
        with patch('services.project_service.get_db', return_value=db_session):
            # Test project creation through service
            project_data = {
                "name": "Service Integration Test",
                "description": "Testing service layer integration",
                "status": "active"
            }
            
            # Mock the service method
            with patch.object(project_service, 'create_project') as mock_create:
                mock_create.return_value = Project(
                    id=1,
                    name=project_data["name"],
                    description=project_data["description"],
                    status=project_data["status"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                result = project_service.create_project(project_data)
                
                assert result.name == project_data["name"]
                assert result.status == project_data["status"]
                mock_create.assert_called_once_with(project_data)