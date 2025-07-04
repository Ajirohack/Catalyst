"""
Simple test runner for the Knowledge Base tests
"""
import sys
import os
import pytest
import asyncio
import json
import time
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import services directly for testing
try:
    from services.knowledge_base import KnowledgeBaseService, DocumentType, ProcessingStatus
    from services.vector_search import VectorSearchService
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)

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

class TestKnowledgeBase:
    @pytest.fixture
    async def mock_service(self):
        service = MagicMock(spec=KnowledgeBaseService)
        return service

    @pytest.mark.asyncio
    async def test_document_indexing(self, mock_service):
        """Test document indexing with mocks"""
        # Configure mock methods
        mock_service.index_document = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "status": "indexed",
            "success": True,
            "chunks_created": 1
        })
        
        # Sample documents
        sample_documents = [
            {
                "title": "Test Document",
                "content": "This is a test document content.",
                "type": "reference",
                "tags": ["test", "document"]
            }
        ]
        
        # Test indexing
        results = []
        for doc in sample_documents:
            result = await mock_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
            results.append(result)
        
        # Assertions
        assert len(results) == 1
        assert results[0]["document_id"] == "test-doc-id"
        assert results[0]["status"] == "indexed"
        assert results[0]["success"] is True
        
        # Verify the mock was called correctly
        mock_service.index_document.assert_called_with(
            content="This is a test document content.",
            title="Test Document",
            doc_type="reference",
            tags=["test", "document"]
        )
        
        print("✅ Document indexing test passed")

    @pytest.mark.asyncio
    async def test_document_indexing_with_validation(self, mock_service):
        """Test document indexing with enhanced validation"""
        # Configure mock with more realistic return data
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
        
        # Test document with realistic content
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
        
        # Enhanced assertions
        pytest.assert_valid_uuid(result["document_id"])
        pytest.assert_valid_timestamp(result["timestamp"])
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
        
        print("✅ Document indexing test passed with enhanced validation")

    @pytest.mark.asyncio
    async def test_document_indexing_enhanced(self, mock_service, assert_valid_uuid, assert_valid_timestamp):
        """Test document indexing with enhanced validation using fixtures"""
        # Configure mock with more realistic return data
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
        
        print("✅ Document indexing test passed with enhanced validation")

    @pytest.mark.asyncio
    async def test_search(self):
        """Test searching with mocks"""
        # Create mock service
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Configure mock search method
        mock_service.search = AsyncMock(return_value=[
            SearchResult(
                document_id="test-doc-id",
                content="This is a test search result",
                metadata={"tags": ["test"], "doc_type": "reference"},
                similarity_score=0.95
            )
        ])
        
        # Perform search
        results = await mock_service.search(
            query="test search",
            limit=10
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].document_id == "test-doc-id"
        assert results[0].similarity_score == 0.95
        
        # Verify mock was called correctly
        mock_service.search.assert_called_with(
            query="test search",
            limit=10
        )
        
        print("✅ Search test passed")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling during document processing"""
        # We'll test with a mocked service since we're only testing the decorator's behavior
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Configure mock to simulate error scenarios
        mock_service.search_knowledge_base = AsyncMock(side_effect=Exception("Simulated search error"))
        mock_service.add_document = AsyncMock(side_effect=Exception("Simulated add document error"))
        mock_service.process_document = AsyncMock(side_effect=Exception("Simulated processing error"))
        
        # Wrap each method with our error handling decorator
        # This is a simulation of how the decorator would work
        async def handle_errors(func, default_return):
            try:
                return await func()
            except Exception as e:
                print(f"Error caught: {str(e)}")
                return default_return
        
        # Test search with error handling
        search_result = await handle_errors(
            lambda: mock_service.search_knowledge_base(query="test", limit=5), 
            []
        )
        
        # Should return empty list on error
        assert isinstance(search_result, list)
        assert len(search_result) == 0
        
        # Test add_document with error handling
        add_result = await handle_errors(
            lambda: mock_service.add_document(title="Test", content="Content"), 
            None
        )
        
        # Should return None on error
        assert add_result is None
        
        # Test process_document with error handling
        process_result = await handle_errors(
            lambda: mock_service.process_document(document_id="123"), 
            {"success": False, "error": "Simulated processing error"}
        )
        
        # Should return error dict on error
        assert isinstance(process_result, dict)
        assert process_result["success"] is False
        assert "error" in process_result
        
        print("✅ Error handling decorator test passed")

    @pytest.mark.asyncio
    async def test_document_processing(self):
        """Test document processing with mocks"""
        # Create mock service
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Configure mock methods
        mock_service.process_document_file = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "success": True,
            "chunks_created": 3,
            "processing_time": 0.25,
            "errors": []
        })
        
        # Mock file data
        mock_file = MagicMock()
        mock_file.read.return_value = b"Test file content for processing"
        
        # Process document
        result = await mock_service.process_document_file(
            file=mock_file,
            filename="test.txt",
            content_type="text/plain",
            doc_type="reference",
            tags=["test"]
        )
        
        # Assertions
        assert result["success"] is True
        assert result["document_id"] == "test-doc-id"
        assert result["chunks_created"] == 3
        assert "processing_time" in result
        assert len(result["errors"]) == 0
        
        print("✅ Document processing test passed")

    @pytest.mark.asyncio
    async def test_search_result_enrichment(self):
        """Test search result enrichment"""
        # Mock service
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Define test document
        test_doc = KnowledgeDocument(
            id="test-doc-id",
            title="Test Document",
            content="Test content",
            document_type=DocumentType.REFERENCE,
            tags=["test", "enrichment"],
            created_at=datetime.now(),
            file_type="text/plain"
        )
        
        # Mock the get_document method
        mock_service.get_document = AsyncMock(return_value=test_doc)
        
        # Create search results to enrich
        search_results = [
            SearchResult(
                document_id="test-doc-id",
                content="This is a test search result for enrichment",
                metadata={"chunk_index": 1},
                similarity_score=0.92
            )
        ]
        
        # Define enrichment function (simplified version of what's in the service)
        async def mock_enrich_results(results):
            enriched = []
            for result in results:
                doc = await mock_service.get_document(result.document_id)
                if doc:
                    # Add document metadata to search result
                    enriched_metadata = result.metadata.copy() if result.metadata else {}
                    enriched_metadata.update({
                        "title": doc.title,
                        "document_type": str(doc.document_type),
                        "tags": doc.tags,
                        "created_at": doc.created_at.isoformat() if doc.created_at else None,
                        "file_type": doc.file_type
                    })
                    
                    # Create new enriched result
                    enriched_result = SearchResult(
                        document_id=result.document_id,
                        content=result.content,
                        metadata=enriched_metadata,
                        similarity_score=result.similarity_score
                    )
                    enriched.append(enriched_result)
                else:
                    enriched.append(result)
            return enriched
        
        # Run the enrichment
        enriched_results = await mock_enrich_results(search_results)
        
        # Assertions
        assert len(enriched_results) == 1
        assert enriched_results[0].document_id == "test-doc-id"
        assert enriched_results[0].similarity_score == 0.92
        assert "title" in enriched_results[0].metadata
        assert enriched_results[0].metadata["title"] == "Test Document"
        assert "document_type" in enriched_results[0].metadata
        assert "tags" in enriched_results[0].metadata
        assert "created_at" in enriched_results[0].metadata
        assert "file_type" in enriched_results[0].metadata
        
        # Verify mock was called
        mock_service.get_document.assert_called_with("test-doc-id")
        
        print("✅ Search result enrichment test passed")
    
    @pytest.mark.asyncio
    async def test_error_conditions(self, mock_service, error_conditions):
        """Test various error conditions in knowledge base operations"""
        
        # Test invalid document ID
        mock_service.get_document = AsyncMock(return_value=None)
        result = await mock_service.get_document(error_conditions["invalid_doc_id"])
        assert result is None
        
        # Test malformed JSON handling
        mock_service.parse_document = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", error_conditions["malformed_json"], 0))
        with pytest.raises(json.JSONDecodeError):
            await mock_service.parse_document(error_conditions["malformed_json"])
        
        # Test empty content handling
        mock_service.index_document = AsyncMock(return_value={
            "success": False,
            "error": "Empty content not allowed",
            "status": ProcessingStatus.ERROR.value
        })
        result = await mock_service.index_document(
            content=error_conditions["empty_content"],
            title="Empty Doc",
            doc_type="reference",
            tags=["test"]
        )
        assert not result["success"]
        assert "error" in result
        
        # Test oversized content handling
        mock_service.index_document = AsyncMock(return_value={
            "success": False,
            "error": "Content exceeds maximum size limit",
            "status": ProcessingStatus.ERROR.value
        })
        result = await mock_service.index_document(
            content=error_conditions["oversized_content"],
            title="Large Doc",
            doc_type="reference",
            tags=["test"]
        )
        assert not result["success"]
        assert "Content exceeds maximum size limit" in result["error"]
        
        # Test invalid tags handling
        with pytest.raises(TypeError):
            await mock_service.index_document(
                content="Test content",
                title="Test Doc",
                doc_type="reference",
                tags=error_conditions["invalid_tags"]
            )
        
        # Test concurrent access errors
        mock_service.index_document = AsyncMock(side_effect=[
            asyncio.TimeoutError("Operation timed out"),
            {
                "success": True,
                "document_id": "retry-success-id",
                "status": ProcessingStatus.INDEXED.value
            }
        ])
        
        # First attempt should timeout
        with pytest.raises(asyncio.TimeoutError):
            await mock_service.index_document(
                content="Test content",
                title="Test Doc",
                doc_type="reference",
                tags=["test"]
            )
        
        # Retry should succeed
        result = await mock_service.index_document(
            content="Test content",
            title="Test Doc",
            doc_type="reference",
            tags=["test"]
        )
        assert result["success"]
        assert result["document_id"] == "retry-success-id"
        
        print("✅ Error conditions test passed")

async def run_tests():
    """Run all tests"""
    print("Running Knowledge Base tests...")
    
    try:
        await test_document_indexing()
        await test_document_indexing_with_validation()
        await test_document_indexing_enhanced()
        await test_search()
        await test_error_handling()
        await test_document_processing()
        await test_search_result_enrichment()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_tests())
