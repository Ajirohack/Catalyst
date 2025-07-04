"""Database base configuration and session management"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Database configuration
class DatabaseConfig:
    """Database configuration and session management"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./catalyst.db")
        self.test_database_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_catalyst.db")
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database engine and session factory"""
        try:
            # Configure engine based on database type
            if self.database_url.startswith("sqlite"):
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=os.getenv("DEBUG_MODE", "false").lower() == "true"
                )
            else:
                # PostgreSQL or other databases
                self.engine = create_engine(
                    self.database_url,
                    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
                    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
                    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
                    echo=os.getenv("DEBUG_MODE", "false").lower() == "true"
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database initialized with URL: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Global database instance (lazy initialization)
db_config = None

def get_db_config():
    """Get database configuration with lazy initialization"""
    global db_config
    if db_config is None:
        db_config = DatabaseConfig()
    return db_config

# Dependency for FastAPI
def get_database_session():
    """Dependency to get database session for FastAPI routes"""
    config = get_db_config()
    session = config.get_session()
    try:
        yield session
    finally:
        session.close()

# Alias for compatibility
def get_db():
    """Get database session - alias for compatibility"""
    return get_database_session()

# Note: Database tables will be created when first accessed
# to avoid import-time SQLAlchemy issues with Python 3.13

# Export commonly used items
__all__ = [
    "Base",
    "DatabaseConfig",
    "db_config",
    "get_database_session",
    "get_db",
    "get_db_config"
]