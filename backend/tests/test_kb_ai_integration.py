"""
Tests for AI integration with Knowledge Base
"""
import pytest
import os
import sys
import uuid
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from services.knowledge_base import KnowledgeBaseService, DocumentType, ProcessingStatus
    from services.ai_service import AIService
    from services.vector_search import VectorSearchService
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)

class TestAIKnowledgeBaseIntegration:
    @pytest.fixture
    async def ai_kb_service(self, temp_storage, mock_ai_service):
        """Create a knowledge base service with AI integration."""
        from services.file_storage_service import FileStorageService
        
        storage_service = FileStorageService(str(temp_storage))
        vector_service = VectorSearchService()
        
        # Create knowledge base with AI service
        kb_service = KnowledgeBaseService(
            storage_service=storage_service,
            vector_service=vector_service,
            ai_service=mock_ai_service
        )
        
        yield kb_service
        
        # Cleanup
        try:
            for file_path in temp_storage.glob("**/*"):
                if file_path.is_file():
                    file_path.unlink()
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    @pytest.mark.asyncio
    async def test_ai_powered_search(self, ai_kb_service, sample_knowledge_doc):
        """Test AI-enhanced semantic search capabilities."""
        # Add sample documents
        doc_ids = []
        for i in range(5):
            content = f"Document {i} about {['communication', 'relationships', 'therapy', 'emotions', 'conflict'][i]}: {sample_knowledge_doc['content']}"
            doc_id = f"ai-doc-{i}"
            doc_ids.append(doc_id)
            
            await ai_kb_service.add_document(
                doc_id=doc_id,
                title=f"AI Test Document {i}",
                content_type="text/plain",
                content=content.encode(),
                document_type=DocumentType.REFERENCE,
                metadata={"topic": ["communication", "relationships", "therapy", "emotions", "conflict"][i]}
            )
            
            # Index the document
            await ai_kb_service.index_document(doc_id)
        
        # Perform semantic search with AI-generated embeddings
        results = await ai_kb_service.semantic_search("How to improve communication in relationships?", limit=3)
        
        # Verify results include appropriate documents (should find communication and relationships documents)
        assert len(results) > 0
        
        # The mock AI service should have been called to generate embeddings
        # and the results should include relevant documents based on the mocked embeddings
        
        topics = [doc.get("metadata", {}).get("topic") for doc in results]
        assert "communication" in topics or "relationships" in topics
    
    @pytest.mark.asyncio
    async def test_document_summarization(self, ai_kb_service, sample_knowledge_doc):
        """Test AI-powered document summarization."""
        # Create a document with substantial content
        doc_id = str(uuid.uuid4())
        content = sample_knowledge_doc["content"] * 10  # Make it longer
        
        await ai_kb_service.add_document(
            doc_id=doc_id,
            title="Document for Summarization",
            content_type="text/plain",
            content=content.encode(),
            document_type=DocumentType.REFERENCE,
            metadata={"summarize": True}
        )
        
        # Request a summary of the document
        summary = await ai_kb_service.summarize_document(doc_id)
        
        # Verify summary was generated
        assert summary is not None
        assert "summary" in summary
        assert summary["summary"] == "This is a summary of the provided content."  # From mock
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, ai_kb_service, sample_knowledge_doc):
        """Test AI-powered entity extraction from documents."""
        # Create a document with entities
        doc_id = str(uuid.uuid4())
        content = "John and Sarah discussed their relationship issues with Dr. Martinez on Monday at the Sunshine Therapy Center."
        
        await ai_kb_service.add_document(
            doc_id=doc_id,
            title="Entity Extraction Test",
            content_type="text/plain",
            content=content.encode(),
            document_type=DocumentType.REFERENCE,
            metadata={"extract_entities": True}
        )
        
        # Extract entities from the document
        entities = await ai_kb_service.extract_entities(doc_id)
        
        # Verify entities were extracted
        assert entities is not None
        assert len(entities) > 0
        
        # Check for expected entity types based on mock
        entity_types = [e["type"] for e in entities]
        assert "skill" in entity_types
        assert "concept" in entity_types
    
    @pytest.mark.asyncio
    async def test_question_answering(self, ai_kb_service, sample_knowledge_doc):
        """Test AI-powered question answering using the knowledge base."""
        # Add multiple documents to form a knowledge corpus
        for i in range(5):
            doc_id = f"qa-doc-{i}"
            topic = ["communication", "conflict resolution", "active listening", "emotional intelligence", "relationship dynamics"][i]
            content = f"This document covers {topic}. " + sample_knowledge_doc["content"]
            
            await ai_kb_service.add_document(
                doc_id=doc_id,
                title=f"QA Document {i}",
                content_type="text/plain",
                content=content.encode(),
                document_type=DocumentType.REFERENCE,
                metadata={"topic": topic}
            )
            
            # Index each document
            await ai_kb_service.index_document(doc_id)
        
        # Ask a question that requires knowledge from the documents
        question = "How can active listening improve relationships?"
        answer = await ai_kb_service.answer_question(question)
        
        # Verify an answer was generated
        assert answer is not None
        assert "answer" in answer
        assert answer["answer"] == "This is a test answer based on the provided context."  # From mock
        assert "confidence" in answer
        assert "sources" in answer
    
    @pytest.mark.asyncio
    async def test_document_classification(self, ai_kb_service, sample_knowledge_doc):
        """Test AI-powered document classification."""
        # Create document classifier method that uses the AI service
        async def classify_document(doc_id):
            # Get document
            doc = await ai_kb_service.get_document(doc_id)
            if not doc:
                return {"status": "error", "error": "Document not found"}
            
            # Use AI service to classify
            # The mock will return entities that we can use as categories
            entities = await ai_kb_service._ai_service.extract_entities(doc.get("content", ""))
            
            # Extract categories from entities
            categories = [e["text"] for e in entities if e["score"] > 0.8]
            
            # Update document metadata with categories
            await ai_kb_service.update_document(
                doc_id=doc_id,
                metadata={"categories": categories}
            )
            
            return {"status": "success", "categories": categories}
        
        # Add a document to classify
        doc_id = str(uuid.uuid4())
        await ai_kb_service.add_document(
            doc_id=doc_id,
            title="Classification Test",
            content_type="text/plain",
            content=sample_knowledge_doc["content"].encode(),
            document_type=DocumentType.REFERENCE,
            metadata={}
        )
        
        # Classify the document
        result = await classify_document(doc_id)
        
        # Verify classification
        assert result["status"] == "success"
        assert "categories" in result
        assert len(result["categories"]) > 0
        
        # Check that document metadata was updated
        doc = await ai_kb_service.get_document(doc_id)
        assert "categories" in doc["metadata"]
        assert doc["metadata"]["categories"] == result["categories"]
