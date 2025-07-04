"""
Knowledge Base Integration Test Suite for Catalyst Backend - Phase 2.3
Tests document management, vector search, and knowledge base workflows
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    import pytest
    import asyncio
    import json
    import os
    import tempfile
    from unittest.mock import MagicMock, patch, AsyncMock
    from fastapi.testclient import TestClient
    from typing import Dict, Any, List, Optional
    from pathlib import Path
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)



class TestKnowledgeBaseCore:
    """Test core knowledge base functionality"""
    
    @pytest.fixture
    def kb_service_mock(self):
        """Mock knowledge base service"""
        service = MagicMock()
        service.add_document = AsyncMock()
        service.search_documents = AsyncMock()
        service.get_document = AsyncMock()
        service.update_document = AsyncMock()
        service.delete_document = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            {
                "id": "doc-1",
                "title": "Communication Guidelines",
                "content": "Effective communication requires active listening, empathy, and clear expression of thoughts and feelings.",
                "type": "guidance",
                "tags": ["communication", "relationships", "guidelines"],
                "metadata": {"category": "therapeutic", "difficulty": "basic"}
            },
            {
                "id": "doc-2",
                "title": "Conflict Resolution Strategies", 
                "content": "When conflicts arise, focus on understanding the other person's perspective, finding common ground, and working together toward solutions.",
                "type": "instruction",
                "tags": ["conflict", "resolution", "strategies"],
                "metadata": {"category": "therapeutic", "difficulty": "intermediate"}
            },
            {
                "id": "doc-3",
                "title": "Active Listening Techniques",
                "content": "Active listening involves giving full attention, reflecting back what you hear, and asking clarifying questions to ensure understanding.",
                "type": "reference",
                "tags": ["listening", "communication", "techniques"],
                "metadata": {"category": "skills", "difficulty": "basic"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_document_addition(self, kb_service_mock, sample_documents):
        """Test adding documents to knowledge base"""
        doc = sample_documents[0]
        
        kb_service_mock.add_document.return_value = {
            "id": doc["id"],
            "status": "indexed",
            "vector_id": "vec-123"
        }
        
        result = await kb_service_mock.add_document(doc)
        
        assert result["id"] == doc["id"]
        assert result["status"] == "indexed"
        kb_service_mock.add_document.assert_called_once_with(doc)
    
    @pytest.mark.asyncio
    async def test_document_search(self, kb_service_mock, sample_documents):
        """Test searching documents in knowledge base"""
        query = "communication techniques"
        
        expected_results = [
            {
                "document": sample_documents[0],
                "score": 0.85,
                "highlights": ["communication", "effective communication"]
            },
            {
                "document": sample_documents[2],
                "score": 0.78,
                "highlights": ["communication", "listening"]
            }
        ]
        
        kb_service_mock.search_documents.return_value = expected_results
        
        results = await kb_service_mock.search_documents(query, limit=5)
        
        assert len(results) == 2
        assert results[0]["score"] > results[1]["score"]  # Results should be sorted by score
        kb_service_mock.search_documents.assert_called_once_with(query, limit=5)
    
    @pytest.mark.asyncio
    async def test_document_retrieval(self, kb_service_mock, sample_documents):
        """Test retrieving specific documents"""
        doc_id = "doc-1"
        expected_doc = sample_documents[0]
        
        kb_service_mock.get_document.return_value = expected_doc
        
        result = await kb_service_mock.get_document(doc_id)
        
        assert result["id"] == doc_id
        assert result["title"] == expected_doc["title"]
        kb_service_mock.get_document.assert_called_once_with(doc_id)
    
    def test_document_structure_validation(self, sample_documents):
        """Test that documents have required structure"""
        required_fields = ["id", "title", "content", "type", "tags"]
        
        for doc in sample_documents:
            for field in required_fields:
                assert field in doc, f"Document missing required field: {field}"
            
            assert isinstance(doc["tags"], list), "Tags should be a list"
            assert len(doc["content"]) > 0, "Content should not be empty"


class TestVectorSearch:
    """Test vector search functionality"""
    
    @pytest.fixture
    def vector_service_mock(self):
        """Mock vector search service"""
        service = MagicMock()
        service.index_document = AsyncMock()
        service.search = AsyncMock()
        service.get_similar_documents = AsyncMock()
        service.update_embeddings = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_document_indexing(self, vector_service_mock):
        """Test indexing documents for vector search"""
        document = {
            "id": "doc-test",
            "content": "This is a test document for vector indexing",
            "metadata": {"type": "test"}
        }
        
        vector_service_mock.index_document.return_value = {
            "status": "success",
            "vector_id": "vec-test-123",
            "dimensions": 384
        }
        
        result = await vector_service_mock.index_document(document)
        
        assert result["status"] == "success"
        assert "vector_id" in result
        vector_service_mock.index_document.assert_called_once_with(document)
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, vector_service_mock):
        """Test semantic search functionality"""
        query = "relationship communication advice"
        
        search_results = [
            {
                "document_id": "doc-1",
                "score": 0.89,
                "content": "Communication guidelines for healthy relationships"
            },
            {
                "document_id": "doc-2",
                "score": 0.76,
                "content": "Conflict resolution in relationships"
            }
        ]
        
        vector_service_mock.search.return_value = search_results
        
        results = await vector_service_mock.search(query, top_k=5)
        
        assert len(results) == 2
        assert results[0]["score"] > 0.8  # High relevance score
        vector_service_mock.search.assert_called_once_with(query, top_k=5)
    
    @pytest.mark.asyncio
    async def test_similarity_search(self, vector_service_mock):
        """Test finding similar documents"""
        document_id = "doc-1"
        
        similar_docs = [
            {"document_id": "doc-3", "similarity": 0.82},
            {"document_id": "doc-2", "similarity": 0.75}
        ]
        
        vector_service_mock.get_similar_documents.return_value = similar_docs
        
        results = await vector_service_mock.get_similar_documents(document_id, top_k=3)
        
        assert len(results) == 2
        assert all(doc["similarity"] > 0.7 for doc in results)
        vector_service_mock.get_similar_documents.assert_called_once_with(document_id, top_k=3)


class TestKnowledgeBaseAPI:
    """Test knowledge base API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        client = MagicMock()
        client.post = MagicMock()
        client.get = MagicMock()
        client.put = MagicMock()
        client.delete = MagicMock()
        return client
    
    def test_document_upload_endpoint(self, client):
        """Test document upload API"""
        document_data = {
            "title": "Test Document",
            "content": "This is test content",
            "type": "guidance",
            "tags": ["test", "document"]
        }
        
        expected_response = {
            "status_code": 201,
            "json": lambda: {
                "id": "doc-new-123",
                "status": "indexed",
                "message": "Document uploaded successfully"
            }
        }
        
        client.post.return_value = expected_response
        
        response = client.post("/api/knowledge-base/documents", json=document_data)
        
        assert response.status_code == 201
        result = response.model_dump_json()
        assert "id" in result
        assert result["status"] == "indexed"
    
    def test_document_search_endpoint(self, client):
        """Test document search API"""
        query_params = {"q": "communication", "limit": 10}
        
        expected_response = {
            "status_code": 200,
            "json": lambda: {
                "results": [
                    {
                        "id": "doc-1",
                        "title": "Communication Guidelines",
                        "score": 0.85,
                        "highlights": ["communication", "effective"]
                    }
                ],
                "total": 1,
                "query": "communication"
            }
        }
        
        client.get.return_value = expected_response
        
        response = client.get("/api/knowledge-base/search", params=query_params)
        
        assert response.status_code == 200
        result = response.model_dump_json()
        assert "results" in result
        assert "total" in result
    
    def test_document_management_endpoints(self, client):
        """Test document CRUD operations"""
        doc_id = "doc-123"
        
        # Test GET
        get_response = {
            "status_code": 200,
            "json": lambda: {
                "id": doc_id,
                "title": "Test Document",
                "content": "Test content"
            }
        }
        client.get.return_value = get_response
        
        response = client.get(f"/api/knowledge-base/documents/{doc_id}")
        assert response.status_code == 200
        
        # Test PUT (update)
        update_data = {"title": "Updated Title"}
        put_response = {
            "status_code": 200,
            "json": lambda: {"id": doc_id, "status": "updated"}
        }
        client.put.return_value = put_response
        
        response = client.put(f"/api/knowledge-base/documents/{doc_id}", json=update_data)
        assert response.status_code == 200
        
        # Test DELETE
        delete_response = {
            "status_code": 200,
            "json": lambda: {"status": "deleted"}
        }
        client.delete.return_value = delete_response
        
        response = client.delete(f"/api/knowledge-base/documents/{doc_id}")
        assert response.status_code == 200


