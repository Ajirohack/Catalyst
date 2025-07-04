"""
Enhanced AI Provider Service
Comprehensive service for managing AI providers with multi-provider support
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from cryptography.fernet import Fernet
import httpx
import os

try:
    from database.models import (
        AIProvider, AIProviderModel, AIUsageLog,
        ProviderType, ModelType, ProviderStatus
    )
    from schemas.ai_provider_schemas_enhanced import (
        AIProviderCreate, AIProviderUpdate, AIProviderResponse,
        AIProviderModelCreate, AIProviderModelUpdate, AIProviderModelResponse,
        ProviderTestRequest, ProviderTestResult, BulkProviderTestResponse,
        AIRequest, AIResponse, UsageMetrics, SystemUsageReport,
        ProviderHealthStatus, SupportedProviderInfo, AuthType
    )
    from services.enhanced_llm_router import EnhancedLLMRouter
except ImportError as e:
    logging.warning(f"Import error in AI Provider Service: {e}")

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        # In production, this should be stored securely (e.g., environment variable, key management service)
        self.key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        if isinstance(self.key, str):
            self.key = self.key.encode()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

class AIProviderService:
    """Enhanced service for managing AI providers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption_service = EncryptionService()
        self.llm_router = None
        self.supported_providers = self._get_supported_providers()
        
        # Initialize LLM router
        try:
            self.llm_router = EnhancedLLMRouter()
        except Exception as e:
            logger.warning(f"Failed to initialize LLM router: {e}")
    
    def _get_supported_providers(self) -> Dict[str, SupportedProviderInfo]:
        """Get information about supported providers"""
        return {
            ProviderType.OPENAI: SupportedProviderInfo(
                provider_type=ProviderType.OPENAI,
                name="OpenAI",
                description="OpenAI's GPT models and services",
                documentation_url="https://platform.openai.com/docs/api-reference",
                supported_models=["gpt-4-turbo-preview", "gpt-4", "gpt-4-32k", "gpt-3.5-turbo-0125", "gpt-3.5-turbo", "text-embedding-ada-002"],
                capabilities=["chat", "completion", "embedding", "function_calling", "vision"],
                auth_methods=[AuthType.BEARER],
                default_base_url="https://api.openai.com/v1",
                supports_dynamic_models=True
            ),
            ProviderType.ANTHROPIC: SupportedProviderInfo(
                provider_type=ProviderType.ANTHROPIC,
                name="Anthropic",
                description="Anthropic's Claude models",
                documentation_url="https://docs.anthropic.com/en/api/",
                supported_models=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                capabilities=["chat", "completion", "function_calling", "vision"],
                auth_methods=[AuthType.API_KEY],
                default_base_url="https://api.anthropic.com",
                supports_dynamic_models=False
            ),
            ProviderType.MISTRAL: SupportedProviderInfo(
                provider_type=ProviderType.MISTRAL,
                name="Mistral AI",
                description="Mistral AI's language models",
                documentation_url="https://docs.mistral.ai/api/",
                supported_models=["open-mistral-7b", "open-mixtral-8x7b", "mistral-small", "mistral-medium", "mistral-large"],
                capabilities=["chat", "completion", "function_calling"],
                auth_methods=[AuthType.BEARER],
                default_base_url="https://api.mistral.ai/v1",
                supports_dynamic_models=True
            ),
            ProviderType.OPENROUTER: SupportedProviderInfo(
                provider_type=ProviderType.OPENROUTER,
                name="OpenRouter",
                description="Access multiple AI models through one API",
                documentation_url="https://openrouter.ai/docs/api-reference",
                supported_models=["anthropic/claude-3-opus", "openai/gpt-4", "meta-llama/llama-2-70b-chat"],
                capabilities=["chat", "completion"],
                auth_methods=[AuthType.BEARER],
                default_base_url="https://openrouter.ai/api/v1",
                supports_dynamic_models=True
            ),
            ProviderType.OLLAMA: SupportedProviderInfo(
                provider_type=ProviderType.OLLAMA,
                name="Ollama",
                description="Local AI models through Ollama",
                documentation_url="https://github.com/ollama/ollama/tree/main/docs",
                supported_models=["llama2", "mistral", "codellama", "phi"],
                capabilities=["chat", "completion"],
                auth_methods=[],  # No auth required for local Ollama
                default_base_url="http://localhost:11434",
                supports_dynamic_models=True
            ),
            ProviderType.GROQ: SupportedProviderInfo(
                provider_type=ProviderType.GROQ,
                name="Groq",
                description="Fast AI inference with Groq chips",
                documentation_url="https://console.groq.com/docs/",
                supported_models=["mixtral-8x7b-32768", "llama2-70b-4096", "llama3-70b-8192"],
                capabilities=["chat", "completion"],
                auth_methods=[AuthType.BEARER],
                default_base_url="https://api.groq.com/openai/v1",
                supports_dynamic_models=False
            ),
            ProviderType.HUGGINGFACE: SupportedProviderInfo(
                provider_type=ProviderType.HUGGINGFACE,
                name="Hugging Face",
                description="Hugging Face Inference API",
                documentation_url="https://huggingface.co/docs/inference-providers/",
                supported_models=["microsoft/DialoGPT-large", "facebook/blenderbot-400M-distill"],
                capabilities=["chat", "completion", "embedding", "classification"],
                auth_methods=[AuthType.BEARER],
                default_base_url="https://api-inference.huggingface.co/models",
                supports_dynamic_models=True
            ),
            ProviderType.GOOGLE: SupportedProviderInfo(
                provider_type=ProviderType.GOOGLE,
                name="Google Gemini",
                description="Google's Gemini multimodal AI models",
                documentation_url="https://ai.google.dev/gemini-api/docs",
                supported_models=["gemini-pro", "gemini-pro-vision", "gemini-ultra"],
                capabilities=["chat", "completion", "vision", "multimodal"],
                auth_methods=[AuthType.API_KEY],
                default_base_url="https://generativelanguage.googleapis.com/v1beta",
                supports_dynamic_models=False
            ),
            ProviderType.DEEPSEEK: SupportedProviderInfo(
                provider_type=ProviderType.DEEPSEEK,
                name="Deepseek",
                description="Deepseek's specialized AI models",
                documentation_url="https://api-docs.deepseek.com",
                supported_models=["deepseek-chat", "deepseek-coder", "deepseek-math"],
                capabilities=["chat", "completion", "code_generation", "math_reasoning"],
                auth_methods=[AuthType.BEARER],
                default_base_url="https://api.deepseek.com/v1",
                supports_dynamic_models=False
            )
        }
    
    # Provider CRUD Operations
    async def create_provider(self, provider_data: Dict[str, Any]) -> AIProvider:
        """Create a new AI provider"""
        try:
            # Validate provider type
            provider_type = provider_data.get("provider_type")
            if provider_type not in self.supported_providers:
                raise ValueError(f"Unsupported provider type: {provider_type}")
            
            # Check if provider already exists
            existing = self.db.query(AIProvider).filter(
                AIProvider.provider_type == provider_type
            ).first()
            if existing:
                raise ValueError(f"Provider {provider_type} already exists")
            
            # Encrypt API key
            api_key = provider_data.pop("api_key", None)
            encrypted_api_key = None
            if api_key:
                encrypted_api_key = self.encryption_service.encrypt(api_key)
            
            # Create provider
            provider = AIProvider(
                api_key_encrypted=encrypted_api_key,
                status=ProviderStatus.INACTIVE,
                **provider_data
            )
            
            self.db.add(provider)
            self.db.commit()
            self.db.refresh(provider)
            
            # If supports dynamic models, try to fetch them
            if provider.supports_dynamic_models and provider.model_list_endpoint:
                await self._fetch_dynamic_models(provider)
            
            logger.info(f"Created AI provider: {provider.name}")
            return provider
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create provider: {e}")
            raise
    
    async def update_provider(self, provider_id: int, update_data: Dict[str, Any]) -> Optional[AIProvider]:
        """Update an existing AI provider"""
        try:
            provider = self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
            if not provider:
                return None
            
            # Handle API key update
            if "api_key" in update_data:
                api_key = update_data.pop("api_key")
                if api_key:
                    provider.api_key_encrypted = self.encryption_service.encrypt(api_key)
                else:
                    provider.api_key_encrypted = None
            
            # Update other fields
            for field, value in update_data.items():
                if hasattr(provider, field):
                    setattr(provider, field, value)
            
            provider.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(provider)
            
            logger.info(f"Updated AI provider: {provider.name}")
            return provider
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update provider {provider_id}: {e}")
            raise
    
    async def delete_provider(self, provider_id: int) -> bool:
        """Delete an AI provider"""
        try:
            provider = self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
            if not provider:
                return False
            
            self.db.delete(provider)
            self.db.commit()
            
            logger.info(f"Deleted AI provider: {provider.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete provider {provider_id}: {e}")
            raise
    
    async def get_provider(self, provider_id: int) -> Optional[AIProvider]:
        """Get a single AI provider by ID"""
        return self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    
    async def get_all_providers(self, include_inactive: bool = True) -> List[AIProvider]:
        """Get all AI providers"""
        query = self.db.query(AIProvider)
        if not include_inactive:
            query = query.filter(AIProvider.enabled == True)
        return query.order_by(AIProvider.priority, AIProvider.name).all()
    
    async def get_active_providers(self) -> List[AIProvider]:
        """Get only active and enabled providers"""
        return self.db.query(AIProvider).filter(
            and_(AIProvider.enabled == True, AIProvider.status == ProviderStatus.ACTIVE)
        ).order_by(AIProvider.priority).all()
    
    # Model Management
    async def create_model(self, model_data: Dict[str, Any]) -> AIProviderModel:
        """Create a new AI model for a provider"""
        try:
            model = AIProviderModel(**model_data)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            
            logger.info(f"Created AI model: {model.model_name}")
            return model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create model: {e}")
            raise
    
    async def update_model(self, model_id: int, update_data: Dict[str, Any]) -> Optional[AIProviderModel]:
        """Update an existing AI model"""
        try:
            model = self.db.query(AIProviderModel).filter(AIProviderModel.id == model_id).first()
            if not model:
                return None
            
            for field, value in update_data.items():
                if hasattr(model, field):
                    setattr(model, field, value)
            
            model.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(model)
            
            return model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update model {model_id}: {e}")
            raise
    
    async def get_provider_models(self, provider_id: int) -> List[AIProviderModel]:
        """Get all models for a specific provider"""
        return self.db.query(AIProviderModel).filter(
            AIProviderModel.provider_id == provider_id
        ).order_by(AIProviderModel.model_name).all()
    
    # Provider Testing and Validation
    async def test_provider(self, provider_id: int, test_request: ProviderTestRequest) -> ProviderTestResult:
        """Test a specific provider's connectivity and functionality"""
        start_time = datetime.utcnow()
        
        try:
            provider = await self.get_provider(provider_id)
            if not provider:
                raise ValueError(f"Provider {provider_id} not found")
            
            if not provider.enabled:
                raise ValueError(f"Provider {provider.name} is disabled")
            
            # Prepare test request
            ai_request = AIRequest(
                messages=[{"role": "user", "content": test_request.test_message}],
                model=provider.default_model,
                max_tokens=test_request.max_tokens,
                temperature=test_request.temperature,
                provider_preference=provider.provider_type
            )
            
            # Make test request through LLM router
            if self.llm_router:
                response = await self.llm_router.generate_response(ai_request.dict())
                
                return ProviderTestResult(
                    provider_id=provider.id,
                    provider_name=provider.name,
                    success=response.success,
                    response_time_ms=response.response_time_ms or response.latency * 1000,
                    test_message=test_request.test_message,
                    response_content=response.content,
                    error_message=None,
                    tokens_used=response.usage.get("total_tokens", 0),
                    cost=response.cost,
                    timestamp=start_time
                )
            else:
                # Fallback test without router
                return await self._basic_provider_test(provider, test_request, start_time)
                
        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return ProviderTestResult(
                provider_id=provider_id,
                provider_name=provider.name if provider else "Unknown",
                success=False,
                response_time_ms=response_time,
                test_message=test_request.test_message,
                response_content=None,
                error_message=str(e),
                tokens_used=0,
                cost=0.0,
                timestamp=start_time
            )
    
    async def test_all_providers(self, test_request: ProviderTestRequest) -> BulkProviderTestResponse:
        """Test all active providers"""
        providers = await self.get_active_providers()
        results = []
        
        # Test providers concurrently
        tasks = [
            self.test_provider(provider.id, test_request)
            for provider in providers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        valid_results = []
        for result in results:
            if isinstance(result, ProviderTestResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Provider test failed: {result}")
        
        successful = sum(1 for r in valid_results if r.success)
        failed = len(valid_results) - successful
        avg_response_time = sum(r.response_time_ms for r in valid_results) / len(valid_results) if valid_results else 0
        
        return BulkProviderTestResponse(
            results=valid_results,
            total_tested=len(valid_results),
            successful=successful,
            failed=failed,
            average_response_time=avg_response_time
        )
    
    async def _basic_provider_test(self, provider: AIProvider, test_request: ProviderTestRequest, start_time: datetime) -> ProviderTestResult:
        """Basic provider test without router"""
        try:
            api_key = None
            if provider.api_key_encrypted:
                api_key = self.encryption_service.decrypt(provider.api_key_encrypted)
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add authentication
            if provider.auth_type == AuthType.BEARER and api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider.auth_type == AuthType.API_KEY and api_key:
                headers["X-API-Key"] = api_key
            
            # Add custom headers
            if provider.custom_headers:
                headers.update(provider.custom_headers)
            
            # Prepare request payload based on provider type
            payload = self._prepare_test_payload(provider, test_request)
            
            # Make HTTP request
            async with httpx.AsyncClient(timeout=provider.timeout_seconds) as client:
                response = await client.post(
                    f"{provider.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    content = self._extract_response_content(data, provider.provider_type)
                    tokens_used = self._extract_token_usage(data)
                    
                    return ProviderTestResult(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        success=True,
                        response_time_ms=response_time,
                        test_message=test_request.test_message,
                        response_content=content,
                        error_message=None,
                        tokens_used=tokens_used,
                        cost=0.0,  # Cost calculation would require model-specific pricing
                        timestamp=start_time
                    )
                else:
                    return ProviderTestResult(
                        provider_id=provider.id,
                        provider_name=provider.name,
                        success=False,
                        response_time_ms=response_time,
                        test_message=test_request.test_message,
                        response_content=None,
                        error_message=f"HTTP {response.status_code}: {response.text}",
                        tokens_used=0,
                        cost=0.0,
                        timestamp=start_time
                    )
                    
        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return ProviderTestResult(
                provider_id=provider.id,
                provider_name=provider.name,
                success=False,
                response_time_ms=response_time,
                test_message=test_request.test_message,
                response_content=None,
                error_message=str(e),
                tokens_used=0,
                cost=0.0,
                timestamp=start_time
            )
    
    def _prepare_test_payload(self, provider: AIProvider, test_request: ProviderTestRequest) -> Dict[str, Any]:
        """Prepare test payload based on provider type"""
        base_payload = {
            "model": provider.default_model,
            "messages": [{"role": "user", "content": test_request.test_message}],
            "max_tokens": test_request.max_tokens,
            "temperature": test_request.temperature
        }
        
        # Provider-specific adjustments
        if provider.provider_type == ProviderType.OPENROUTER:
            base_payload["extra_headers"] = {
                "HTTP-Referer": "https://catalyst-ai.com",
                "X-Title": "Catalyst AI Platform"
            }
        
        return base_payload
    
    def _extract_response_content(self, data: Dict[str, Any], provider_type: str) -> str:
        """Extract response content from provider-specific response format"""
        try:
            if provider_type in [ProviderType.OPENAI, ProviderType.OPENROUTER, ProviderType.GROQ]:
                return data["choices"][0]["message"]["content"]
            elif provider_type == ProviderType.ANTHROPIC:
                return data["content"][0]["text"]
            elif provider_type == ProviderType.MISTRAL:
                return data["choices"][0]["message"]["content"]
            elif provider_type == ProviderType.OLLAMA:
                return data["message"]["content"]
            else:
                return str(data)
        except (KeyError, IndexError):
            return "Response received but content extraction failed"
    
    def _extract_token_usage(self, data: Dict[str, Any]) -> int:
        """Extract token usage from response"""
        try:
            if "usage" in data:
                return data["usage"].get("total_tokens", 0)
            return 0
        except:
            return 0
    
    # Dynamic Model Fetching
    async def _fetch_dynamic_models(self, provider: AIProvider) -> List[str]:
        """Fetch available models from provider API"""
        try:
            if not provider.model_list_endpoint:
                return []
            
            api_key = None
            if provider.api_key_encrypted:
                api_key = self.encryption_service.decrypt(provider.api_key_encrypted)
            
            headers = {}
            if provider.auth_type == AuthType.BEARER and api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider.auth_type == AuthType.API_KEY and api_key:
                headers["X-API-Key"] = api_key
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(provider.model_list_endpoint, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    models = self._parse_model_list(data, provider.provider_type)
                    
                    # Update provider's available models
                    provider.available_models = models
                    self.db.commit()
                    
                    return models
                    
        except Exception as e:
            logger.error(f"Failed to fetch models for {provider.name}: {e}")
            
        return []
    
    def _parse_model_list(self, data: Dict[str, Any], provider_type: str) -> List[str]:
        """Parse model list from provider-specific response format"""
        try:
            if provider_type == ProviderType.OPENAI:
                return [model["id"] for model in data.get("data", [])]
            elif provider_type == ProviderType.OPENROUTER:
                return [model["id"] for model in data.get("data", [])]
            elif provider_type == ProviderType.OLLAMA:
                return [model["name"] for model in data.get("models", [])]
            elif provider_type == ProviderType.HUGGINGFACE:
                # Hugging Face would require different approach
                return []
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to parse model list: {e}")
            return []
    
    # Usage Analytics
    async def get_usage_metrics(self, provider_id: Optional[int] = None, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[UsageMetrics]:
        """Get usage metrics for providers"""
        query = self.db.query(AIUsageLog)
        
        if provider_id:
            query = query.filter(AIUsageLog.provider_id == provider_id)
        
        if start_date:
            query = query.filter(AIUsageLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AIUsageLog.created_at <= end_date)
        
        # Group by provider and aggregate
        results = query.with_entities(
            AIUsageLog.provider_id,
            func.count(AIUsageLog.id).label("total_requests"),
            func.sum(AIUsageLog.input_tokens).label("total_input_tokens"),
            func.sum(AIUsageLog.output_tokens).label("total_output_tokens"),
            func.sum(AIUsageLog.cost).label("total_cost"),
            func.avg(AIUsageLog.response_time_ms).label("avg_response_time"),
            func.avg(AIUsageLog.success.cast("float")).label("success_rate")
        ).group_by(AIUsageLog.provider_id).all()
        
        metrics = []
        for result in results:
            provider = await self.get_provider(result.provider_id)
            if provider:
                metrics.append(UsageMetrics(
                    provider_id=result.provider_id,
                    provider_name=provider.name,
                    total_requests=result.total_requests or 0,
                    total_input_tokens=result.total_input_tokens or 0,
                    total_output_tokens=result.total_output_tokens or 0,
                    total_cost=float(result.total_cost or 0),
                    average_response_time=float(result.avg_response_time or 0),
                    success_rate=float(result.success_rate or 0),
                    period_start=start_date or datetime.utcnow() - timedelta(days=30),
                    period_end=end_date or datetime.utcnow()
                ))
        
        return metrics
    
    # Health Monitoring
    async def update_provider_health(self, provider_id: int, health_data: Dict[str, Any]) -> None:
        """Update provider health status"""
        try:
            provider = await self.get_provider(provider_id)
            if provider:
                provider.last_health_check = datetime.utcnow()
                provider.status = health_data.get("status", provider.status)
                provider.last_error = health_data.get("error_message")
                
                # Update performance metrics
                if "response_time" in health_data:
                    provider.average_response_time = health_data["response_time"]
                if "success_rate" in health_data:
                    provider.success_rate = health_data["success_rate"]
                
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update provider health: {e}")
    
    # Utility Methods
    async def get_supported_providers_info(self) -> List[SupportedProviderInfo]:
        """Get information about all supported providers"""
        return list(self.supported_providers.values())
    
    async def validate_provider_config(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provider configuration"""
        errors = []
        warnings = []
        
        provider_type = provider_data.get("provider_type")
        if provider_type not in self.supported_providers:
            errors.append(f"Unsupported provider type: {provider_type}")
        else:
            provider_info = self.supported_providers[provider_type]
            
            # Validate required fields
            if not provider_data.get("api_key") and provider_info.auth_methods:
                errors.append("API key is required for this provider")
            
            # Validate base URL
            base_url = provider_data.get("base_url")
            if base_url and not base_url.startswith(("http://", "https://")):
                errors.append("Base URL must start with http:// or https://")
            
            # Validate model
            default_model = provider_data.get("default_model")
            if default_model and provider_info.supported_models:
                if default_model not in provider_info.supported_models:
                    warnings.append(f"Model '{default_model}' is not in the known model list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
