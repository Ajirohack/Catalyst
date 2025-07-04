#!/usr/bin/env python3
"""
AI Provider Configuration Validator and Tester
Validates all AI provider configurations and tests API connectivity
"""

import os
import asyncio
import httpx
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProviderConfig:
    name: str
    api_key_env: str
    base_url_env: str
    model_env: str
    required: bool = True
    test_endpoint: Optional[str] = None

# Define all provider configurations
PROVIDERS = {
    "openai": ProviderConfig(
        name="OpenAI",
        api_key_env="OPENAI_API_KEY",
        base_url_env="OPENAI_BASE_URL",
        model_env="OPENAI_MODEL",
        test_endpoint="https://api.openai.com/v1/models"
    ),
    "anthropic": ProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY", 
        base_url_env="ANTHROPIC_BASE_URL",
        model_env="ANTHROPIC_MODEL",
        test_endpoint="https://api.anthropic.com/v1/messages"
    ),
    "google_ai": ProviderConfig(
        name="Google AI (Gemini)",
        api_key_env="GOOGLE_AI_API_KEY",
        base_url_env="GOOGLE_AI_BASE_URL", 
        model_env="GOOGLE_AI_MODEL",
        test_endpoint="https://generativelanguage.googleapis.com/v1beta/models"
    ),
    "mistral": ProviderConfig(
        name="Mistral AI",
        api_key_env="MISTRAL_API_KEY",
        base_url_env="MISTRAL_BASE_URL",
        model_env="MISTRAL_MODEL",
        test_endpoint="https://api.mistral.ai/v1/models"
    ),
    "deepseek": ProviderConfig(
        name="Deepseek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL", 
        model_env="DEEPSEEK_MODEL",
        test_endpoint="https://api.deepseek.com/v1/models"
    ),
    "openrouter": ProviderConfig(
        name="OpenRouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url_env="OPENROUTER_BASE_URL",
        model_env="OPENROUTER_MODEL", 
        test_endpoint="https://openrouter.ai/api/v1/models"
    ),
    "groq": ProviderConfig(
        name="Groq",
        api_key_env="GROQ_API_KEY",
        base_url_env="GROQ_BASE_URL",
        model_env="GROQ_MODEL",
        test_endpoint="https://api.groq.com/openai/v1/models"
    ),
    "huggingface": ProviderConfig(
        name="HuggingFace",
        api_key_env="HUGGINGFACE_API_KEY",
        base_url_env="HUGGINGFACE_BASE_URL",
        model_env="HUGGINGFACE_MODEL",
        required=False  # Optional provider
    ),
    "ollama": ProviderConfig(
        name="Ollama (Local)",
        api_key_env="OLLAMA_API_KEY",  # Not needed but kept for consistency
        base_url_env="OLLAMA_BASE_URL",
        model_env="OLLAMA_MODEL",
        required=False,  # Optional local provider
        test_endpoint="http://localhost:11434/api/tags"
    )
}

def validate_environment_variables() -> Tuple[List[str], List[str], List[str]]:
    """Validate all environment variables for AI providers"""
    configured = []
    missing = []
    warnings = []
    
    print("🔍 Validating AI Provider Environment Variables...")
    print("=" * 60)
    
    for provider_id, config in PROVIDERS.items():
        print(f"\n📡 {config.name}:")
        
        # Check API key
        api_key = os.getenv(config.api_key_env)
        base_url = os.getenv(config.base_url_env)
        model = os.getenv(config.model_env)
        
        if provider_id == "ollama":
            # Ollama doesn't need API key
            if base_url and model:
                print(f"  ✅ Base URL: {base_url}")
                print(f"  ✅ Model: {model}")
                configured.append(config.name)
            else:
                if config.required:
                    missing.append(f"{config.name}: Missing base URL or model")
                else:
                    warnings.append(f"{config.name}: Optional provider not configured")
        else:
            # Regular API providers
            if api_key and not api_key.startswith("sk-test") and not api_key.startswith("your-"):
                print(f"  ✅ API Key: {api_key[:8]}...")
                print(f"  ✅ Base URL: {base_url or 'Using default'}")
                print(f"  ✅ Model: {model or 'Using default'}")
                configured.append(config.name)
            elif api_key and (api_key.startswith("sk-test") or api_key.startswith("your-")):
                warnings.append(f"{config.name}: Using test/placeholder API key")
                print(f"  ⚠️  API Key: Test/placeholder key detected")
            else:
                if config.required:
                    missing.append(f"{config.name}: Missing API key ({config.api_key_env})")
                    print(f"  ❌ API Key: Missing ({config.api_key_env})")
                else:
                    warnings.append(f"{config.name}: Optional provider not configured")
                    print(f"  ⚠️  API Key: Optional provider not configured")
    
    return configured, missing, warnings

