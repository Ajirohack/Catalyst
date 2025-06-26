"""
Enhanced AI Provider Service
Provides comprehensive management for multiple AI providers with database persistence
"""

import asyncio
import logging
import json
import httpx
import os
import base64

try:
    from typing import Dict, List, Optional, Any, Tuple
    from datetime import datetime, timedelta, timezone
    from sqlalchemy.orm import Session
    from sqlalchemy import and_, desc, func
    from cryptography.fernet import Fernet
except ImportError:
    pass

try:
    from catalyst_backend.database.models_ai_providers import AIProvider, AIProviderModel, AIUsageLog, AIProviderSecret
    from catalyst_backend.schemas.ai_provider_schema import (
        AIProviderCreateRequest, AIProviderUpdateRequest, AIProviderResponse,
        AIModelCreateRequest, AIModelUpdateRequest, AIModelResponse,
        ProviderUsageStats, SystemUsageReport
    )
    from catalyst_backend.config.ai_providers import AIProviderType
except ImportError:
    pass

try:
    from .llm_router import llm_router
except ImportError:
    pass

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        # Get encryption key from environment or generate one
        self.encryption_key = os.getenv("AI_PROVIDER_ENCRYPTION_KEY")
        if not self.encryption_key:
            # Generate a new key if none exists (store this securely in production)
            self.encryption_key = Fernet.generate_key().decode()
            logger.warning("No encryption key found, generated new key. Store this securely!")
            
        self.fernet = Fernet(self.encryption_key.encode())
    
    def encrypt(self, value: str) -> str:
        """Encrypt a string value"""
        if not value:
            return ""
        return self.fernet.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt an encrypted string value"""
        if not encrypted_value:
            return ""
        return self.fernet.decrypt(encrypted_value.encode()).decode()

class AIProviderService:
    """Enhanced service for managing AI providers with database persistence"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.encryption_service = EncryptionService()
        self._supported_providers = {
            "openai": {
                "name": "OpenAI",
                "default_base_url": "https://api.openai.com/v1",
                "auth_type": "bearer",
                "default_models": {
                    "gpt-4-turbo": {
                        "type": "chat",
                        "max_tokens": 128000,
                        "cost_input_per_1k": 0.01,
                        "cost_output_per_1k": 0.03,
                        "supports_functions": True
                    },
                    "gpt-3.5-turbo": {
                        "type": "chat",
                        "max_tokens": 16384,
                        "cost_input_per_1k": 0.0015,
                        "cost_output_per_1k": 0.002,
                        "supports_functions": True
                    }
                }
            },
            "anthropic": {
                "name": "Anthropic",
                "default_base_url": "https://api.anthropic.com",
                "auth_type": "header",
                "default_models": {
                    "claude-3-opus-20240229": {
                        "type": "chat",
                        "max_tokens": 200000,
                        "cost_input_per_1k": 0.015,
                        "cost_output_per_1k": 0.075
                    },
                    "claude-3-sonnet-20240229": {
                        "type": "chat",
                        "max_tokens": 200000,
                        "cost_input_per_1k": 0.003,
                        "cost_output_per_1k": 0.015
                    }
                }
            },
            "mistral": {
                "name": "Mistral AI",
                "default_base_url": "https://api.mistral.ai/v1",
                "auth_type": "bearer",
                "default_models": {
                    "mistral-large-latest": {
                        "type": "chat",
                        "max_tokens": 32000,
                        "cost_input_per_1k": 0.008,
                        "cost_output_per_1k": 0.024
                    },
                    "mistral-medium-latest": {
                        "type": "chat",
                        "max_tokens": 32000,
                        "cost_input_per_1k": 0.0027,
                        "cost_output_per_1k": 0.0081
                    }
                }
            },
            "openrouter": {
                "name": "OpenRouter",
                "default_base_url": "https://openrouter.ai/api/v1",
                "auth_type": "bearer",
                "default_models": {
                    "anthropic/claude-3-opus": {
                        "type": "chat",
                        "max_tokens": 200000,
                        "cost_input_per_1k": 0.015,
                        "cost_output_per_1k": 0.075
                    },
                    "openai/gpt-4-turbo": {
                        "type": "chat",
                        "max_tokens": 128000,
                        "cost_input_per_1k": 0.01,
                        "cost_output_per_1k": 0.03
                    }
                }
            },
            "ollama": {
                "name": "Ollama (Local)",
                "default_base_url": "http://localhost:11434",
                "auth_type": "none",
                "default_models": {
                    "llama2": {
                        "type": "chat",
                        "max_tokens": 4096,
                        "cost_input_per_1k": 0.0,
                        "cost_output_per_1k": 0.0
                    },
                    "codellama": {
                        "type": "chat",
                        "max_tokens": 4096,
                        "cost_input_per_1k": 0.0,
                        "cost_output_per_1k": 0.0
                    }
                }
            },
            "groq": {
                "name": "Groq",
                "default_base_url": "https://api.groq.com/openai/v1",
                "auth_type": "bearer",
                "default_models": {
                    "llama2-70b-4096": {
                        "type": "chat",
                        "max_tokens": 4096,
                        "cost_input_per_1k": 0.0007,
                        "cost_output_per_1k": 0.0008
                    },
                    "mixtral-8x7b-32768": {
                        "type": "chat",
                        "max_tokens": 32768,
                        "cost_input_per_1k": 0.0002,
                        "cost_output_per_1k": 0.0002
                    }
                }
            },
            "huggingface": {
                "name": "Hugging Face",
                "default_base_url": "https://api-inference.huggingface.co",
                "auth_type": "bearer",
                "default_models": {
                    "microsoft/DialoGPT-large": {
                        "type": "chat",
                        "max_tokens": 1024,
                        "cost_input_per_1k": 0.0,
                        "cost_output_per_1k": 0.0
                    },
                    "microsoft/DialoGPT-medium": {
                        "type": "chat",
                        "max_tokens": 1024,
                        "cost_input_per_1k": 0.0,
                        "cost_output_per_1k": 0.0
                    }
                }
            }
        }
    
    async def get_all_providers(self, include_inactive: bool = True) -> List[Dict[str, Any]]:
        """Get all AI providers with their configurations and status"""
        try:
            query = self.db.query(AIProvider)
            if not include_inactive:
                query = query.filter(AIProvider.enabled == True)
            
            providers = query.order_by(AIProvider.priority, AIProvider.name).all()
            result = []
            
            for provider in providers:
                provider_dict = provider.to_dict()
                
                # Get models for this provider
                models = self.db.query(AIProviderModel).filter(
                    AIProviderModel.provider_id == provider.id
                ).all()
                provider_dict["models"] = [model.to_dict() for model in models]
                
                # Get recent usage stats
                usage_stats = await self._get_provider_usage_stats(provider.id)
                provider_dict["usage_stats"] = usage_stats
                
                result.append(provider_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get providers: {str(e)}")
            raise
    
    async def get_provider_by_id(self, provider_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific provider by ID"""
        try:
            provider = self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
            if not provider:
                return None
            
            provider_dict = provider.to_dict()
            
            # Get models
            models = self.db.query(AIProviderModel).filter(
                AIProviderModel.provider_id == provider.id
            ).all()
            provider_dict["models"] = [model.to_dict() for model in models]
            
            # Get secrets (without values)
            secrets = self.db.query(AIProviderSecret).filter(
                AIProviderSecret.provider_id == provider.id,
                AIProviderSecret.active == True
            ).all()
            provider_dict["secrets"] = [secret.to_dict() for secret in secrets]
            
            # Get usage stats
            usage_stats = await self._get_provider_usage_stats(provider.id)
            provider_dict["usage_stats"] = usage_stats
            
            return provider_dict
            
        except Exception as e:
            logger.error(f"Failed to get provider {provider_id}: {str(e)}")
            raise
    
    async def create_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new AI provider"""
        try:
            # Validate provider type
            provider_type = provider_data.get("provider_type")
            if provider_type not in self._supported_providers:
                raise ValueError(f"Unsupported provider type: {provider_type}")
            
            # Check if provider already exists
            existing = self.db.query(AIProvider).filter(
                AIProvider.provider_type == provider_type
            ).first()
            if existing:
                raise ValueError(f"Provider {provider_type} already exists")
            
            # Get default configuration
            default_config = self._supported_providers[provider_type]
            
            # Create provider
            provider = AIProvider(
                provider_type=provider_type,
                name=provider_data.get("name", default_config["name"]),
                description=provider_data.get("description", ""),
                enabled=provider_data.get("enabled", True),
                priority=provider_data.get("priority", 1),
                base_url=provider_data.get("base_url", default_config["default_base_url"]),
                api_version=provider_data.get("api_version"),
                default_model=provider_data.get("default_model"),
                models_config=provider_data.get("models_config", {}),
                rate_limits=provider_data.get("rate_limits", {}),
                timeout_seconds=provider_data.get("timeout_seconds", 30),
                max_retries=provider_data.get("max_retries", 3),
                confidence_score=provider_data.get("confidence_score", 0.8),
                quality_rating=provider_data.get("quality_rating", 0.8),
                status="inactive"
            )
            
            self.db.add(provider)
            self.db.flush()  # Get the ID
            
            # Create default models
            default_models = default_config.get("default_models", {})
            for model_name, model_config in default_models.items():
                model = AIProviderModel(
                    provider_id=provider.id,
                    model_name=model_name,
                    model_type=model_config.get("type", "chat"),
                    max_tokens=model_config.get("max_tokens", 4096),
                    supports_functions=model_config.get("supports_functions", False),
                    supports_vision=model_config.get("supports_vision", False),
                    supports_tools=model_config.get("supports_tools", False),
                    cost_input_per_1k=model_config.get("cost_input_per_1k", 0.0),
                    cost_output_per_1k=model_config.get("cost_output_per_1k", 0.0),
                    quality_score=model_config.get("quality_score", 0.8),
                    speed_score=model_config.get("speed_score", 0.8),
                    context_window=model_config.get("context_window", model_config.get("max_tokens", 4096)),
                    enabled=True
                )
                self.db.add(model)
            
            # Set default model if not specified
            if not provider.default_model and default_models:
                provider.default_model = list(default_models.keys())[0]
            
            # Handle API key if provided
            if "api_key" in provider_data and provider_data["api_key"]:
                await self._store_api_key(provider.id, provider_data["api_key"])
            
            self.db.commit()
            
            return await self.get_provider_by_id(provider.id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create provider: {str(e)}")
            raise
    
    async def update_provider(self, provider_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing AI provider"""
        try:
            provider = self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
            if not provider:
                raise ValueError(f"Provider {provider_id} not found")
            
            # Update fields
            for field, value in update_data.items():
                if field == "api_key":
                    # Handle API key separately
                    if value:
                        await self._store_api_key(provider.id, value)
                elif hasattr(provider, field):
                    setattr(provider, field, value)
            
            provider.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            
            return await self.get_provider_by_id(provider.id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update provider {provider_id}: {str(e)}")
            raise
    
    async def delete_provider(self, provider_id: int) -> bool:
        """Delete an AI provider and all its associated data"""
        try:
            provider = self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
            if not provider:
                return False
            
            # Delete associated models
            self.db.query(AIProviderModel).filter(AIProviderModel.provider_id == provider_id).delete()
            
            # Delete associated secrets
            self.db.query(AIProviderSecret).filter(AIProviderSecret.provider_id == provider_id).delete()
            
            # Delete usage logs (optional - you might want to keep for auditing)
            # self.db.query(AIUsageLog).filter(AIUsageLog.provider_id == provider_id).delete()
            
            # Delete provider
            self.db.delete(provider)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete provider {provider_id}: {str(e)}")
            raise
    
    async def test_provider_connection(self, provider_id: int) -> Dict[str, Any]:
        """Test connection to a specific provider"""
        try:
            provider = self.db.query(AIProvider).filter(AIProvider.id == provider_id).first()
            if not provider:
                raise ValueError(f"Provider {provider_id} not found")
            
            start_time = datetime.now(timezone.utc)
            
            # Get API key
            api_key = await self._get_api_key(provider.id)
            
            # Test based on provider type
            if provider.provider_type == "ollama":
                success, message = await self._test_ollama_connection(provider.base_url)
            elif provider.provider_type in ["openai", "mistral", "groq", "openrouter"]:
                success, message = await self._test_openai_compatible_connection(
                    provider.base_url, api_key, provider.default_model
                )
            elif provider.provider_type == "anthropic":
                success, message = await self._test_anthropic_connection(
                    provider.base_url, api_key, provider.default_model
                )
            elif provider.provider_type == "huggingface":
                success, message = await self._test_huggingface_connection(
                    provider.base_url, api_key
                )
            else:
                success, message = False, f"Unsupported provider type: {provider.provider_type}"
            
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Update provider status
            provider.status = "active" if success else "error"
            provider.last_error = None if success else message
            provider.last_health_check = datetime.now(timezone.utc)
            self.db.commit()
            
            return {
                "provider_id": provider_id,
                "provider_type": provider.provider_type,
                "success": success,
                "message": message,
                "response_time_ms": response_time,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to test provider {provider_id}: {str(e)}")
            raise
    
    async def get_supported_providers(self) -> Dict[str, Any]:
        """Get list of all supported provider types with their capabilities"""
        return {
            provider_type: {
                "name": config["name"],
                "default_base_url": config["default_base_url"],
                "auth_type": config["auth_type"],
                "default_models": list(config["default_models"].keys()),
                "capabilities": {
                    "chat": True,
                    "embedding": provider_type in ["openai", "huggingface"],
                    "function_calling": provider_type in ["openai", "anthropic", "mistral"],
                    "vision": provider_type in ["openai", "anthropic"],
                    "local_deployment": provider_type == "ollama"
                }
            }
            for provider_type, config in self._supported_providers.items()
        }
    
    async def _store_api_key(self, provider_id: int, api_key: str):
        """Securely store an API key for a provider"""
        # Delete existing API key
        self.db.query(AIProviderSecret).filter(
            and_(
                AIProviderSecret.provider_id == provider_id,
                AIProviderSecret.secret_type == "api_key"
            )
        ).delete()
        
        # Store new encrypted API key
        encrypted_key = self.encryption_service.encrypt(api_key)
        secret = AIProviderSecret(
            provider_id=provider_id,
            secret_type="api_key",
            secret_name="Primary API Key",
            encrypted_value=encrypted_key,
            active=True
        )
        self.db.add(secret)
    
    async def _get_api_key(self, provider_id: int) -> Optional[str]:
        """Retrieve and decrypt API key for a provider"""
        secret = self.db.query(AIProviderSecret).filter(
            and_(
                AIProviderSecret.provider_id == provider_id,
                AIProviderSecret.secret_type == "api_key",
                AIProviderSecret.active == True
            )
        ).first()
        
        if secret:
            return self.encryption_service.decrypt(secret.encrypted_value)
        return None
    
    async def _get_provider_usage_stats(self, provider_id: int, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for a provider"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get usage stats from logs
            stats = self.db.query(
                func.count(AIUsageLog.id).label("total_requests"),
                func.sum(AIUsageLog.total_tokens).label("total_tokens"),
                func.sum(AIUsageLog.cost).label("total_cost"),
                func.avg(AIUsageLog.response_time_ms).label("avg_response_time"),
                func.count(func.nullif(AIUsageLog.success, True)).label("error_count")
            ).filter(
                and_(
                    AIUsageLog.provider_id == provider_id,
                    AIUsageLog.created_at >= cutoff_date
                )
            ).first()
            
            return {
                "total_requests": stats.total_requests or 0,
                "total_tokens": stats.total_tokens or 0,
                "total_cost": float(stats.total_cost or 0),
                "average_response_time_ms": float(stats.avg_response_time or 0),
                "error_count": stats.error_count or 0,
                "success_rate": (
                    (stats.total_requests - (stats.error_count or 0)) / stats.total_requests
                    if stats.total_requests else 1.0
                ),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats for provider {provider_id}: {str(e)}")
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "average_response_time_ms": 0.0,
                "error_count": 0,
                "success_rate": 1.0,
                "period_days": days
            }
    
    async def _test_ollama_connection(self, base_url: str) -> Tuple[bool, str]:
        """Test connection to Ollama"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}/api/tags")
                if response.status_code == 200:
                    return True, "Connection successful"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    async def _test_openai_compatible_connection(self, base_url: str, api_key: str, model: str) -> Tuple[bool, str]:
        """Test connection to OpenAI-compatible API"""
        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": model or "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1
                    }
                )
                if response.status_code in [200, 400]:  # 400 might be due to model availability
                    return True, "Connection successful"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    async def _test_anthropic_connection(self, base_url: str, api_key: str, model: str) -> Tuple[bool, str]:
        """Test connection to Anthropic API"""
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            } if api_key else {}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{base_url}/v1/messages",
                    headers=headers,
                    json={
                        "model": model or "claude-3-sonnet-20240229",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "test"}]
                    }
                )
                if response.status_code in [200, 400]:
                    return True, "Connection successful"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    async def _test_huggingface_connection(self, base_url: str, api_key: str) -> Tuple[bool, str]:
        """Test connection to Hugging Face API"""
        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{base_url}/models",
                    headers=headers
                )
                if response.status_code == 200:
                    return True, "Connection successful"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
