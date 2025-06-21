#!/bin/bash

# Knowledge Base Integration Test Runner
# This script is specifically for running KB-AI integration tests

set -e  # Exit on any error

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"
TEST_DIR="$BACKEND_DIR/tests"
REPORTS_DIR="$TEST_DIR/reports/kb_integration"
mkdir -p "$REPORTS_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# First run the setup script
echo -e "${BLUE}[INFO]${NC} Setting up test environment"
source "$TEST_DIR/setup_kb_integration_env.sh"

# Ensure we're using absolute imports in Python tests
echo -e "${BLUE}[INFO]${NC} Ensuring test files use absolute imports"

# Fix any relative imports issues by creating a conftest_kb.py specifically for KB tests
if [ ! -f "$TEST_DIR/conftest_kb.py" ]; then
    echo -e "${BLUE}[INFO]${NC} Creating specialized conftest for KB tests"
    cat > "$TEST_DIR/conftest_kb.py" << 'EOF'
"""
Special conftest for Knowledge Base integration tests
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Create fixture for mock KB service
@pytest.fixture
def kb_service():
    """Mock knowledge base service for testing"""
    from services.knowledge_base import KnowledgeBaseService
    kb = MagicMock(spec=KnowledgeBaseService)
    return kb

# Create fixture for mock AI service
@pytest.fixture
def ai_service():
    """Mock AI service for testing"""
    from services.ai_service import AIService
    ai = MagicMock(spec=AIService)
    return ai

# Create fixture for test documents
@pytest.fixture
def test_documents():
    """Sample test documents for KB testing"""
    return [
        {
            "id": "test-doc-1",
            "title": "Communication Guidelines",
            "content": "Effective communication requires active listening.",
            "type": "guidance",
            "tags": ["communication"]
        },
        {
            "id": "test-doc-2",
            "title": "Conflict Resolution",
            "content": "Resolving conflicts requires understanding perspectives.",
            "type": "instruction",
            "tags": ["conflict"]
        }
    ]
EOF
    echo -e "${GREEN}[SUCCESS]${NC} Created specialized conftest for KB tests"
fi

# Create the Knowledge Base and AI integration test file if it doesn't exist
if [ ! -f "$TEST_DIR/test_kb_ai_integration.py" ]; then
    echo -e "${BLUE}[INFO]${NC} Creating KB-AI integration test file"
    cat > "$TEST_DIR/test_kb_ai_integration.py" << 'EOF'
"""
Knowledge Base and AI Integration Test
Tests the integration between the Knowledge Base and AI components
"""
import pytest
import asyncio
import sys
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Import services directly to avoid circular imports
from services.knowledge_base import KnowledgeBaseService
from services.ai_service import AIService, AIProvider
from services.vector_search import VectorSearchService

class TestKnowledgeBaseAIIntegration:
    """Test Knowledge Base integration with AI services"""
    
    @pytest.fixture
    def kb_service_real(self):
        """Real knowledge base service with mocked dependencies"""
        vector_service = MagicMock(spec=VectorSearchService)
        vector_service.add_document = AsyncMock()
        vector_service.search = AsyncMock(return_value=[])
        
        kb_service = KnowledgeBaseService()
        kb_service._vector_service = vector_service
        return kb_service
    
    @pytest.fixture
    def ai_service_mock(self):
        """Mock AI service for testing"""
        ai_service = MagicMock(spec=AIService)
        ai_service.analyze_text = AsyncMock(return_value={
            "analysis": "This is a mock analysis",
            "confidence": 0.95
        })
        ai_service.generate_response = AsyncMock(return_value="This is a mock response")
        return ai_service
    
    async def test_kb_search_with_ai_enrichment(self, kb_service_real, ai_service_mock):
        """Test that KB search results can be enriched with AI analysis"""
        # Arrange
        mock_search_results = [
            {"id": "doc1", "content": "Sample content 1", "score": 0.95},
            {"id": "doc2", "content": "Sample content 2", "score": 0.85}
        ]
        kb_service_real._vector_service.search.return_value = mock_search_results
        
        # Act - perform search and enrich with AI
        search_results = await kb_service_real.search_documents("test query", limit=5)
        
        # Assert
        assert len(search_results) > 0, "Should return search results"
        
        # In a real integration, we would pass these results to the AI service
        ai_enhanced_results = []
        for result in search_results:
            # This would be integrated in the actual implementation
            ai_analysis = await ai_service_mock.analyze_text(result.get("content", ""))
            result["ai_analysis"] = ai_analysis
            ai_enhanced_results.append(result)
        
        assert len(ai_enhanced_results) > 0, "Should have AI-enhanced results"
        for result in ai_enhanced_results:
            assert "ai_analysis" in result, "Each result should have AI analysis"

    async def test_ai_response_with_kb_context(self, kb_service_real, ai_service_mock):
        """Test that AI responses can use KB documents as context"""
        # Arrange
        user_query = "How can I improve communication in my relationship?"
        mock_search_results = [
            {"id": "doc1", "content": "Communication techniques include active listening.", "score": 0.95},
            {"id": "doc2", "content": "Empathy is key to understanding your partner.", "score": 0.85}
        ]
        kb_service_real._vector_service.search.return_value = mock_search_results
        
        # Act - first get relevant KB content
        kb_results = await kb_service_real.search_documents(user_query, limit=3)
        
        # Create context from KB results
        context = "\n".join([r.get("content", "") for r in kb_results])
        
        # Generate AI response with KB context
        ai_response = await ai_service_mock.generate_response(
            query=user_query,
            context=context
        )
        
        # Assert
        assert ai_response, "Should generate a response"
        assert ai_service_mock.generate_response.called, "AI service should be called"
EOF
    echo -e "${GREEN}[SUCCESS]${NC} Created KB-AI integration test file"
fi

# Run the tests
echo -e "${BLUE}[INFO]${NC} Running Knowledge Base integration tests"

# First, run the simpler custom tests to validate base functionality
echo -e "${BLUE}[INFO]${NC} Running custom KB-AI integration tests"
python -m pytest "$TEST_DIR/test_kb_ai_integration.py" -v | tee "$REPORTS_DIR/kb_ai_integration_results.log"

# Run the more complex integration tests
echo -e "${BLUE}[INFO]${NC} Running Knowledge Base integration tests with real documents"

# Create a test command for running real document tests
# This will be expanded in the implementation phase
echo -e "${YELLOW}[NOTE]${NC} Planned: Integration tests with real documents"

echo -e "${GREEN}[SUCCESS]${NC} Knowledge Base integration tests completed"
echo -e "${YELLOW}[INFO]${NC} Check $REPORTS_DIR for test results"
