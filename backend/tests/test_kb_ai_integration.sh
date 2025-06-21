#!/bin/bash

# Knowledge Base and AI Integration Test Script
# This script tests the integration between KB and AI components

set -e  # Exit on any error

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"
TEST_DIR="$BACKEND_DIR/tests"
DATA_DIR="$BACKEND_DIR/data/test_data"
REPORTS_DIR="$TEST_DIR/reports/kb_ai_test"
mkdir -p "$REPORTS_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}[INFO]${NC} Running Knowledge Base and AI Integration Tests"

# First run the setup script
echo -e "${BLUE}[INFO]${NC} Setting up test environment"
source "$TEST_DIR/setup_kb_integration_env.sh"

# Create test data directory if it doesn't exist
if [ ! -d "$DATA_DIR/kb_ai_test" ]; then
    mkdir -p "$DATA_DIR/kb_ai_test"
fi

# Create sample test documents
if [ ! -f "$DATA_DIR/kb_ai_test/communication_guide.txt" ]; then
    echo "# Effective Communication Guide

Communication is the foundation of any healthy relationship. 
This guide provides techniques for improving communication with your partner.

## Active Listening

Active listening involves fully concentrating on what is being said. Tips:
- Give your full attention
- Avoid interrupting
- Reflect back what you've heard
- Ask clarifying questions

## Expressing Feelings

When expressing feelings, use 'I' statements rather than 'you' statements.
For example, say 'I feel frustrated when plans change at the last minute' 
instead of 'You always change plans at the last minute.'

## Conflict Resolution

Approach conflicts as opportunities for growth rather than battles to be won.
Focus on finding solutions together rather than assigning blame." > "$DATA_DIR/kb_ai_test/communication_guide.txt"
    
    echo -e "${GREEN}[SUCCESS]${NC} Created sample test document: communication_guide.txt"
fi

if [ ! -f "$DATA_DIR/kb_ai_test/relationship_stages.txt" ]; then
    echo "# Stages of Romantic Relationships

Relationships typically evolve through several distinct stages.
Understanding these stages can help couples navigate challenges.

## Honeymoon Phase

The initial stage characterized by intense attraction and idealization.
- Heightened romantic feelings
- Overlooking flaws
- Frequent communication
- Strong desire to spend time together

## Power Struggle

After the honeymoon phase, differences become apparent.
- Conflicts emerge
- Reality replaces idealization
- Communication challenges
- Testing of boundaries

## Stability

Partners accept each other's differences and develop deeper bonds.
- Mutual respect
- Effective communication patterns
- Shared goals
- Balance of togetherness and independence

## Commitment

Long-term dedication to the relationship.
- Deep trust
- Shared vision for the future
- Weathering challenges together
- Continued growth" > "$DATA_DIR/kb_ai_test/relationship_stages.txt"
    
    echo -e "${GREEN}[SUCCESS]${NC} Created sample test document: relationship_stages.txt"
fi

# Create a Python test script for the KB-AI integration
if [ ! -f "$TEST_DIR/test_kb_ai_manual.py" ]; then
    cat > "$TEST_DIR/test_kb_ai_manual.py" << 'EOF'
"""
Manual test script for Knowledge Base and AI Integration
Run this script directly to test the integration
"""
import asyncio
import os
import sys
import json
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from services.kb_ai_integration import KnowledgeBaseAIIntegration
from services.knowledge_base import KnowledgeBaseService, DocumentType
from services.ai_service_kb import AIService

async def run_kb_ai_tests():
    """Run tests for KB-AI integration"""
    # Initialize services
    print("Initializing services...")
    kb_service = KnowledgeBaseService()
    ai_service = AIService()
    kb_ai = KnowledgeBaseAIIntegration(kb_service, ai_service)
    
    # Test data
    test_docs_dir = os.path.join(backend_dir, "data", "test_data", "kb_ai_test")
    
    # Index test documents
    for filename in os.listdir(test_docs_dir):
        if not filename.endswith('.txt'):
            continue
        
        filepath = os.path.join(test_docs_dir, filename)
        print(f"Indexing document: {filename}")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        doc_type = DocumentType.GUIDANCE
        if "stages" in filename:
            doc_type = DocumentType.REFERENCE
        
        # Index the document
        doc_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await kb_service.add_document(
            document_id=doc_id,
            title=filename.replace('.txt', '').replace('_', ' ').title(),
            content=content,
            document_type=doc_type
        )
        print(f"  Document indexed with ID: {doc_id}")
    
    # Test AI-enhanced search
    print("\nTesting AI-enhanced search...")
    query = "How can I improve communication in my relationship?"
    results = await kb_ai.semantic_search_with_ai_enrichment(
        query=query,
        limit=3,
        enrich_with=["summary", "sentiment"]
    )
    
    print(f"Search results for '{query}':")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Score: {result.get('score', 0)}")
        print(f"  AI Summary: {result.get('ai_summary', 'No summary available')}")
        
        sentiment = result.get('ai_sentiment', {})
        if sentiment:
            print(f"  Sentiment: {sentiment.get('sentiment', 'unknown')}")
    
    # Test KB-enhanced AI response
    print("\nTesting KB-enhanced AI response...")
    query = "What are the stages of a relationship?"
    response = await kb_ai.answer_with_knowledge_context(query=query, use_kb_results=2)
    
    print(f"AI response for '{query}':")
    print(response.get("response", "No response"))
    print("\nSources:")
    for source in response.get("sources", []):
        print(f"  - {source.get('title', 'Unknown')}")
    
    print("\nTests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_kb_ai_tests())
EOF
    
    echo -e "${GREEN}[SUCCESS]${NC} Created test script: test_kb_ai_manual.py"
fi

# Run the Python test script
echo -e "${BLUE}[INFO]${NC} Running KB-AI integration test script"
python "$TEST_DIR/test_kb_ai_manual.py" | tee "$REPORTS_DIR/manual_test_results.log"

echo -e "${GREEN}[SUCCESS]${NC} KB-AI integration tests completed"
echo -e "${YELLOW}[INFO]${NC} Check $REPORTS_DIR for test results"
