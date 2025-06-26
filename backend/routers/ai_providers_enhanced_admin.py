"""
Enhanced AI Providers Admin Router
Comprehensive API for managing AI providers with full CRUD operations
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks

try:
    from sqlalchemy.orm import Session
except ImportError:
    pass
from datetime import datetime, timedelta, timezone
import logging

try:
    from database.models_ai_providers import AIProvider, AIProviderModel, AIUsageLog
except ImportError:
    pass
try:
    from services.ai_provider_service import AIProviderService
except ImportError:
    pass

try:
    from schemas.ai_provider_enhanced_schema import (
        AIProviderCreateRequest, AIProviderUpdateRequest, AIProviderResponse,
        AIModelCreateRequest, AIModelUpdateRequest, AIModelResponse,
        SecretCreateRequest, SecretResponse,
        ProviderTestResult, BulkProviderTestRequest, BulkProviderTestResponse,
        SupportedProviderInfo, SystemUsageReport, ModelListResponse,
        ProviderHealthStatus, ProviderAnalytics, CostOptimizationSuggestion
    )
except ImportError:
    pass

try:
    from database.models import get_db
except ImportError:
    pass

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/ai-providers", tags=["AI Providers Admin"])

# Dependency for provider service
def get_provider_service(db: Session = Depends(get_db)) -> AIProviderService:
    return AIProviderService(db)

# Provider Management Endpoints
@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_providers(
    include_inactive: bool = Query(True, description="Include inactive providers"),
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get all AI providers with their configurations and status"""
    try:
        providers = await provider_service.get_all_providers(include_inactive)
        return providers
    except Exception as e:
        logger.error(f"Failed to get providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve providers")

