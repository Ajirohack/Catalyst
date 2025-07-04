"""
Vector Search Service for Catalyst Knowledge Base
Provides semantic search capabilities using vector embeddings
"""

import asyncio
import logging
import hashlib
import json
import os
try:
    from typing import List, Dict, Any, Optional, Union, Tuple
    from datetime import datetime, timezone
    from dataclasses import dataclass, asdict
    from enum import Enum
    import numpy as np
except ImportError:
    pass

    pass

    pass
# Try importing vector database libraries, with fallbacks
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    pinecone = None
    PINECONE_AVAILABLE = False

# Try importing embedding libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class VectorProvider(str, Enum):
    """Supported vector database providers"""
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    MEMORY = "memory"  # In-memory fallback

class EmbeddingProvider(str, Enum):
    """Supported embedding providers"""
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"
    SIMPLE = "simple"  # Simple fallback

@dataclass
class SearchResult:
    """Vector search result"""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None

@dataclass
class VectorDocument:
    """Document for vector storage"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class VectorSearchService:
    """
    Vector search service with support for multiple providers and embedding models
    """
    
    def __init__(self, 
                 vector_provider: Optional[str] = None,
                 embedding_provider: Optional[str] = None,
                 **kwargs):
        """
        Initialize vector search service
        
        Args:
            vector_provider: Vector database provider (chromadb, pinecone, memory)
            embedding_provider: Embedding model provider (sentence_transformers, openai, simple)
            **kwargs: Additional configuration options
        """
        self.config = self._load_config(vector_provider, embedding_provider, **kwargs)
        self.vector_provider = self.config.get("vector_provider", VectorProvider.MEMORY)
        self.embedding_provider = self.config.get("embedding_provider", EmbeddingProvider.SIMPLE)
        
        # Initialize components
        self.embedder = None
        self.vector_db = None
        self.memory_store = {}  # Fallback in-memory storage
        
        logger.info(f"Initializing VectorSearchService with provider: {self.vector_provider}, embedder: {self.embedding_provider}")
    
    def _load_config(self, vector_provider: Optional[str] = None, embedding_provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Load configuration from environment and parameters"""
        config = {
            # Vector database configuration
            "vector_provider": vector_provider or os.getenv("CATALYST_VECTOR_PROVIDER", VectorProvider.CHROMADB),
            "chromadb_path": os.getenv("CATALYST_CHROMADB_PATH", "./data/chromadb"),
            "chromadb_collection": os.getenv("CATALYST_CHROMADB_COLLECTION", "catalyst_knowledge"),
            "pinecone_api_key": os.getenv("PINECONE_API_KEY"),
            "pinecone_environment": os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp"),
            "pinecone_index": os.getenv("CATALYST_PINECONE_INDEX", "catalyst-knowledge"),
            
            # Embedding configuration
            "embedding_provider": embedding_provider or os.getenv("CATALYST_EMBEDDING_PROVIDER", EmbeddingProvider.SENTENCE_TRANSFORMERS),
            "embedding_model": os.getenv("CATALYST_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "embedding_dimension": int(os.getenv("CATALYST_EMBEDDING_DIMENSION", "384")),
            "chunk_size": int(os.getenv("CATALYST_CHUNK_SIZE", "1000")),
            "chunk_overlap": int(os.getenv("CATALYST_CHUNK_OVERLAP", "200")),
            
            # Search configuration
            "default_search_limit": int(os.getenv("CATALYST_SEARCH_LIMIT", "10")),
            "min_similarity_threshold": float(os.getenv("CATALYST_MIN_SIMILARITY", "0.1")),
        }
        
        # Override with any provided kwargs
        config.update(kwargs)
        return config
    
    async def initialize(self) -> bool:
        """
        Initialize the vector search service
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize embedding provider
            await self._initialize_embedder()
            
            # Initialize vector database
            await self._initialize_vector_db()
            
            logger.info("Vector search service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector search service: {e}")
            return False
    
    async def _initialize_embedder(self):
        """Initialize the embedding provider"""
        if self.embedding_provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                try:
                    model_name = self.config.get("embedding_model", "all-MiniLM-L6-v2")
                    self.embedder = SentenceTransformer(model_name)
                    logger.info(f"Initialized SentenceTransformers with model: {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize SentenceTransformers: {e}, falling back to simple embedder")
                    self.embedding_provider = EmbeddingProvider.SIMPLE
            else:
                logger.warning("SentenceTransformers not available, falling back to simple embedder")
                self.embedding_provider = EmbeddingProvider.SIMPLE
                
        elif self.embedding_provider == EmbeddingProvider.OPENAI:
            if OPENAI_AVAILABLE and self.config.get("openai_api_key"):
                try:
                    openai.api_key = self.config["openai_api_key"]
                    # Test the connection
                    await self._generate_openai_embedding("test")
                    logger.info("Initialized OpenAI embeddings")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI embeddings: {e}, falling back to simple embedder")
                    self.embedding_provider = EmbeddingProvider.SIMPLE
            else:
                logger.warning("OpenAI not available or API key missing, falling back to simple embedder")
                self.embedding_provider = EmbeddingProvider.SIMPLE
        
        # Always have a fallback
        if self.embedding_provider == EmbeddingProvider.SIMPLE:
            logger.info("Using simple hash-based embedder")
    
    async def _initialize_vector_db(self):
        """Initialize the vector database"""
        if self.vector_provider == VectorProvider.CHROMADB:
            if CHROMADB_AVAILABLE:
                try:
                    db_path = self.config.get("chromadb_path", "./data/chromadb")
                    os.makedirs(db_path, exist_ok=True)
                    
                    self.vector_db = chromadb.PersistentClient(
                        path=db_path,
                        settings=Settings(anonymized_telemetry=False)
                    )
                    
                    collection_name = self.config.get("chromadb_collection", "catalyst_knowledge")
                    self.collection = self.vector_db.get_or_create_collection(
                        name=collection_name,
                        metadata={"description": "Catalyst knowledge base"}
                    )
                    
                    logger.info(f"Initialized ChromaDB at {db_path}")
                except Exception as e:
                    logger.warning(f"Failed to initialize ChromaDB: {e}, falling back to memory storage")
                    self.vector_provider = VectorProvider.MEMORY
            else:
                logger.warning("ChromaDB not available, falling back to memory storage")
                self.vector_provider = VectorProvider.MEMORY
                
        elif self.vector_provider == VectorProvider.PINECONE:
            if PINECONE_AVAILABLE and self.config.get("pinecone_api_key"):
                try:
                    pinecone.init(
                        api_key=self.config["pinecone_api_key"],
                        environment=self.config.get("pinecone_environment", "us-west1-gcp")
                    )
                    
                    index_name = self.config.get("pinecone_index", "catalyst-knowledge")
                    if index_name not in pinecone.list_indexes():
                        # Create index if it doesn't exist
                        pinecone.create_index(
                            index_name,
                            dimension=self.config.get("embedding_dimension", 384),
                            metric="cosine"
                        )
                    
                    self.vector_db = pinecone.Index(index_name)
                    logger.info(f"Initialized Pinecone index: {index_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize Pinecone: {e}, falling back to memory storage")
                    self.vector_provider = VectorProvider.MEMORY
            else:
                logger.warning("Pinecone not available or API key missing, falling back to memory storage")
                self.vector_provider = VectorProvider.MEMORY
        
        # Memory storage is always available as fallback
        if self.vector_provider == VectorProvider.MEMORY:
            self.memory_store = {}
            logger.info("Using in-memory vector storage")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Vector embedding
        """
        if not text.strip():
            return [0.0] * self.config.get("embedding_dimension", 384)
        
        try:
            if self.embedding_provider == EmbeddingProvider.SENTENCE_TRANSFORMERS and self.embedder:
                embedding = self.embedder.encode(text, convert_to_numpy=True)
                return embedding.tolist()
                
            elif self.embedding_provider == EmbeddingProvider.OPENAI:
                return await self._generate_openai_embedding(text)
                
            else:
                # Simple hash-based embedding (fallback)
                return self._generate_simple_embedding(text)
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._generate_simple_embedding(text)
    
    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate OpenAI embedding"""
        try:
            response = await openai.Embedding.acreate(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            return self._generate_simple_embedding(text)
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate simple hash-based embedding (fallback)"""
        # Create a simple embedding based on text hash and basic features
        text_hash = hashlib.md5(text.encode()).digest()
        
        # Convert hash bytes to float values
        embedding = []
        for i in range(0, len(text_hash), 4):
            chunk = text_hash[i:i+4]
            if len(chunk) == 4:
                val = int.from_bytes(chunk, byteorder='big')
                normalized_val = (val / (2**32)) * 2 - 1  # Normalize to [-1, 1]
                embedding.append(normalized_val)
        
        # Pad to desired dimension
        target_dim = self.config.get("embedding_dimension", 384)
        while len(embedding) < target_dim:
            embedding.extend(embedding[:min(len(embedding), target_dim - len(embedding))])
        
        return embedding[:target_dim]
    
    async def index_document(self, 
                           document_id: str, 
                           content: str, 
                           metadata: Optional[Dict[str, Any]] = None,
                           chunk_content: bool = True) -> bool:
        """
        Index a document in the vector database
        
        Args:
            document_id: Unique document identifier
            content: Document content to index
            metadata: Additional metadata
            chunk_content: Whether to chunk large content
            
        Returns:
            bool: True if indexing successful
        """
        try:
            if not content.strip():
                logger.warning(f"Empty content for document {document_id}")
                return False
            
            metadata = metadata or {}
            metadata.update({
                "document_id": document_id,
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "content_length": len(content)
            })
            
            # Chunk content if necessary
            if chunk_content and len(content) > self.config.get("chunk_size", 1000):
                chunks = self._chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{document_id}_chunk_{i}"
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "is_chunk": True
                    })
                    
                    await self._index_single_item(chunk_id, chunk, chunk_metadata)
            else:
                await self._index_single_item(document_id, content, metadata)
            
            logger.info(f"Successfully indexed document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {e}")
            return False
    
    async def _index_single_item(self, item_id: str, content: str, metadata: Dict[str, Any]):
        """Index a single item (document or chunk)"""
        # Generate embedding
        embedding = await self.generate_embedding(content)
        
        # Store in vector database
        if self.vector_provider == VectorProvider.CHROMADB and self.collection:
            self.collection.upsert(
                ids=[item_id],
                documents=[content],
                metadatas=[metadata],
                embeddings=[embedding]
            )
            
        elif self.vector_provider == VectorProvider.PINECONE and self.vector_db:
            self.vector_db.upsert(
                vectors=[(item_id, embedding, metadata)]
            )
            
        else:  # Memory storage
            self.memory_store[item_id] = {
                "content": content,
                "metadata": metadata,
                "embedding": embedding
            }
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into smaller pieces with overlap
        
        Args:
            text: Text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        chunk_size = self.config.get("chunk_size", 1000)
        chunk_overlap = self.config.get("chunk_overlap", 200)
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at word boundary
            if end < len(text):
                # Look for space within last 100 characters
                space_pos = text.rfind(' ', start, end)
                if space_pos > start + chunk_size - 100:
                    end = space_pos
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def search(self, 
                    query: str, 
                    limit: Optional[int] = None,
                    min_similarity: Optional[float] = None,
                    filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            filters: Metadata filters
            
        Returns:
            List[SearchResult]: Search results
        """
        try:
            if not query.strip():
                return []
            
            limit = limit or self.config.get("default_search_limit", 10)
            min_similarity = min_similarity if min_similarity is not None else self.config.get("min_similarity_threshold", 0.1)
            filters = filters or {}
            
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Search in vector database
            if self.vector_provider == VectorProvider.CHROMADB and self.collection:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=filters
                )
                
                search_results = []
                for i in range(len(results['ids'][0])):
                    similarity = 1.0 - results['distances'][0][i]  # ChromaDB returns distances
                    if similarity >= min_similarity:
                        search_results.append(SearchResult(
                            document_id=results['ids'][0][i],
                            content=results['documents'][0][i],
                            metadata=results['metadatas'][0][i] or {},
                            similarity_score=similarity,
                            chunk_index=results['metadatas'][0][i].get('chunk_index') if results['metadatas'][0][i] else None,
                            total_chunks=results['metadatas'][0][i].get('total_chunks') if results['metadatas'][0][i] else None
                        ))
                
                return search_results
                
            elif self.vector_provider == VectorProvider.PINECONE and self.vector_db:
                # Pinecone search
                results = self.vector_db.query(
                    vector=query_embedding,
                    top_k=limit,
                    filter=filters,
                    include_metadata=True
                )
                
                search_results = []
                for match in results['matches']:
                    if match['score'] >= min_similarity:
                        search_results.append(SearchResult(
                            document_id=match['id'],
                            content=match['metadata'].get('content', ''),
                            metadata=match['metadata'],
                            similarity_score=match['score'],
                            chunk_index=match['metadata'].get('chunk_index'),
                            total_chunks=match['metadata'].get('total_chunks')
                        ))
                
                return search_results
                
            else:  # Memory storage
                return await self._search_memory_store(query_embedding, limit, min_similarity, filters)
                
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    async def _search_memory_store(self, 
                                 query_embedding: List[float], 
                                 limit: int, 
                                 min_similarity: float,
                                 filters: Dict[str, Any]) -> List[SearchResult]:
        """Search in memory store"""
        results = []
        
        for item_id, item_data in self.memory_store.items():
            # Apply filters
            if filters:
                metadata = item_data['metadata']
                if not all(metadata.get(k) == v for k, v in filters.items()):
                    continue
            
            # Calculate similarity
            similarity = self._cosine_similarity(query_embedding, item_data['embedding'])
            
            if similarity >= min_similarity:
                results.append(SearchResult(
                    document_id=item_id,
                    content=item_data['content'],
                    metadata=item_data['metadata'],
                    similarity_score=similarity,
                    chunk_index=item_data['metadata'].get('chunk_index'),
                    total_chunks=item_data['metadata'].get('total_chunks')
                ))
        
        # Sort by similarity and limit
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays for calculation
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
        except Exception:
            return 0.0
    
    async def update_document(self, 
                            document_id: str, 
                            content: str, 
                            metadata: Dict[str, Any] = None) -> bool:
        """
        Update an existing document
        
        Args:
            document_id: Document identifier
            content: New content
            metadata: Updated metadata
            
        Returns:
            bool: True if update successful
        """
        try:
            # First delete existing document
            await self.delete_document(document_id)
            
            # Then add updated version
            return await self.index_document(document_id, content, metadata)
            
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector database
        
        Args:
            document_id: Document identifier
            
        Returns:
            bool: True if deletion successful
        """
        try:
            if self.vector_provider == VectorProvider.CHROMADB and self.collection:
                # Find all items related to this document (including chunks)
                results = self.collection.get(
                    where={"document_id": document_id}
                )
                
                if results['ids']:
                    self.collection.delete(ids=results['ids'])
                
            elif self.vector_provider == VectorProvider.PINECONE and self.vector_db:
                # Delete all chunks for this document
                self.vector_db.delete(filter={"document_id": document_id})
                
            else:  # Memory storage
                # Remove all items with this document_id
                to_remove = [k for k, v in self.memory_store.items() 
                           if v['metadata'].get('document_id') == document_id]
                for key in to_remove:
                    del self.memory_store[key]
            
            logger.info(f"Successfully deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def get_document_count(self) -> int:
        """Get total number of indexed documents"""
        try:
            if self.vector_provider == VectorProvider.CHROMADB and self.collection:
                return self.collection.count()
                
            elif self.vector_provider == VectorProvider.PINECONE and self.vector_db:
                stats = self.vector_db.describe_index_stats()
                return stats['total_vector_count']
                
            else:  # Memory storage
                return len(self.memory_store)
                
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health
        
        Returns:
            Dict[str, Any]: Health status
        """
        status = {
            "service": "vector_search",
            "status": "healthy",
            "vector_provider": self.vector_provider,
            "embedding_provider": self.embedding_provider,
            "document_count": 0,
            "errors": []
        }
        
        try:
            # Check document count
            status["document_count"] = await self.get_document_count()
            
            # Test embedding generation
            test_embedding = await self.generate_embedding("health check test")
            if not test_embedding:
                status["errors"].append("Embedding generation failed")
            
            # Test search functionality
            search_results = await self.search("health check", limit=1)
            
        except Exception as e:
            status["status"] = "unhealthy"
            status["errors"].append(str(e))
        
        return status

# Convenience function for creating service instance
def create_vector_search_service(**kwargs) -> VectorSearchService:
    """Create and initialize vector search service"""
    service = VectorSearchService(**kwargs)
    return service
