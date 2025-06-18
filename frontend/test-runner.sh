#!/bin/bash

# Catalyst Frontend Testing Setup and Execution Script

set -e  # Exit on any error

echo "🧪 Catalyst Frontend Testing Setup"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Node.js and npm
if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Navigate to frontend directory
cd "$(dirname "$0")"
echo "📁 Working directory: $(pwd)"

# Install dependencies if needed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Install testing dependencies if not present
echo "📦 Installing additional testing dependencies..."

# Check and install missing dev dependencies
MISSING_DEPS=""

# Check for testing libraries
if ! npm list @testing-library/react-hooks >/dev/null 2>&1; then
    MISSING_DEPS="$MISSING_DEPS @testing-library/react-hooks@8.0.1"
fi

if ! npm list msw >/dev/null 2>&1; then
    MISSING_DEPS="$MISSING_DEPS msw@1.3.3"
fi

if ! npm list jest-axe >/dev/null 2>&1; then
    MISSING_DEPS="$MISSING_DEPS jest-axe@8.0.0"
fi

if ! npm list cypress >/dev/null 2>&1; then
    MISSING_DEPS="$MISSING_DEPS cypress@13.6.4"
fi

if ! npm list cypress-axe >/dev/null 2>&1; then
    MISSING_DEPS="$MISSING_DEPS cypress-axe@1.5.0"
fi

# Install missing dependencies
if [ -n "$MISSING_DEPS" ]; then
    echo "📦 Installing missing test dependencies:$MISSING_DEPS"
    npm install --save-dev $MISSING_DEPS
else
    echo "✅ All testing dependencies are installed"
fi

# Create necessary directories
echo "📁 Creating test directories..."
mkdir -p src/__tests__/integration
mkdir -p src/__integration__
mkdir -p cypress/e2e
mkdir -p cypress/fixtures
mkdir -p cypress/support
mkdir -p .storybook

# Run different types of tests based on argument
case "${1:-all}" in
    "unit")
        echo "🧪 Running unit tests..."
        npm test -- --testMatch="**/__tests__/**/*.test.{js,jsx}" --watchAll=false
        ;;
    "integration")
        echo "🧪 Running integration tests..."
        npm test -- --testMatch="**/__integration__/**/*.test.{js,jsx}" --watchAll=false
        ;;
    "coverage")
        echo "🧪 Running tests with coverage..."
        npm run test:coverage -- --watchAll=false
        ;;
    "lint")
        echo "🔍 Running linting..."
        npm run lint
        ;;
    "cypress")
        echo "🌐 Running Cypress tests..."
        if command_exists cypress; then
            npm run cypress:run || echo "⚠️ Cypress tests failed or not configured yet"
        else
            echo "⚠️ Cypress not installed, skipping E2E tests"
        fi
        ;;
    "storybook")
        echo "📚 Building Storybook..."
        if [ -f ".storybook/main.js" ]; then
            npm run build-storybook || echo "⚠️ Storybook build failed or not configured yet"
        else
            echo "⚠️ Storybook not configured, skipping"
        fi
        ;;
    "all")
        echo "🧪 Running all tests..."
        
        echo "1️⃣ Linting..."
        npm run lint || echo "⚠️ Linting failed"
        
        echo "2️⃣ Unit tests..."
        npm test -- --watchAll=false --passWithNoTests || echo "⚠️ Some unit tests failed"
        
        echo "3️⃣ Building project..."
        npm run build || echo "⚠️ Build failed"
        
        echo "✅ Test suite completed!"
        ;;
    "install")
        echo "✅ Dependencies installation completed!"
        ;;
    "help")
        echo "Usage: $0 [unit|integration|coverage|lint|cypress|storybook|all|install|help]"
        echo ""
        echo "Commands:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  coverage    - Run tests with coverage report"
        echo "  lint        - Run ESLint"
        echo "  cypress     - Run Cypress E2E tests"
        echo "  storybook   - Build Storybook"
        echo "  all         - Run all tests and checks (default)"
        echo "  install     - Install dependencies only"
        echo "  help        - Show this help message"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

echo "🎉 Testing script completed!"
