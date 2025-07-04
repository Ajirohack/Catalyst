"""
Knowledge Base Pydantic Schemas

This module defines the Pydantic models for knowledge base API requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    """Document type enumeration"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"
    OTHER = "other"

class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentMetadata(BaseModel):
    """Document metadata model"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    title: Optional[str] = Field(None, description="Document title")
    content_type: str = Field(..., description="MIME content type")
    file_size: int = Field(..., description="File size in bytes")
    document_type: DocumentType = Field(..., description="Document type")
    category: Optional[str] = Field(None, description="Document category")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    chunk_count: int = Field(0, description="Number of text chunks")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    status: DocumentStatus = Field(..., description="Processing status")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Uploaded filename")
    status: DocumentStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    chunks_created: int = Field(0, description="Number of chunks created")
    auto_tags: List[str] = Field(default_factory=list, description="Automatically generated tags")
    auto_category: Optional[str] = Field(None, description="Automatically assigned category")

class SearchResult(BaseModel):
    """Individual search result"""
    document_id: str = Field(..., description="Document identifier")
    chunk_id: str = Field(..., description="Chunk identifier")
    content: str = Field(..., description="Matching content")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    document_metadata: Optional[DocumentMetadata] = Field(None, description="Full document metadata")

class DocumentSearchFilter(BaseModel):
    """Document search filters"""
    category: Optional[str] = Field(None, description="Filter by category")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    document_type: Optional[DocumentType] = Field(None, description="Filter by document type")
    status: Optional[DocumentStatus] = Field(None, description="Filter by status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    search_query: Optional[str] = Field(None, description="Text search query")

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    filters: Optional[DocumentSearchFilter] = Field(None, description="Search filters")
    include_content: bool = Field(True, description="Include content in results")
    
    @field_validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class SearchResponse(BaseModel):
    """Search response model"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    execution_time: Optional[float] = Field(None, description="Query execution time in seconds")

class TaggingRequest(BaseModel):
    """Request to update document tags"""
    tags: List[str] = Field(..., description="List of tags")
    replace: bool = Field(False, description="Replace existing tags (True) or add to them (False)")
    
    @field_validator('tags')
    def validate_tags(cls, v):
        # Remove empty tags and duplicates
        cleaned_tags = list(set([tag.strip() for tag in v if tag.strip()]))
        return cleaned_tags

class CategoryAnalytics(BaseModel):
    """Analytics for a document category"""
    category: str = Field(..., description="Category name")
    document_count: int = Field(..., description="Number of documents")
    total_size: int = Field(..., description="Total size in bytes")
    avg_chunks: float = Field(..., description="Average chunks per document")

class TagAnalytics(BaseModel):
    """Analytics for a document tag"""
    tag: str = Field(..., description="Tag name")
    document_count: int = Field(..., description="Number of documents with this tag")
    usage_percentage: float = Field(..., description="Percentage of documents with this tag")

class AnalyticsResponse(BaseModel):
    """Knowledge base analytics response"""
    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    total_size: int = Field(..., description="Total storage size in bytes")
    categories: List[CategoryAnalytics] = Field(..., description="Category analytics")
    top_tags: List[TagAnalytics] = Field(..., description="Most used tags")
    document_types: Dict[str, int] = Field(..., description="Document type distribution")
    recent_uploads: int = Field(..., description="Documents uploaded in last 24 hours")
    processing_status: Dict[str, int] = Field(..., description="Documents by processing status")

class ReindexRequest(BaseModel):
    """Request to reindex documents"""
    document_ids: Optional[List[str]] = Field(None, description="Specific documents to reindex (all if None)")
    force: bool = Field(False, description="Force reindexing even if up to date")

class ReindexResponse(BaseModel):
    """Response for reindex operation"""
    task_id: str = Field(..., description="Background task identifier")
    message: str = Field(..., description="Status message")
    documents_to_process: int = Field(..., description="Number of documents to reindex")

class SystemStatus(BaseModel):
    """System status response"""
    vector_store_status: str = Field(..., description="Vector store status")
    embedding_model_status: str = Field(..., description="Embedding model status")
    total_documents: int = Field(..., description="Total documents in system")
    total_chunks: int = Field(..., description="Total chunks indexed")
    storage_usage: Dict[str, Any] = Field(..., description="Storage usage information")
    last_backup: Optional[datetime] = Field(None, description="Last backup timestamp")
    system_health: str = Field(..., description="Overall system health")

class DocumentChunk(BaseModel):
    """Document chunk model"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Index within document")
    start_char: int = Field(..., description="Start character position")
    end_char: int = Field(..., description="End character position")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    embedding_vector: Optional[List[float]] = Field(None, description="Embedding vector")

class BulkUploadRequest(BaseModel):
    """Request for bulk document upload"""
    auto_tag: bool = Field(True, description="Enable automatic tagging")
    auto_categorize: bool = Field(True, description="Enable automatic categorization")
    default_category: Optional[str] = Field(None, description="Default category for all documents")
    default_tags: List[str] = Field(default_factory=list, description="Default tags for all documents")

class BulkUploadResponse(BaseModel):
    """Response for bulk document upload"""
    task_id: str = Field(..., description="Background task identifier")
    total_files: int = Field(..., description="Total number of files to process")
    message: str = Field(..., description="Status message")

class DocumentPreview(BaseModel):
    """Document preview model"""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Document filename")
    preview_text: str = Field(..., description="Preview text content")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    key_phrases: List[str] = Field(default_factory=list, description="Extracted key phrases")
    summary: Optional[str] = Field(None, description="Document summary")

# Utility functions for schema validation
def validate_file_size(size: int, max_size: int = 50 * 1024 * 1024) -> bool:
    """Validate file size against maximum allowed size"""
    return size <= max_size

def validate_file_type(filename: str, allowed_types: List[str] = None) -> bool:
    """Validate file type based on extension"""
    if allowed_types is None:
        allowed_types = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif']
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return f'.{file_ext}' in allowed_types
