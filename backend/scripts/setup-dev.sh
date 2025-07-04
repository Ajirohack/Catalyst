#!/bin/bash

# Catalyst Backend Development Setup Script
# This script sets up the development environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 Setting up Catalyst Backend development environment..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Navigate to project directory
cd "$PROJECT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data/knowledge_base/{documents,processed,temp} reports

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.enhanced.example" ]; then
        echo "📄 Creating .env file from example..."
        cp .env.enhanced.example .env
        echo "⚠️  Please update .env file with your configuration"
    else
        echo "📄 Creating basic .env file..."
        cat > .env << EOF
# Catalyst Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=DEBUG

# AI Provider API Keys (optional)
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database (optional)
# DATABASE_URL=sqlite:///./catalyst.db
EOF
    fi
else
    echo "✅ .env file already exists"
fi

# Run tests to verify setup
echo "🧪 Running basic tests..."
if command_exists pytest; then
    pytest tests/ -v --tb=short || echo "⚠️  Some tests failed, but setup is complete"
else
    echo "⚠️  pytest not available, skipping tests"
fi

# Check if server can start
echo "🚀 Testing server startup..."
timeout 10s python main.py &
SERVER_PID=$!
sleep 5

if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Server started successfully!"
else
    echo "⚠️  Server startup test failed, but setup is complete"
fi

# Clean up
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Update .env file with your configuration"
echo "3. Start development server: python main.py"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For Docker development:"
echo "1. Run: ./scripts/deploy.sh development"
echo "2. Visit http://localhost:8000"
echo ""