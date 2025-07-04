#!/bin/bash

# Catalyst Backend Deployment Script
# Usage: ./scripts/deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying Catalyst Backend to $ENVIRONMENT environment..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
if ! command_exists docker; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR"

# Environment-specific deployment
case $ENVIRONMENT in
    "development")
        echo "📦 Building development environment..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
        echo "🔄 Starting development services..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        ;;
    "production")
        echo "📦 Building production environment..."
        docker-compose --profile production build
        echo "🔄 Starting production services..."
        docker-compose --profile production up -d
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Available environments: development, production"
        exit 1
        ;;
esac

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Deployment successful! Services are healthy."
    echo "📍 API available at: http://localhost:8000"
    echo "📚 Documentation at: http://localhost:8000/docs"
else
    echo "❌ Deployment failed! Services are not responding."
    echo "📋 Checking logs..."
    docker-compose logs catalyst-backend
    exit 1
fi

echo "🎉 Deployment completed successfully!"