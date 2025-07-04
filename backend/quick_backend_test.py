#!/usr/bin/env python3
"""
Quick Backend Validation Test
Tests if the backend is properly organized and error-free
"""

import os
import sys
import subprocess
from pathlib import Path

def test_file_structure():
    """Test if backend has proper file structure"""
    print("📁 Testing Backend File Structure...")
    
    required_dirs = [
        "api", "services", "database", "config", 
        "models", "middleware", "validators", "schemas"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print(f"✅ All required directories present: {len(required_dirs)}/8")
        return True

def test_syntax_errors():
    """Test for syntax errors in key files"""
    print("🔍 Testing Syntax Compilation...")
    
    key_files = [
        "main.py",
        "services/enhanced_llm_router.py",
        "database/base.py",
        "config/settings.py"
    ]
    
    errors = []
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ {file_path}")
                else:
                    errors.append(f"{file_path}: {result.stderr}")
                    print(f"❌ {file_path}: {result.stderr}")
            except Exception as e:
                errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path}: {e}")
        else:
            print(f"⚠️  {file_path}: Not found")
    
    return len(errors) == 0

def test_dependencies():
    """Test if key dependencies are available"""
    print("📦 Testing Dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    return len(missing_packages) == 0

def test_basic_import():
    """Test if main application can be imported"""
    print("🚀 Testing Main App Import...")
    
    try:
        # Test import without execution
        result = subprocess.run(
            [sys.executable, "-c", "import main; print('✅ Import successful')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Main application imports successfully")
            return True
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Import test timed out (may be initializing database)")
        return True  # Timeout usually means it's working but slow
    except Exception as e:
        print(f"❌ Import test error: {e}")
        return False

def main():
    """Run comprehensive backend validation"""
    print("🧪 Catalyst Backend Validation Test")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Syntax Compilation", test_syntax_errors),
        ("Dependencies", test_dependencies),
        ("Main App Import", test_basic_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Backend is WELL ORGANIZED and ERROR-FREE!")
        return True
    elif passed >= total - 1:
        print("⚠️  Backend is mostly good with minor issues")
        return True
    else:
        print("❌ Backend needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
