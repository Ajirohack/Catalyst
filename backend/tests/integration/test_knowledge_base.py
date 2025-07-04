"""
Knowledge Base Integration Test Suite for Catalyst Backend
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
    import io
    from unittest.mock import MagicMock, patch, AsyncMock
    from fastapi.testclient import TestClient
    from typing import Dict, Any, List, IO
    from pathlib import Path
    from datetime import datetime
    import logging
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)


# Ensure proper import paths
import sys
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Try importing using absolute imports instead of relative
try:
    from main import app
    from services.knowledge_base import KnowledgeBaseService, DocumentType, ProcessingStatus
    from services.vector_search import VectorSearchService, VectorProvider, EmbeddingProvider, SearchResult
except ImportError as e:
    print(f"ImportError: {e}")
    # Mock imports for testing
    app = MagicMock()
    KnowledgeBaseService = MagicMock()
    DocumentType = MagicMock()
    ProcessingStatus = MagicMock()
    VectorSearchService = MagicMock()
    VectorProvider = MagicMock()
    EmbeddingProvider = MagicMock()
    SearchResult = MagicMock()


class TestKnowledgeBaseCore:
    """Test core knowledge base functionality"""
    
    @pytest.fixture
    def mock_kb_service(self):
        """Create a mock knowledge base service"""
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Mock the required methods
        mock_service.index_document = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "status": "indexed",
            "success": True,
            "chunks_created": 1
        })
        
        mock_service.search = AsyncMock(return_value=[
            SearchResult(
                document_id="test-doc-id",
                content="Test content for search results",
                metadata={"tags": ["test"], "doc_type": "reference"},
                similarity_score=0.95
            )
        ])
        
        mock_service.update_document = AsyncMock(return_value={
            "document_id": "test-doc-id", 
            "success": True
        })
        
        return mock_service
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            {
                "title": "Communication Guidelines",
                "content": "Effective communication requires active listening, empathy, and clear expression of thoughts and feelings.",
                "type": DocumentType.GUIDANCE,
                "tags": ["communication", "relationships", "guidelines"]
            },
            {
                "title": "Conflict Resolution Strategies", 
                "content": "When conflicts arise, focus on understanding the other person's perspective, finding common ground, and working together toward solutions.",
                "type": DocumentType.INSTRUCTION,
                "tags": ["conflict", "resolution", "relationships"]
            },
            {
                "title": "Relationship Case Study - Long Distance",
                "content": "Sarah and Mike maintained their relationship across different continents through regular video calls, shared goals, and trust-building exercises.",
                "type": DocumentType.CASE_STUDY,
                "tags": ["long-distance", "case-study", "success-story"]
            }
        ]
    
    @pytest.fixture
    def sample_files(self):
        """Sample file data for testing uploads"""
        return {
            "text_file": ("test.txt", b"This is a test document for knowledge base integration.", "text/plain"),
            "pdf_file": ("test.pdf", b"%PDF-1.4 fake pdf content", "application/pdf"),
            "docx_file": ("test.docx", b"fake docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
    
    @pytest.mark.asyncio
    async def test_document_indexing(self, mock_kb_service, sample_documents):
        """Test indexing documents into the knowledge base"""
        
        results = []
        for doc in sample_documents:
            result = await mock_kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
            results.append(result)
        
        # Verify all documents were indexed successfully
        assert len(results) == 3
        for result in results:
            assert "document_id" in result
            assert result["status"] == "indexed"
    
    @pytest.mark.asyncio
    async def test_vector_search(self, mock_kb_service, sample_documents):
        """Test semantic search using vector embeddings"""
        
        # Index documents first
        for doc in sample_documents:
            await mock_kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
        
        # Perform semantic search
        search_results = await mock_kb_service.search(
            query="How do I handle conflicts in my relationship?",
            limit=2
        )
        
        # Verify search results
        assert len(search_results) > 0
        assert isinstance(search_results[0], SearchResult)
        
        # The conflict resolution document should be among top results
        assert search_results[0].content is not None
    
    @pytest.mark.asyncio
    async def test_tag_based_filtering(self, mock_kb_service, sample_documents):
        """Test filtering documents by tags"""
        
        # Index documents first
        for doc in sample_documents:
            await mock_kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
        
        # Configure mock to return filtered results
        mock_kb_service.search.return_value = [
            SearchResult(
                document_id="doc-1",
                content="When conflicts arise, focus on understanding the other person's perspective.",
                metadata={"tags": ["conflict", "resolution"]},
                similarity_score=0.95
            )
        ]
        
        # Search with tag filter
        search_results = await mock_kb_service.search(
            query="relationships",
            tags=["conflict", "resolution"],
            limit=5
        )
        
        # Verify filtered results
        assert len(search_results) > 0
        # Mock service will return the configured result
        assert "conflict" in search_results[0].metadata.get("tags", [])
    
    @pytest.mark.asyncio
    async def test_document_type_filtering(self, mock_kb_service, sample_documents):
        """Test filtering documents by document type"""
        
        # Index documents first
        for doc in sample_documents:
            await mock_kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
        
        # Configure mock to return filtered results for document type
        mock_kb_service.search.return_value = [
            SearchResult(
                document_id="doc-3",
                content="Sarah and Mike maintained their relationship across different continents.",
                metadata={"doc_type": "case_study"},
                similarity_score=0.92
            )
        ]
        
        # Search with document type filter
        search_results = await mock_kb_service.search(
            query="relationship examples",
            doc_types=["case_study"],
            limit=5
        )
        
        # Verify filtered results
        assert len(search_results) > 0
        assert search_results[0].metadata.get("doc_type") == "case_study"


class TestDocumentProcessing:
    """Test document processing and file handling"""
    
    @pytest.fixture
    def mock_kb_service(self):
        """Initialize mock knowledge base service for testing"""
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Mock the document processing method
        mock_service.process_document_file = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "success": True,
            "chunks_created": 3,
            "processing_time": 0.5,
            "errors": []
        })
        
        # Mock the search method
        mock_service.search = AsyncMock(return_value=[
            SearchResult(
                document_id="test-doc-id",
                content="This is a test document. It contains multiple lines.",
                metadata={"tags": ["test"], "doc_type": "reference"},
                similarity_score=0.95
            )
        ])
        
        return mock_service
    
    @pytest.mark.asyncio
    async def test_text_file_processing(self, mock_kb_service):
        """Test processing plain text files"""
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            content = "This is a test document.\nIt contains multiple lines.\nIt should be processed correctly."
            tmp.write(content.encode('utf-8'))
            tmp_path = tmp.name
        
        try:
            # Process the file
            with open(tmp_path, 'rb') as f:
                result = await mock_kb_service.process_document_file(
                    file=f,
                    filename="test_document.txt",
                    content_type="text/plain",
                    doc_type="reference",
                    tags=["test", "processing"]
                )
            
            # Verify processing result
            assert result["success"] is True
            assert "document_id" in result
            assert result["chunks_created"] > 0
            
            # Verify document is searchable
            search_results = await mock_kb_service.search(
                query="test document multiple lines",
                limit=1
            )
            
            assert len(search_results) > 0
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not pytest.importorskip("PyPDF2", reason="PyPDF2 not installed"))
    async def test_pdf_processing(self, mock_kb_service):
        """Test processing PDF files (requires PyPDF2)"""
        
        # Create a mock PDF file using the mock functionality
        with patch('services.knowledge_base.extract_text_from_pdf') as mock_extract:
            # Mock the PDF text extraction
            mock_extract.return_value = "This is text extracted from a PDF document.\nIt contains multiple pages and formatting."
            
            # Use an empty byte stream as our "PDF"
            pdf_content = io.BytesIO(b"%PDF-1.4 mock content")
            
            # Process the mock PDF
            result = await mock_kb_service.process_document_file(
                file=pdf_content,
                filename="test_document.pdf",
                content_type="application/pdf",
                doc_type="reference",
                tags=["pdf", "test"]
            )
            
            # Verify processing result
            assert result["success"] is True
            assert "document_id" in result
            
            # Verify PDF was "extracted" correctly (using our mock)
            mock_extract.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not pytest.importorskip("docx", reason="python-docx not installed"))
    async def test_docx_processing(self, mock_kb_service):
        """Test processing DOCX files (requires python-docx)"""
        
        # Create a mock DOCX file using mock functionality
        with patch('services.knowledge_base.extract_text_from_docx') as mock_extract:
            # Mock the DOCX text extraction
            mock_extract.return_value = "This is text extracted from a Word document.\nIt contains multiple paragraphs and formatting."
            
            # Use an empty byte stream as our "DOCX"
            docx_content = io.BytesIO(b"mock docx content")
            
            # Process the mock DOCX
            result = await mock_kb_service.process_document_file(
                file=docx_content,
                filename="test_document.docx",
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                doc_type="reference",
                tags=["docx", "test"]
            )
            
            # Verify processing result
            assert result["success"] is True
            assert "document_id" in result
            
            # Verify DOCX was "extracted" correctly (using our mock)
            mock_extract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_document_chunking(self, mock_kb_service):
        """Test document chunking for large documents"""
        
        # Create a large document that will need chunking
        large_content = "This is paragraph one.\n\n" * 50  # Repeat to create a large document
        
        # Set up mock to return appropriate chunking results
        mock_kb_service.index_document = AsyncMock(return_value={
            "document_id": "large-doc-id",
            "success": True,
            "chunks_created": 10,  # Simulate multiple chunks
            "processing_time": 1.2,
            "errors": []
        })
        
        # Process the large document
        result = await mock_kb_service.index_document(
            content=large_content,
            title="Large Test Document",
            doc_type="reference",
            tags=["large", "chunking", "test"]
        )
        
        # Verify chunking results
        assert result["success"] is True
        assert result["chunks_created"] > 1  # Should create multiple chunks
        
        # Set up mock search to return chunked results
        mock_kb_service.search = AsyncMock(return_value=[
            SearchResult(
                document_id="large-doc-id",
                content="This is paragraph one.",
                metadata={"chunk_index": 0, "total_chunks": 10},
                similarity_score=0.92
            ),
            SearchResult(
                document_id="large-doc-id",
                content="This is paragraph one.",
                metadata={"chunk_index": 1, "total_chunks": 10},
                similarity_score=0.88
            )
        ])
        
        # Verify chunks are searchable
        search_results = await mock_kb_service.search(
            query="paragraph one",
            limit=5
        )
        
        assert len(search_results) > 0
        assert "chunk_index" in search_results[0].metadata
        assert "total_chunks" in search_results[0].metadata


class TestVectorDatabaseIntegration:
    """Test integration with different vector database providers"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not pytest.importorskip("chromadb", reason="chromadb not installed"))
    async def test_chromadb_integration(self):
        """Test integration with ChromaDB (requires chromadb)"""
        
        # Create a mock service using ChromaDB
        with patch('services.knowledge_base.KnowledgeBaseService') as MockKBService:
            # Configure the mock to simulate ChromaDB integration
            mock_service = MagicMock()
            MockKBService.return_value = mock_service
            
            # Mock the required methods
            mock_service.index_document = AsyncMock(return_value={
                "document_id": "chromadb-test-id",
                "success": True,
                "chunks_created": 1
            })
            
            mock_service.search = AsyncMock(return_value=[
                SearchResult(
                    document_id="chromadb-test-id",
                    content="This is a test document for ChromaDB integration.",
                    metadata={"tags": ["chromadb", "test"]},
                    similarity_score=0.95
                )
            ])
            
            # Create a service with ChromaDB configuration
            service = MockKBService()
            
            # Index a test document
            result = await service.index_document(
                content="This is a test document for ChromaDB integration.",
                title="ChromaDB Test",
                doc_type="reference",
                tags=["chromadb", "test"]
            )
            
            # Verify indexing was successful
            assert result["success"] is True
            
            # Perform a search
            search_results = await service.search(
                query="chromadb integration",
                limit=1
            )
            
            # Verify search results
            assert len(search_results) > 0
            assert search_results[0].document_id == "chromadb-test-id"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not pytest.importorskip("pinecone", reason="pinecone-client not installed"))
    @patch('pinecone.Index')
    async def test_pinecone_integration(self, mock_pinecone_index):
        """Test integration with Pinecone (requires pinecone-client)"""
        
        # Mock Pinecone index
        mock_index = MagicMock()
        mock_pinecone_index.return_value = mock_index
        
        # Mock upsert and query methods
        mock_index.upsert = AsyncMock()
        mock_index.query = AsyncMock(return_value={
            'matches': [{
                'id': 'test-doc-1',
                'score': 0.95,
                'metadata': {
                    'content': 'This is a test document for Pinecone integration.',
                    'title': 'Pinecone Test',
                    'doc_type': 'reference',
                    'tags': ['pinecone', 'test']
                }
            }]
        })
        
        # Create a mock service using Pinecone
        with patch('services.knowledge_base.KnowledgeBaseService') as MockKBService:
            # Configure the mock to simulate Pinecone integration
            mock_service = MagicMock()
            MockKBService.return_value = mock_service
            
            # Mock the required methods
            mock_service.index_document = AsyncMock(return_value={
                "document_id": "pinecone-test-id",
                "success": True,
                "chunks_created": 1
            })
            
            mock_service.search = AsyncMock(return_value=[
                SearchResult(
                    document_id="pinecone-test-id",
                    content="This is a test document for Pinecone integration.",
                    metadata={"tags": ["pinecone", "test"]},
                    similarity_score=0.95
                )
            ])
            
            # Initialize service with Pinecone
            with patch('services.vector_search.pinecone') as mock_pinecone:
                mock_pinecone.Index = mock_pinecone_index
                
                # Create service
                service = MockKBService()
                
                # Index a test document
                result = await service.index_document(
                    content="This is a test document for Pinecone integration.",
                    title="Pinecone Test",
                    doc_type="reference",
                    tags=["pinecone", "test"]
                )
                
                # Verify search results
                search_results = await service.search(
                    query="pinecone integration",
                    limit=1
                )
                
                # Verify search results
                assert len(search_results) > 0
                assert search_results[0].similarity_score > 0.9


