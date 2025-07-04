"""
Property-based tests for the Catalyst backend using Hypothesis.
These tests verify that the system behaves correctly across a wide range of inputs.
"""
import os
import sys
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from typing import List, Dict, Any, Optional
import random
import string
import uuid

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

# Import services conditionally to handle missing dependencies
try:
    from services.analysis_service import AnalysisService
    analysis_available = True
except ImportError:
    analysis_available = False

try:
    from services.project_service import ProjectService
    project_available = True
except ImportError:
    project_available = False

try:
    from validators.input_validators import validate_project_data, validate_analysis_request
    validators_available = True
except ImportError:
    validators_available = False


# Custom Hypothesis strategies
@st.composite
def project_data_strategy(draw):
    """Generate valid project data with various edge cases."""
    # Required fields
    name = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    # Optional fields with some variations
    has_description = draw(st.booleans())
    description = draw(st.text(max_size=500)) if has_description else None
    
    # Project type with valid options and some invalid ones to test validation
    project_type = draw(st.sampled_from([
        "romantic", "family", "friendship", "professional", 
        # Occasionally generate invalid types
        *([f"invalid_type_{i}" for i in range(3)] if draw(st.booleans()) else [])
    ]))
    
    # Generate 1-5 participants
    num_participants = draw(st.integers(min_value=1, max_value=5))
    participants = [
        draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
        for _ in range(num_participants)
    ]
    
    # Generate 0-10 goals
    num_goals = draw(st.integers(min_value=0, max_value=10))
    goals = [
        draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
        for _ in range(num_goals)
    ]
    
    # Settings with variable fields
    settings = {}
    if draw(st.booleans()):
        settings["notifications"] = draw(st.booleans())
    if draw(st.booleans()):
        settings["privacy_level"] = draw(st.sampled_from(["low", "medium", "high"]))
    if draw(st.booleans()):
        settings["auto_analysis"] = draw(st.booleans())
    
    # Generate the complete project data
    project_data = {
        "name": name,
        "participants": participants,
        "project_type": project_type,
    }
    
    # Add optional fields
    if description is not None:
        project_data["description"] = description
    if goals:
        project_data["goals"] = goals
    if settings:
        project_data["settings"] = settings
    
    # Occasionally add an invalid field
    if draw(st.booleans()) and draw(st.booleans()):  # 25% chance
        invalid_key = draw(st.text(min_size=1, max_size=20).filter(lambda x: x not in project_data))
        invalid_value = draw(st.one_of(
            st.text(),
            st.integers(),
            st.booleans(),
            st.lists(st.text(), max_size=3)
        ))
        project_data[invalid_key] = invalid_value
    
    return project_data


@st.composite
def conversation_text_strategy(draw):
    """Generate conversation text with various formats and edge cases."""
    # Determine number of messages
    num_messages = draw(st.integers(min_value=1, max_value=50))
    
    # Generate participants
    participants = draw(st.lists(
        st.text(min_size=1, max_size=20, alphabet=string.ascii_letters).filter(lambda x: x.strip()),
        min_size=1, max_size=5, unique=True
    ))
    
    # Generate conversation messages
    messages = []
    for _ in range(num_messages):
        participant = draw(st.sampled_from(participants))
        
        # Message content with various formatting
        message_type = draw(st.sampled_from(["normal", "empty", "multiline", "special_chars"]))
        
        if message_type == "normal":
            content = draw(st.text(min_size=1, max_size=200, alphabet=string.printable))
        elif message_type == "empty":
            content = ""
        elif message_type == "multiline":
            num_lines = draw(st.integers(min_value=2, max_value=5))
            content = "\n".join([
                draw(st.text(min_size=0, max_size=100, alphabet=string.printable))
                for _ in range(num_lines)
            ])
        else:  # special_chars
            content = draw(st.text(alphabet=string.punctuation + "✓✗★♥♦♣♠", min_size=1, max_size=50))
        
        # Format with different separators
        separator = draw(st.sampled_from([":", ">", "-", "=>"]))
        message = f"{participant}{separator} {content}"
        messages.append(message)
    
    # Join messages with newlines and occasionally add extra newlines
    conversation = ""
    for message in messages:
        conversation += message
        # Add 1-3 newlines between messages
        num_newlines = draw(st.integers(min_value=1, max_value=3))
        conversation += "\n" * num_newlines
    
    return conversation


