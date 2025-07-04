#!/usr/bin/env python3
"""
Configuration Validation Script for Catalyst AI Providers
Validates and aligns provider configurations with documentation
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    # Load .env file from the current directory
    load_dotenv(dotenv_path='.env', override=True)
    print("✅ Loaded .env file successfully")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")


class ProviderConfigValidator:
    """Validates AI provider configurations"""
    
    def __init__(self):
        self.required_configs = {
            "OpenAI": {
                "api_key": "OPENAI_API_KEY",
                "model": "OPENAI_MODEL",
                "base_url": "OPENAI_BASE_URL",
                "recommended_model": "gpt-4-turbo-preview",
                "default_base_url": "https://api.openai.com/v1"
            },
            "Anthropic": {
                "api_key": "ANTHROPIC_API_KEY", 
                "model": "ANTHROPIC_MODEL",
                "base_url": "ANTHROPIC_BASE_URL",
                "recommended_model": "claude-3-sonnet-20240229",
                "default_base_url": "https://api.anthropic.com"
            },
            "Mistral": {
                "api_key": "MISTRAL_API_KEY",
                "model": "MISTRAL_MODEL", 
                "base_url": "MISTRAL_BASE_URL",
                "recommended_model": "mistral-medium-latest",
                "default_base_url": "https://api.mistral.ai/v1"
            },
            "Groq": {
                "api_key": "GROQ_API_KEY",
                "model": "GROQ_MODEL",
                "base_url": "GROQ_BASE_URL", 
                "recommended_model": "mixtral-8x7b-32768",
                "default_base_url": "https://api.groq.com/openai/v1"
            },
            "HuggingFace": {
                "api_key": "HUGGINGFACE_API_KEY",
                "model": "HUGGINGFACE_MODEL",
                "base_url": "HUGGINGFACE_BASE_URL",
                "recommended_model": "google/gemma-7b-it", 
                "default_base_url": "https://api-inference.huggingface.co"
            },
            "Google Gemini": {
                "api_key": "GOOGLE_AI_API_KEY",
                "model": "GOOGLE_AI_MODEL",
                "base_url": "GOOGLE_AI_BASE_URL",
                "recommended_model": "gemini-pro",
                "default_base_url": "https://generativelanguage.googleapis.com/v1beta"
            },
            "OpenRouter": {
                "api_key": "OPENROUTER_API_KEY",
                "model": "OPENROUTER_MODEL",
                "base_url": "OPENROUTER_BASE_URL",
                "recommended_model": "openai/gpt-3.5-turbo",
                "default_base_url": "https://openrouter.ai/api/v1"
            },
            "Deepseek": {
                "api_key": "DEEPSEEK_API_KEY",
                "model": "DEEPSEEK_MODEL",
                "base_url": "DEEPSEEK_BASE_URL",
                "recommended_model": "deepseek-chat",
                "default_base_url": "https://api.deepseek.com/v1"
            },
            "Ollama": {
                "api_key": None,  # Ollama doesn't need API key
                "model": "OLLAMA_MODEL", 
                "base_url": "OLLAMA_BASE_URL",
                "recommended_model": "llama2",
                "default_base_url": "http://localhost:11434"
            }
        }
        
        self.issues = []
        self.suggestions = []
    
    def validate_all_providers(self) -> Tuple[List[str], List[str]]:
        """Validate all provider configurations"""
        print("🔍 Validating AI Provider Configurations...\n")
        
        for provider_name, config in self.required_configs.items():
            self._validate_provider(provider_name, config)
        
        return self.issues, self.suggestions
    
    def _validate_provider(self, provider_name: str, config: Dict[str, str]):
        """Validate a single provider configuration"""
        print(f"📋 Checking {provider_name}...")
        
        # Check API Key
        api_key_var = config.get("api_key")
        if api_key_var:
            api_key = os.getenv(api_key_var)
            placeholder_patterns = ['your-api-key-here', 'your-mistral-api-key-here', 'test-key', 'sk-test-key', 'sk-ant-test-key']
            
            if not api_key or any(pattern in api_key for pattern in placeholder_patterns):
                self.issues.append(f"❌ {provider_name}: Missing {api_key_var}")
                self.suggestions.append(f"   Set {api_key_var}=your-api-key-here")
            else:
                print(f"   ✅ API Key: {api_key_var} is set")
        else:
            print(f"   ℹ️  No API key required for {provider_name}")
        
        # Check Model Configuration
        model_var = config.get("model")
        if model_var:
            current_model = os.getenv(model_var)
            recommended_model = config.get("recommended_model")
            
            if not current_model:
                self.suggestions.append(f"   💡 {provider_name}: Set {model_var}={recommended_model}")
                print(f"   ⚠️  Model: {model_var} not set (will use default)")
            elif current_model != recommended_model:
                self.suggestions.append(f"   💡 {provider_name}: Consider updating {model_var}={recommended_model} (currently: {current_model})")
                print(f"   ⚠️  Model: {current_model} (recommended: {recommended_model})")
            else:
                print(f"   ✅ Model: {current_model}")
        
        # Check Base URL
        base_url_var = config.get("base_url")
        if base_url_var:
            current_url = os.getenv(base_url_var)
            default_url = config.get("default_base_url")
            
            if not current_url:
                print(f"   ℹ️  Base URL: Using default ({default_url})")
            else:
                print(f"   ✅ Base URL: {current_url}")
        
        print()
    
    def generate_env_template(self) -> str:
        """Generate a .env template with all recommended configurations"""
        template = "# AI Provider Configuration Template\n"
        template += "# Generated by Catalyst Configuration Validator\n\n"
        
        for provider_name, config in self.required_configs.items():
            template += f"# {provider_name} Configuration\n"
            
            if config.get("api_key"):
                template += f"{config['api_key']}=your-api-key-here\n"
            
            if config.get("model"):
                template += f"{config['model']}={config['recommended_model']}\n"
            
            if config.get("base_url"):
                template += f"# {config['base_url']}={config['default_base_url']}\n"
            
            template += "\n"
        
        return template
    
    def create_migration_guide(self) -> str:
        """Create a migration guide for updating existing configurations"""
        guide = "# Configuration Migration Guide\n\n"
        guide += "## Environment Variable Changes\n\n"
        
        # Old vs New variable names
        migrations = {
            "OPENAI_DEFAULT_MODEL": "OPENAI_MODEL",
            "ANTHROPIC_DEFAULT_MODEL": "ANTHROPIC_MODEL", 
            "MISTRAL_DEFAULT_MODEL": "MISTRAL_MODEL",
            "GROQ_DEFAULT_MODEL": "GROQ_MODEL",
            "HUGGINGFACE_DEFAULT_MODEL": "HUGGINGFACE_MODEL",
            "OLLAMA_DEFAULT_MODEL": "OLLAMA_MODEL",
            "GOOGLE_API_KEY": "GOOGLE_AI_API_KEY",
            "GOOGLE_MODEL": "GOOGLE_AI_MODEL"
        }
        
        guide += "### Variable Name Updates\n\n"
        for old_var, new_var in migrations.items():
            old_value = os.getenv(old_var)
            if old_value:
                guide += f"- `{old_var}` → `{new_var}` (current value: {old_value})\n"
            else:
                guide += f"- `{old_var}` → `{new_var}`\n"
        
        guide += "\n### Recommended Model Updates\n\n"
        model_updates = {
            "OPENAI_MODEL": ("gpt-3.5-turbo", "gpt-4-turbo-preview"),
            "GROQ_MODEL": ("llama2-70b-4096", "mixtral-8x7b-32768"),
            "HUGGINGFACE_MODEL": ("microsoft/DialoGPT-large", "google/gemma-7b-it"),
            "OPENROUTER_MODEL": ("anthropic/claude-3-opus", "openai/gpt-3.5-turbo")
        }
        
        for var, (old_model, new_model) in model_updates.items():
            current = os.getenv(var) or os.getenv(var.replace("_MODEL", "_DEFAULT_MODEL"))
            if current == old_model:
                guide += f"- `{var}`: {old_model} → {new_model} ⚠️ Update recommended\n"
            else:
                guide += f"- `{var}`: {old_model} → {new_model}\n"
        
        return guide


def main():
    """Main validation function"""
    print("🚀 Catalyst AI Provider Configuration Validator\n")
    
    validator = ProviderConfigValidator()
    issues, suggestions = validator.validate_all_providers()
    
    # Print Summary
    print("📊 Validation Summary:")
    print(f"   Issues found: {len(issues)}")
    print(f"   Suggestions: {len(suggestions)}\n")
    
    if issues:
        print("❌ Issues that need attention:")
        for issue in issues:
            print(issue)
        print()
    
    if suggestions:
        print("💡 Suggestions for optimization:")
        for suggestion in suggestions:
            print(suggestion)
        print()
    
    # Generate templates
    print("📝 Generating configuration templates...\n")
    
    # Write .env template
    env_template = validator.generate_env_template()
    with open(".env.template", "w") as f:
        f.write(env_template)
    print("✅ Generated .env.template")
    
    # Write migration guide
    migration_guide = validator.create_migration_guide()
    with open("CONFIGURATION_MIGRATION.md", "w") as f:
        f.write(migration_guide)
    print("✅ Generated CONFIGURATION_MIGRATION.md")
    
    # Final recommendations
    print("\n🎯 Next Steps:")
    print("1. Review and fix any issues listed above")
    print("2. Check .env.template for complete configuration")
    print("3. Review CONFIGURATION_MIGRATION.md for upgrade path")
    print("4. Test provider connections after updates")
    
    if issues:
        print("\n⚠️  Some providers may not work until issues are resolved!")
        sys.exit(1)
    else:
        print("\n✅ All provider configurations look good!")
        sys.exit(0)


if __name__ == "__main__":
    main()
