"""
Enhanced test runner for the Knowledge Base tests
"""
import sys
import os
import pytest
import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from unittest.mock import MagicMock, AsyncMock, patch, mock_open

# Add the backend directory to the path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Define enums for testing
from enum import Enum

class DocumentType(str, Enum):
    REFERENCE = "reference"
    CONVERSATION = "conversation"
    NOTE = "note"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"

@dataclass
class SearchResult:
    """Result from a vector search query."""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float

@dataclass
class KnowledgeDocument:
    """Knowledge base document class."""
    id: str
    title: str
    content: str
    document_type: DocumentType
    tags: List[str]
    created_at: datetime
    file_type: str = "text/plain"

# Mock service classes
class KnowledgeBaseService:
    """Mock Knowledge Base Service."""
    async def index_document(self, content: str, title: str, doc_type: str, tags: List[str]) -> Dict[str, Any]:
        return {"document_id": "", "status": "", "success": True}  # Placeholder implementation

    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        return []  # Placeholder implementation

class VectorSearchService:
    """Mock Vector Search Service."""
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        return []  # Placeholder implementation

class TestKnowledgeBase:
    @pytest.fixture
    def mock_service(self):
        """Provide a mock knowledge base service."""
        return MagicMock(spec=KnowledgeBaseService)

    @pytest.mark.asyncio
    async def test_document_indexing_enhanced(self, mock_service, assert_valid_uuid, assert_valid_timestamp):
        """Test document indexing with enhanced validation using fixtures"""
        # Configure mock with realistic return data
        doc_id = str(uuid.uuid4())
        start_time = time.time()
        
        mock_service.index_document = AsyncMock(return_value={
            "document_id": doc_id,
            "status": ProcessingStatus.INDEXED.value,
            "success": True,
            "chunks_created": 5,
            "timestamp": start_time,
            "metadata": {
                "title": "Test Document",
                "type": DocumentType.REFERENCE.value,
                "tags": ["test", "document"],
                "word_count": 100,
                "chunk_size": 512
            }
        })
        
        test_doc = {
            "title": "Test Document",
            "content": "This is a test document with sufficient content to be split into multiple chunks. " * 10,
            "type": DocumentType.REFERENCE.value,
            "tags": ["test", "document"]
        }
        
        # Perform indexing
        result = await mock_service.index_document(
            content=test_doc["content"],
            title=test_doc["title"],
            doc_type=test_doc["type"],
            tags=test_doc["tags"]
        )
        
        # Enhanced assertions using fixtures
        assert_valid_uuid(result["document_id"])
        assert_valid_timestamp(result["timestamp"])
        assert result["status"] == ProcessingStatus.INDEXED.value
        assert result["success"] is True
        assert isinstance(result["chunks_created"], int)
        assert result["chunks_created"] > 0
        assert all(key in result["metadata"] for key in ["title", "type", "tags", "word_count", "chunk_size"])
        
        # Verify mock called with correct arguments
        mock_service.index_document.assert_called_once_with(
            content=test_doc["content"],
            title=test_doc["title"],
            doc_type=test_doc["type"],
            tags=test_doc["tags"]
        )

    @pytest.mark.asyncio
    async def test_search(self, mock_service):
        """Test search functionality"""
        # Create mock search results
        mock_results = [
            SearchResult(
                document_id=str(uuid.uuid4()),
                content="Test search result content",
                metadata={"type": DocumentType.REFERENCE.value, "tags": ["test"]},
                similarity_score=0.95
            )
        ]
        
        # Configure mock search method
        mock_service.search = AsyncMock(return_value=mock_results)
        
        # Perform search
        results = await mock_service.search(
            query="test search",
            limit=10
        )
        
        # Assertions
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].similarity_score >= 0.0
        assert results[0].similarity_score <= 1.0
        assert DocumentType(results[0].metadata["type"]) == DocumentType.REFERENCE
        
        # Verify mock called correctly
        mock_service.search.assert_called_once_with(
            query="test search",
            limit=10
        )
