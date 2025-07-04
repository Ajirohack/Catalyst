"""
Knowledge Base API Router

This module provides API endpoints for knowledge base functionality including:
- Document upload and management
- Vector search and semantic search
- Document tagging and categorization
- Knowledge base analytics

"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime
import json
import asyncio
from io import BytesIO

from services.knowledge_base import KnowledgeBaseService
from services.vector_search import VectorSearchService
from schemas.knowledge_base import (
    DocumentMetadata,
    DocumentUploadResponse,
    SearchRequest,
    SearchResponse,
    DocumentSearchFilter,
    TaggingRequest,
    AnalyticsResponse
)
from config.enhanced_config import settings
from config import get_logger

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])
logger = get_logger(__name__)

# Initialize services
kb_service = KnowledgeBaseService()
vector_service = VectorSearchService()

@router.post("/documents/upload", response_model=DocumentUploadResponse, summary="Upload Document")
async def upload_document(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    auto_tag: bool = Form(True),
    auto_categorize: bool = Form(True)
):
    """
    Upload a document to the knowledge base.
    
    - **file**: Document file (PDF, DOCX, TXT, images)
    - **tags**: Comma-separated list of tags
    - **category**: Document category
    - **auto_tag**: Enable automatic tagging
    - **auto_categorize**: Enable automatic categorization
    """
    try:
        logger.info(f"Uploading document: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
        
        # Process tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Process document
        result = await kb_service.process_document(
            file_content=content,
            filename=file.filename,
            tags=tag_list,
            category=category,
            auto_tag=auto_tag,
            auto_categorize=auto_categorize
        )
        
        logger.info(f"Successfully processed document: {result['document_id']}")
        return DocumentUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.get("/documents", response_model=List[DocumentMetadata], summary="List Documents")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search_query: Optional[str] = Query(None)
):
    """
    List documents in the knowledge base with optional filtering.
    
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    - **category**: Filter by category
    - **tags**: Filter by tags (comma-separated)
    - **search_query**: Text search in document titles/content
    """
    try:
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        filter_params = DocumentSearchFilter(
            category=category,
            tags=tag_list,
            search_query=search_query
        )
        
        documents = await kb_service.list_documents(
            skip=skip,
            limit=limit,
            filters=filter_params
        )
        
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/documents/{document_id}", response_model=DocumentMetadata, summary="Get Document")
async def get_document(document_id: str):
    """
    Get detailed information about a specific document.
    """
    try:
        document = await kb_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.delete("/documents/{document_id}", summary="Delete Document")
async def delete_document(document_id: str):
    """
    Delete a document from the knowledge base.
    """
    try:
        success = await kb_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.post("/search", response_model=SearchResponse, summary="Semantic Search")
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search across the knowledge base.
    
    - **query**: Search query text
    - **limit**: Maximum number of results
    - **threshold**: Similarity threshold (0.0-1.0)
    - **filters**: Optional filters for category, tags, etc.
    """
    try:
        logger.info(f"Performing semantic search: {request.query}")
        
        results = await vector_service.search(
            query=request.query,
            limit=request.limit,
            threshold=request.threshold,
            filters=request.filters
        )
        
        # Enrich results with document metadata
        enriched_results = await kb_service.enrich_search_results(results)
        
        return SearchResponse(
            query=request.query,
            results=enriched_results,
            total_results=len(enriched_results)
        )
        
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/documents/{document_id}/tags", summary="Update Document Tags")
async def update_document_tags(document_id: str, request: TaggingRequest):
    """
    Update tags for a specific document.
    """
    try:
        success = await kb_service.update_document_tags(
            document_id=document_id,
            tags=request.tags,
            replace=request.replace
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Tags updated successfully", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tags for document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update tags: {str(e)}")

@router.get("/categories", summary="List Categories")
async def list_categories():
    """
    Get all available document categories.
    """
    try:
        categories = await kb_service.get_categories()
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error listing categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list categories: {str(e)}")

@router.get("/tags", summary="List Tags")
async def list_tags():
    """
    Get all available document tags.
    """
    try:
        tags = await kb_service.get_tags()
        return {"tags": tags}
        
    except Exception as e:
        logger.error(f"Error listing tags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list tags: {str(e)}")

@router.get("/analytics", response_model=AnalyticsResponse, summary="Knowledge Base Analytics")
async def get_analytics():
    """
    Get analytics and statistics about the knowledge base.
    """
    try:
        analytics = await kb_service.get_analytics()
        return AnalyticsResponse(**analytics)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/documents/{document_id}/download", summary="Download Document")
async def download_document(document_id: str):
    """
    Download the original document file.
    """
    try:
        file_path, filename, content_type = await kb_service.get_document_file(document_id)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")

@router.post("/reindex", summary="Reindex Knowledge Base")
async def reindex_knowledge_base():
    """
    Reindex all documents in the knowledge base.
    This is useful after changing embedding models or vector store configurations.
    """
    try:
        logger.info("Starting knowledge base reindexing")
        
        # This is a background task that might take a while
        task_id = str(uuid.uuid4())
        
        # Start reindexing in background
        asyncio.create_task(kb_service.reindex_all_documents(task_id))
        
        return {
            "message": "Reindexing started",
            "task_id": task_id,
            "status": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Error starting reindexing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start reindexing: {str(e)}")

@router.get("/status", summary="Knowledge Base Status")
async def get_status():
    """
    Get the current status of the knowledge base system.
    """
    try:
        status = await kb_service.get_system_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