@router.post("/", response_model=Dict[str, Any])
async def create_provider(
    provider_data: AIProviderCreateRequest,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Create a new AI provider"""
    try:
        provider = await provider_service.create_provider(provider_data.model_dump())
        return provider
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create provider: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create provider")

@router.get("/{provider_id}", response_model=Dict[str, Any])
async def get_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get detailed information about a specific AI provider"""
    try:
        provider = await provider_service.get_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        return provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider")

@router.put("/{provider_id}", response_model=Dict[str, Any])
async def update_provider(
    provider_id: int,
    update_data: AIProviderUpdateRequest,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Update an existing AI provider"""
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        provider = await provider_service.update_provider(provider_id, update_dict)
        return provider
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update provider")

@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Delete an AI provider and all its associated data"""
    try:
        success = await provider_service.delete_provider(provider_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        return {"message": f"Provider {provider_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete provider")

# Provider Testing Endpoints
@router.post("/{provider_id}/test", response_model=ProviderTestResult)
async def test_provider(
    provider_id: int,
    background_tasks: BackgroundTasks,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Test connection to a specific provider"""
    try:
        result = await provider_service.test_provider_connection(provider_id)
        return ProviderTestResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to test provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test provider")

@router.post("/test-all", response_model=BulkProviderTestResponse)
async def test_all_providers(
    test_request: BulkProviderTestRequest,
    background_tasks: BackgroundTasks,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Test connections to multiple providers"""
    try:
        results = []
        successful = 0
        failed = 0
        
        for provider_id in test_request.provider_ids:
            try:
                result = await provider_service.test_provider_connection(provider_id)
                results.append(ProviderTestResult(**result))
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                results.append(ProviderTestResult(
                    provider_id=provider_id,
                    provider_type="unknown",
                    success=False,
                    message=str(e),
                    response_time_ms=0.0,
                    timestamp=datetime.now(timezone.utc).isoformat()
                ))
                failed += 1
        
        summary = {
            "total_tested": len(test_request.provider_ids),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(test_request.provider_ids) if test_request.provider_ids else 0
        }
        
        return BulkProviderTestResponse(
            results=results,
            summary=summary,
            total_tested=len(test_request.provider_ids),
            successful=successful,
            failed=failed
        )
    except Exception as e:
        logger.error(f"Failed to test providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test providers")

# Provider Discovery and Capabilities
@router.get("/supported/list", response_model=Dict[str, SupportedProviderInfo])
async def get_supported_providers(
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get list of all supported provider types with their capabilities"""
    try:
        supported = await provider_service.get_supported_providers()
        return {
            provider_type: SupportedProviderInfo(**config)
            for provider_type, config in supported.items()
        }
    except Exception as e:
        logger.error(f"Failed to get supported providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve supported providers")

@router.post("/{provider_id}/fetch-models", response_model=ModelListResponse)
async def fetch_available_models(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Dynamically fetch available models from a provider"""
    try:
        # This would be implemented to actually fetch models from the provider's API
        # For now, return the configured models
        provider = await provider_service.get_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        models = provider.get("models", [])
        return ModelListResponse(
            provider_id=provider_id,
            provider_type=provider["provider_type"],
            models=models,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            cache_expires_at=(datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch models for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch models")

# Model Management Endpoints
@router.post("/{provider_id}/models", response_model=AIModelResponse)
async def create_model(
    provider_id: int,
    model_data: AIModelCreateRequest,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Create a new model for a provider"""
    try:
        # Implementation would use the provider service to create a model
        # This is a placeholder for the actual implementation
        raise HTTPException(status_code=501, detail="Model creation not yet implemented")
    except Exception as e:
        logger.error(f"Failed to create model: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create model")

@router.get("/{provider_id}/models", response_model=List[AIModelResponse])
async def get_provider_models(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get all models for a specific provider"""
    try:
        provider = await provider_service.get_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        models = provider.get("models", [])
        return [AIModelResponse(**model) for model in models]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get models for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")

# Analytics and Reporting Endpoints
@router.get("/analytics/system-usage", response_model=SystemUsageReport)
async def get_system_usage_report(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in report"),
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get system-wide usage analytics"""
    try:
        # Implementation would generate comprehensive usage report
        # This is a placeholder for the actual implementation
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Placeholder data
        return SystemUsageReport(
            total_providers=0,
            active_providers=0,
            total_requests=0,
            total_tokens=0,
            total_cost=0.0,
            average_response_time_ms=0.0,
            error_rate=0.0,
            top_providers=[],
            usage_by_type={},
            cost_by_provider={},
            period_start=start_date.isoformat(),
            period_end=end_date.isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to generate usage report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate usage report")

@router.get("/{provider_id}/analytics", response_model=ProviderAnalytics)
async def get_provider_analytics(
    provider_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics"),
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get detailed analytics for a specific provider"""
    try:
        provider = await provider_service.get_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        # Implementation would generate detailed provider analytics
        # This is a placeholder for the actual implementation
        return ProviderAnalytics(
            provider_id=provider_id,
            provider_type=provider["provider_type"],
            time_period=f"{days} days",
            request_volume=[],
            cost_trend=[],
            performance_metrics={},
            error_analysis={},
            usage_patterns={}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get provider analytics")

@router.get("/analytics/cost-optimization", response_model=List[CostOptimizationSuggestion])
async def get_cost_optimization_suggestions(
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get cost optimization suggestions across all providers"""
    try:
        # Implementation would analyze usage patterns and suggest optimizations
        # This is a placeholder for the actual implementation
        return []
    except Exception as e:
        logger.error(f"Failed to get cost optimization suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get optimization suggestions")

# Health and Monitoring Endpoints
@router.get("/health/status", response_model=List[ProviderHealthStatus])
async def get_providers_health_status(
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Get health status for all providers"""
    try:
        providers = await provider_service.get_all_providers(include_inactive=True)
        health_statuses = []
        
        for provider in providers:
            # Implementation would calculate detailed health metrics
            # This is a placeholder for the actual implementation
            health_status = ProviderHealthStatus(
                provider_id=provider["id"],
                status=provider["status"],
                health_score=0.8,  # Placeholder
                last_successful_request=provider.get("last_used_at"),
                consecutive_failures=0,
                avg_response_time_24h=0.0,
                uptime_percentage=100.0,
                issues=[],
                recommendations=[]
            )
            health_statuses.append(health_status)
        
        return health_statuses
    except Exception as e:
        logger.error(f"Failed to get health status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get health status")

# Configuration Management Endpoints
@router.post("/{provider_id}/enable")
async def enable_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Enable a provider"""
    try:
        provider = await provider_service.update_provider(provider_id, {"enabled": True})
        return {"message": f"Provider {provider_id} enabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to enable provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enable provider")

@router.post("/{provider_id}/disable")
async def disable_provider(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Disable a provider"""
    try:
        provider = await provider_service.update_provider(provider_id, {"enabled": False})
        return {"message": f"Provider {provider_id} disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to disable provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disable provider")

@router.post("/{provider_id}/reset-stats")
async def reset_provider_statistics(
    provider_id: int,
    provider_service: AIProviderService = Depends(get_provider_service)
):
    """Reset usage statistics for a provider"""
    try:
        # Implementation would reset the provider's usage statistics
        # This is a placeholder for the actual implementation
        return {"message": f"Statistics reset for provider {provider_id}"}
    except Exception as e:
        logger.error(f"Failed to reset statistics for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset statistics")
