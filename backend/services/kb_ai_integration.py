"""
Knowledge Base AI Integration Service
Combines the Knowledge Base and AI capabilities for enhanced functionality
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Union

from services.knowledge_base import KnowledgeBaseService, SearchFilters
from services.ai_service_kb import AIService
from services.ai_service import AIProvider, AnalysisType
from config import get_logger

logger = get_logger(__name__)

class KnowledgeBaseAIIntegration:
    """Service that integrates Knowledge Base and AI functionalities"""
    
    def __init__(
        self,
        kb_service: Optional[KnowledgeBaseService] = None,
        ai_service: Optional[AIService] = None
    ):
        """Initialize the integration service with KB and AI services"""
        self.kb_service = kb_service or KnowledgeBaseService()
        self.ai_service = ai_service or AIService()
        logger.info("Initialized Knowledge Base AI Integration service")
    
    async def semantic_search_with_ai_enrichment(
        self, 
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        enrich_with: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search and enrich results with AI analysis
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters for the search
            enrich_with: List of AI enrichment types to apply (e.g., 'summary', 'sentiment')
            
        Returns:
            List of search results with AI enrichments
        """
        # Default enrichment types if not specified
        enrich_with = enrich_with or ["summary"]
        
        # Convert dict filters to SearchFilters object if provided
        search_filters = None
        if filters:
            search_filters = SearchFilters()
            if 'tags' in filters:
                search_filters.tags = filters.get('tags')
            if 'document_types' in filters:
                search_filters.document_types = filters.get('document_types')
            if 'file_types' in filters:
                search_filters.file_types = filters.get('file_types')
        
        # Perform the knowledge base search
        search_results = await self.kb_service.search_knowledge_base(
            query=query,
            limit=limit,
            filters=search_filters
        )
        
        # Early return if no results
        if not search_results:
            return []
        
        # Enrich results with AI analysis
        enriched_results = []
        for result in search_results:
            # Convert SearchResult to dict
            if hasattr(result, '__dict__'):
                # Convert the object to a dictionary
                enriched_result = {k: v for k, v in result.__dict__.items()}
            else:
                # If it's already a dict-like object
                enriched_result = dict()
                for key in dir(result):
                    if not key.startswith('_') and not callable(getattr(result, key)):
                        enriched_result[key] = getattr(result, key)
            
            # Get content for AI processing
            content = enriched_result.get('content', '')
            if not content and hasattr(result, 'content'):
                content = result.content
                
            if not content:
                enriched_results.append(enriched_result)
                continue
            
            # Apply requested enrichments
            if "summary" in enrich_with:
                try:
                    summary = await self.ai_service.generate_summary(content)
                    enriched_result["ai_summary"] = summary
                except Exception as e:
                    logger.error(f"Error generating summary: {str(e)}")
                    enriched_result["ai_summary"] = "Summary unavailable"
            
            if "sentiment" in enrich_with:
                try:
                    sentiment = await self.ai_service.analyze_text(
                        content, 
                        analysis_type=AnalysisType.SENTIMENT
                    )
                    enriched_result["ai_sentiment"] = sentiment
                except Exception as e:
                    logger.error(f"Error analyzing sentiment: {str(e)}")
                    enriched_result["ai_sentiment"] = {"status": "error", "message": str(e)}
            
            enriched_results.append(enriched_result)
        
        return enriched_results
    
    async def answer_with_knowledge_context(
        self,
        query: str,
        use_kb_results: int = 3,
        kb_filters: Optional[Dict[str, Any]] = None,
        ai_provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI response using Knowledge Base content as context
        
        Args:
            query: User question or query
            use_kb_results: Number of KB results to include as context
            kb_filters: Optional filters for the KB search
            ai_provider: Optional specific AI provider to use
            
        Returns:
            Dictionary with the AI response and metadata
        """
        # Convert dict filters to SearchFilters object if provided
        search_filters = None
        if kb_filters:
            search_filters = SearchFilters()
            if 'tags' in kb_filters:
                search_filters.tags = kb_filters.get('tags')
            if 'document_types' in kb_filters:
                search_filters.document_types = kb_filters.get('document_types')
            if 'file_types' in kb_filters:
                search_filters.file_types = kb_filters.get('file_types')
        
        # Search knowledge base for relevant content
        kb_results = await self.kb_service.search_knowledge_base(
            query=query,
            limit=use_kb_results,
            filters=search_filters
        )
        
        # Extract content from results to use as context
        kb_context = ""
        kb_sources = []
        
        for result in kb_results:
            # Access content from the SearchResult
            if hasattr(result, 'content'):
                content = result.content
            elif hasattr(result, '__dict__'):
                content = result.__dict__.get('content', '')
            else:
                content = ""
                
            if content:
                kb_context += f"{content}\n\n"
                
                # Track source for citation
                source = {
                    "id": getattr(result, 'id', 'unknown'),
                    "title": getattr(result, 'title', 'Unknown Document'),
                    "score": getattr(result, 'score', 0.0)
                }
                kb_sources.append(source)
        
        # Generate AI response with the KB context
        response_text = await self.ai_service.generate_response(
            query=query,
            context=kb_context,
            provider=ai_provider
        )
        
        # Return the response with metadata
        return {
            "response": response_text,
            "sources": kb_sources,
            "has_kb_context": bool(kb_context),
            "kb_results_count": len(kb_results)
        }
    
    async def auto_tag_document(
        self,
        document_id: str,
        content: Optional[str] = None
    ) -> List[str]:
        """
        Use AI to automatically generate tags for a document
        
        Args:
            document_id: ID of the document to tag
            content: Optional document content (will be fetched if not provided)
            
        Returns:
            List of generated tags
        """
        # Get document content if not provided
        if not content:
            doc = await self.kb_service.get_document(document_id)
            if doc:
                # KnowledgeDocument class - access content attribute
                content = doc.content if hasattr(doc, 'content') else ""
            else:
                logger.warning(f"Document {document_id} not found")
                return []
            
        if not content:
            logger.warning(f"No content available for document {document_id}")
            return []
        
        # Use AI to generate tags
        try:
            tags_response = await self.ai_service.generate_tags(content)
            
            # Process the response into a list of tags
            if isinstance(tags_response, list):
                tags = tags_response
            else:
                # Should not happen with our implementation
                logger.warning(f"Unexpected tag format from AI: {tags_response}")
                tags = []
            
            # Update the document with these tags
            if tags:
                # Note: update_document expects separate parameters, not a dict
                await self.kb_service.update_document(
                    document_id=document_id,
                    tags=tags
                )
            
            return tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return []