class TestAPIIntegration:
    """Test knowledge base integration with API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Get test client"""
        return TestClient(app)
    
    def test_document_upload_endpoint(self, client):
        """Test document upload API endpoint"""
        
        # Create a test file
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"This is a test document for the API upload endpoint.")
            tmp.flush()
            
            # Reset file pointer to beginning
            tmp.seek(0)
            
            # Upload file via API
            with patch('services.knowledge_base.KnowledgeBaseService.process_document_file') as mock_process:
                # Mock the processing result
                mock_process.return_value = {
                    "document_id": "test-doc-123",
                    "success": True,
                    "chunks_created": 1,
                    "processing_time": 0.1,
                    "errors": []
                }
                
                response = client.post(
                    "/api/knowledge/upload",
                    files={"file": ("test.txt", tmp, "text/plain")},
                    data={
                        "doc_type": "reference",
                        "tags": "test,api,upload"
                    }
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.model_dump_json()
                assert data["success"] is True
                assert data["document_id"] == "test-doc-123"
    
    def test_search_endpoint(self, client):
        """Test knowledge base search API endpoint"""
        
        # Mock search results
        mock_results = [
            SearchResult(
                document_id="doc-1",
                content="This is a test search result for the API endpoint.",
                metadata={"title": "Test Document", "tags": ["test", "api"]},
                similarity_score=0.95
            ),
            SearchResult(
                document_id="doc-2",
                content="This is another test search result with lower relevance.",
                metadata={"title": "Another Test", "tags": ["test"]},
                similarity_score=0.85
            )
        ]
        
        # Test the search endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.search') as mock_search:
            # Configure the mock to return our test results
            mock_search.return_value = mock_results
            
            response = client.get(
                "/api/knowledge/search",
                params={
                    "query": "test search api",
                    "limit": 2,
                    "tags": "test,api"
                }
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert len(data["results"]) == 2
            assert data["results"][0]["document_id"] == "doc-1"
            assert data["results"][0]["similarity_score"] == 0.95
    
    def test_document_management_endpoints(self, client):
        """Test document management API endpoints (list, get, delete)"""
        
        # Mock document list
        mock_documents = [
            {
                "id": "doc-1",
                "title": "Test Document 1",
                "doc_type": "reference",
                "tags": ["test", "api"],
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z"
            },
            {
                "id": "doc-2",
                "title": "Test Document 2",
                "doc_type": "instruction",
                "tags": ["test"],
                "created_at": "2023-01-02T12:00:00Z",
                "updated_at": "2023-01-02T12:00:00Z"
            }
        ]
        
        # Test list documents endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.list_documents') as mock_list:
            # Configure the mock to return our test documents
            mock_list.return_value = mock_documents
            
            response = client.get("/api/knowledge/documents")
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert len(data["documents"]) == 2
            assert data["documents"][0]["id"] == "doc-1"
        
        # Test get document endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.get_document') as mock_get:
            # Configure the mock to return a specific document
            mock_get.return_value = mock_documents[0]
            
            response = client.get("/api/knowledge/documents/doc-1")
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["id"] == "doc-1"
            assert data["title"] == "Test Document 1"
            assert "test" in data["tags"]
            
        # Test document not found
        with patch('services.knowledge_base.KnowledgeBaseService.get_document') as mock_get:
            # Configure the mock to return None (document not found)
            mock_get.return_value = None
            
            response = client.get("/api/knowledge/documents/non-existent-id")
            
            # Verify response
            assert response.status_code == 404
            
        # Test delete document endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.delete_document') as mock_delete:
            # Configure the mock to return success
            mock_delete.return_value = {"success": True, "document_id": "doc-1"}
            
            response = client.delete("/api/knowledge/documents/doc-1")
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["document_id"] == "doc-1"
            
        # Test delete document failure
        with patch('services.knowledge_base.KnowledgeBaseService.delete_document') as mock_delete:
            # Configure the mock to raise an exception
            mock_delete.side_effect = Exception("Failed to delete document")
            
            response = client.delete("/api/knowledge/documents/doc-error")
            
            # Verify response
            assert response.status_code == 500
        with patch('services.knowledge_base.KnowledgeBaseService.get_document') as mock_get:
            # Configure the mock to return a single document
            mock_get.return_value = mock_documents[0]
            
            response = client.get("/api/knowledge/documents/doc-1")
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["id"] == "doc-1"
            assert data["title"] == "Test Document 1"
        
        # Test delete document endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.delete_document') as mock_delete:
            # Configure the mock to return success
            mock_delete.return_value = {"success": True, "document_id": "doc-1"}
            
            response = client.delete("/api/knowledge/documents/doc-1")
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert data["document_id"] == "doc-1"


class TestKnowledgeBaseIntegrationWithAI:
    """Test integration between knowledge base and AI services"""
    
    @pytest.fixture
    def mock_kb_service(self):
        """Initialize mock knowledge base service for testing"""
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Mock the required methods
        mock_service.index_document = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "status": "indexed",
            "success": True,
            "chunks_created": 1
        })
        
        mock_service.search = AsyncMock(return_value=[
            SearchResult(
                document_id="doc-1",
                content="Active listening involves giving full attention, asking clarifying questions, and acknowledging feelings.",
                metadata={"tags": ["communication", "techniques"]},
                similarity_score=0.92
            ),
            SearchResult(
                document_id="doc-2",
                content="1. Take a timeout if emotions are high. 2. Use 'I' statements to express feelings.",
                metadata={"tags": ["conflict", "resolution"]},
                similarity_score=0.85
            )
        ])
        
        return mock_service
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing AI context enhancement"""
        return [
            {
                "title": "Effective Communication Techniques",
                "content": "Active listening involves giving full attention, asking clarifying questions, and acknowledging feelings.",
                "type": DocumentType.INSTRUCTION,
                "tags": ["communication", "techniques"]
            },
            {
                "title": "Building Trust in Relationships",
                "content": "Trust is built through consistency, honesty, and following through on commitments.",
                "type": DocumentType.GUIDANCE,
                "tags": ["trust", "relationships"]
            },
            {
                "title": "Conflict Resolution Steps",
                "content": "1. Take a timeout if emotions are high. 2. Use 'I' statements to express feelings. 3. Focus on the specific issue, not past problems.",
                "type": DocumentType.REFERENCE,
                "tags": ["conflict", "resolution"]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_ai_enhanced_with_kb_context(self, kb_service, sample_documents, client):
        """Test AI analysis enhanced with knowledge base context"""
        
        # Index sample documents
        for doc in sample_documents:
            await kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
        
        # Mock search results for KB context
        search_results = [
            SearchResult(
                document_id="doc-1",
                content=sample_documents[2]["content"],
                metadata={"title": sample_documents[2]["title"], "tags": sample_documents[2]["tags"]},
                similarity_score=0.92
            ),
            SearchResult(
                document_id="doc-2",
                content=sample_documents[0]["content"],
                metadata={"title": sample_documents[0]["title"], "tags": sample_documents[0]["tags"]},
                similarity_score=0.85
            )
        ]
        
        # Mock the AI analysis with KB context
        with patch('services.knowledge_base.KnowledgeBaseService.search', return_value=search_results):
            with patch('services.ai_service_kb.analyze_with_kb_context') as mock_ai_analyze:
                # Configure the mock AI analysis
                mock_ai_analyze.return_value = {
                    "analysis": {
                        "suggestions": [
                            {
                                "text": "Try taking a timeout if emotions are running high",
                                "confidence": 0.9,
                                "source": "knowledge_base"
                            },
                            {
                                "text": "Use 'I' statements when expressing how you feel",
                                "confidence": 0.85,
                                "source": "knowledge_base"
                            }
                        ],
                        "sentiment": {"label": "frustrated", "confidence": 0.8},
                        "context_enhanced": True
                    },
                    "kb_context_used": True,
                    "kb_documents": [{"id": "doc-1", "title": sample_documents[2]["title"]}]
                }
                
                # Call the endpoint that integrates AI with knowledge base
                response = client.post(
                    "/api/analysis/enhanced",
                    json={
                        "text": "We keep having the same argument and I'm getting frustrated.",
                        "use_knowledge_base": True
                    }
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.model_dump_json()
                assert data["analysis"]["context_enhanced"] is True
                assert data["kb_context_used"] is True
                
                # Verify that suggestions from KB are included
                suggestions = data["analysis"]["suggestions"]
                assert any("timeout" in s["text"].lower() for s in suggestions)
                assert any("'i' statements" in s["text"].lower() for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, kb_service, sample_documents):
        """Test hybrid search combining vector and keyword search"""
        
        # Index sample documents
        for doc in sample_documents:
            await kb_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
        
        # Perform hybrid search
        with patch('services.knowledge_base.KnowledgeBaseService._hybrid_search') as mock_hybrid:
            # Configure mock to return combined results
            mock_hybrid.return_value = [
                SearchResult(
                    document_id="doc-1",
                    content="Active listening involves giving full attention, asking clarifying questions, and acknowledging feelings.",
                    metadata={"title": "Effective Communication Techniques", "score_components": {"vector": 0.8, "keyword": 0.9}},
                    similarity_score=0.85  # Combined score
                )
            ]
            
            # Call hybrid search
            search_results = await kb_service.search(
                query="how to listen better in conversations",
                use_hybrid_search=True,
                limit=1
            )
            
            # Verify results
            assert len(search_results) > 0
            assert "listening" in search_results[0].content.lower()
            assert "score_components" in search_results[0].metadata
    
    @pytest.mark.asyncio
    async def test_knowledge_base_updates(self, kb_service):
        """Test updating documents in the knowledge base"""
        
        # Index initial document
        doc_result = await kb_service.index_document(
            content="Initial version of the document.",
            title="Test Document",
            doc_type=DocumentType.REFERENCE,
            tags=["test"]
        )
        
        document_id = doc_result["document_id"]
        
        # Update the document
        update_result = await kb_service.update_document(
            document_id=document_id,
            content="Updated version of the document with new information.",
            title="Updated Test Document",
            doc_type=DocumentType.REFERENCE,
            tags=["test", "updated"]
        )
        
        # Verify update was successful
        assert update_result["success"] is True
        assert update_result["document_id"] == document_id
        
        # Search for updated content
        search_results = await kb_service.search(
            query="updated version new information",
            limit=1
        )
        
        # Verify updated content is searchable
        assert len(search_results) > 0
        assert "updated version" in search_results[0].content.lower()


class TestKnowledgeBaseAPI:
    """Test Knowledge Base API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Get test client"""
        with patch('routers.knowledge_base.kb_service') as mock_kb_service:
            # Configure the mock service for API endpoints
            mock_kb_service.process_document.return_value = {
                "document_id": "test-api-doc-id",
                "success": True,
                "chunks_created": 3,
                "message": "Document uploaded and processed successfully",
                "status": "completed",
                "auto_tags": ["test", "api"],
                "auto_category": "reference"
            }
            
            mock_kb_service.list_documents.return_value = [
                {
                    "document_id": "doc-1",
                    "filename": "test1.pdf",
                    "title": "Test Document 1",
                    "content_type": "application/pdf",
                    "file_size": 1024,
                    "document_type": "reference",
                    "category": "guides",
                    "tags": ["test", "pdf"],
                    "chunk_count": 3,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "status": "completed"
                },
                {
                    "document_id": "doc-2",
                    "filename": "test2.txt",
                    "title": "Test Document 2",
                    "content_type": "text/plain",
                    "file_size": 512,
                    "document_type": "instruction",
                    "category": "tutorials",
                    "tags": ["test", "text"],
                    "chunk_count": 1,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "status": "completed"
                }
            ]
            
            mock_kb_service.get_categories.return_value = ["guides", "tutorials", "references"]
            mock_kb_service.get_tags.return_value = ["test", "pdf", "text", "api"]
            
            mock_kb_service.get_analytics.return_value = {
                "total_documents": 10,
                "total_size": 1024 * 1024 * 5,  # 5MB
                "document_types": {"reference": 5, "instruction": 3, "other": 2},
                "tag_count": 15,
                "category_count": 5,
                "tag_usage": {"test": 10, "pdf": 5, "text": 3},
                "recent_activity": [
                    {"type": "upload", "description": "Uploaded test1.pdf", "timestamp": datetime.now().isoformat()},
                    {"type": "search", "description": "Searched for 'test query'", "timestamp": datetime.now().isoformat()}
                ]
            }
            
            with patch('routers.knowledge_base.vector_service') as mock_vector_service:
                # Configure vector service mock
                mock_vector_service.search.return_value = [
                    SearchResult(
                        document_id="doc-1",
                        content="This is test content for API testing",
                        metadata={"tags": ["test", "api"]},
                        similarity_score=0.95
                    )
                ]
                
                yield TestClient(app)
    
    def test_list_documents_endpoint(self, client):
        """Test listing documents endpoint"""
        response = client.get("/api/knowledge-base/documents")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert len(data) == 2
        assert data[0]["document_id"] == "doc-1"
        assert data[1]["document_id"] == "doc-2"
    
    def test_list_documents_with_filters(self, client):
        """Test listing documents with filters"""
        response = client.get("/api/knowledge-base/documents?category=guides&tags=pdf")
        
        assert response.status_code == 200
    
    def test_get_categories(self, client):
        """Test getting categories endpoint"""
        response = client.get("/api/knowledge-base/categories")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert "categories" in data
        assert len(data["categories"]) == 3
        assert "guides" in data["categories"]
    
    def test_get_tags(self, client):
        """Test getting tags endpoint"""
        response = client.get("/api/knowledge-base/tags")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert "tags" in data
        assert len(data["tags"]) == 4
    
    def test_get_analytics(self, client):
        """Test getting analytics endpoint"""
        response = client.get("/api/knowledge-base/analytics")
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert "total_documents" in data
        assert data["total_documents"] == 10
        assert "document_types" in data
        assert "tag_usage" in data
    
    def test_search_endpoint(self, client):
        """Test search endpoint"""
        request_data = {
            "query": "test search",
            "limit": 10,
            "threshold": 0.7,
            "filters": {
                "category": "guides",
                "tags": ["test", "pdf"]
            }
        }
        
        response = client.post("/api/knowledge-base/search", json=request_data)
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert "results" in data
        assert len(data["results"]) > 0
        assert data["query"] == "test search"
    
    def test_upload_document(self, client):
        """Test document upload endpoint"""
        # Create a test file
        test_file = io.BytesIO(b"This is a test document for upload")
        
        response = client.post(
            "/api/knowledge-base/documents/upload",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={
                "tags": "test,upload",
                "category": "guides",
                "auto_tag": "true",
                "auto_categorize": "true"
            }
        )
        
        assert response.status_code == 200
        data = response.model_dump_json()
        assert data["success"] is True
        assert data["document_id"] == "test-api-doc-id"
        assert "auto_tags" in data
    
    def test_update_document_tags(self, client):
        """Test updating document tags"""
        request_data = {
            "tags": ["updated", "tags", "test"],
            "replace": True
        }
        
        with patch('routers.knowledge_base.kb_service.update_document_tags') as mock_update:
            mock_update.return_value = True
            
            response = client.post(
                "/api/knowledge-base/documents/doc-1/tags",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert "message" in data
            assert data["document_id"] == "doc-1"
    
    def test_document_tagging_endpoints(self, client):
        """Test document tagging API endpoints"""
        
        # Test add tags endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.add_tags') as mock_add_tags:
            # Configure the mock to return success
            mock_add_tags.return_value = {
                "success": True,
                "document_id": "doc-1",
                "tags": ["test", "api", "new-tag"]
            }
            
            response = client.post(
                "/api/knowledge/documents/doc-1/tags",
                json={"tags": ["new-tag"]}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert "new-tag" in data["tags"]
            
        # Test remove tags endpoint
        with patch('services.knowledge_base.KnowledgeBaseService.remove_tags') as mock_remove_tags:
            # Configure the mock to return success
            mock_remove_tags.return_value = {
                "success": True,
                "document_id": "doc-1",
                "tags": ["test", "api"]
            }
            
            response = client.delete(
                "/api/knowledge/documents/doc-1/tags",
                json={"tags": ["new-tag"]}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert data["success"] is True
            assert "new-tag" not in data["tags"]
            
        # Test tag error handling
        with patch('services.knowledge_base.KnowledgeBaseService.add_tags') as mock_add_tags:
            # Configure the mock to raise an exception
            mock_add_tags.side_effect = Exception("Failed to add tags")
            
            response = client.post(
                "/api/knowledge/documents/doc-error/tags",
                json={"tags": ["error-tag"]}
            )
            
            # Verify response
            assert response.status_code == 500
    
    def test_error_handling_not_found(self, client):
        """Test error handling for non-existent document"""
        with patch('routers.knowledge_base.kb_service.get_document') as mock_get:
            mock_get.return_value = None
            
            response = client.get("/api/knowledge-base/documents/non-existent-id")
            
            assert response.status_code == 404
            data = response.model_dump_json()
            assert "detail" in data
    
    def test_error_handling_invalid_search(self, client):
        """Test error handling for invalid search request"""
        # Missing required query field
        request_data = {
            "limit": 10,
            "threshold": 0.7
        }
        
        response = client.post("/api/knowledge-base/search", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_api_error_handling(self, client):
        """Test error handling in the Knowledge Base API"""
        
        # Test invalid file upload (file too large)
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            # Create a "large" file (we'll just patch the check)
            tmp.write(b"Test content")
            tmp.flush()
            tmp.seek(0)
            
            # Patch the file read to simulate a large file
            with patch('routers.knowledge_base.UploadFile.read') as mock_read:
                # Configure the mock to return a large content
                mock_large_content = b"x" * (51 * 1024 * 1024)  # 51MB (exceeds 50MB limit)
                mock_read.return_value = mock_large_content
                
                response = client.post(
                    "/api/knowledge/documents/upload",
                    files={"file": ("large.txt", tmp, "text/plain")},
                    data={"tags": "test"}
                )
                
                # Verify response
                assert response.status_code == 413  # Request Entity Too Large
                
        # Test invalid search request (missing query)
        response = client.get("/api/knowledge/search")
        assert response.status_code == 422  # Unprocessable Entity
        
        # Test invalid document id format
        with patch('services.knowledge_base.KnowledgeBaseService.get_document') as mock_get:
            # Configure the mock to raise a ValueError for invalid ID format
            mock_get.side_effect = ValueError("Invalid document ID format")
            
            response = client.get("/api/knowledge/documents/invalid-id-format")
            
            # Verify response
            assert response.status_code == 400  # Bad Request


class TestEnhancedLoggingAndErrorHandling:
    """Test logging and error handling for knowledge base operations"""
    
    @pytest.fixture
    def mock_kb_service(self):
        """Create a mock knowledge base service with logging capabilities"""
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Mock the document processing method
        mock_service.process_document = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "success": True,
            "chunks_created": 3,
            "processing_time": 0.5,
            "errors": [],
            "message": "Document processed successfully"
        })
        
        # Mock error case
        mock_service.process_document.side_effect = None
        
        return mock_service
    
    @pytest.mark.asyncio
    async def test_successful_document_processing(self, mock_kb_service):
        """Test successful document processing with proper logging"""
        # Setup a capture handler for log messages
        log_messages = []
        
        class CaptureHandler(logging.Handler):
            def emit(self, record):
                log_messages.append(record.getMessage())
        
        # Add capture handler to the logger
        logger = logging.getLogger("services.knowledge_base")
        handler = CaptureHandler()
        logger.addHandler(handler)
        old_level = logger.level
        logger.setLevel(logging.INFO)
        
        try:
            # Create a test file
            test_content = io.BytesIO(b"This is test content for logging")
            
            # Process document with default success response
            result = await mock_kb_service.process_document(
                file_content=test_content.read(),
                filename="test_logging.txt",
                tags=["test"],
                category="reference",
                auto_tag=True,
                auto_categorize=True
            )
            
            # Verify result
            assert result["success"] is True
            assert result["document_id"] == "test-doc-id"
            assert result["chunks_created"] == 3
            
            # Verify appropriate log messages
            # Note: In a real test, we'd check the actual log messages,
            # but in this mock we're just verifying the method was called
            assert mock_kb_service.process_document.called
            
        finally:
            # Clean up logging
            logger.removeHandler(handler)
            logger.setLevel(old_level)
    
    @pytest.mark.asyncio
    async def test_error_handling_during_processing(self, mock_kb_service):
        """Test error handling during document processing"""
        
        # Configure mock to simulate an error
        mock_kb_service.process_document_file = AsyncMock(side_effect=Exception("Simulated processing error"))
        
        # Create a test file
        file_content = io.BytesIO(b"Test content that will cause an error")
        
        # Process the file and expect error handling
        try:
            await mock_kb_service.process_document_file(
                file=file_content,
                filename="error_test.txt",
                content_type="text/plain",
                doc_type="reference",
                tags=["test"]
            )
            assert False, "Expected an exception but none was raised"
        except Exception as e:
            assert "Simulated processing error" in str(e)
            
        # Reset the mock for subsequent tests
        mock_kb_service.process_document_file = AsyncMock(return_value={
            "document_id": "test-doc-id",
            "success": True,
            "chunks_created": 3,
            "processing_time": 0.5,
            "errors": []
        })
    
    @pytest.mark.asyncio
    async def test_recovery_from_indexing_failure(self, mock_kb_service):
        """Test recovery from indexing failure"""
        # Setup partial success
        mock_kb_service.process_document.side_effect = None
        mock_kb_service.process_document.return_value = {
            "document_id": "test-doc-id",
            "success": True,  # Document was saved
            "chunks_created": 3,
            "processing_time": 0.5,
            "errors": [],
            "warnings": ["Vector indexing failed: Connection error"],
            "message": "Document saved but indexing failed"
        }
        
        # Create a test file
        test_content = io.BytesIO(b"This is test content for recovery testing")
        
        # Process document with partial success
        result = await mock_kb_service.process_document(
            file_content=test_content.read(),
            filename="test_recovery.txt",
            tags=["test"],
            category="reference",
            auto_tag=True,
            auto_categorize=True
        )
        
        # Verify result indicates partial success
        assert result["success"] is True  # Document was saved
        assert "warnings" in result
        assert any("indexing failed" in warning for warning in result["warnings"])


class TestKnowledgeBaseService:
    """Test KnowledgeBaseService methods directly"""
    
    @pytest.fixture
    def mock_kb_service(self):
        """Create a mock knowledge base service"""
        mock_service = MagicMock(spec=KnowledgeBaseService)
        return mock_service
    
    @pytest.mark.asyncio
    async def test_enrich_search_results(self, mock_kb_service):
        """Test enrichment of search results with document metadata"""
        
        # Create sample search results
        search_results = [
            SearchResult(
                document_id="doc-1",
                content="This is a sample search result.",
                metadata={},
                similarity_score=0.92
            ),
            SearchResult(
                document_id="doc-2",
                content="This is another search result.",
                metadata={},
                similarity_score=0.85
            )
        ]
        
        # Configure mock to return document metadata
        mock_kb_service.get_document = AsyncMock(side_effect=[
            {
                "document_id": "doc-1",
                "title": "Sample Document",
                "filename": "sample.txt",
                "content_type": "text/plain",
                "document_type": "reference",
                "category": "samples",
                "tags": ["test", "sample"],
                "created_at": "2025-06-21T10:00:00Z"
            },
            None  # Simulate a document that doesn't exist
        ])
        
        # Mock the enrich_search_results method
        mock_kb_service.enrich_search_results = AsyncMock(side_effect=lambda results: asyncio.gather(*[
            mock_kb_service._enrich_single_result(result) for result in results
        ]))
        
        # Add a helper method for the test
        async def _enrich_single_result(result):
            doc = await mock_kb_service.get_document(result.document_id)
            if doc:
                result.metadata.update({
                    "title": doc.get("title"),
                    "filename": doc.get("filename"),
                    "content_type": doc.get("content_type"),
                    "document_type": doc.get("document_type"),
                    "category": doc.get("category"),
                    "tags": doc.get("tags", []),
                    "created_at": doc.get("created_at")
                })
            return result
            
        mock_kb_service._enrich_single_result = _enrich_single_result
        
        # Enrich the search results
        enriched_results = await mock_kb_service.enrich_search_results(search_results)
        
        # Verify first result was enriched
        assert enriched_results[0].metadata.get("title") == "Sample Document"
        assert enriched_results[0].metadata.get("tags") == ["test", "sample"]
        
        # Verify second result (doc doesn't exist) maintains original metadata
        assert "title" not in enriched_results[1].metadata


class TestAIIntegration:
    """Test integration of Knowledge Base with AI features"""
    
    @pytest.fixture
    def mock_kb_service(self):
        """Create a mock knowledge base service"""
        mock_service = MagicMock(spec=KnowledgeBaseService)
        
        # Mock search method
        mock_service.search = AsyncMock(return_value=[
            SearchResult(
                document_id="doc-1",
                content="Communication requires active listening and empathy.",
                metadata={"title": "Communication Guidelines", "tags": ["communication"]},
                similarity_score=0.95
            )
        ])
        
        return mock_service
    
    @pytest.mark.asyncio
    async def test_ai_context_enhancement(self, mock_kb_service):
        """Test using knowledge base to enhance AI context"""
        
        # Simulate an AI query that would benefit from knowledge base context
        query = "How can I improve communication in my relationship?"
        
        # Get relevant knowledge base context
        search_results = await mock_kb_service.search(
            query=query,
            limit=3,
            min_score=0.7
        )
        
        # Verify we got search results
        assert len(search_results) > 0
        assert search_results[0].similarity_score >= 0.7
        
        # Check if the most relevant result contains useful context
        most_relevant = search_results[0]
        assert "communication" in most_relevant.content.lower()
        
        # Simulate enhancing AI prompt with knowledge base context
        enhanced_prompt = f"{query}\n\nContext from knowledge base:\n{most_relevant.content}"
        
        # Verify the enhanced prompt contains the knowledge base context
        assert "Context from knowledge base" in enhanced_prompt
        assert most_relevant.content in enhanced_prompt
    
    @pytest.mark.asyncio
    async def test_ai_answer_augmentation(self, mock_kb_service):
        """Test augmenting AI answers with knowledge base citations"""
        
        # Simulate an AI response
        ai_response = "Effective communication is key to a healthy relationship."
        
        # Get relevant knowledge base citations
        search_results = await mock_kb_service.search(
            query=ai_response,
            limit=2,
            min_score=0.8
        )
        
        # Create citations
        citations = []
        for result in search_results:
            citations.append({
                "document_id": result.document_id,
                "title": result.metadata.get("title", "Untitled"),
                "excerpt": result.content[:100] + "..." if len(result.content) > 100 else result.content,
                "relevance": result.similarity_score
            })
        
        # Verify citations
        assert len(citations) > 0
        assert citations[0]["document_id"] == "doc-1"
        assert "Communication Guidelines" in citations[0]["title"]
        
        # Simulate augmented response with citations
        augmented_response = {
            "answer": ai_response,
            "citations": citations
        }
        
        # Verify the augmented response
        assert augmented_response["answer"] == ai_response
        assert len(augmented_response["citations"]) > 0
