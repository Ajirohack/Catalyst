"""
Integration tests for the Knowledge Base with actual file storage
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator
from datetime import datetime

from services.knowledge_base import KnowledgeBaseService, DocumentType, ProcessingStatus
from services.vector_search import VectorSearchService

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

class TestKnowledgeBaseFileStorage:
    @pytest.fixture(autouse=True)
    async def setup_storage(self, temp_storage, sample_knowledge_doc, sample_file_content):
        """Set up temporary storage and test files."""
        self.storage_path = temp_storage
        self.test_doc = sample_knowledge_doc
        self.test_file_content = sample_file_content
        
        # Create test file
        test_file_path = self.storage_path / "test_document.txt"
        test_file_path.write_bytes(self.test_file_content)
        self.test_file_path = test_file_path
        
        # Initialize services with actual storage
        self.kb_service = KnowledgeBaseService(storage_path=str(self.storage_path))
        self.vector_service = VectorSearchService()
        
        yield
        
        # Cleanup any created files
        if test_file_path.exists():
            test_file_path.unlink()

    async def test_document_indexing_with_file(self, assert_valid_uuid, assert_valid_timestamp):
        """Test indexing a document from an actual file."""
        # Index the test document
        result = await self.kb_service.index_document(
            content=self.test_file_content.decode(),
            title=self.test_doc["title"],
            doc_type=self.test_doc["type"],
            tags=self.test_doc["tags"]
        )
        
        # Verify the document was indexed
        assert result["success"] is True
        assert result["status"] == ProcessingStatus.INDEXED.value
        assert_valid_uuid(result["document_id"])
        assert result["chunks_created"] > 0
        assert_valid_timestamp(result["timestamp"])
        
        # Verify the document files were created
        doc_path = self.storage_path / f"{result['document_id']}.json"
        assert doc_path.exists()
        
        # Test searching for the indexed content
        search_results = await self.kb_service.search(
            query="sample document content",
            limit=5
        )
        
        assert len(search_results) > 0
        assert search_results[0].similarity_score > 0.5
        assert self.test_doc["title"] in search_results[0].metadata.get("title", "")

    @pytest.mark.performance
    async def test_batch_indexing_performance(self, performance_timer, performance_thresholds):
        """Test performance of batch document indexing."""
        num_docs = 10
        docs = []
        
        # Create multiple test documents
        for i in range(num_docs):
            content = f"Test document {i} content. " * 20
            docs.append({
                "content": content,
                "title": f"Test Doc {i}",
                "type": "reference",
                "tags": ["test", f"doc-{i}"]
            })
        
        # Measure indexing performance
        performance_timer.start()
        
        results = []
        for doc in docs:
            result = await self.kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
            results.append(result)
            
        performance_timer.stop()
        
        # Verify performance meets thresholds
        assert performance_timer.elapsed < performance_thresholds["indexing"]["max_time"]
        assert all(r["success"] for r in results)
        assert len(results) == num_docs

    async def test_concurrent_operations(self):
        """Test concurrent indexing and searching operations."""
        async def index_doc(content: str, title: str) -> dict:
            return await self.kb_service.index_document(
                content=content,
                title=title,
                doc_type="reference",
                tags=["test"]
            )
        
        async def search_docs(query: str) -> list:
            return await self.kb_service.search(query=query, limit=5)
        
        # Create multiple concurrent tasks
        tasks = []
        for i in range(5):
            content = f"Concurrent test document {i} content. " * 10
            tasks.append(index_doc(content, f"Concurrent Doc {i}"))
            tasks.append(search_docs("test document"))
        
        # Run operations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify no exceptions occurred
        assert not any(isinstance(r, Exception) for r in results)
        
        # Verify indexing and search results
        index_results = [r for r in results[::2]]  # Even indices are index results
        search_results = [r for r in results[1::2]]  # Odd indices are search results
        
        assert all(r["success"] for r in index_results)
        assert all(len(r) > 0 for r in search_results)

    @pytest.mark.error_handling
    async def test_error_conditions(self, error_conditions):
        """Test error handling with various invalid inputs."""
        # Test empty content
        with pytest.raises(ValueError):
            await self.kb_service.index_document(
                content=error_conditions["empty_content"],
                title="Empty Doc",
                doc_type="reference",
                tags=["test"]
            )
        
        # Test oversized content
        with pytest.raises(ValueError):
            await self.kb_service.index_document(
                content=error_conditions["oversized_content"],
                title="Oversized Doc",
                doc_type="reference",
                tags=["test"]
            )
        
        # Test invalid document type
        with pytest.raises(ValueError):
            await self.kb_service.index_document(
                content="Valid content",
                title="Invalid Type Doc",
                doc_type="invalid_type",
                tags=["test"]
            )
        
        # Test invalid tag types
        with pytest.raises(TypeError):
            await self.kb_service.index_document(
                content="Valid content",
                title="Invalid Tags Doc",
                doc_type="reference",
                tags=error_conditions["invalid_tags"]
            )
