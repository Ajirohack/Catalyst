"""Knowledge Base Service for Catalyst"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid
import json
from pydantic import BaseModel, Field
import asyncio

logger = logging.getLogger(__name__)

class KnowledgeEntry(BaseModel):
    """Knowledge base entry data structure."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Entry title")
    content: str = Field(..., description="Entry content")
    category: str = Field(default="general", description="Entry category")
    tags: List[str] = Field(default_factory=list, description="Entry tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether entry is active")

class KnowledgeBaseService:
    """Service for managing knowledge base operations"""
    
    def __init__(self) -> None:
        """Initialize the knowledge base service."""
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        logger.info("Knowledge Base Service initialized")
    
    async def add_entry(self, entry: KnowledgeEntry) -> str:
        """Add a new knowledge entry."""
        try:
            self.entries[entry.id] = entry
            
            # Update categories index
            if entry.category not in self.categories:
                self.categories[entry.category] = []
            self.categories[entry.category].append(entry.id)
            
            # Update tags index
            for tag in entry.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(entry.id)
            
            logger.info(f"Added knowledge entry: {entry.id}")
            return entry.id
            
        except Exception as e:
            logger.error(f"Error adding knowledge entry: {e}")
            raise
    
    async def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get a knowledge entry by ID."""
        return self.entries.get(entry_id)
    
    async def search_entries(
        self, 
        query: str, 
        category: Optional[str] = None, 
        tags: Optional[List[str]] = None
    ) -> List[KnowledgeEntry]:
        """Search knowledge entries."""
        try:
            # Simple text search in title and content
            results = []
            query_lower = query.lower()
            
            for entry in self.entries.values():
                if not entry.is_active:
                    continue
                    
                # Check category filter
                if category and entry.category != category:
                    continue
                    
                # Check tags filter
                if tags and not any(tag in entry.tags for tag in tags):
                    continue
                    
                # Check if query matches title or content
                if (
                    query_lower in entry.title.lower() or 
                    query_lower in entry.content.lower()
                ):
                    results.append(entry)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge entries: {e}")
            return []
    
    async def get_all_entries(self) -> List[KnowledgeEntry]:
        """Get all knowledge entries."""
        return [entry for entry in self.entries.values() if entry.is_active]
    
    async def get_categories(self) -> List[str]:
        """Get all categories."""
        return list(self.categories.keys())
    
    async def get_tags(self) -> List[str]:
        """Get all tags."""
        return list(self.tags.keys())
    
    async def update_entry(
        self, entry_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Update an existing knowledge entry."""
        try:
            entry = self.entries.get(entry_id)
            if not entry:
                return False
            
            # Update the entry with provided updates
            for key, value in updates.items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
            
            entry.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Updated knowledge entry: {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge entry: {e}")
            return False
    
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry."""
        try:
            entry = self.entries.get(entry_id)
            if entry:
                entry.is_active = False
                entry.updated_at = datetime.now(timezone.utc)
                logger.info(f"Deleted knowledge entry: {entry_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting knowledge entry: {e}")
            return False

    async def get_entries_by_category(
        self, category: str
    ) -> List[KnowledgeEntry]:
        """Get all entries in a specific category."""
        entry_ids = self.categories.get(category, [])
        return [self.entries[entry_id] for entry_id in entry_ids 
                if entry_id in self.entries and self.entries[entry_id].is_active]
    
    async def get_entries_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        """Get all entries with a specific tag."""
        entry_ids = self.tags.get(tag, [])
        return [self.entries[entry_id] for entry_id in entry_ids 
                if entry_id in self.entries and self.entries[entry_id].is_active]


# Global instance
knowledge_base_service = KnowledgeBaseService()