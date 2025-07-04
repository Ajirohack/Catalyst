#!/usr/bin/env python3
"""
Simple Docker Configuration Review
Reviews Docker files and prepares for containerization
"""

import os
from pathlib import Path

def analyze_docker_files():
    """Analyze Docker configuration files"""
    print("🐳 Docker Configuration Review")
    print("=" * 40)
    
    backend_path = Path(".")
    files_to_check = {
        "Dockerfile": "Main container configuration",
        "docker-compose.yml": "Production orchestration",
        "docker-compose.dev.yml": "Development orchestration", 
        ".dockerignore": "Build context optimization",
        ".env.docker": "Docker environment configuration"
    }
    
    found_files = []
    missing_files = []
    
    print("📁 Checking Docker Files:")
    for filename, description in files_to_check.items():
        filepath = backend_path / filename
        if filepath.exists():
            size = filepath.stat().st_size
            found_files.append(filename)
            print(f"✅ {filename} - {description} ({size} bytes)")
        else:
            missing_files.append(filename)
            print(f"❌ {filename} - {description} (MISSING)")
    
    print(f"\n📊 Summary:")
    print(f"✅ Found: {len(found_files)}/{len(files_to_check)} Docker files")
    print(f"❌ Missing: {len(missing_files)} files")
    
    return len(found_files) >= 4  # Need at least Dockerfile + compose files

def check_dockerfile_quality():
    """Check Dockerfile for best practices"""
    print("\n📄 Dockerfile Analysis:")
    
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found")
        return False
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    checks = {
        "Multi-stage build": "FROM" in content and " as " in content,
        "Non-root user": "USER app" in content,
        "Health check": "HEALTHCHECK" in content,
        "Python optimization": "PYTHONUNBUFFERED" in content,
        "Security practices": "groupadd" in content,
        "Production server": "gunicorn" in content,
        "Layer optimization": "COPY requirements.txt" in content
    }
    
    passed = 0
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Dockerfile Quality: {passed}/{len(checks)} checks passed")
    return passed >= len(checks) * 0.8  # 80% of checks should pass

def check_compose_configuration():
    """Check docker-compose configuration"""
    print("\n🐙 Docker Compose Analysis:")
    
    compose_files = ["docker-compose.yml", "docker-compose.dev.yml"]
    valid_composes = 0
    
    for compose_file in compose_files:
        filepath = Path(compose_file)
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Basic checks
            has_services = "services:" in content
            has_networks = "networks:" in content
            has_volumes = "volumes:" in content
            has_health_checks = "healthcheck:" in content
            
            checks_passed = sum([has_services, has_networks, has_volumes, has_health_checks])
            print(f"✅ {compose_file}: {checks_passed}/4 features configured")
            
            if checks_passed >= 3:
                valid_composes += 1
        else:
            print(f"❌ {compose_file}: Not found")
    
    return valid_composes >= 1

def check_environment_configuration():
    """Check environment file configuration"""
    print("\n🔧 Environment Configuration:")
    
    env_files = {
        ".env": "Development environment",
        ".env.docker": "Docker production environment",
        ".env.template": "Environment template"
    }
    
    configured_envs = 0
    for env_file, description in env_files.items():
        filepath = Path(env_file)
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for essential configurations
            has_api_config = "API_HOST" in content and "API_PORT" in content
            has_db_config = "DATABASE_URL" in content
            has_ai_config = "OPENAI_API_KEY" in content or "ANTHROPIC_API_KEY" in content
            
            essential_configs = sum([has_api_config, has_db_config, has_ai_config])
            print(f"✅ {env_file}: {essential_configs}/3 essential configs present")
            
            if essential_configs >= 2:
                configured_envs += 1
        else:
            print(f"❌ {env_file}: Not found")
    
    return configured_envs >= 2

def test_docker_readiness():
    """Test if Docker environment is ready"""
    print("\n🚀 Docker Readiness Test:")
    
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
            docker_available = True
        else:
            print("❌ Docker not available")
            docker_available = False
    except FileNotFoundError:
        print("❌ Docker not installed")
        docker_available = False
    
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose available: {result.stdout.strip()}")
            compose_available = True
        else:
            print("❌ Docker Compose not available")
            compose_available = False
    except FileNotFoundError:
        print("❌ Docker Compose not installed")
        compose_available = False
    
    return docker_available and compose_available

def generate_docker_summary():
    """Generate overall Docker readiness summary"""
    print("\n" + "="*50)
    print("🎯 DOCKER CONTAINERIZATION SUMMARY")
    print("="*50)
    
    # Run all checks
    docker_files_ok = analyze_docker_files()
    dockerfile_ok = check_dockerfile_quality()
    compose_ok = check_compose_configuration()
    env_ok = check_environment_configuration()
    docker_ready = test_docker_readiness()
    
    # Calculate overall score
    checks = [docker_files_ok, dockerfile_ok, compose_ok, env_ok, docker_ready]
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    print(f"\n📊 Overall Readiness: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🟢 EXCELLENT: Ready for Docker deployment!")
        recommendations = [
            "🚀 Run: docker-compose up -d",
            "📊 Monitor: docker-compose logs -f",
            "🔧 Debug: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up"
        ]
    elif passed_checks >= total_checks * 0.8:
        print("🟡 GOOD: Minor fixes needed before deployment")
        recommendations = [
            "🔧 Fix any missing configurations",
            "🧪 Test: docker build -t catalyst-backend .",
            "📋 Review environment variables"
        ]
    else:
        print("🔴 NEEDS WORK: Significant Docker setup required")
        recommendations = [
            "📄 Review Dockerfile configuration",
            "🐙 Set up docker-compose files",
            "🔧 Configure environment files",
            "🐳 Install Docker if needed"
        ]
    
    print(f"\n💡 Next Steps:")
    for rec in recommendations:
        print(f"   {rec}")
    
    return passed_checks >= total_checks * 0.8

if __name__ == "__main__":
    success = generate_docker_summary()
    
    print(f"\n🎉 Docker Analysis Complete!")
    print(f"Status: {'✅ Ready for containerization' if success else '⚠️ Needs attention'}")
