"""
File Storage Service for Catalyst Backend
Provides secure file upload, storage, and management capabilities with database integration
"""

import os
import hashlib
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

try:
    from fastapi import UploadFile, HTTPException
except ImportError:
    class UploadFile:
        def __init__(self):
            self.filename = "test.txt"
            self.content_type = "text/plain"
        
        async def read(self):
            return b"test content"
    
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail

try:
    from services.file_storage_database import get_file_storage_database, FileStorageDatabase
except ImportError:
    # Create mock implementations
    class FileStorageDatabase:
        def __init__(self):
            self._file_metadata = {}
        
        async def save_file_metadata(self, metadata):
            self._file_metadata[metadata.id] = metadata
            return metadata
        
        async def get_file_metadata(self, file_id):
            return self._file_metadata.get(file_id)
        
        async def delete_file_metadata(self, file_id):
            if file_id in self._file_metadata:
                del self._file_metadata[file_id]
                return True
            return False
        
        async def list_files_by_user(self, user_id, limit=50, offset=0):
            files = [f for f in self._file_metadata.values() if f.uploaded_by == user_id]
            return files[offset:offset+limit]
        
        async def list_files_by_project(self, project_id, limit=50, offset=0):
            files = [f for f in self._file_metadata.values() if f.project_id == project_id]
            return files[offset:offset+limit]
        
        async def search_files(self, query=None, file_type=None, user_id=None, project_id=None, limit=50, offset=0):
            files = list(self._file_metadata.values())
            if query:
                files = [f for f in files if query.lower() in f.original_filename.lower()]
            if file_type:
                files = [f for f in files if f.file_type == file_type]
            if user_id:
                files = [f for f in files if f.uploaded_by == user_id]
            if project_id:
                files = [f for f in files if f.project_id == project_id]
            return files[offset:offset+limit]
        
        async def get_statistics(self):
            files = list(self._file_metadata.values())
            total_size = sum(f.size_bytes for f in files)
            return {
                "total_files": len(files),
                "total_size_bytes": total_size,
                "file_types": {},
                "processing_status": {}
            }
    
    def get_file_storage_database():
        return FileStorageDatabase()

try:
    from database.enhanced_models import (
        FileMetadata,
        FileType, StorageLocation, ProcessingStatus, VirusScanStatus
    )
