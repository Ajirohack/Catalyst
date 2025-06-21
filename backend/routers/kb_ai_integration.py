"""
Knowledge Base AI Integration Router
Provides endpoints for KB-AI integration features
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import asyncio

from services.kb_ai_integration import KnowledgeBaseAIIntegration
from services.ai_service import AIProvider
from config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Initialize the integrated service
kb_ai_service = KnowledgeBaseAIIntegration()

@router.get(
    "/search",
    summary="Enhanced Knowledge Base Search", 
    description="Search the knowledge base with AI-powered enrichment"
)
async def enhanced_search(
    query: str, 
    limit: int = Query(5, ge=1, le=20),
    enrich_with: Optional[List[str]] = Query(None, description="AI enrichment types to apply"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    doc_type: Optional[str] = Query(None, description="Filter by document type")
):
    """
    Search the knowledge base with AI-enhanced results
    """
    # Prepare filters
    filters = {}
    if tags:
        filters["tags"] = tags
    if doc_type:
        filters["type"] = doc_type
    
    try:
        results = await kb_ai_service.semantic_search_with_ai_enrichment(
            query=query,
            limit=limit,
            filters=filters,
            enrich_with=enrich_with
        )
        
        return {
            "results": results,
            "count": len(results),
            "query": query,
            "enrichments": enrich_with or []
        }
    except Exception as e:
        logger.error(f"Enhanced search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post(
    "/answer",
    summary="AI Answer with Knowledge Base Context",
    description="Generate an AI response using relevant knowledge base content as context"
)
async def answer_with_kb(
    query: str,
    kb_results: int = Query(3, ge=1, le=10, description="Number of KB results to use as context"),
    provider: Optional[str] = Query(None, description="AI provider to use"),
    tags: Optional[List[str]] = Query(None, description="Filter KB results by tags"),
    doc_type: Optional[str] = Query(None, description="Filter KB results by document type")
):
    """
    Generate an AI response with KB context
    """
    # Prepare filters and provider
    filters = {}
    if tags:
        filters["tags"] = tags
    if doc_type:
        filters["type"] = doc_type
    
    ai_provider = None
    if provider:
        try:
            ai_provider = AIProvider(provider)
        except ValueError:
            logger.warning(f"Invalid provider '{provider}', using default")
    
    try:
        response = await kb_ai_service.answer_with_knowledge_context(
            query=query,
            use_kb_results=kb_results,
            kb_filters=filters,
            ai_provider=ai_provider
        )
        
        return response
    except Exception as e:
        logger.error(f"KB-AI answer error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

@router.post(
    "/documents/{document_id}/auto-tag",
    summary="Auto-Tag Document",
    description="Use AI to automatically generate tags for a document"
)
async def auto_tag_document(document_id: str):
    """
    Generate tags for a document using AI
    """
    try:
        tags = await kb_ai_service.auto_tag_document(document_id)
        
        return {
            "document_id": document_id,
            "tags": tags,
            "count": len(tags)
        }
    except Exception as e:
        logger.error(f"Auto-tagging error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-tag document: {str(e)}")
