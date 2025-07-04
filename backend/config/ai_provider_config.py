"""
AI Provider Configuration Utility
Provides default configurations for all supported AI providers
"""

import os
from typing import Dict, Optional
from services.enhanced_llm_router import ProviderConfig, AIProviderType

def get_default_provider_configs() -> Dict[str, ProviderConfig]:
    """Get default configurations for all supported providers"""
    
    configs = {}
    
    # OpenAI Configuration
    if os.getenv("OPENAI_API_KEY"):
        configs[AIProviderType.OPENAI] = ProviderConfig(
            provider_type=AIProviderType.OPENAI,
            name="OpenAI",
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY"),
            default_model="gpt-4-turbo-preview",
            enabled=True,
            priority=1,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=3500,
            confidence_score=0.9
        )
    
    # Anthropic Configuration  
    if os.getenv("ANTHROPIC_API_KEY"):
        configs[AIProviderType.ANTHROPIC] = ProviderConfig(
            provider_type=AIProviderType.ANTHROPIC,
            name="Anthropic Claude",
            base_url="https://api.anthropic.com",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            default_model="claude-3-sonnet-20240229",
            enabled=True,
            priority=2,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=60,
            confidence_score=0.9
        )
    
    # Mistral AI Configuration
    if os.getenv("MISTRAL_API_KEY"):
        configs[AIProviderType.MISTRAL] = ProviderConfig(
            provider_type=AIProviderType.MISTRAL,
            name="Mistral AI",
            base_url="https://api.mistral.ai/v1",
            api_key=os.getenv("MISTRAL_API_KEY"),
            default_model="mistral-small",
            enabled=True,
            priority=3,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=60,
            confidence_score=0.8
        )
    
    # OpenRouter Configuration
    if os.getenv("OPENROUTER_API_KEY"):
        configs[AIProviderType.OPENROUTER] = ProviderConfig(
            provider_type=AIProviderType.OPENROUTER,
            name="OpenRouter",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_model="openai/gpt-3.5-turbo",
            enabled=True,
            priority=4,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=100,
            confidence_score=0.85
        )
    
    # Groq Configuration
    if os.getenv("GROQ_API_KEY"):
        configs[AIProviderType.GROQ] = ProviderConfig(
            provider_type=AIProviderType.GROQ,
            name="Groq",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            default_model="mixtral-8x7b-32768",
            enabled=True,
            priority=5,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=30,
            confidence_score=0.8
        )
    
    # HuggingFace Configuration
    if os.getenv("HUGGINGFACE_API_KEY"):
        configs[AIProviderType.HUGGINGFACE] = ProviderConfig(
            provider_type=AIProviderType.HUGGINGFACE,
            name="HuggingFace",
            base_url="https://api-inference.huggingface.co/models",
            api_key=os.getenv("HUGGINGFACE_API_KEY"),
            default_model="google/gemma-7b-it",
            enabled=True,
            priority=6,
            timeout=60,  # HF models can take time to load
            max_retries=3,
            rate_limit_rpm=100,
            confidence_score=0.7
        )
    
    # Google Gemini Configuration
    if os.getenv("GOOGLE_AI_API_KEY"):
        configs[AIProviderType.GEMINI] = ProviderConfig(
            provider_type=AIProviderType.GEMINI,
            name="Google Gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key=os.getenv("GOOGLE_AI_API_KEY"),
            default_model="gemini-pro",
            enabled=True,
            priority=7,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=60,
            confidence_score=0.85
        )
    
    # Deepseek Configuration
    if os.getenv("DEEPSEEK_API_KEY"):
        configs[AIProviderType.DEEPSEEK] = ProviderConfig(
            provider_type=AIProviderType.DEEPSEEK,
            name="Deepseek",
            base_url="https://api.deepseek.com/v1",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            default_model="deepseek-chat",
            enabled=True,
            priority=8,
            timeout=30,
            max_retries=3,
            rate_limit_rpm=100,
            confidence_score=0.75
        )
    
    return configs

def get_provider_models() -> Dict[str, list]:
    """Get available models for each provider"""
    
    return {
        AIProviderType.OPENAI: [
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview", 
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        AIProviderType.ANTHROPIC: [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ],
        AIProviderType.MISTRAL: [
            "open-mistral-7b",
            "open-mixtral-8x7b",
            "mistral-small",
            "mistral-medium", 
            "mistral-large"
        ],
        AIProviderType.GROQ: [
            "mixtral-8x7b-32768",
            "llama2-70b-4096",
            "llama3-70b-8192"
        ],
        AIProviderType.GEMINI: [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-ultra"
        ],
        AIProviderType.DEEPSEEK: [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-math"
        ],
        AIProviderType.HUGGINGFACE: [
            "google/gemma-7b-it",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "microsoft/DialoGPT-large",
            "meta-llama/Llama-2-7b-chat-hf",
            "bigcode/starcoder"
        ]
    }

def validate_provider_config(config: ProviderConfig) -> tuple[bool, str]:
    """Validate a provider configuration"""
    
    if not config.api_key and config.provider_type != AIProviderType.HUGGINGFACE:
        return False, f"API key required for {config.provider_type}"
    
    if not config.base_url:
        return False, f"Base URL required for {config.provider_type}"
    
    if not config.default_model:
        return False, f"Default model required for {config.provider_type}"
    
    # Validate base URLs match expected patterns
    expected_urls = {
        AIProviderType.OPENAI: "https://api.openai.com/v1",
        AIProviderType.ANTHROPIC: "https://api.anthropic.com",
        AIProviderType.MISTRAL: "https://api.mistral.ai/v1",
        AIProviderType.OPENROUTER: "https://openrouter.ai/api/v1",
        AIProviderType.GROQ: "https://api.groq.com/openai/v1",
        AIProviderType.HUGGINGFACE: "https://api-inference.huggingface.co/models",
        AIProviderType.GEMINI: "https://generativelanguage.googleapis.com/v1beta",
        AIProviderType.DEEPSEEK: "https://api.deepseek.com/v1"
    }
    
    if config.provider_type in expected_urls:
        if not config.base_url.startswith(expected_urls[config.provider_type]):
            return False, f"Unexpected base URL for {config.provider_type}. Expected: {expected_urls[config.provider_type]}"
    
    return True, "Configuration valid"

def get_environment_template() -> str:
    """Get environment variable template for all providers"""
    
    return """
# AI Provider Configuration Template
# Copy this to your .env file and fill in your API keys

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Configuration  
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_VERSION=2023-06-01

# Mistral AI Configuration
MISTRAL_API_KEY=your-mistral-api-key-here
MISTRAL_MODEL=mistral-small

# OpenRouter Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_DEFAULT_MODEL=openai/gpt-3.5-turbo
OPENROUTER_APP_NAME=Catalyst AI Platform
OPENROUTER_APP_URL=https://github.com/your-repo

# Groq Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=mixtral-8x7b-32768

# HuggingFace Configuration (API key optional for public models)
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
HUGGINGFACE_MODEL=google/gemma-7b-it

# Google Gemini Configuration
GOOGLE_AI_API_KEY=your-google-ai-api-key-here
GOOGLE_AI_MODEL=gemini-pro

# Deepseek Configuration
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat
"""
