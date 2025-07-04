#!/usr/bin/env python3
"""
Docker Build Test Script
Tests Docker build process and configuration validation
"""

import subprocess
import sys
import json
from pathlib import Path
import yaml
import os


def run_command(cmd, capture_output=True, text=True, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=text, 
            cwd=cwd,
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"❌ Error running command: {cmd}, Error: {e}")
        return None


def test_docker_availability():
    """Test if Docker is available and running."""
    print("🔍 Testing Docker availability...")
    
    result = run_command("docker --version")
    if result and result.returncode == 0:
        print(f"✅ Docker is available: {result.stdout.strip()}")
    else:
        print("❌ Docker is not available or not running")
        return False
    
    result = run_command("docker-compose --version")
    if result and result.returncode == 0:
        print(f"✅ Docker Compose is available: {result.stdout.strip()}")
    else:
        print("❌ Docker Compose is not available")
        return False
    
    return True


def test_dockerfile_syntax():
    """Test Dockerfile syntax and best practices."""
    print("\n🔍 Testing Dockerfile syntax...")
    
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found")
        return False
    
    # Test dockerfile syntax with hadolint if available
    result = run_command("hadolint Dockerfile")
    if result:
        if result.returncode == 0:
            print("✅ Dockerfile syntax is valid (hadolint)")
        else:
            print("⚠️  Hadolint warnings found:")
            print(result.stdout)
    else:
        print("ℹ️  Hadolint not available, skipping advanced checks")
    
    # Basic syntax check
    with open("Dockerfile", 'r') as f:
        content = f.read()
        
    if "FROM" not in content:
        print("❌ No FROM instruction found")
        return False
    
    if "WORKDIR" not in content:
        print("❌ No WORKDIR instruction found")
        return False
    
    print("✅ Basic Dockerfile syntax checks passed")
    return True


def test_docker_compose_syntax():
    """Test docker-compose file syntax."""
    print("\n🔍 Testing docker-compose syntax...")
    
    compose_files = ["docker-compose.yml", "docker-compose.dev.yml"]
    
    for compose_file in compose_files:
        if not Path(compose_file).exists():
            print(f"❌ {compose_file} not found")
            continue
        
        result = run_command(f"docker-compose -f {compose_file} config --quiet")
        if result and result.returncode == 0:
            print(f"✅ {compose_file} syntax is valid")
        else:
            print(f"❌ {compose_file} has syntax errors")
            if result:
                print(result.stderr)
            return False
    
    return True


def test_requirements_validity():
    """Test that requirements.txt is valid."""
    print("\n🔍 Testing requirements.txt validity...")
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    with open("requirements.txt", 'r') as f:
        requirements = f.read()
    
    # Check for common issues
    issues = []
    lines = requirements.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '==' not in line and '>=' not in line and '~=' not in line:
            issues.append(f"Line {line_num}: No version specified for '{line}'")
    
    if issues:
        print("⚠️  Requirements.txt issues found:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ requirements.txt format looks good")
    
    return True


def test_docker_build():
    """Test Docker build process."""
    print("\n🔍 Testing Docker build process...")
    
    # Test development build
    print("Building development image...")
    result = run_command(
        "docker build --target development -t catalyst-backend:dev .", 
        capture_output=False
    )
    
    if result and result.returncode == 0:
        print("✅ Development build successful")
        dev_build_success = True
    else:
        print("❌ Development build failed")
        dev_build_success = False
    
    # Test production build
    print("\nBuilding production image...")
    result = run_command(
        "docker build --target production -t catalyst-backend:prod .", 
        capture_output=False
    )
    
    if result and result.returncode == 0:
        print("✅ Production build successful")
        prod_build_success = True
    else:
        print("❌ Production build failed")
        prod_build_success = False
    
    return dev_build_success and prod_build_success


def test_environment_files():
    """Test environment file configurations."""
    print("\n🔍 Testing environment file configurations...")
    
    env_files = [".env.docker", ".dockerignore"]
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"✅ {env_file} exists")
        else:
            print(f"❌ {env_file} missing")
            return False
    
    # Check .env.docker has required variables
    with open(".env.docker", 'r') as f:
        env_content = f.read()
    
    required_vars = [
        "API_HOST", "API_PORT", "DATABASE_URL", "REDIS_URL", 
        "SECRET_KEY", "ENVIRONMENT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ Environment files configured correctly")
    return True


def cleanup_images():
    """Clean up test images."""
    print("\n🧹 Cleaning up test images...")
    
    images = ["catalyst-backend:dev", "catalyst-backend:prod"]
    for image in images:
        result = run_command(f"docker rmi {image}", capture_output=True)
        if result and result.returncode == 0:
            print(f"✅ Removed {image}")
        else:
            print(f"ℹ️  {image} not found or already removed")


def main():
    """Run all Docker tests."""
    print("🐳 Catalyst Backend Docker Configuration Test")
    print("=" * 50)
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    tests = [
        ("Docker Availability", test_docker_availability),
        ("Dockerfile Syntax", test_dockerfile_syntax),
        ("Docker Compose Syntax", test_docker_compose_syntax),
        ("Requirements Validity", test_requirements_validity),
        ("Environment Files", test_environment_files),
        ("Docker Build", test_docker_build),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Clean up after tests
    cleanup_images()
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Docker tests passed! Container setup is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
