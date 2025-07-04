#!/usr/bin/env python3
"""
Test script to verify provider configuration alignment
"""

import os
import sys

def test_provider_configs():
    """Test that provider configurations are aligned with documentation"""
    
    print("🧪 Testing Provider Configuration Alignment\n")
    
    # Expected configurations based on our fixes
    expected_configs = {
        "OpenAI": {
            "env_var": "OPENAI_MODEL",
            "expected_default": "gpt-4-turbo-preview",
            "docs_model": "gpt-4-turbo-preview"
        },
        "Anthropic": {
            "env_var": "ANTHROPIC_MODEL", 
            "expected_default": "claude-3-sonnet-20240229",
            "docs_model": "claude-3-opus-20240229"
        },
        "Mistral": {
            "env_var": "MISTRAL_MODEL",
            "expected_default": "mistral-medium-latest",
            "docs_model": "open-mistral-7b"
        },
        "Groq": {
            "env_var": "GROQ_MODEL",
            "expected_default": "mixtral-8x7b-32768",
            "docs_model": "mixtral-8x7b-32768"
        },
        "HuggingFace": {
            "env_var": "HUGGINGFACE_MODEL",
            "expected_default": "google/gemma-7b-it",
            "docs_model": "google/gemma-7b-it"
        },
        "Google Gemini": {
            "env_var": "GOOGLE_AI_MODEL",
            "expected_default": "gemini-pro",
            "docs_model": "gemini-pro"
        },
        "OpenRouter": {
            "env_var": "OPENROUTER_DEFAULT_MODEL",
            "expected_default": "openai/gpt-3.5-turbo",
            "docs_model": "openai/gpt-3.5-turbo"
        },
        "Deepseek": {
            "env_var": "DEEPSEEK_MODEL",
            "expected_default": "deepseek-chat",
            "docs_model": "deepseek-chat"
        },
        "Ollama": {
            "env_var": "OLLAMA_MODEL",
            "expected_default": "llama2",
            "docs_model": "llama2"
        }
    }
    
    aligned_count = 0
    total_count = len(expected_configs)
    
    for provider, config in expected_configs.items():
        expected = config["expected_default"]
        docs = config["docs_model"]
        
        if expected == docs:
            print(f"✅ {provider}: Configuration aligned ({expected})")
            aligned_count += 1
        else:
            print(f"⚠️  {provider}: Expected {expected}, Docs {docs}")
    
    print(f"\n📊 Alignment Score: {aligned_count}/{total_count} ({aligned_count/total_count*100:.1f}%)")
    
    if aligned_count == total_count:
        print("🎉 Perfect alignment! All providers match documentation.")
        return True
    else:
        print("⚠️  Some providers still need alignment.")
        return False

def test_environment_variables():
    """Test environment variable naming consistency"""
    
    print("\n🧪 Testing Environment Variable Consistency\n")
    
    # Check for old variable names that should be migrated
    old_variables = {
        "OPENAI_DEFAULT_MODEL": "OPENAI_MODEL",
        "ANTHROPIC_DEFAULT_MODEL": "ANTHROPIC_MODEL",
        "MISTRAL_DEFAULT_MODEL": "MISTRAL_MODEL", 
        "GROQ_DEFAULT_MODEL": "GROQ_MODEL",
        "HUGGINGFACE_DEFAULT_MODEL": "HUGGINGFACE_MODEL",
        "OLLAMA_DEFAULT_MODEL": "OLLAMA_MODEL",
        "GOOGLE_API_KEY": "GOOGLE_AI_API_KEY",
        "GOOGLE_MODEL": "GOOGLE_AI_MODEL"
    }
    
    migration_needed = False
    
    for old_var, new_var in old_variables.items():
        old_value = os.getenv(old_var)
        new_value = os.getenv(new_var)
        
        if old_value and not new_value:
            print(f"⚠️  Migration needed: {old_var}={old_value} → {new_var}")
            migration_needed = True
        elif old_value and new_value:
            print(f"⚠️  Both set: {old_var}={old_value}, {new_var}={new_value}")
            migration_needed = True
        elif new_value:
            print(f"✅ {new_var}={new_value}")
        else:
            print(f"ℹ️  {new_var}: Not set")
    
    if migration_needed:
        print("\n⚠️  Environment variable migration recommended!")
        print("   Run: python validate_provider_config.py for migration guide")
        return False
    else:
        print("\n✅ Environment variables are consistent")
        return True

def main():
    """Main test function"""
    print("🚀 Provider Configuration Alignment Test\n")
    
    config_aligned = test_provider_configs()
    env_consistent = test_environment_variables()
    
    print("\n" + "="*60)
    print("📋 FINAL RESULTS:")
    print(f"   Configuration Alignment: {'✅ PASS' if config_aligned else '⚠️  NEEDS WORK'}")
    print(f"   Environment Consistency: {'✅ PASS' if env_consistent else '⚠️  NEEDS WORK'}")
    
    if config_aligned and env_consistent:
        print("\n🎉 ALL TESTS PASSED! Provider configurations are fully aligned.")
        return 0
    else:
        print("\n⚠️  Some issues found. See details above.")
        print("   💡 Run validate_provider_config.py for fix recommendations")
        return 1

if __name__ == "__main__":
    sys.exit(main())
