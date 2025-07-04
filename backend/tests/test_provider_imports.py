#!/usr/bin/env python3
"""Test AI provider service imports"""

print("Testing AI provider service imports...")

try:
    from database.models import ProviderType
    print("✅ ProviderType import successful")
    print(f"Available providers: {[p.value for p in ProviderType]}")
except Exception as e:
    print(f"❌ ProviderType import failed: {e}")

try:
    from schemas.ai_provider_schemas_enhanced import AuthType, SupportedProviderInfo
    print("✅ Schema imports successful")
except Exception as e:
    print(f"❌ Schema imports failed: {e}")

try:
    from services.ai_provider_service_enhanced import AIProviderService
    print("✅ AI Provider Service import successful")
except Exception as e:
    print(f"❌ AI Provider Service import failed: {e}")
    import traceback
    traceback.print_exc()
