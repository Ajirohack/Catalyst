import pytest
import asyncio
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import uuid
import time
from typing import Any
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Import app directly to avoid relative import issues
try:
    from main import app
except ImportError as e:
    print(f"ImportError: {e}")
    # Create a mock app for testing
    app = MagicMock()
    print("Using mock app for testing")

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
    """Clean all database types before each test."""
    db_modules = [
        ('routers.projects', ['projects_db']),
        ('routers.analysis', ['analysis_history', 'active_sessions']),
        ('routers.knowledge_base', ['kb_documents', 'kb_index']),
        ('routers.therapeutic_interventions', ['interventions_db']),
        ('routers.ai_providers', ['providers_db'])
    ]
    
    # Clean before test
    for module_name, attrs in db_modules:
        try:
            module = __import__(module_name, fromlist=attrs)
            for attr in attrs:
                if hasattr(module, attr):
                    db = getattr(module, attr)
                    if hasattr(db, 'clear'):
                        db.clear()
        except ImportError as e:
            print(f"Warning: Could not clean {module_name}.{attrs}: {e}")
    
    yield
    
    # Clean after test
    for module_name, attrs in db_modules:
        try:
            module = __import__(module_name, fromlist=attrs)
            for attr in attrs:
                if hasattr(module, attr):
                    db = getattr(module, attr)
                    if hasattr(db, 'clear'):
                        db.clear()
        except ImportError as e:
            print(f"Warning: Could not clean {module_name}.{attrs}: {e}")

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

@pytest.fixture
def sample_knowledge_doc():
    """Provide a sample knowledge document for testing."""
    return {
        "title": "Sample Document",
        "content": "This is a sample document content with sufficient length for testing. " * 5,
        "type": "reference",
        "tags": ["test", "sample", "reference"],
        "metadata": {
            "author": "Test Author",
            "created_date": datetime.now().isoformat(),
            "version": "1.0"
        }
    }

@pytest.fixture
def sample_file_content():
    """Provide sample file content for testing file operations."""
    return b"This is a sample file content for testing file storage operations.\n" * 10

@pytest.fixture
def error_conditions():
    """Provide common error conditions for testing error handling."""
    return {
        "invalid_doc_id": "invalid-id-123",
        "malformed_json": "{invalid-json",
        "empty_content": "",
        "oversized_content": "x" * (10 * 1024 * 1024),  # 10MB of content
        "invalid_tags": [123, True, None],  # Invalid tag types
        "invalid_metadata": {"score": float('inf')},  # Invalid metadata value
    }

@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for benchmark tests."""
    return {
        "indexing": {
            "max_time": 2.0,  # seconds
            "max_memory": 100 * 1024 * 1024,  # 100MB
        },
        "search": {
            "max_time": 0.5,  # seconds
            "max_memory": 50 * 1024 * 1024,  # 50MB
        },
        "file_processing": {
            "max_time": 5.0,  # seconds
            "max_memory": 200 * 1024 * 1024,  # 200MB
        }
    }

@pytest.fixture
def temp_storage(tmp_path):
    """Provide a temporary storage directory for file operations."""
    storage_dir = tmp_path / "test_storage"
    storage_dir.mkdir()
    return storage_dir

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

@pytest.fixture
def assert_valid_uuid():
    """Fixture to validate UUIDs."""
    def _assert(value):
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, AttributeError, TypeError):
            pytest.fail(f"Expected a valid UUID, got {value}")
    return _assert

@pytest.fixture
def assert_valid_timestamp():
    """Fixture to validate timestamps."""
    def _assert(value):
        try:
            timestamp = float(value)
            current_time = time.time()
            # Check if timestamp is within last 24 hours
            assert current_time - 86400 <= timestamp <= current_time + 86400
            return True
        except (ValueError, TypeError, AssertionError):
            pytest.fail(f"Expected a valid timestamp, got {value}")
    return _assert

@pytest.fixture
def assert_response_time():
    """Fixture to validate response times."""
    def _assert(start_time: float, max_seconds: float = 1.0):
        elapsed = time.time() - start_time
        if elapsed > max_seconds:
            pytest.fail(f"Response time {elapsed:.2f}s exceeded limit of {max_seconds:.2f}s")
        return True
    return _assert

@pytest.fixture
def mock_ai_service():
    """Mock the AI service for testing knowledge base integration."""
    with patch('services.ai_service.AIService') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock AI processing results
        mock_instance.generate_embeddings.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 50  # 250-dim vector
        mock_instance.extract_entities.return_value = [
            {"text": "communication", "type": "skill", "score": 0.92},
            {"text": "relationship", "type": "concept", "score": 0.85},
            {"text": "weekend", "type": "time", "score": 0.78}
        ]
        mock_instance.summarize.return_value = "This is a summary of the provided content."
        mock_instance.answer_question.return_value = {
            "answer": "This is a test answer based on the provided context.",
            "confidence": 0.87,
            "sources": ["doc1", "doc2"]
        }
        
        yield mock_instance

@pytest.fixture
def sample_vector_data():
    """Provide sample vector data for testing vector search."""
    return {
        "vectors": [
            {"id": "doc1", "vector": [0.1, 0.2, 0.3, 0.4, 0.5] * 50, "metadata": {"title": "Document 1"}},
            {"id": "doc2", "vector": [0.5, 0.4, 0.3, 0.2, 0.1] * 50, "metadata": {"title": "Document 2"}},
            {"id": "doc3", "vector": [0.3, 0.3, 0.3, 0.3, 0.3] * 50, "metadata": {"title": "Document 3"}}
        ],
        "query_vector": [0.2, 0.2, 0.2, 0.2, 0.2] * 50,
        "expected_results": ["doc1", "doc3", "doc2"]  # In order of expected similarity
    }

@pytest.fixture
def assert_valid_api_response():
    """Fixture to validate common API response patterns."""
    def _assert(response, expected_status_code=200, expected_fields=None):
        assert response.status_code == expected_status_code, f"Expected status code {expected_status_code}, got {response.status_code}"
        
        if expected_fields:
            response_json = response.json()
            for field in expected_fields:
                assert field in response_json, f"Expected field '{field}' missing from response"
        
        return True
    return _assert

@pytest.fixture
def mock_file_processor():
    """Mock the file processor for testing file operations."""
    with patch('services.file_processor.FileProcessor') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock file processing results
        mock_instance.process_text_file.return_value = {
            "content": "This is the extracted text content.",
            "metadata": {
                "lines": 10,
                "words": 100,
                "characters": 500
            }
        }
        
        mock_instance.process_document.return_value = {
            "content": "This is the extracted document content.",
            "metadata": {
                "title": "Test Document",
                "author": "Test Author",
                "pages": 5
            }
        }
        
        mock_instance.process_audio.return_value = {
            "transcript": "This is the transcribed audio content.",
            "metadata": {
                "duration": 120.5,  # seconds
                "speakers": 2
            }
        }
        
        yield mock_instance

@pytest.fixture
def sample_validation_errors():
    """Provide sample validation errors for testing error handling."""
    return {
        "field_errors": [
            {"field": "name", "error": "Field cannot be empty"},
            {"field": "email", "error": "Invalid email format"},
            {"field": "age", "error": "Must be a positive integer"}
        ],
        "general_errors": [
            "Request exceeded rate limit",
            "Service temporarily unavailable",
            "Invalid authentication token"
        ],
        "expected_status_codes": {
            "validation_error": 422,
            "not_found": 404,
            "unauthorized": 401,
            "forbidden": 403,
            "rate_limit": 429,
            "server_error": 500
        }
    }