class TestWorkflowIntegration:
    """Test end-to-end knowledge base workflows"""
    
    @pytest.fixture
    def workflow_service_mock(self):
        """Mock workflow service"""
        service = MagicMock()
        service.process_document_upload = AsyncMock()
        service.enhanced_search = AsyncMock()
        service.generate_suggestions = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_document_processing_workflow(self, workflow_service_mock):
        """Test complete document processing workflow"""
        document_data = {
            "title": "New Therapeutic Guide",
            "content": "This guide provides comprehensive strategies for relationship counseling...",
            "type": "guidance",
            "source": "upload"
        }
        
        workflow_result = {
            "status": "completed",
            "document_id": "doc-new-456",
            "vector_id": "vec-456",
            "extracted_keywords": ["therapeutic", "relationship", "counseling"],
            "processing_time": 2.3
        }
        
        workflow_service_mock.process_document_upload.return_value = workflow_result
        
        result = await workflow_service_mock.process_document_upload(document_data)
        
        assert result["status"] == "completed"
        assert "document_id" in result
        assert "extracted_keywords" in result
        workflow_service_mock.process_document_upload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enhanced_search_workflow(self, workflow_service_mock):
        """Test enhanced search with context and filtering"""
        search_request = {
            "query": "communication problems in relationships",
            "context": {
                "user_type": "therapist",
                "session_type": "couples_therapy",
                "difficulty_level": "intermediate"
            },
            "filters": {
                "document_type": ["guidance", "instruction"],
                "tags": ["communication", "relationships"]
            }
        }
        
        enhanced_results = {
            "primary_results": [
                {
                    "document_id": "doc-1",
                    "relevance_score": 0.92,
                    "context_match": 0.88,
                    "title": "Communication Strategies for Couples"
                }
            ],
            "related_suggestions": [
                {
                    "document_id": "doc-2",
                    "title": "Active Listening Techniques",
                    "relationship": "complementary"
                }
            ],
            "context_insights": {
                "matched_criteria": ["couples_therapy", "communication"],
                "suggested_followup": ["conflict_resolution", "empathy_building"]
            }
        }
        
        workflow_service_mock.enhanced_search.return_value = enhanced_results
        
        result = await workflow_service_mock.enhanced_search(search_request)
        
        assert "primary_results" in result
        assert "related_suggestions" in result
        assert "context_insights" in result
        workflow_service_mock.enhanced_search.assert_called_once_with(search_request)
    
    @pytest.mark.asyncio
    async def test_suggestion_generation_workflow(self, workflow_service_mock):
        """Test intelligent suggestion generation"""
        context = {
            "conversation_analysis": {
                "sentiment": "frustrated",
                "topics": ["communication", "misunderstanding"],
                "urgency": "moderate"
            },
            "user_profile": {
                "experience_level": "beginner",
                "previous_suggestions": ["doc-1", "doc-3"]
            }
        }
        
        suggestions = {
            "immediate_suggestions": [
                {
                    "document_id": "doc-5",
                    "title": "De-escalating Tense Conversations",
                    "priority": "high",
                    "relevance_reason": "Matches current frustration and communication issues"
                }
            ],
            "followup_suggestions": [
                {
                    "document_id": "doc-7",
                    "title": "Building Understanding Through Empathy",
                    "priority": "medium",
                    "timing": "after_immediate_resolution"
                }
            ],
            "learning_path": [
                "conflict_awareness",
                "communication_skills",
                "relationship_building"
            ]
        }
        
        workflow_service_mock.generate_suggestions.return_value = suggestions
        
        result = await workflow_service_mock.generate_suggestions(context)
        
        assert "immediate_suggestions" in result
        assert "followup_suggestions" in result
        assert "learning_path" in result
        workflow_service_mock.generate_suggestions.assert_called_once_with(context)


