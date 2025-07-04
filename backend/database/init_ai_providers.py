"""
Database initialization for AI Provider Management
Creates tables and seeds initial data
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Optional
import os
import logging
import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.models import Base, AIProvider, AIProviderModel
from services.ai_provider_service import AIProviderService

logger = logging.getLogger(__name__)

def create_database_tables(database_url: Optional[str] = None):
    """Create all AI provider management tables"""
    if not database_url:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./catalyst.db")
    
    engine = create_engine(database_url)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("AI Provider tables created successfully")
    
    return engine

async def seed_default_providers(database_url: Optional[str] = None):
    """Seed database with default provider configurations"""
    if not database_url:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./catalyst.db")
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if providers already exist
        existing_providers = db.query(AIProvider).count()
        if existing_providers > 0:
            logger.info("Providers already exist, skipping seed")
            return
        
        provider_service = AIProviderService(db)
        
        # Seed OpenAI provider
        openai_config = {
            "provider_type": "openai",
            "name": "OpenAI",
            "description": "Advanced AI models including GPT-4 and GPT-3.5",
            "enabled": True,
            "priority": 1,
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-3.5-turbo",
            "timeout_seconds": 30,
            "max_retries": 3,
            "confidence_score": 0.9,
            "quality_rating": 0.95,
            "rate_limits": {
                "requests_per_minute": 3500,
                "tokens_per_minute": 90000
            }
        }
        
        # Seed Anthropic provider
        anthropic_config = {
            "provider_type": "anthropic",
            "name": "Anthropic",
            "description": "Claude models for advanced reasoning and analysis",
            "enabled": True,
            "priority": 2,
            "base_url": "https://api.anthropic.com",
            "default_model": "claude-3-sonnet-20240229",
            "timeout_seconds": 30,
            "max_retries": 3,
            "confidence_score": 0.85,
            "quality_rating": 0.9,
            "rate_limits": {
                "requests_per_minute": 1000,
                "tokens_per_minute": 80000
            }
        }
        
        # Seed Mistral provider
        mistral_config = {
            "provider_type": "mistral",
            "name": "Mistral AI",
            "description": "High-performance European AI models",
            "enabled": False,  # Disabled by default until API key is configured
            "priority": 3,
            "base_url": "https://api.mistral.ai/v1",
            "default_model": "mistral-medium-latest",
            "timeout_seconds": 30,
            "max_retries": 3,
            "confidence_score": 0.8,
            "quality_rating": 0.85,
            "rate_limits": {
                "requests_per_minute": 500,
                "tokens_per_minute": 50000
            }
        }
        
        # Seed OpenRouter provider
        openrouter_config = {
            "provider_type": "openrouter",
            "name": "OpenRouter",
            "description": "Access to multiple AI models through a unified API",
            "enabled": False,
            "priority": 4,
            "base_url": "https://openrouter.ai/api/v1",
            "default_model": "anthropic/claude-3-opus",
            "timeout_seconds": 30,
            "max_retries": 3,
            "confidence_score": 0.8,
            "quality_rating": 0.85,
            "rate_limits": {
                "requests_per_minute": 1000,
                "tokens_per_minute": 60000
            }
        }
        
        # Seed Ollama provider
        ollama_config = {
            "provider_type": "ollama",
            "name": "Ollama (Local)",
            "description": "Local AI models running on your hardware",
            "enabled": False,
            "priority": 5,
            "base_url": "http://localhost:11434",
            "default_model": "llama2",
            "timeout_seconds": 60,
            "max_retries": 2,
            "confidence_score": 0.7,
            "quality_rating": 0.75,
            "rate_limits": {
                "requests_per_minute": 100,
                "tokens_per_minute": 10000
            }
        }
        
        # Seed Groq provider
        groq_config = {
            "provider_type": "groq",
            "name": "Groq",
            "description": "Ultra-fast AI inference with specialized hardware",
            "enabled": False,
            "priority": 6,
            "base_url": "https://api.groq.com/openai/v1",
            "default_model": "llama2-70b-4096",
            "timeout_seconds": 15,
            "max_retries": 3,
            "confidence_score": 0.8,
            "quality_rating": 0.8,
            "rate_limits": {
                "requests_per_minute": 300,
                "tokens_per_minute": 30000
            }
        }
        
        # Seed Hugging Face provider
        huggingface_config = {
            "provider_type": "huggingface",
            "name": "Hugging Face",
            "description": "Open-source AI models and inference API",
            "enabled": False,
            "priority": 7,
            "base_url": "https://api-inference.huggingface.co",
            "default_model": "microsoft/DialoGPT-large",
            "timeout_seconds": 30,
            "max_retries": 3,
            "confidence_score": 0.7,
            "quality_rating": 0.75,
            "rate_limits": {
                "requests_per_minute": 1000,
                "tokens_per_minute": 50000
            }
        }
        
        # Create providers
        configs = [
            openai_config, anthropic_config, mistral_config, openrouter_config,
            ollama_config, groq_config, huggingface_config
        ]
        
        for config in configs:
            try:
                await provider_service.create_provider(config)
                logger.info(f"Created provider: {config['name']}")
            except Exception as e:
                logger.error(f"Failed to create provider {config['name']}: {str(e)}")
        
        logger.info("Default providers seeded successfully")
        
    except Exception as e:
        logger.error(f"Failed to seed providers: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

async def initialize_ai_provider_system(database_url: Optional[str] = None):
    """Initialize the complete AI provider system"""
    try:
        # Create database tables
        engine = create_database_tables(database_url)
        logger.info("Database tables created")
        
        # Seed default providers
        await seed_default_providers(database_url)
        logger.info("Default providers seeded")
        
        # Initialize the enhanced LLM router
        from services.enhanced_llm_router import enhanced_llm_router
        logger.info("Enhanced LLM router initialized")
        
        logger.info("AI Provider system initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI provider system: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    # Run initialization
    asyncio.run(initialize_ai_provider_system())
