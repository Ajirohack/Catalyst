"""File Upload API Endpoints for Catalyst Backend
Provides REST API endpoints for file upload, management, and retrieval
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from ..services.file_storage_service import get_file_storage_service
# Import the class directly to avoid issues
from ..services.file_storage_service import FileStorageService
from ..database.enhanced_models import FileMetadata, FileType, ProcessingStatus

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/files", tags=["files"])

# Request/Response Models
class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    message: str

class FileListResponse(BaseModel):
    """Response model for file listing"""
    files: List[FileMetadata]
    total_count: int
    page: int
    page_size: int

class FileSearchRequest(BaseModel):
    """Request model for file search"""
    query: Optional[str] = None
    file_type: Optional[FileType] = None
    project_id: Optional[str] = None
    conversation_id: Optional[str] = None
    uploaded_after: Optional[datetime] = None
    uploaded_before: Optional[datetime] = None
    status: Optional[ProcessingStatus] = None

class FileProcessingStatus(BaseModel):
    """File processing status response"""
    file_id: str
    status: ProcessingStatus
    processing_progress: float = 0.0
    processing_message: str = ""
    extracted_text_preview: Optional[str] = None
    metadata_summary: Dict[str, Any] = Field(default_factory=dict)

# Dependency to get current user (placeholder)
async def get_current_user() -> str:
    """Get current user ID (placeholder for actual authentication)"""
    # This would be replaced with actual JWT token validation
    return "user_123"

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Upload a file to the system
    
    Args:
        file: The file to upload
        project_id: Optional project ID to associate with the file
        conversation_id: Optional conversation ID to associate with the file
        description: Optional file description
        tags: Optional comma-separated tags
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        FileUploadResponse with upload details
    """
    try:
        logger.info(f"File upload started by user {current_user}: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Upload file
        metadata = await file_service.upload_file(
            file=file,
            uploaded_by=current_user,
            project_id=project_id,
            conversation_id=conversation_id
        )
        
        # Add additional metadata if provided
        if description:
            metadata.extracted_metadata["description"] = description
        
        if tags:
            metadata.extracted_metadata["tags"] = [tag.strip() for tag in tags.split(",")]
        
        # Save metadata to database via file service
        await file_service.save_file_metadata(metadata)
        
        logger.info(f"File upload completed: {metadata.id}")
        
        return FileUploadResponse(
            success=True,
            file_id=metadata.id,
            filename=metadata.original_filename,
            file_type=metadata.file_type.value,
            size_bytes=metadata.size_bytes,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.post("/upload-multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    project_id: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Upload multiple files to the system
    
    Args:
        files: List of files to upload
        project_id: Optional project ID to associate with the files
        conversation_id: Optional conversation ID to associate with the files
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        List of FileUploadResponse objects
    """
    try:
        logger.info(f"Multiple file upload started by user {current_user}: {len(files)} files")
        
        results = []
        
        for file in files:
            try:
                metadata = await file_service.upload_file(
                    file=file,
                    uploaded_by=current_user,
                    project_id=project_id,
                    conversation_id=conversation_id
                )
                
                results.append(FileUploadResponse(
                    success=True,
                    file_id=metadata.id,
                    filename=metadata.original_filename,
                    file_type=metadata.file_type.value,
                    size_bytes=metadata.size_bytes,
                    message="File uploaded successfully"
                ))
                
            except Exception as e:
                logger.error(f"Failed to upload {file.filename}: {e}")
                results.append(FileUploadResponse(
                    success=False,
                    file_id="",
                    filename=file.filename or "unknown",
                    file_type="unknown",
                    size_bytes=0,
                    message=f"Upload failed: {str(e)}"
                ))
        
        logger.info(f"Multiple file upload completed: {len([r for r in results if r.success])}/{len(files)} successful")
        
        return results
        
    except Exception as e:
        logger.error(f"Multiple file upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multiple file upload failed: {str(e)}")

@router.get("/list", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_type: Optional[FileType] = Query(None),
    project_id: Optional[str] = Query(None),
    status: Optional[ProcessingStatus] = Query(None),
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """List files with pagination and filtering
    
    Args:
        page: Page number (1-based)
        page_size: Number of files per page
        file_type: Optional file type filter
        project_id: Optional project ID filter
        status: Optional status filter
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        FileListResponse with paginated file list
    """
    try:
        # Get paginated files from database via file service
        offset = (page - 1) * page_size
        
        files = await file_service.list_files_for_user(
            user_id=current_user,
            file_type=file_type,
            project_id=project_id,
            status=status,
            limit=page_size,
            offset=offset
        )
        
        # Get total count for pagination
        total_count = await file_service.count_files_for_user(
            user_id=current_user,
            file_type=file_type,
            project_id=project_id,
            status=status
        )
        
        logger.info(f"File list requested by user {current_user}: page {page}, size {page_size}")
        
        return FileListResponse(
            files=files,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"File listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"File listing failed: {str(e)}")

@router.get("/{file_id}", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Get file metadata by ID
    
    Args:
        file_id: File ID to retrieve
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        FileMetadata object
    """
    try:
        metadata = await file_service.get_file_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        if not file_service._check_file_access(metadata, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"File metadata retrieved: {file_id} by user {current_user}")
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File metadata retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"File metadata retrieval failed: {str(e)}")

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Download a file by ID
    
    Args:
        file_id: File ID to download
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        StreamingResponse with file content
    """
    try:
        # Get file metadata first
        metadata = await file_service.get_file_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file content
        content, mime_type = await file_service.get_file_content(file_id, current_user)
        
        logger.info(f"File download: {file_id} by user {current_user}")
        
        # Create streaming response
        response = StreamingResponse(
            iter([content]),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{metadata.original_filename}\"",
                "Content-Length": str(len(content))
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

@router.get("/{file_id}/status", response_model=FileProcessingStatus)
async def get_file_processing_status(
    file_id: str,
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Get file processing status
    
    Args:
        file_id: File ID to check
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        FileProcessingStatus object
    """
    try:
        metadata = await file_service.get_file_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        if not file_service._check_file_access(metadata, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Calculate processing progress
        progress = 0.0
        message = "Pending"
        
        if metadata.processing_status == ProcessingStatus.PROCESSING:
            progress = 50.0
            message = "Processing file..."
        elif metadata.processing_status == ProcessingStatus.COMPLETED:
            progress = 100.0
            message = "Processing completed"
        elif metadata.processing_status in [ProcessingStatus.ERROR, ProcessingStatus.FAILED]:
            progress = 0.0
            message = f"Processing failed: {metadata.processing_error or 'Unknown error'}"
        
        # Get text preview
        text_preview = None
        if metadata.extracted_text:
            text_preview = metadata.extracted_text[:200] + "..." if len(metadata.extracted_text) > 200 else metadata.extracted_text
        
        return FileProcessingStatus(
            file_id=file_id,
            status=metadata.status,
            processing_progress=progress,
            processing_message=message,
            extracted_text_preview=text_preview,
            metadata_summary=metadata.extracted_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"File status check failed: {str(e)}")

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Delete a file
    
    Args:
        file_id: File ID to delete
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        Success message
    """
    try:
        success = await file_service.delete_file(file_id, current_user)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found or deletion failed")
        
        logger.info(f"File deleted: {file_id} by user {current_user}")
        
        return {"success": True, "message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")

@router.post("/search", response_model=FileListResponse)
async def search_files(
    search_request: FileSearchRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Search files based on various criteria
    
    Args:
        search_request: Search criteria
        page: Page number
        page_size: Page size
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        FileListResponse with search results
    """
    try:
        # Implement database search with full-text search capabilities
        offset = (page - 1) * page_size
        
        search_results = await file_service.search_files(
            query=search_request.query,
            file_type=search_request.file_type,
            project_id=search_request.project_id,
            conversation_id=search_request.conversation_id,
            user_id=current_user,
            uploaded_after=search_request.uploaded_after,
            uploaded_before=search_request.uploaded_before,
            status=search_request.status,
            limit=page_size,
            offset=offset
        )
        
        # Get total count for pagination
        total_count = await file_service.count_search_results(
            query=search_request.query,
            file_type=search_request.file_type,
            project_id=search_request.project_id,
            conversation_id=search_request.conversation_id,
            user_id=current_user,
            uploaded_after=search_request.uploaded_after,
            uploaded_before=search_request.uploaded_before,
            status=search_request.status
        )
        
        files = []
        total_count = 0
        
        logger.info(f"File search by user {current_user}: query='{search_request.query}'")
        
        return FileListResponse(
            files=files,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"File search failed: {e}")
        raise HTTPException(status_code=500, detail=f"File search failed: {str(e)}")

@router.get("/{file_id}/thumbnail")
async def get_file_thumbnail(
    file_id: str,
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Get file thumbnail (for images)
    
    Args:
        file_id: File ID
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        StreamingResponse with thumbnail image
    """
    try:
        metadata = await file_service.get_file_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        if not file_service._check_file_access(metadata, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if thumbnail exists
        if not metadata.thumbnail_path:
            raise HTTPException(status_code=404, detail="No thumbnail available")
        
        thumbnail_path = Path(metadata.thumbnail_path)
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail file not found")
        
        # Read thumbnail content
        with open(thumbnail_path, 'rb') as file:
            content = file.read()
        
        return StreamingResponse(
            iter([content]),
            media_type="image/jpeg",
            headers={"Content-Length": str(len(content))}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Thumbnail retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Thumbnail retrieval failed: {str(e)}")

@router.get("/{file_id}/extract-text")
async def extract_text_from_file(
    file_id: str,
    file_service: FileStorageService = Depends(get_file_storage_service),
    current_user: str = Depends(get_current_user)
):
    """Extract text content from a file
    
    Args:
        file_id: File ID
        file_service: File storage service
        current_user: Current user ID
        
    Returns:
        Extracted text content
    """
    try:
        metadata = await file_service.get_file_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        if not file_service._check_file_access(metadata, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not metadata.extracted_text:
            raise HTTPException(status_code=404, detail="No text content available")
        
        return {
            "file_id": file_id,
            "filename": metadata.original_filename,
            "extracted_text": metadata.extracted_text,
            "character_count": len(metadata.extracted_text),
            "word_count": len(metadata.extracted_text.split()),
            "extraction_metadata": metadata.extracted_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for file service"""
    return {
        "status": "healthy",
        "service": "file_upload_api",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
