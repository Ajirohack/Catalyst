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
                documentation_url="https://docs.anthropic.com/en/api/",
                supported_features=["chat", "completion", "function_calling", "vision"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="mistral",
                name="Mistral AI", 
                description="Mistral AI models for efficient and powerful language understanding",
                website="https://mistral.ai",
                documentation_url="https://docs.mistral.ai/api/",
                supported_features=["chat", "completion", "embeddings", "function_calling"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="google",
                name="Google AI (Gemini)",
                description="Google's Gemini models for text and multimodal generation",
                website="https://ai.google.dev",
                documentation_url="https://ai.google.dev/gemini-api/docs",
                supported_features=["chat", "completion", "vision", "multimodal"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="deepseek",
                name="Deepseek",
                description="Deepseek's specialized models for chat, coding, and mathematics",
                website="https://deepseek.com", 
                documentation_url="https://api-docs.deepseek.com",
                supported_features=["chat", "completion", "code_generation", "math_reasoning"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="openrouter",
                name="OpenRouter",
                description="Access to 100+ AI models through a unified API interface",
                website="https://openrouter.ai",
                documentation_url="https://openrouter.ai/docs",
                supported_features=["chat", "completion", "model_routing", "cost_optimization"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="groq",
                name="Groq",
                description="Lightning-fast inference for open-source models",
                website="https://groq.com",
                documentation_url="https://console.groq.com/docs/",
                supported_features=["chat", "completion", "high_speed_inference"],
                authentication_methods=["api_key"],
                pricing_model="pay_per_use"
            ),
            SupportedProviderInfo(
                provider_type="huggingface",
                name="Hugging Face",
                description="Access to thousands of open-source models",
                website="https://huggingface.co",
                documentation_url="https://huggingface.co/docs/hub/api",
                supported_features=["chat", "completion", "embeddings", "custom_models", "inference_api"],
                authentication_methods=["api_key"],
                pricing_model="freemium"
            ),
            SupportedProviderInfo(
                provider_type="ollama",
                name="Ollama",
                description="Local LLM deployment for privacy and control",
                website="https://ollama.ai",
                documentation_url="https://github.com/ollama/ollama/tree/main/docs",
                supported_features=["chat", "completion", "embeddings", "local_deployment"],
                authentication_methods=["none"],
                pricing_model="self_hosted"
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

# OpenRouter Specific Endpoints

@router.get("/openrouter/models")
async def get_openrouter_models(
    include_pricing: bool = Query(True, description="Include pricing information"),
    include_free_only: bool = Query(False, description="Show only free models")
):
    """Get available models from OpenRouter with pricing and capability information"""
    try:
        import httpx
        
        # OpenRouter models endpoint
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            models = data.get("data", [])
            
            # Process models to match our format
            processed_models = []
            for model in models:
                model_info = {
                    "id": model.get("id"),
                    "name": model.get("name", model.get("id")),
                    "description": model.get("description", ""),
                    "context_length": model.get("context_length", 0),
                    "architecture": model.get("architecture", {}),
                    "pricing": model.get("pricing", {}),
                    "top_provider": model.get("top_provider", {}),
                    "per_request_limits": model.get("per_request_limits"),
                }
                
                # Add pricing analysis
                if include_pricing and model_info["pricing"]:
                    pricing = model_info["pricing"]
                    prompt_cost = float(pricing.get("prompt", "0"))
                    completion_cost = float(pricing.get("completion", "0"))
                    
                    model_info["is_free"] = prompt_cost == 0 and completion_cost == 0
                    model_info["cost_per_1k_input"] = prompt_cost * 1000
                    model_info["cost_per_1k_output"] = completion_cost * 1000
                else:
                    model_info["is_free"] = False
                
                # Filter by free models if requested
                if include_free_only and not model_info.get("is_free", False):
                    continue
                    
                processed_models.append(model_info)
            
            # Sort by name
            processed_models.sort(key=lambda x: x.get("name", ""))
            
            return {
                "models": processed_models,
                "total_count": len(processed_models),
                "free_models_count": len([m for m in processed_models if m.get("is_free", False)]),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "openrouter"
            }
            
    except Exception as e:
        logger.error(f"Error fetching OpenRouter models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch OpenRouter models: {str(e)}")

@router.get("/huggingface/models")
async def get_huggingface_models(
    task: str = Query("text-generation", description="Model task type"),
    limit: int = Query(20, description="Number of models to return"),
    sort: str = Query("downloads", description="Sort by downloads, likes, or created_at")
):
    """Get popular models from Hugging Face Hub"""
    try:
        import httpx
        
        # Hugging Face Hub API
        url = "https://huggingface.co/api/models"
        params = {
            "filter": task,
            "sort": sort,
            "direction": -1,
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            models = response.json()
            
            # Process models to our format
            processed_models = []
            for model in models:
                model_info = {
                    "id": model.get("id"),
                    "name": model.get("id"),
                    "description": model.get("description", ""),
                    "downloads": model.get("downloads", 0),
                    "likes": model.get("likes", 0),
                    "tags": model.get("tags", []),
                    "pipeline_tag": model.get("pipeline_tag"),
                    "library_name": model.get("library_name"),
                    "created_at": model.get("created_at"),
                    "updated_at": model.get("lastModified"),
                    "is_private": model.get("private", False),
                    "gated": model.get("gated", False)
                }
                processed_models.append(model_info)
            
            return {
                "models": processed_models,
                "total_count": len(processed_models),
                "task": task,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "huggingface"
            }
            
    except Exception as e:
        logger.error(f"Error fetching Hugging Face models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Hugging Face models: {str(e)}")

@router.get("/provider-configs")
async def get_provider_base_configs():
    """Get base configuration templates for all supported providers"""
    try:
        configs = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "auth_type": "bearer",
                "required_headers": ["Authorization"],
                "default_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "capabilities": ["chat", "completion", "embeddings", "fine_tuning"],
                "rate_limits": {"requests_per_minute": 3500, "tokens_per_minute": 90000}
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com",
                "auth_type": "api_key",
                "required_headers": ["x-api-key", "anthropic-version"],
                "default_models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                "capabilities": ["chat", "completion", "function_calling", "vision"],
                "rate_limits": {"requests_per_minute": 5, "tokens_per_minute": 4000}
            },
            "mistral": {
                "base_url": "https://api.mistral.ai/v1",
                "auth_type": "bearer",
                "required_headers": ["Authorization"],
                "default_models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
                "capabilities": ["chat", "completion", "embeddings", "function_calling"],
                "rate_limits": {"requests_per_minute": 10, "tokens_per_minute": 32000}
            },
            "google": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "auth_type": "api_key",
                "required_headers": ["X-goog-api-key"],
                "default_models": ["gemini-pro", "gemini-pro-vision", "gemini-ultra"],
                "capabilities": ["chat", "completion", "vision", "multimodal"],
                "rate_limits": {"requests_per_minute": 60, "tokens_per_minute": 40000}
            },
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "auth_type": "bearer",
                "required_headers": ["Authorization"],
                "default_models": ["deepseek-chat", "deepseek-coder", "deepseek-math"],
                "capabilities": ["chat", "completion", "code_generation", "math_reasoning"],
                "rate_limits": {"requests_per_minute": 100, "tokens_per_day": 1000000}
            },
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "auth_type": "bearer",
                "required_headers": ["Authorization", "HTTP-Referer", "X-Title"],
                "default_models": ["openai/gpt-3.5-turbo", "anthropic/claude-3-opus", "google/gemini-pro"],
                "capabilities": ["chat", "completion", "model_routing", "cost_optimization"],
                "rate_limits": {"requests_per_minute": 100, "tokens_per_day": 1000000}
            },
            "groq": {
                "base_url": "https://api.groq.com/openai/v1",
                "auth_type": "bearer",
                "required_headers": ["Authorization"],
                "default_models": ["mixtral-8x7b-32768", "llama2-70b-4096", "llama3-70b-8192"],
                "capabilities": ["chat", "completion", "high_speed_inference"],
                "rate_limits": {"requests_per_minute": 10, "tokens_per_minute": 10000}
            },
            "huggingface": {
                "base_url": "https://api-inference.huggingface.co/models",
                "auth_type": "bearer",
                "required_headers": ["Authorization"],
                "default_models": ["google/gemma-7b-it", "mistralai/Mistral-7B-Instruct-v0.2"],
                "capabilities": ["chat", "completion", "embeddings", "custom_models", "inference_api"],
                "rate_limits": {"requests_per_minute": 1000, "compute_time_per_month": 30000}
            },
            "ollama": {
                "base_url": "http://localhost:11434",
                "auth_type": "none",
                "required_headers": [],
                "default_models": ["llama2", "codellama", "mistral"],
                "capabilities": ["chat", "completion", "embeddings", "local_deployment"],
                "rate_limits": {"note": "No rate limits for local deployment"}
            }
        }
        
        return {
            "provider_configs": configs,
            "total_providers": len(configs),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting provider configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
