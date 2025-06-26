"""AI Provider Configuration for Catalyst
Enhanced configuration system for managing multiple AI providers
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AIProviderType(str, Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    HUGGINGFACE = "huggingface"

class ModelType(str, Enum):
    """Model types for different use cases"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"

class ProviderConfig:
    """Configuration for individual AI providers"""
    
    def __init__(
        self,
        provider_type: AIProviderType,
        name: str,
        models: Dict[str, Any],
        api_key_env: str = None,
        base_url: str = None,
        default_model: str = None,
        cost_per_token: Dict[str, float] = None,
        rate_limits: Dict[str, int] = None,
        enabled: bool = True,
        priority: int = 1
    ):
        self.provider_type = provider_type
        self.name = name
        self.models = models
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.default_model = default_model
        self.cost_per_token = cost_per_token or {}
        self.rate_limits = rate_limits or {}
        self.enabled = enabled
        self.priority = priority
        
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment"""
        if self.api_key_env:
            return os.getenv(self.api_key_env)
        return None
    
    def is_available(self) -> bool:
        """Check if provider is available and configured"""
        if not self.enabled:
            return False
        
        if self.provider_type in [AIProviderType.OPENAI, AIProviderType.ANTHROPIC, AIProviderType.HUGGINGFACE]:
            return bool(self.get_api_key())
        
        return True  # Local models don't need API keys

class AIProvidersConfig(BaseSettings):
    """Main configuration for AI providers"""
    
    # Default provider settings
    default_provider: AIProviderType = Field(default=AIProviderType.OPENAI, env="DEFAULT_AI_PROVIDER")
    fallback_enabled: bool = Field(default=True, env="AI_FALLBACK_ENABLED")
    cost_tracking_enabled: bool = Field(default=True, env="AI_COST_TRACKING_ENABLED")
    usage_analytics_enabled: bool = Field(default=True, env="AI_USAGE_ANALYTICS_ENABLED")
    
    # Rate limiting and timeout settings
    global_rate_limit: int = Field(default=1000, env="AI_GLOBAL_RATE_LIMIT")  # requests per hour
    request_timeout: int = Field(default=30, env="AI_REQUEST_TIMEOUT")  # seconds
    max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    
    # Quality and performance settings
    min_confidence_threshold: float = Field(default=0.7, env="AI_MIN_CONFIDENCE_THRESHOLD")
    enable_response_caching: bool = Field(default=True, env="AI_RESPONSE_CACHING")
    cache_ttl: int = Field(default=3600, env="AI_CACHE_TTL")  # seconds
    
    # Provider confidence defaults
    openai_confidence: float = 0.9
    anthropic_confidence: float = 0.85
    local_confidence: float = 0.7
    
    # Rate limiting delays
    rate_limit_delay_ms: int = 100
    
    # Retry configuration
    retry_base_delay: int = 2  # seconds for exponential backoff
    
    # Analysis configuration settings
    analysis_max_tokens: int = 800
    analysis_temperature: float = 0.3
    communication_max_tokens: int = 600  
    communication_temperature: float = 0.2
    relationship_max_tokens: int = 700
    relationship_temperature: float = 0.2
    insights_max_tokens: int = 400
    insights_temperature: float = 0.4
    recommendations_max_tokens: int = 500
    recommendations_temperature: float = 0.3
    
    # Whisper service configuration
    whisper_max_tokens: int = 150
    whisper_temperature: float = 0.4
    whisper_coaching_max_tokens: int = 800
    whisper_coaching_temperature: float = 0.3
    whisper_improvement_max_tokens: int = 400
    whisper_improvement_temperature: float = 0.2

    model_config = {
        "env_file": ".env",
        "env_prefix": "AI_"
    }

# Provider configurations
PROVIDER_CONFIGS = {
    AIProviderType.OPENAI: ProviderConfig(
        provider_type=AIProviderType.OPENAI,
        name="OpenAI",
        api_key_env="OPENAI_API_KEY",
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        default_model="gpt-3.5-turbo",
        models={
            "gpt-4": {
                "type": ModelType.CHAT,
                "max_tokens": 8192,
                "supports_functions": True,
                "cost_per_1k_tokens": {"input": 0.03, "output": 0.06}
            },
            "gpt-4-turbo": {
                "type": ModelType.CHAT,
                "max_tokens": 128000,
                "supports_functions": True,
                "cost_per_1k_tokens": {"input": 0.01, "output": 0.03}
            },
            "gpt-3.5-turbo": {
                "type": ModelType.CHAT,
                "max_tokens": 16384,
                "supports_functions": True,
                "cost_per_1k_tokens": {"input": 0.0015, "output": 0.002}
            },
            "text-embedding-3-small": {
                "type": ModelType.EMBEDDING,
                "dimensions": 1536,
                "cost_per_1k_tokens": {"input": 0.00002, "output": 0}
            }
        },
        rate_limits={"requests_per_minute": 3500, "tokens_per_minute": 90000},
        priority=1
    ),
    
    AIProviderType.ANTHROPIC: ProviderConfig(
        provider_type=AIProviderType.ANTHROPIC,
        name="Anthropic Claude",
        api_key_env="ANTHROPIC_API_KEY",
        base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        default_model="claude-3-sonnet-20240229",
        models={
            "claude-3-opus-20240229": {
                "type": ModelType.CHAT,
                "max_tokens": 200000,
                "supports_functions": False,
                "cost_per_1k_tokens": {"input": 0.015, "output": 0.075}
            },
            "claude-3-sonnet-20240229": {
                "type": ModelType.CHAT,
                "max_tokens": 200000,
                "supports_functions": False,
                "cost_per_1k_tokens": {"input": 0.003, "output": 0.015}
            },
            "claude-3-haiku-20240307": {
                "type": ModelType.CHAT,
                "max_tokens": 200000,
                "supports_functions": False,
                "cost_per_1k_tokens": {"input": 0.00025, "output": 0.00125}
            }
        },
        rate_limits={"requests_per_minute": 1000, "tokens_per_minute": 80000},
        priority=2
    ),
    
    AIProviderType.LOCAL: ProviderConfig(
        provider_type=AIProviderType.LOCAL,
        name="Local Models",
        base_url=os.getenv("LOCAL_MODEL_BASE_URL", "http://localhost:11434"),  # Configurable Ollama URL
        default_model="llama2",
        models={
            "llama2": {
                "type": ModelType.CHAT,
                "max_tokens": 4096,
                "supports_functions": False,
                "cost_per_1k_tokens": {"input": 0, "output": 0}
            },
            "mistral": {
                "type": ModelType.CHAT,
                "max_tokens": 8192,
                "supports_functions": False,
                "cost_per_1k_tokens": {"input": 0, "output": 0}
            },
            "codellama": {
                "type": ModelType.CHAT,
                "max_tokens": 16384,
                "supports_functions": False,
                "cost_per_1k_tokens": {"input": 0, "output": 0}
            }
        },
        rate_limits={"requests_per_minute": 60, "tokens_per_minute": 10000},
        priority=3,
        enabled=False  # Disabled by default, enable when local setup is ready
    )
}

def get_provider_config(provider_type: AIProviderType) -> Optional[ProviderConfig]:
    """Get configuration for a specific provider"""
    return PROVIDER_CONFIGS.get(provider_type)

def get_available_providers() -> List[ProviderConfig]:
    """Get list of available and enabled providers"""
    available = []
    for config in PROVIDER_CONFIGS.values():
        if config.is_available():
            available.append(config)
    
    # Sort by priority
    return sorted(available, key=lambda x: x.priority)

def get_default_provider() -> Optional[ProviderConfig]:
    """Get the default provider configuration"""
    settings = AIProvidersConfig()
    default_config = get_provider_config(settings.default_provider)
    
    if default_config and default_config.is_available():
        return default_config
    
    # Fallback to first available provider
    available = get_available_providers()
    return available[0] if available else None

def validate_provider_setup() -> Dict[str, Any]:
    """Validate provider setup and return status"""
    status = {
        "providers_configured": 0,
        "providers_available": 0,
        "default_provider_available": False,
        "issues": []
    }
    
    for provider_type, config in PROVIDER_CONFIGS.items():
        status["providers_configured"] += 1
        
        if config.is_available():
            status["providers_available"] += 1
        else:
            if config.enabled:
                if config.api_key_env and not config.get_api_key():
                    status["issues"].append(f"{config.name}: Missing API key ({config.api_key_env})")
                else:
                    status["issues"].append(f"{config.name}: Configuration issue")
    
    default_config = get_default_provider()
    status["default_provider_available"] = default_config is not None
    
    if not status["default_provider_available"]:
        status["issues"].append("No default provider available")
    
    return status

# Initialize configuration
ai_config = AIProvidersConfig()

# Log configuration status on import
logger.info(f"AI Providers Configuration initialized")
logger.info(f"Default provider: {ai_config.default_provider}")
logger.info(f"Available providers: {len(get_available_providers())}")

validation_status = validate_provider_setup()
if validation_status["issues"]:
    logger.warning(f"Provider setup issues: {validation_status['issues']}")
