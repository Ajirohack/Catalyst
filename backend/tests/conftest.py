import pytest
import asyncio
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def client():
    """Create a test client for each test function."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def clean_database():
    """Clean the in-memory database before each test."""
    # Clear projects database
    try:
        from routers.projects import projects_db
        projects_db.clear()
    except ImportError:
        pass
    
    # Clear analysis history
    try:
        from routers.analysis import analysis_history, active_sessions
        analysis_history.clear()
        active_sessions.clear()
    except ImportError:
        pass
    
    yield
    
    # Clean up after test
    try:
        from routers.projects import projects_db
        projects_db.clear()
    except ImportError:
        pass
    
    try:
        from routers.analysis import analysis_history, active_sessions
        analysis_history.clear()
        active_sessions.clear()
    except ImportError:
        pass

@pytest.fixture
def sample_project():
    """Provide sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "project_type": "romantic",
        "participants": ["Alice", "Bob"],
        "goals": ["Improve communication", "Spend quality time"],
        "settings": {
            "notifications": True,
            "privacy_level": "high",
            "auto_analysis": True
        }
    }

@pytest.fixture
def sample_analysis_data():
    """Provide sample analysis data for testing."""
    return {
        "text": "This is a sample conversation for testing analysis functionality.",
        "project_id": "test-project-123",
        "analysis_type": "sentiment"
    }

@pytest.fixture
def sample_conversation_file():
    """Provide sample conversation file content for testing."""
    return b"""Alice: Hi Bob, how was your day?
Bob: It was good, thanks for asking. How about yours?
Alice: Pretty good too. I was thinking we should plan something fun for the weekend.
Bob: That sounds great! What did you have in mind?
Alice: Maybe we could go hiking or have a picnic in the park.
Bob: I love both ideas. Let's check the weather and decide."""

@pytest.fixture
def mock_analysis_service():
    """Mock the analysis service for testing."""
    with patch('services.analysis_service.AnalysisService') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock analysis results
        mock_instance.analyze_sentiment.return_value = {
            "sentiment": "positive",
            "confidence": 0.85,
            "emotions": ["happiness", "contentment"]
        }
        
        mock_instance.extract_keywords.return_value = [
            "communication", "relationship", "quality time"
        ]
        
        mock_instance.generate_suggestions.return_value = [
            "Try active listening techniques",
            "Schedule regular check-ins",
            "Plan more shared activities"
        ]
        
        yield mock_instance

@pytest.fixture
def mock_whisper_service():
    """Mock the whisper service for testing."""
    with patch('services.whisper_service.WhisperService') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock whisper suggestions
        mock_instance.generate_suggestion.return_value = {
            "suggestion": "Consider acknowledging your partner's feelings",
            "confidence": 0.9,
            "type": "communication",
            "priority": "high"
        }
        
        mock_instance.process_message.return_value = {
            "suggestions": ["Consider acknowledging your partner's feelings"],
            "urgency_level": "medium",
            "category": "general",
            "confidence": 0.9,
            "context": {
                "sender": "test",
                "platform": "test",
                "project_id": "test"
            }
        }
        
        yield mock_instance

@pytest.fixture
def mock_project_service():
    """Mock the project service for testing."""
    with patch('services.project_service.ProjectService') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock project operations
        mock_instance.calculate_progress.return_value = {
            "total_goals": 5,
            "completed_goals": 2,
            "progress_percentage": 40.0,
            "days_active": 15
        }
        
        mock_instance.validate_project.return_value = True
        
        yield mock_instance

@pytest.fixture(scope="session")
def test_settings():
    """Provide test-specific settings."""
    return {
        "testing": True,
        "database_url": "sqlite:///:memory:",
        "secret_key": "test-secret-key",
        "debug": True,
        "cors_origins": ["http://localhost:3000", "http://localhost:8080"],
        "max_file_size": 10 * 1024 * 1024,  # 10MB for testing
        "rate_limit": 1000  # Higher limit for testing
    }

@pytest.fixture
def authenticated_headers():
    """Provide headers for authenticated requests (if auth is implemented)."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def websocket_session_id():
    """Provide a unique session ID for WebSocket testing."""
    import uuid
    return f"test-session-{uuid.uuid4().hex[:8]}"

@pytest.fixture
def performance_timer():
    """Provide a timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

@pytest.fixture
def temp_file():
    """Provide a temporary file for testing file uploads."""
    import tempfile
    import os
    
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.txt')
    
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write("This is a test file for upload testing.")
        yield path
    finally:
        # Clean up
        if os.path.exists(path):
            os.unlink(path)

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Set test environment variables
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    
    yield
    
    # Cleanup is automatic with monkeypatch

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "websocket: marks tests that use WebSocket connections"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests that measure performance"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_websocket" in item.name.lower():
            item.add_marker(pytest.mark.websocket)
        elif "test_performance" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)

# Custom assertions
def assert_valid_uuid(uuid_string):
    """Assert that a string is a valid UUID."""
    import uuid
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def assert_valid_timestamp(timestamp_string):
    """Assert that a string is a valid ISO timestamp."""
    from datetime import datetime
    try:
        datetime.fromisoformat(timestamp_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def assert_response_time(response_time, max_time=1.0):
    """Assert that response time is within acceptable limits."""
    assert response_time < max_time, f"Response time {response_time}s exceeds maximum {max_time}s"

# Add custom assertions to pytest namespace
pytest.assert_valid_uuid = assert_valid_uuid
pytest.assert_valid_timestamp = assert_valid_timestamp
pytest.assert_response_time = assert_response_time