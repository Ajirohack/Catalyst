#!/usr/bin/env python3
"""
Test backend core functionality after cleanup
"""

def test_database_imports():
    """Test database models import"""
    try:
        from database.models import Base, User, Project, Analysis, AIProvider
        print("✅ Database models import successful")
        return True
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False

def test_router_imports():
    """Test router imports"""
    try:
        from routers.v1 import projects_router, analysis_router, ai_providers_router
        print("✅ Router imports successful")
        return True
    except Exception as e:
        print(f"❌ Router import failed: {e}")
        return False

def test_service_imports():
    """Test service imports"""
    try:
        from services.enhanced_llm_router import EnhancedLLMRouter
        from services.file_storage_service import FileStorageService
        print("✅ Service imports successful")
        return True
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing backend functionality after cleanup...")
    
    tests = [
        test_database_imports,
        test_router_imports,
        test_service_imports
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Backend cleanup successful.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