except ImportError:
    # Define local enum classes
    class FileType(Enum):
        TEXT = "text"
        DOCUMENT = "document"
        IMAGE = "image"
        AUDIO = "audio"
        VIDEO = "video"
        ARCHIVE = "archive"
        SPREADSHEET = "spreadsheet"
        CHAT_EXPORT = "chat_export"
        OTHER = "other"
    
    class StorageLocation(Enum):
        LOCAL = "local"
        CLOUD = "cloud"
    
    class ProcessingStatus(Enum):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
    
    class VirusScanStatus(Enum):
        PENDING = "pending"
        CLEAN = "clean"
        INFECTED = "infected"
        FAILED = "failed"
    
    @dataclass
    class FileMetadata:
        id: str
        filename: str
        original_filename: str
        file_type: FileType
        mime_type: str
        size_bytes: int
        checksum_md5: str
        checksum_sha256: str
        storage_path: str
        uploaded_by: str
        project_id: Optional[str] = None
        conversation_id: Optional[str] = None
        analysis_id: Optional[str] = None
        processing_status: ProcessingStatus = ProcessingStatus.PENDING
        processing_error: Optional[str] = None
        version: int = 1
        parent_file_id: Optional[str] = None
        storage_location: StorageLocation = StorageLocation.LOCAL
        virus_scan_status: VirusScanStatus = VirusScanStatus.PENDING
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None
        last_accessed_at: Optional[datetime] = None
        expires_at: Optional[datetime] = None
        description: Optional[str] = None
        extracted_text: Optional[str] = None

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class FileValidationResult:
    """Result of file validation"""
    is_valid: bool
    file_type: FileType
    mime_type: str
    size_bytes: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class FileStorageService:
    """Enhanced file storage service with database integration"""
    
    def __init__(self, 
                 storage_root: str = "./storage",
                 max_file_size: int = 100 * 1024 * 1024):  # 100MB
        """Initialize file storage service
        
        Args:
            storage_root: Root directory for file storage
            max_file_size: Maximum file size in bytes
        """
        self.storage_root = Path(storage_root)
        self.max_file_size = max_file_size
        self.database = get_file_storage_database()
        
        # Default allowed extensions
        self.allowed_extensions = [
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
            # Documents
            '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt',
            # Spreadsheets
            '.xls', '.xlsx', '.csv', '.ods',
            # Chat exports
            '.zip', '.json', '.xml', '.html',
            # Media
            '.mp4', '.avi', '.mov', '.mp3', '.wav', '.m4a',
            # Archives
            '.tar', '.gz', '.7z', '.rar'
        ]
        
        # Initialize storage directories
        self._init_storage_structure()
        
        logger.info(f"FileStorageService initialized with root: {self.storage_root}")

    def _init_storage_structure(self):
        """Initialize storage directory structure"""
        directories = [
            "uploads",      # Original uploaded files
            "processed",    # Processed files
            "thumbnails",   # Generated thumbnails
            "temp",         # Temporary files
            "quarantine",   # Quarantined files
            "exports"       # Exported files
        ]
        
        for directory in directories:
            dir_path = self.storage_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {dir_path}")

    def _get_storage_path(self, file_type: FileType, filename: str) -> Path:
        """Get storage path for a file"""
        # Create date-based subdirectory
        date_dir = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        type_dir = file_type.value
        
        storage_path = self.storage_root / "uploads" / type_dir / date_dir
        storage_path.mkdir(parents=True, exist_ok=True)
        
        return storage_path / filename

    async def _validate_file(self, file: UploadFile) -> FileValidationResult:
        """Validate uploaded file"""
        errors = []
        warnings = []
        
        # Check filename
        if not file.filename:
            errors.append("Filename is required")
            return FileValidationResult(
                is_valid=False,
                file_type=FileType.OTHER,
                errors=errors,
                warnings=warnings,
                size_bytes=0,
                mime_type="application/octet-stream"
            )
        
        # Check file size
        content = await file.read()
        size_bytes = len(content)
        await file.seek(0)  # Reset file pointer
        
        if size_bytes > self.max_file_size:
            errors.append(f"File size ({size_bytes} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)")
        
        if size_bytes == 0:
            errors.append("File is empty")
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            errors.append(f"File extension '{file_extension}' is not allowed")
        
        # Determine MIME type and file type
        mime_type = file.content_type or "application/octet-stream"
        
        # Map MIME types to file types
        file_type_mapping = {
            'text/plain': FileType.TEXT,
            'text/html': FileType.DOCUMENT,
            'text/csv': FileType.SPREADSHEET,
            'application/pdf': FileType.DOCUMENT,
            'application/msword': FileType.DOCUMENT,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': FileType.DOCUMENT,
            'application/json': FileType.OTHER,
            'application/zip': FileType.ARCHIVE,
            'image/jpeg': FileType.IMAGE,
            'image/png': FileType.IMAGE,
            'image/gif': FileType.IMAGE,
            'video/mp4': FileType.VIDEO,
            'audio/mpeg': FileType.AUDIO,
        }
        
        file_type = file_type_mapping.get(mime_type, FileType.OTHER)
        
        # Special handling for chat exports
        if file_extension == '.zip' and 'chat' in file.filename.lower():
            file_type = FileType.CHAT_EXPORT
        
        return FileValidationResult(
            is_valid=len(errors) == 0,
            file_type=file_type,
            mime_type=mime_type,
            size_bytes=size_bytes,
            errors=errors,
            warnings=warnings
        )

    async def upload_file(self,
                         file: UploadFile,
                         uploaded_by: str,
                         project_id: Optional[str] = None,
                         conversation_id: Optional[str] = None) -> FileMetadata:
        """Upload and process a file"""
        try:
            # Validate file
            validation_result = await self._validate_file(file)
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File validation failed: {', '.join(validation_result.errors)}"
                )
            
            # Read file content
            content = await file.read()
            
            # Generate checksums
            md5_hash = hashlib.md5(content).hexdigest()
            sha256_hash = hashlib.sha256(content).hexdigest()
            
            # Generate stored filename
            if not file.filename:
                raise ValueError("Filename is required")
            
            file_extension = Path(file.filename).suffix.lower()
            stored_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Determine storage path
            storage_path = self._get_storage_path(validation_result.file_type, stored_filename)
            
            # Create file metadata
            file_id = str(uuid.uuid4())
            current_time = datetime.now()
            metadata = FileMetadata(
                id=file_id,
                filename=stored_filename,
                original_filename=file.filename,
                file_type=validation_result.file_type,
                mime_type=validation_result.mime_type,
                size_bytes=validation_result.size_bytes,
                checksum_md5=md5_hash,
                checksum_sha256=sha256_hash,
                storage_path=str(storage_path),
                uploaded_by=uploaded_by,
                project_id=project_id,
                conversation_id=conversation_id,
                analysis_id=None,
                processing_status=ProcessingStatus.PENDING,
                processing_error=None,
                version=1,
                parent_file_id=None,
                created_at=current_time,
                updated_at=current_time,
                last_accessed_at=None,
                expires_at=None,
                description=None,
                extracted_text=None
            )
            
            # Save file to storage
            with open(storage_path, 'wb') as f:
                f.write(content)
            
            # Save metadata to database
            saved_metadata = await self.database.save_file_metadata(metadata)
            
            logger.info(f"File uploaded successfully: {metadata.id} ({file.filename})")
            return saved_metadata
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID"""
        try:
            return await self.database.get_file_metadata(file_id)
        except Exception as e:
            logger.error(f"Failed to get file metadata: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get file metadata: {str(e)}")

    async def get_file_content(self, file_id: str, user_id: str) -> Tuple[bytes, str]:
        """Get file content and MIME type"""
        try:
            metadata = await self.database.get_file_metadata(file_id)
            if not metadata:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Check permissions (basic check)
            if metadata.uploaded_by != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Read file content
            storage_path = Path(metadata.storage_path)
            if not storage_path.exists():
                raise HTTPException(status_code=404, detail="File not found on storage")
            
            with open(storage_path, 'rb') as f:
                content = f.read()
            
            return content, metadata.mime_type
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get file content: {str(e)}")

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file and its metadata"""
        try:
            metadata = await self.database.get_file_metadata(file_id)
            if not metadata:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Check permissions
            if metadata.uploaded_by != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Delete file from storage
            storage_path = Path(metadata.storage_path)
            if storage_path.exists():
                storage_path.unlink()
            
            # Delete metadata from database
            await self.database.delete_file_metadata(file_id)
            
            logger.info(f"File deleted: {file_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    async def list_user_files(self, user_id: str, limit: int = 100, offset: int = 0) -> List[FileMetadata]:
        """List files uploaded by a user"""
        try:
            return await self.database.list_files_by_user(user_id, limit, offset)
        except Exception as e:
            logger.error(f"Failed to list user files: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

    async def list_project_files(self, project_id: str, limit: int = 100, offset: int = 0) -> List[FileMetadata]:
        """List files associated with a project"""
        try:
            return await self.database.list_files_by_project(project_id, limit, offset)
        except Exception as e:
            logger.error(f"Failed to list project files: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list project files: {str(e)}")

    async def search_files(self,
                           query: Optional[str] = None,
                          file_type: Optional[FileType] = None,
                          user_id: Optional[str] = None,
                          project_id: Optional[str] = None,
                          limit: int = 100,
                          offset: int = 0) -> List[FileMetadata]:
        """Search files based on criteria"""
        try:
            return await self.database.search_files(
                query=query,
                file_type=file_type,
                user_id=user_id,
                project_id=project_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to search files: {str(e)}")

    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage system statistics"""
        try:
            return await self.database.get_statistics()
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Global service instance
_service_instance: Optional[FileStorageService] = None

def get_file_storage_service() -> FileStorageService:
    """Get global file storage service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = FileStorageService()
    return _service_instance