@st.composite
def knowledge_document_strategy(draw):
    """Generate knowledge document data with various edge cases."""
    # Required fields with edge cases
    title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    # Content with various lengths and special cases
    content_type = draw(st.sampled_from(["short", "medium", "long", "special_chars"]))
    
    if content_type == "short":
        content = draw(st.text(min_size=1, max_size=100))
    elif content_type == "medium":
        content = draw(st.text(min_size=100, max_size=1000))
    elif content_type == "long":
        # Generate paragraphs for longer content
        num_paragraphs = draw(st.integers(min_value=3, max_value=10))
        paragraphs = [
            draw(st.text(min_size=50, max_size=200))
            for _ in range(num_paragraphs)
        ]
        content = "\n\n".join(paragraphs)
    else:  # special_chars
        content = draw(st.text(alphabet=string.printable + "✓✗★♥♦♣♠", min_size=10, max_size=500))
    
    # Document type
    doc_type = draw(st.sampled_from([
        "reference", "guide", "note", "transcript", "summary",
        # Occasionally generate custom types
        *(["custom_type_" + ''.join(random.choices(string.ascii_lowercase, k=5))] if draw(st.booleans()) else [])
    ]))
    
    # Tags with edge cases
    num_tags = draw(st.integers(min_value=0, max_value=10))
    tags = [
        draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip()))
        for _ in range(num_tags)
    ]
    
    # Metadata with variable fields and edge cases
    metadata = {}
    
    # Author field
    if draw(st.booleans()):
        metadata["author"] = draw(st.text(min_size=0, max_size=50))
    
    # Created date
    if draw(st.booleans()):
        # Either valid ISO format or custom format
        date_format = draw(st.sampled_from(["iso", "custom"]))
        if date_format == "iso":
            from datetime import datetime
            metadata["created_date"] = datetime.now().isoformat()
        else:
            metadata["created_date"] = draw(st.text(min_size=1, max_size=30))
    
    # Version
    if draw(st.booleans()):
        version_type = draw(st.sampled_from(["semantic", "number", "text"]))
        if version_type == "semantic":
            metadata["version"] = f"{draw(st.integers(min_value=0, max_value=10))}.{draw(st.integers(min_value=0, max_value=99))}.{draw(st.integers(min_value=0, max_value=99))}"
        elif version_type == "number":
            metadata["version"] = str(draw(st.floats(min_value=0.1, max_value=10.0)))
        else:
            metadata["version"] = draw(st.text(min_size=1, max_size=10))
    
    # Custom metadata fields
    num_custom_fields = draw(st.integers(min_value=0, max_value=5))
    for _ in range(num_custom_fields):
        key = draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip() and x not in metadata))
        value_type = draw(st.sampled_from(["text", "number", "boolean", "list"]))
        
        if value_type == "text":
            value = draw(st.text(max_size=50))
        elif value_type == "number":
            value = draw(st.one_of(st.integers(), st.floats()))
        elif value_type == "boolean":
            value = draw(st.booleans())
        else:  # list
            value = [draw(st.text(max_size=20)) for _ in range(draw(st.integers(min_value=1, max_value=3)))]
        
        metadata[key] = value
    
    # Assemble the document
    document = {
        "title": title,
        "content": content,
        "type": doc_type
    }
    
    # Add optional fields
    if tags:
        document["tags"] = tags
    if metadata:
        document["metadata"] = metadata
    
    # Generate an ID (either UUID or custom)
    id_type = draw(st.sampled_from(["uuid", "custom", "none"]))
    if id_type == "uuid":
        document["id"] = str(uuid.uuid4())
    elif id_type == "custom":
        document["id"] = draw(st.text(min_size=1, max_size=36))
    # No ID for "none" option
    
    return document


@pytest.mark.property
class TestProjectValidation:
    """Property-based tests for project data validation."""
    
    @pytest.mark.skipif(not validators_available, reason="Validators not available")
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(project_data=project_data_strategy())
    def test_project_validation(self, project_data):
        """Test that valid project data passes validation."""
        # Filter out test cases with invalid project types to focus on other validation aspects
        assume(project_data.get("project_type") in ["romantic", "family", "friendship", "professional"])
        
        # Run validation
        try:
            result = validate_project_data(project_data)
            # If validation passes, check that required fields are present
            assert "name" in result
            assert "participants" in result
            assert "project_type" in result
            
            # Check that participants is a list with at least one item
            assert isinstance(result["participants"], list)
            assert len(result["participants"]) > 0
            
            # If goals is present, ensure it's a list
            if "goals" in result:
                assert isinstance(result["goals"], list)
            
            # If settings is present, ensure it's a dict
            if "settings" in result:
                assert isinstance(result["settings"], dict)
        
        except Exception as e:
            # For debugging: print details when validation fails unexpectedly
            print(f"Validation failed for: {project_data}")
            print(f"Error: {str(e)}")
            raise


