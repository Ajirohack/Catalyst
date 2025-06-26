"""
AI Providers Admin Router for Catalyst
Provides admin endpoints for managing AI providers
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
import logging

try:
    from services.llm_router import (
        llm_router, test_providers, get_system_usage_metrics,
        get_providers_status, route_analysis_request
    )
except ImportError:
    # Fallback service definitions
    def llm_router(*args, **kwargs): return {"error": "LLM router not available"}
    def test_providers(*args, **kwargs): return {"error": "Provider testing not available"}
    def get_system_usage_metrics(*args, **kwargs): return {"error": "Usage metrics not available"}
    def get_providers_status(*args, **kwargs): return {}
    async def route_analysis_request(*args, **kwargs): return {"error": "Analysis routing not available"}

try:
    from schemas.ai_provider_schema import (
        ProviderConfigSchema, ProviderStatusSchema, ProviderTestResponse,
        UsageMetrics, AIServiceStatus, RouteAnalysisRequest, RouteAnalysisResponse,
        ProviderUpdateRequest, SystemUsageReport, ProviderTestRequest
    )
except ImportError:
    # Fallback schema definitions
    from pydantic import BaseModel
    class ProviderConfigSchema(BaseModel): pass
    class ProviderStatusSchema(BaseModel): pass
    class ProviderTestResponse(BaseModel): pass
    class UsageMetrics(BaseModel): pass
    class AIServiceStatus(BaseModel): pass
    class RouteAnalysisRequest(BaseModel): pass
    class RouteAnalysisResponse(BaseModel): pass
    class ProviderUpdateRequest(BaseModel): pass
    class SystemUsageReport(BaseModel): pass
    class ProviderTestRequest(BaseModel): pass

try:
    from config.ai_providers import (
        get_available_providers, get_provider_config, AIProviderType,
        get_default_provider, validate_provider_setup
    )
except ImportError:
    # Fallback definitions
    AIProviderType = str
    def get_available_providers(): return []
    def get_provider_config(provider_id): return None
    def get_default_provider(): return None
    def validate_provider_setup(): return {"status": "error", "message": "AI providers not configured"}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/ai-providers", tags=["AI Providers Admin"])

@router.get("/", response_model=List[ProviderConfigSchema])
async def get_ai_providers():
    """Get all AI providers with their configuration and status"""
    try:
        providers = []
        available_providers = get_available_providers()
        provider_status = get_providers_status()
        usage_metrics = get_system_usage_metrics("last_24h")
        
        for provider_config in available_providers:
            provider_data = ProviderConfigSchema(
                provider_type=provider_config.provider_type,
                name=provider_config.name,
                enabled=provider_config.enabled,
                priority=provider_config.priority,
                base_url=provider_config.base_url,
                default_model=provider_config.default_model,
                models=provider_config.models,
                rate_limits=provider_config.rate_limits,
                api_key_configured=bool(provider_config.get_api_key())
            )
            
            # Add status and usage information
            provider_dict = provider_data.model_dump()
            provider_dict["status"] = provider_status.get(provider_config.provider_type, "inactive")
            provider_dict["available"] = provider_config.is_available()
            
            # Add usage metrics if available
            if provider_config.provider_type in usage_metrics:
                usage = usage_metrics[provider_config.provider_type]
                provider_dict["usage"] = {
                    "requests_count": usage.requests_count,
                    "total_tokens": usage.total_tokens,
                    "total_cost": usage.total_cost,
                    "average_response_time": usage.average_response_time,
                    "error_count": usage.error_count,
                    "last_used": usage.last_used.isoformat() if usage.last_used else None
                }
            
            providers.append(provider_dict)
        
        return providers
        
    except Exception as e:
        logger.error(f"Failed to get AI providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI providers")

@router.get("/{provider_id}", response_model=ProviderConfigSchema)
async def get_ai_provider(provider_id: AIProviderType):
    """Get detailed information about a specific AI provider"""
    try:
        provider_config = get_provider_config(provider_id)
        if not provider_config:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        return ProviderConfigSchema(
            provider_type=provider_config.provider_type,
            name=provider_config.name,
            enabled=provider_config.enabled,
            priority=provider_config.priority,
            base_url=provider_config.base_url,
            default_model=provider_config.default_model,
            models=provider_config.models,
            rate_limits=provider_config.rate_limits,
            api_key_configured=bool(provider_config.get_api_key())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider information")

@router.post("/{provider_id}/test", response_model=ProviderTestResponse)
async def test_ai_provider(provider_id: AIProviderType, test_request: Optional[ProviderTestRequest] = None):
    """Test connectivity to a specific AI provider"""
    try:
        if provider_id not in llm_router.clients:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not available")
        
        client = llm_router.clients[provider_id]
        result = await client.test_connection()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test provider {provider_id}: {str(e)}")
        return ProviderTestResponse(
            provider_type=provider_id,
            success=False,
            response_time_ms=0,
            error_message=str(e)
        )

@router.post("/test-all", response_model=List[ProviderTestResponse])
async def test_all_ai_providers():
    """Test connectivity to all available AI providers"""
    try:
        results = await test_providers()
        return results
        
    except Exception as e:
        logger.error(f"Failed to test all providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to test providers")

@router.post("/{provider_id}/toggle")
async def toggle_ai_provider(provider_id: AIProviderType):
    """Toggle provider enabled/disabled status"""
    try:
        provider_config = get_provider_config(provider_id)
        if not provider_config:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        # Toggle the enabled status (this would typically update a database)
        # For now, we'll just return a success message
        new_status = not provider_config.enabled
        
        return {
            "provider_type": provider_id,
            "enabled": new_status,
            "message": f"Provider {provider_id} {'enabled' if new_status else 'disabled'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle provider")

@router.put("/{provider_id}", response_model=ProviderConfigSchema)
async def update_ai_provider(provider_id: AIProviderType, updates: ProviderUpdateRequest):
    """Update AI provider configuration"""
    try:
        provider_config = get_provider_config(provider_id)
        if not provider_config:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        # Apply updates (this would typically update a database)
        # For now, we'll just return the current configuration
        
        return ProviderConfigSchema(
            provider_type=provider_config.provider_type,
            name=provider_config.name,
            enabled=updates.enabled if updates.enabled is not None else provider_config.enabled,
            priority=updates.priority if updates.priority is not None else provider_config.priority,
            base_url=provider_config.base_url,
            default_model=updates.default_model if updates.default_model else provider_config.default_model,
            models=provider_config.models,
            rate_limits=updates.rate_limits if updates.rate_limits else provider_config.rate_limits,
            api_key_configured=bool(provider_config.get_api_key())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update provider")

@router.get("/{provider_id}/usage", response_model=UsageMetrics)
async def get_ai_provider_usage(
    provider_id: AIProviderType,
    time_period: str = Query(default="last_24h", description="Time period for usage metrics")
):
    """Get usage metrics for a specific AI provider"""
    try:
        usage_metrics = get_system_usage_metrics(time_period)
        
        if provider_id not in usage_metrics:
            # Return empty metrics if no usage found
            return UsageMetrics(
                provider_type=provider_id,
                model="no_usage",
                requests_count=0,
                total_tokens=0,
                input_tokens=0,
                output_tokens=0,
                total_cost=0.0,
                average_response_time=0.0,
                error_count=0,
                last_used=None
            )
        
        return usage_metrics[provider_id]
        
    except Exception as e:
        logger.error(f"Failed to get usage for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage metrics")

@router.get("/status", response_model=AIServiceStatus)
async def get_ai_service_status():
    """Get overall AI service status"""
    try:
        provider_status = get_providers_status()
        available_providers = get_available_providers()
        default_provider = get_default_provider()
        
        # Create provider health checks
        provider_health = []
        for provider_type, status in provider_status.items():
            provider_health.append({
                "provider_type": provider_type,
                "healthy": status == "active",
                "last_check": datetime.now(timezone.utc),
                "uptime_percentage": 100.0 if status == "active" else 0.0
            })
        
        return AIServiceStatus(
            service_healthy=len([p for p in provider_status.values() if p == "active"]) > 0,
            active_providers=len([p for p in provider_status.values() if p == "active"]),
            total_providers=len(provider_status),
            default_provider=default_provider.provider_type if default_provider else AIProviderType.OPENAI,
            fallback_enabled=True,  # This would come from configuration
            provider_health=provider_health
        )
        
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve service status")

@router.get("/metrics", response_model=Dict[str, UsageMetrics])
async def get_ai_metrics(
    time_period: str = Query(default="last_24h", description="Time period for metrics")
):
    """Get system-wide AI usage metrics"""
    try:
        metrics = get_system_usage_metrics(time_period)
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get AI metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.get("/costs", response_model=Dict[str, Any])
async def get_ai_costs(
    time_period: str = Query(default="last_24h", description="Time period for cost analysis")
):
    """Get cost analysis across all AI providers"""
    try:
        usage_metrics = get_system_usage_metrics(time_period)
        
        total_cost = sum(metrics.total_cost for metrics in usage_metrics.values())
        total_requests = sum(metrics.requests_count for metrics in usage_metrics.values())
        total_tokens = sum(metrics.total_tokens for metrics in usage_metrics.values())
        
        cost_by_provider = {}
        for provider_type, metrics in usage_metrics.items():
            cost_by_provider[provider_type] = {
                "total_cost": metrics.total_cost,
                "requests": metrics.requests_count,
                "cost_per_request": metrics.total_cost / metrics.requests_count if metrics.requests_count > 0 else 0,
                "tokens": metrics.total_tokens,
                "cost_per_token": metrics.total_cost / metrics.total_tokens if metrics.total_tokens > 0 else 0
            }
        
        return {
            "time_period": time_period,
            "total_cost": total_cost,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
            "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0,
            "by_provider": cost_by_provider,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get cost analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cost analysis")

@router.post("/route-analysis", response_model=RouteAnalysisResponse)
async def route_analysis(request: RouteAnalysisRequest):
    """Get routing recommendation for an analysis request"""
    try:
        try:
            from schemas.ai_provider_schema import AIRequest
        except ImportError:
            pass
            
        # Convert to AIRequest format
        ai_request = AIRequest(
            messages=[{"role": "user", "content": request.content}],
            analysis_type=request.analysis_type,
            context=request.context
        )
        
        # Get routing recommendation
        routing_response = await route_analysis_request(ai_request)
        return routing_response
        
    except Exception as e:
        logger.error(f"Failed to route analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to route analysis request")

@router.get("/validation")
async def validate_ai_setup():
    """Validate AI provider setup and return detailed status"""
    try:
        validation_result = validate_provider_setup()
        
        return {
            "valid": len(validation_result["issues"]) == 0,
            "providers_configured": validation_result["providers_configured"],
            "providers_available": validation_result["providers_available"],
            "default_provider_available": validation_result["default_provider_available"],
            "issues": validation_result["issues"],
            "recommendations": [
                "Configure OpenAI API key for best performance",
                "Set up Anthropic API key for fallback",
                "Consider local models for cost savings",
                "Enable fallback mechanisms for reliability"
            ] if validation_result["issues"] else []
        }
        
    except Exception as e:
        logger.error(f"Failed to validate AI setup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate AI setup")
