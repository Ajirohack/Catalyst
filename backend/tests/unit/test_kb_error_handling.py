"""
Tests for error handling in the Knowledge Base services
"""
import pytest
import os
import sys
import uuid
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from services.knowledge_base import KnowledgeBaseService, DocumentType, ProcessingStatus
    from services.vector_search import VectorSearchService
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)

class TestKnowledgeBaseErrorHandling:
    @pytest.fixture
    async def kb_service(self, temp_storage):
        """Create a knowledge base service for error testing."""
        from services.file_storage_service import FileStorageService
        
        storage_service = FileStorageService(str(temp_storage))
        kb_service = KnowledgeBaseService(storage_service=storage_service)
        
        yield kb_service
        
        # Cleanup
        try:
            for file_path in temp_storage.glob("**/*"):
                if file_path.is_file():
                    file_path.unlink()
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    @pytest.mark.asyncio
    async def test_invalid_document_id(self, kb_service, error_conditions):
        """Test handling of invalid document IDs."""
        # Try to get a document with an invalid ID
        invalid_id = error_conditions["invalid_doc_id"]
        result = await kb_service.get_document(invalid_id)
        
        # Should return None for non-existent documents
        assert result is None
        
        # Try to delete a non-existent document
        delete_result = await kb_service.delete_document(invalid_id)
        
        # Should handle gracefully without error
        assert delete_result is not None
        assert delete_result.get("status") == "not_found"
    
    @pytest.mark.asyncio
    async def test_malformed_metadata(self, kb_service, sample_knowledge_doc):
        """Test handling of malformed metadata."""
        doc_id = str(uuid.uuid4())
        
        # Test with invalid metadata types
        with pytest.raises(Exception):
            await kb_service.add_document(
                doc_id=doc_id,
                title=sample_knowledge_doc["title"],
                content_type="text/plain",
                content=sample_knowledge_doc["content"].encode(),
                document_type=DocumentType.REFERENCE,
                metadata=123  # Invalid metadata type
            )
        
        # Test with invalid metadata values
        with pytest.raises(Exception):
            await kb_service.add_document(
                doc_id=doc_id,
                title=sample_knowledge_doc["title"],
                content_type="text/plain",
                content=sample_knowledge_doc["content"].encode(),
                document_type=DocumentType.REFERENCE,
                metadata={"value": float('inf')}  # Invalid infinity value
            )
    
    @pytest.mark.asyncio
    async def test_storage_failures(self, temp_storage, sample_knowledge_doc):
        """Test handling of storage failures."""
        from services.file_storage_service import FileStorageService
        
        # Create a mock storage service that fails
        mock_storage = MagicMock(spec=FileStorageService)
        mock_storage.store_file.side_effect = Exception("Storage failure")
        
        # Create KB service with failing storage
        kb_service = KnowledgeBaseService(storage_service=mock_storage)
        
        doc_id = str(uuid.uuid4())
        
        # Attempt to add document with failing storage
        result = await kb_service.add_document(
            doc_id=doc_id,
            title=sample_knowledge_doc["title"],
            content_type="text/plain",
            content=sample_knowledge_doc["content"].encode(),
            document_type=DocumentType.REFERENCE,
            metadata=sample_knowledge_doc["metadata"]
        )
        
        # Should return error status
        assert result["status"] == ProcessingStatus.ERROR
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_indexing_failures(self, temp_storage, sample_knowledge_doc):
        """Test handling of indexing failures."""
        from services.file_storage_service import FileStorageService
        
        # Create real storage service
        storage_service = FileStorageService(str(temp_storage))
        
        # Create mock vector service that fails
        mock_vector = MagicMock(spec=VectorSearchService)
        mock_vector.index_document.side_effect = Exception("Indexing failure")
        
        # Create KB service with failing vector service
        kb_service = KnowledgeBaseService(
            storage_service=storage_service,
            vector_service=mock_vector
        )
        
        # Add a document successfully
        doc_id = str(uuid.uuid4())
        add_result = await kb_service.add_document(
            doc_id=doc_id,
            title=sample_knowledge_doc["title"],
            content_type="text/plain",
            content=sample_knowledge_doc["content"].encode(),
            document_type=DocumentType.REFERENCE,
            metadata=sample_knowledge_doc["metadata"]
        )
        
        # Verify document was added
        assert add_result["status"] == ProcessingStatus.COMPLETED
        
        # Attempt to index with failing vector service
        index_result = await kb_service.index_document(doc_id)
        
        # Should return error status
        assert index_result["status"] == ProcessingStatus.ERROR
        assert "error" in index_result
    
    @pytest.mark.asyncio
    async def test_empty_content(self, kb_service, error_conditions):
        """Test handling of empty content."""
        doc_id = str(uuid.uuid4())
        
        # Try to add document with empty content
        result = await kb_service.add_document(
            doc_id=doc_id,
            title="Empty Document",
            content_type="text/plain",
            content=error_conditions["empty_content"].encode(),
            document_type=DocumentType.REFERENCE,
            metadata={}
        )
        
        # Should handle empty content gracefully
        assert result["status"] == ProcessingStatus.COMPLETED
        
        # Retrieve and check the document
        doc = await kb_service.get_document(doc_id)
        assert doc is not None
        assert doc["doc_id"] == doc_id
        
        # Try to index empty document
        index_result = await kb_service.index_document(doc_id)
        
        # Should handle empty content indexing appropriately
        # (exact behavior depends on implementation - could be warning or error)
        assert index_result is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_errors(self, kb_service, sample_knowledge_doc):
        """Test handling of errors during concurrent operations."""
        # Create valid and invalid document operations
        async def add_valid_doc(index):
            doc_id = f"valid-doc-{index}"
            return await kb_service.add_document(
                doc_id=doc_id,
                title=f"Valid Document {index}",
                content_type="text/plain",
                content=sample_knowledge_doc["content"].encode(),
                document_type=DocumentType.REFERENCE,
                metadata={"index": index}
            )
        
        async def add_invalid_doc(index):
            doc_id = f"invalid-doc-{index}"
            # Force an error with invalid document type
            try:
                return await kb_service.add_document(
                    doc_id=doc_id,
                    title=f"Invalid Document {index}",
                    content_type="text/plain",
                    content=sample_knowledge_doc["content"].encode(),
                    document_type="invalid_type",  # Invalid enum value
                    metadata={"index": index}
                )
            except Exception as e:
                return {"status": "error", "error": str(e), "doc_id": doc_id}
        
        # Mix valid and invalid operations
        tasks = []
        for i in range(5):
            if i % 2 == 0:
                tasks.append(add_valid_doc(i))
            else:
                tasks.append(add_invalid_doc(i))
        
        # Run concurrently and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify some operations succeeded and others failed
        valid_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == ProcessingStatus.COMPLETED)
        error_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "error" or isinstance(r, Exception))
        
        # We expect alternating success/failure
        assert valid_count > 0
        assert error_count > 0
        assert valid_count + error_count == 5