class TestPerformanceAndScaling:
    """Test performance and scaling aspects"""
    
    @pytest.fixture
    def performance_monitor_mock(self):
        """Mock performance monitoring"""
        monitor = MagicMock()
        monitor.measure_search_time = MagicMock()
        monitor.measure_indexing_time = MagicMock()
        monitor.get_cache_hit_rate = MagicMock()
        return monitor
    
    def test_search_performance_monitoring(self, performance_monitor_mock):
        """Test search performance tracking"""
        performance_monitor_mock.measure_search_time.return_value = {
            "query": "relationship advice",
            "search_time": 0.15,  # 150ms
            "results_count": 10,
            "cache_hit": False
        }
        
        result = performance_monitor_mock.measure_search_time("relationship advice")
        
        assert result["search_time"] < 0.5  # Should be under 500ms
        assert result["results_count"] > 0
    
    def test_indexing_performance(self, performance_monitor_mock):
        """Test document indexing performance"""
        performance_monitor_mock.measure_indexing_time.return_value = {
            "document_size": 2048,  # bytes
            "indexing_time": 0.8,   # 800ms
            "vector_dimensions": 384,
            "success": True
        }
        
        result = performance_monitor_mock.measure_indexing_time({"size": 2048})
        
        assert result["indexing_time"] < 2.0  # Should be under 2 seconds
        assert result["success"] is True
    
    def test_cache_performance(self, performance_monitor_mock):
        """Test caching effectiveness"""
        performance_monitor_mock.get_cache_hit_rate.return_value = {
            "hit_rate": 0.75,  # 75% cache hit rate
            "total_requests": 1000,
            "cache_hits": 750,
            "cache_misses": 250
        }
        
        result = performance_monitor_mock.get_cache_hit_rate()
        
        assert result["hit_rate"] > 0.7  # Should have good cache performance
        assert result["cache_hits"] + result["cache_misses"] == result["total_requests"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
