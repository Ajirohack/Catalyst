"""Database service for File Storage System
Provides database integration for file metadata storage and retrieval
"""

import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum

try:
    from database.enhanced_models import (
        FileMetadata, FileType, StorageLocation, 
        ProcessingStatus, VirusScanStatus
    )
except ImportError:
    # Define local enum classes if imports fail
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

class FileStorageDatabase:
    """Database service for file storage system"""
    
    def __init__(self):
        """Initialize database service"""
        # Note: In a real implementation, this would connect to actual database
        # For now, using in-memory storage for testing
        self._file_metadata: Dict[str, FileMetadata] = {}
        logger.info("FileStorageDatabase initialized with in-memory storage")
    
    async def save_file_metadata(self, metadata: FileMetadata) -> FileMetadata:
        """Save file metadata to database
        
        Args:
            metadata: FileMetadata object to save
            
        Returns:
            Saved FileMetadata object
        """
        try:
            # In a real implementation, this would save to database
            self._file_metadata[metadata.id] = metadata
            logger.info(f"File metadata saved: {metadata.id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to save file metadata: {e}")
            raise
    
    async def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Retrieve file metadata by ID
        
        Args:
            file_id: File ID to retrieve
            
        Returns:
            FileMetadata object or None if not found
        """
        try:
            metadata = self._file_metadata.get(file_id)
            if metadata:
                # Update last accessed time
                metadata.last_accessed_at = datetime.now(timezone.utc)
                await self.save_file_metadata(metadata)
                logger.debug(f"File metadata retrieved: {file_id}")
            else:
                logger.warning(f"File metadata not found: {file_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to retrieve file metadata: {e}")
            raise
    
    async def update_file_metadata(self, file_id: str, updates: Dict[str, Any]) -> Optional[FileMetadata]:
        """Update file metadata
        
        Args:
            file_id: File ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated FileMetadata object or None if not found
        """
        try:
            metadata = self._file_metadata.get(file_id)
            if not metadata:
                logger.warning(f"File metadata not found for update: {file_id}")
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(metadata, field):
                    setattr(metadata, field, value)
                    logger.debug(f"Updated {field} for file {file_id}")
            
            # Save updated metadata
            await self.save_file_metadata(metadata)
            logger.info(f"File metadata updated: {file_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to update file metadata: {e}")
            raise
    
    async def delete_file_metadata(self, file_id: str) -> bool:
        """Delete file metadata
        
        Args:
            file_id: File ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            if file_id in self._file_metadata:
                del self._file_metadata[file_id]
                logger.info(f"File metadata deleted: {file_id}")
                return True
            else:
                logger.warning(f"File metadata not found for deletion: {file_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file metadata: {e}")
            raise
    
    async def list_files_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> List[FileMetadata]:
        """List files uploaded by a specific user
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileMetadata objects
        """
        try:
            user_files = [
                metadata for metadata in self._file_metadata.values()
                if metadata.uploaded_by == user_id
            ]
            
            # Sort by upload date (newest first)
            user_files.sort(key=lambda x: x.created_at or datetime.now(), reverse=True)
            
            # Apply pagination
            paginated_files = user_files[offset:offset + limit]
            
            logger.debug(f"Retrieved {len(paginated_files)} files for user {user_id}")
            return paginated_files
            
        except Exception as e:
            logger.error(f"Failed to list files for user: {e}")
            raise
    
    async def list_files_by_project(self, project_id: str, limit: int = 100, offset: int = 0) -> List[FileMetadata]:
        """List files associated with a specific project
        
        Args:
            project_id: Project ID to filter by
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileMetadata objects
        """
        try:
            project_files = [
                metadata for metadata in self._file_metadata.values()
                if metadata.project_id == project_id
            ]
            
            # Sort by upload date (newest first)
            project_files.sort(key=lambda x: x.created_at or datetime.now(), reverse=True)
            
            # Apply pagination
            paginated_files = project_files[offset:offset + limit]
            
            logger.debug(f"Retrieved {len(paginated_files)} files for project {project_id}")
            return paginated_files
            
        except Exception as e:
            logger.error(f"Failed to list files for project: {e}")
            raise
    
    async def search_files(self, 
                          query: Optional[str] = None,
                          file_type: Optional[FileType] = None,
                          user_id: Optional[str] = None,
                          project_id: Optional[str] = None,
                          limit: int = 100,
                          offset: int = 0) -> List[FileMetadata]:
        """Search files based on various criteria
        
        Args:
            query: Text to search in filename and extracted text
            file_type: File type to filter by
            user_id: User ID to filter by
            project_id: Project ID to filter by
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileMetadata objects matching criteria
        """
        try:
            results = list(self._file_metadata.values())
            
            # Apply filters
            if user_id:
                results = [f for f in results if f.uploaded_by == user_id]
            
            if project_id:
                results = [f for f in results if f.project_id == project_id]
            
            if file_type:
                results = [f for f in results if f.file_type == file_type]
            
            if query:
                query_lower = query.lower()
                results = [
                    f for f in results
                    if (query_lower in f.filename.lower() or
                        query_lower in f.original_filename.lower() or
                        (f.extracted_text and query_lower in f.extracted_text.lower()) or
                        (f.description and query_lower in f.description.lower()))
                ]
            
            # Sort by relevance (for now, just by upload date)
            results.sort(key=lambda x: x.created_at or datetime.now(), reverse=True)
            
            # Apply pagination
            paginated_results = results[offset:offset + limit]
            
            logger.debug(f"Search returned {len(paginated_results)} files")
            return paginated_results
            
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            raise
    
    async def get_files_by_checksum(self, checksum_md5: str) -> List[FileMetadata]:
        """Find files with the same checksum (duplicates)
        
        Args:
            checksum_md5: MD5 checksum to search for
            
        Returns:
            List of FileMetadata objects with matching checksum
        """
        try:
            duplicate_files = [
                metadata for metadata in self._file_metadata.values()
                if metadata.checksum_md5 == checksum_md5
            ]
            
            logger.debug(f"Found {len(duplicate_files)} files with checksum {checksum_md5}")
            return duplicate_files
            
        except Exception as e:
            logger.error(f"Failed to search by checksum: {e}")
            raise
    
    async def get_expiring_files(self, days_ahead: int = 7) -> List[FileMetadata]:
        """Get files that are expiring within specified days
        
        Args:
            days_ahead: Number of days to look ahead for expiring files
            
        Returns:
            List of FileMetadata objects that are expiring
        """
        try:
            cutoff_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            
            expiring_files = [
                metadata for metadata in self._file_metadata.values()
                if metadata.expires_at and metadata.expires_at <= cutoff_date
            ]
            
            # Sort by expiration date (earliest first)
            expiring_files.sort(key=lambda x: x.expires_at or datetime.max)
            
            logger.debug(f"Found {len(expiring_files)} files expiring within {days_ahead} days")
            return expiring_files
            
        except Exception as e:
            logger.error(f"Failed to get expiring files: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get file storage statistics
        
        Returns:
            Dictionary containing various statistics
        """
        try:
            files = list(self._file_metadata.values())
            
            if not files:
                return {
                    "total_files": 0,
                    "total_size_bytes": 0,
                    "file_types": {},
                    "storage_locations": {},
                    "processing_status": {},
                    "virus_scan_status": {}
                }
            
            # Calculate statistics
            total_size = sum(f.size_bytes for f in files)
            
            # Group by file types
            file_types = {}
            for f in files:
                file_types[f.file_type.value] = file_types.get(f.file_type.value, 0) + 1
            
            # Group by storage locations
            storage_locations = {}
            for f in files:
                storage_locations[f.storage_location.value] = storage_locations.get(f.storage_location.value, 0) + 1
            
            # Group by processing status
            processing_status = {}
            for f in files:
                processing_status[f.processing_status.value] = processing_status.get(f.processing_status.value, 0) + 1
            
            # Group by virus scan status
            virus_scan_status = {}
            for f in files:
                virus_scan_status[f.virus_scan_status.value] = virus_scan_status.get(f.virus_scan_status.value, 0) + 1
            
            stats = {
                "total_files": len(files),
                "total_size_bytes": total_size,
                "average_size_bytes": total_size / len(files),
                "file_types": file_types,
                "storage_locations": storage_locations,
                "processing_status": processing_status,
                "virus_scan_status": virus_scan_status,
                "oldest_file": min(f.created_at or datetime.now() for f in files).isoformat(),
                "newest_file": max(f.created_at or datetime.now() for f in files).isoformat()
            }
            
            logger.debug("File storage statistics calculated")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            raise

# Global database instance
_db_instance: Optional[FileStorageDatabase] = None

def get_file_storage_database() -> FileStorageDatabase:
    """Get global file storage database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = FileStorageDatabase()
    return _db_instance