@pytest.mark.property
class TestAnalysisService:
    """Property-based tests for the analysis service."""
    
    @pytest.mark.skipif(not analysis_available, reason="Analysis service not available")
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(conversation=conversation_text_strategy())
    def test_sentiment_analysis_robustness(self, conversation):
        """Test that sentiment analysis handles various conversation formats."""
        analysis_service = AnalysisService()
        
        # The sentiment analysis should work for any valid conversation text
        result = analysis_service.analyze_sentiment(conversation)
        
        # Basic structure validation
        assert isinstance(result, dict)
        assert "sentiment" in result
        assert "confidence" in result
        
        # Sentiment should be one of the expected values
        assert result["sentiment"] in ["positive", "negative", "neutral", "mixed"]
        
        # Confidence should be a number between 0 and 1
        assert 0 <= result["confidence"] <= 1
        
        # If emotions are present, they should be a list of strings
        if "emotions" in result:
            assert isinstance(result["emotions"], list)
            assert all(isinstance(emotion, str) for emotion in result["emotions"])
    
    @pytest.mark.skipif(not analysis_available, reason="Analysis service not available")
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(conversation=conversation_text_strategy())
    def test_keyword_extraction_robustness(self, conversation):
        """Test that keyword extraction handles various conversation formats."""
        analysis_service = AnalysisService()
        
        # The keyword extraction should work for any valid conversation text
        keywords = analysis_service.extract_keywords(conversation)
        
        # Basic validation
        assert isinstance(keywords, list)
        
        # All keywords should be strings
        assert all(isinstance(keyword, str) for keyword in keywords)
        
        # There should be no empty strings
        assert all(keyword.strip() for keyword in keywords)


@pytest.mark.property
class TestKnowledgeBaseService:
    """Property-based tests for the knowledge base service."""
    
    @pytest.mark.skipif(not kb_available, reason="Knowledge base service not available")
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(document=knowledge_document_strategy())
    def test_document_processing(self, document, temp_storage):
        """Test that the knowledge base can process various document structures."""
        from services.knowledge_base_service import KnowledgeBaseService
        
        # Create a test-specific storage directory
        test_id = str(uuid.uuid4())[:8]
        storage_dir = os.path.join(temp_storage, f"kb_test_{test_id}")
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize the service
        kb_service = KnowledgeBaseService(storage_dir=storage_dir)
        
        try:
            # Process and index the document
            if "id" not in document:
                # Add an ID if not present
                document["id"] = str(uuid.uuid4())
            
            # Add the document to the knowledge base
            doc_id = kb_service.add_document(document)
            
            # Verify the document was added
            assert doc_id is not None
            
            # Retrieve the document
            retrieved = kb_service.get_document(doc_id)
            
            # Verify essential fields
            assert retrieved["id"] == doc_id
            assert retrieved["title"] == document["title"]
            assert retrieved["content"] == document["content"]
            assert retrieved["type"] == document["type"]
            
            # Check tags if present
            if "tags" in document:
                assert "tags" in retrieved
                assert set(retrieved["tags"]) == set(document["tags"])
            
            # Check metadata if present
            if "metadata" in document:
                assert "metadata" in retrieved
                # Check basic metadata structure, not comparing exact values
                # as some processors might modify metadata
                assert isinstance(retrieved["metadata"], dict)
        
        finally:
            # Clean up
            import shutil
            if os.path.exists(storage_dir):
                shutil.rmtree(storage_dir)
    
    @pytest.mark.skipif(not kb_available, reason="Knowledge base service not available")
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    @given(
        documents=st.lists(knowledge_document_strategy(), min_size=1, max_size=10),
        query=st.text(min_size=1, max_size=100)
    )
    def test_search_robustness(self, documents, query, temp_storage):
        """Test that search functionality works across varied documents and queries."""
        from services.knowledge_base_service import KnowledgeBaseService
        
        # Create a test-specific storage directory
        test_id = str(uuid.uuid4())[:8]
        storage_dir = os.path.join(temp_storage, f"kb_search_test_{test_id}")
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize the service
        kb_service = KnowledgeBaseService(storage_dir=storage_dir)
        
        try:
            # Add all documents
            for doc in documents:
                if "id" not in doc:
                    doc["id"] = str(uuid.uuid4())
                kb_service.add_document(doc)
            
            # Perform a search
            results = kb_service.search(query)
            
            # Basic validation
            assert isinstance(results, list)
            
            # Each result should have basic structure
            for result in results:
                assert "id" in result
                assert "title" in result
                assert "score" in result
                assert 0 <= result["score"] <= 1  # Score should be normalized
        
        finally:
            # Clean up
            import shutil
            if os.path.exists(storage_dir):
                shutil.rmtree(storage_dir)


# Execute with: pytest -xvs tests/property/test_properties.py
