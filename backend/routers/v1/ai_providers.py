"""
Unified AI Providers Router
Comprehensive API for managing AI providers with full CRUD operations
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import logging
import json

# Try to import required dependencies with graceful fallbacks
try:
    from sqlalchemy.orm import Session
    from database.base import get_db
except ImportError:
    Session = Any
    def get_db():
        yield None

try:
    from database.ai_provider_models_enhanced import AIProvider, AIProviderModel, AIUsageLog
except ImportError:
    try:
        from database.models_ai_providers import AIProvider, AIProviderModel, AIUsageLog
    except ImportError:
        # Mock classes for development
        class AIProvider: pass
        class AIProviderModel: pass  
        class AIUsageLog: pass

try:
    from services.ai_provider_service_enhanced import AIProviderService
except ImportError:
    try:
        from services.ai_provider_service import AIProviderService
    except ImportError:
        # Mock service for development
        class AIProviderService:
            def __init__(self, db):
                self.db = db

try:
    from schemas.ai_provider_schemas_enhanced import (
        AIProviderCreate, AIProviderUpdate, AIProviderResponse,
        AIProviderModelCreate, AIProviderModelUpdate, AIProviderModelResponse,
        ProviderTestRequest, ProviderTestResult, BulkProviderTestRequest, BulkProviderTestResponse,
        AIRequest, AIResponse, UsageMetrics, SystemUsageReport,
        ProviderHealthStatus, SupportedProviderInfo, ModelListResponse
    )
except ImportError:
    try:
        from schemas.ai_provider_enhanced_schema import (
            AIProviderCreateRequest as AIProviderCreate,
            AIProviderUpdateRequest as AIProviderUpdate, 
            AIProviderResponse,
            AIModelCreateRequest as AIProviderModelCreate,
            AIModelUpdateRequest as AIProviderModelUpdate,
            AIModelResponse as AIProviderModelResponse,
            ProviderTestResult, BulkProviderTestRequest, BulkProviderTestResponse,
            SupportedProviderInfo, SystemUsageReport, ModelListResponse,
            ProviderHealthStatus, ProviderAnalytics, CostOptimizationSuggestion
        )
    except ImportError:
        # Mock schemas for development
        class AIProviderCreate: pass
        class AIProviderUpdate: pass
        class AIProviderResponse: pass
        class AIProviderModelCreate: pass
        class AIProviderModelUpdate: pass
        class AIProviderModelResponse: pass
        class ProviderTestResult: pass
        class BulkProviderTestRequest: pass
        class BulkProviderTestResponse: pass
        class SupportedProviderInfo: pass
        class SystemUsageReport: pass
        class ModelListResponse: pass
        class ProviderHealthStatus: pass

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/ai-providers", tags=["AI Providers"])

# Dependency for provider service
def get_provider_service(db: Session = Depends(get_db)) -> AIProviderService:
    """Get AI provider service instance"""
    return AIProviderService(db)

# Provider Management Endpoints

@router.get("/", response_model=List[AIProviderResponse])
async def list_providers(
    include_inactive: bool = Query(True, description="Include inactive providers"),
    provider_type: Optional[str] = Query(None, description="Filter by provider type"),
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get all AI providers with their configurations and status"""
    try:
        providers = await provider_service.get_all_providers(
            include_inactive=include_inactive,
            provider_type=provider_type
        )
        return [AIProviderResponse.from_orm(provider) for provider in providers]
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=AIProviderResponse)
async def create_provider(
    provider_data: AIProviderCreate,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Create a new AI provider"""
    try:
        provider = await provider_service.create_provider(provider_data)
        return AIProviderResponse.from_orm(provider)
    except Exception as e:
        logger.error(f"Error creating provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{provider_id}", response_model=AIProviderResponse)
async def get_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get a specific AI provider by ID"""
    try:
        provider = await provider_service.get_provider(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        return AIProviderResponse.from_orm(provider)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{provider_id}", response_model=AIProviderResponse)
async def update_provider(
    provider_id: int,
    provider_data: AIProviderUpdate,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Update an existing AI provider"""
    try:
        provider = await provider_service.update_provider(provider_id, provider_data)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        return AIProviderResponse.from_orm(provider)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Delete an AI provider"""
    try:
        success = await provider_service.delete_provider(provider_id)
        if not success:
            raise HTTPException(status_code=404, detail="Provider not found")
        return {"message": "Provider deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Provider Testing Endpoints

@router.post("/{provider_id}/test", response_model=ProviderTestResult)
async def test_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Test connection to a specific AI provider"""
    try:
        result = await provider_service.test_provider_connection(provider_id)
        return result
    except Exception as e:
        logger.error(f"Error testing provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-all", response_model=BulkProviderTestResponse)
async def test_all_providers(
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Test connections to all active providers"""
    try:
        results = await provider_service.test_all_providers()
        return BulkProviderTestResponse(results=results)
    except Exception as e:
        logger.error(f"Error testing all providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model Management Endpoints

@router.get("/{provider_id}/models", response_model=List[AIProviderModelResponse])
async def list_provider_models(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get all models for a specific provider"""
    try:
        models = await provider_service.get_provider_models(provider_id)
        return [AIProviderModelResponse.from_orm(model) for model in models]
    except Exception as e:
        logger.error(f"Error listing models for provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{provider_id}/models/sync")
async def sync_provider_models(
    provider_id: int,
    background_tasks: BackgroundTasks,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Sync models from the provider's API"""
    try:
        background_tasks.add_task(provider_service.sync_provider_models, provider_id)
        return {"message": "Model sync started in background"}
    except Exception as e:
        logger.error(f"Error syncing models for provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health and Status Endpoints

@router.get("/health/status", response_model=List[ProviderHealthStatus])
async def get_providers_health(
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get health status of all providers"""
    try:
        health_status = await provider_service.get_providers_health()
        return health_status
    except Exception as e:
        logger.error(f"Error getting providers health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/report", response_model=SystemUsageReport)
async def get_usage_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get system usage report"""
    try:
        report = await provider_service.get_usage_report(start_date, end_date)
        return report
    except Exception as e:
        logger.error(f"Error generating usage report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Supported Providers Information

@router.get("/supported", response_model=List[SupportedProviderInfo])
async def get_supported_providers():
    """Get information about all supported AI providers"""
    try:
        supported_providers = [
            SupportedProviderInfo(
                provider_type="openai",
                name="OpenAI",
                description="OpenAI GPT models including GPT-4 and GPT-3.5",
                website="https://openai.com",
                documentation_url="https://platform.openai.com/docs",
                supported_features=["chat", "completion", "embeddings", "fine_tuning"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="anthropic",
                name="Anthropic",
                description="Claude AI models for safe and helpful AI assistance",
                website="https://anthropic.com",
                documentation_url="https://docs.anthropic.com",
                supported_features=["chat", "completion"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="mistral",
                name="Mistral AI",
                description="Mistral AI models for efficient and powerful language understanding",
                website="https://mistral.ai",
                documentation_url="https://docs.mistral.ai",
                supported_features=["chat", "completion", "embeddings"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="openrouter",
                name="OpenRouter",
                description="Access to 100+ AI models through a single API",
                website="https://openrouter.ai",
                documentation_url="https://openrouter.ai/docs",
                supported_features=["chat", "completion"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="ollama",
                name="Ollama",
                description="Local LLM deployment for privacy and control",
                website="https://ollama.ai",
                documentation_url="https://github.com/ollama/ollama/tree/main/docs",
                supported_features=["chat", "completion", "embeddings"],
                authentication_methods=["none"],
                pricing_model="self_hosted"
            ),
            SupportedProviderInfo(
                provider_type="groq",
                name="Groq",
                description="Lightning-fast inference for open-source models",
                website="https://groq.com",
                documentation_url="https://console.groq.com/docs",
                supported_features=["chat", "completion"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="huggingface",
                name="Hugging Face",
                description="Access to thousands of open-source models",
                website="https://huggingface.co",
                documentation_url="https://huggingface.co/docs",
                supported_features=["chat", "completion", "embeddings", "custom_models"],
                authentication_methods=["api_key"],
                pricing_model="freemium"
            )
        ]
        return supported_providers
    except Exception as e:
        logger.error(f"Error getting supported providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Information

@router.get("/system/info")
async def get_system_info():
    """Get system information and statistics"""
    try:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": "catalyst-ai-backend",
            "version": "2.0.0",
            "status": "operational",
            "supported_providers": 7,
            "features": {
                "multi_provider_support": True,
                "dynamic_model_sync": True,
                "health_monitoring": True,
                "usage_analytics": True,
                "cost_optimization": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
