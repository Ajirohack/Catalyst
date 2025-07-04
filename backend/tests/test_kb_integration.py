"""
Integration tests for Knowledge Base with actual file storage
"""
import pytest
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path

from services.knowledge_base import KnowledgeBaseService, DocumentType, ProcessingStatus
from services.vector_search import VectorSearchService

class TestKnowledgeBaseIntegration:
    @pytest.fixture
    async def storage_service(self, temp_storage):
        """Create a real storage service instance for testing."""
        service = KnowledgeBaseService(storage_path=str(temp_storage))
        await service.initialize()
        yield service
        # Cleanup after tests
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_file_storage_integration(self, storage_service, sample_file_content, temp_storage):
        """Test integration with actual file storage"""
        # Create a test file
        test_file_path = temp_storage / "test_document.txt"
        test_file_path.write_bytes(sample_file_content)

        # Index the file
        result = await storage_service.index_document_file(
            file_path=str(test_file_path),
            title="Test Document",
            doc_type=DocumentType.REFERENCE.value,
            tags=["test", "integration"]
        )

        # Verify indexing result
        assert result["success"]
        assert "document_id" in result
        doc_id = result["document_id"]

        # Verify file was stored properly
        stored_path = Path(storage_service.get_document_path(doc_id))
        assert stored_path.exists()
        assert stored_path.read_bytes() == sample_file_content

        # Test searching for the indexed content
        search_results = await storage_service.search(
            query="sample file content",
            limit=5
        )

        assert len(search_results) > 0
        assert any(doc_id in result.document_id for result in search_results)

        # Test document retrieval
        doc = await storage_service.get_document(doc_id)
        assert doc is not None
        assert doc.title == "Test Document"
        assert doc.document_type == DocumentType.REFERENCE

        print("✅ File storage integration test passed")

    @pytest.mark.asyncio
    async def test_concurrent_access(self, storage_service, sample_knowledge_doc):
        """Test concurrent access to the knowledge base"""
        # Create multiple concurrent indexing operations
        async def index_doc(index):
            doc = sample_knowledge_doc.copy()
            doc["title"] = f"Concurrent Doc {index}"
            return await storage_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )

        # Run multiple indexing operations concurrently
        tasks = [index_doc(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # Verify all operations succeeded
        assert all(result["success"] for result in results)
        assert len(set(result["document_id"] for result in results)) == 5  # All IDs should be unique

        # Test concurrent searches
        async def search_docs(query):
            return await storage_service.search(query=query, limit=10)

        search_tasks = [
            search_docs("sample document"),
            search_docs("concurrent"),
            search_docs("test")
        ]
        search_results = await asyncio.gather(*search_tasks)

        # Verify search results
        assert all(len(results) > 0 for results in search_results)

        print("✅ Concurrent access test passed")

    @pytest.mark.asyncio
    async def test_large_document_handling(self, storage_service, temp_storage):
        """Test handling of large documents"""
        # Create a large test document (5MB)
        large_content = "Large document content for testing. " * (5 * 1024 * 1024 // 30)
        large_file_path = temp_storage / "large_document.txt"
        large_file_path.write_text(large_content)

        start_time = datetime.now()
        
        # Index the large document
        result = await storage_service.index_document_file(
            file_path=str(large_file_path),
            title="Large Test Document",
            doc_type=DocumentType.REFERENCE.value,
            tags=["test", "large"]
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        # Verify indexing result
        assert result["success"]
        assert "chunks_created" in result
        assert result["chunks_created"] > 1  # Should be split into multiple chunks

        # Verify processing time is reasonable
        assert processing_time < 30  # Should process within 30 seconds

        # Test searching in the large document
        search_results = await storage_service.search(
            query="document content",
            limit=5
        )

        assert len(search_results) > 0
        assert search_results[0].similarity_score > 0.5

        print("✅ Large document handling test passed")