async def test_provider_connectivity() -> Dict[str, bool]:
    """Test connectivity to configured providers"""
    print("\\n\\n🌐 Testing Provider Connectivity...")
    print("=" * 60)
    
    results = {}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for provider_id, config in PROVIDERS.items():
            if not config.test_endpoint:
                continue
                
            api_key = os.getenv(config.api_key_env)
            
            # Skip if no API key (except for Ollama)
            if provider_id != "ollama" and not api_key:
                results[config.name] = False
                continue
            
            print(f"\\n🔗 Testing {config.name}...")
            
            try:
                headers = {}
                
                # Set appropriate headers for each provider
                if provider_id == "openai":
                    headers["Authorization"] = f"Bearer {api_key}"
                elif provider_id == "anthropic":
                    headers["Authorization"] = f"Bearer {api_key}"
                    headers["anthropic-version"] = "2023-06-01"
                elif provider_id == "google_ai":
                    # Google AI uses query parameter
                    test_url = f"{config.test_endpoint}?key={api_key}"
                elif provider_id == "mistral":
                    headers["Authorization"] = f"Bearer {api_key}"
                elif provider_id == "deepseek":
                    headers["Authorization"] = f"Bearer {api_key}"
                elif provider_id == "openrouter":
                    headers["Authorization"] = f"Bearer {api_key}"
                    headers["HTTP-Referer"] = os.getenv("OPENROUTER_APP_URL", "https://github.com/catalyst-ai")
                    headers["X-Title"] = os.getenv("OPENROUTER_APP_NAME", "Catalyst AI")
                elif provider_id == "groq":
                    headers["Authorization"] = f"Bearer {api_key}"
                elif provider_id == "huggingface":
                    headers["Authorization"] = f"Bearer {api_key}"
                
                # Make test request
                if provider_id == "google_ai":
                    response = await client.get(test_url)
                else:
                    response = await client.get(config.test_endpoint, headers=headers)
                
                if response.status_code in [200, 401, 403]:
                    # 401/403 means the endpoint exists but auth might be wrong
                    print(f"  ✅ Endpoint reachable (Status: {response.status_code})")
                    results[config.name] = True
                else:
                    print(f"  ❌ Unexpected status: {response.status_code}")
                    results[config.name] = False
                    
            except Exception as e:
                print(f"  ❌ Connection failed: {str(e)}")
                results[config.name] = False
    
    return results

def generate_configuration_report(configured: List[str], missing: List[str], warnings: List[str], connectivity: Dict[str, bool]):
    """Generate a comprehensive configuration report"""
    print("\\n\\n📊 Configuration Report")
    print("=" * 60)
    
    print(f"\\n✅ Configured Providers ({len(configured)}):")
    for provider in configured:
        connectivity_status = "🟢 Online" if connectivity.get(provider, False) else "🔴 Offline"
        print(f"  • {provider} - {connectivity_status}")
    
    if warnings:
        print(f"\\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")
    
    if missing:
        print(f"\\n❌ Missing Required Configurations ({len(missing)}):")
        for item in missing:
            print(f"  • {item}")
    
    # Configuration recommendations
    print("\\n💡 Recommendations:")
    if missing:
        print("  • Add missing API keys to your .env file")
        print("  • Obtain API keys from the respective provider websites")
    
    if any("test" in warning.lower() or "placeholder" in warning.lower() for warning in warnings):
        print("  • Replace test/placeholder API keys with real ones for production use")
    
    print("  • Test connectivity to ensure providers are working correctly")
    print("  • Consider setting up Ollama for local AI processing")
    
    # Summary score
    total_providers = len(PROVIDERS)
    working_providers = len([p for p in configured if connectivity.get(p, False)])
    score = (working_providers / total_providers) * 100
    
    print(f"\\n🎯 Configuration Score: {score:.1f}% ({working_providers}/{total_providers} providers working)")
    
    if score >= 80:
        print("🟢 Excellent configuration!")
    elif score >= 60:
        print("🟡 Good configuration, minor improvements needed")
    elif score >= 40:
        print("🟠 Fair configuration, several providers need attention")
    else:
        print("🔴 Poor configuration, significant setup required")

async def main():
    """Main validation function"""
    print("🤖 Catalyst AI Provider Configuration Validator")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Step 1: Validate environment variables
    configured, missing, warnings = validate_environment_variables()
    
    # Step 2: Test connectivity
    connectivity = await test_provider_connectivity()
    
    # Step 3: Generate report
    generate_configuration_report(configured, missing, warnings, connectivity)
    
    # Step 4: Show next steps
    print("\\n🚀 Next Steps:")
    print("  1. Review the configuration report above")
    print("  2. Add missing API keys to your .env file")
    print("  3. Test your configuration with actual AI requests")
    print("  4. Run this validator again to verify improvements")
    
    return len(missing) == 0 and len([p for p in configured if connectivity.get(p, False)]) > 0

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\nValidation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\\n\\nValidation failed with error: {e}")
        exit(1)
