#!/bin/bash

# Enhanced setup script for Knowledge Base integration testing
# This script ensures proper import paths and prepares the test environment

set -e  # Exit on any error

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"
TEST_DIR="$BACKEND_DIR/tests"
DATA_DIR="$BACKEND_DIR/data/test_data"
KB_TEMP_DIR="$DATA_DIR/kb_temp"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}[INFO]${NC} Setting up Knowledge Base integration test environment"

# Create necessary directories
echo -e "${BLUE}[INFO]${NC} Creating test data directories if needed"
mkdir -p "$DATA_DIR"
mkdir -p "$KB_TEMP_DIR"

# Set PYTHONPATH properly
echo -e "${BLUE}[INFO]${NC} Setting PYTHONPATH to include backend directory"
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
echo "PYTHONPATH=$PYTHONPATH"

# Generate symbolic link to help pytest resolve imports properly
if [ ! -L "$TEST_DIR/backend" ]; then
    echo -e "${BLUE}[INFO]${NC} Creating symbolic link for backend module"
    ln -sf "$BACKEND_DIR" "$TEST_DIR/backend"
fi

# Make sample test files available for document testing
if [ ! -d "$DATA_DIR/sample_docs" ]; then
    echo -e "${BLUE}[INFO]${NC} Setting up sample test documents"
    mkdir -p "$DATA_DIR/sample_docs"
    
    # Create a sample text file for testing
    echo "This is a sample document for Knowledge Base testing.
It contains information about relationship communication techniques.
Effective communication involves active listening and empathy." > "$DATA_DIR/sample_docs/sample_kb_test.txt"
    
    echo -e "${GREEN}[SUCCESS]${NC} Created sample test documents"
fi

# Install test dependencies if needed (optionally uncomment)
# pip install -r "$TEST_DIR/requirements.txt"

echo -e "${GREEN}[SUCCESS]${NC} Knowledge Base integration test environment setup complete"
echo -e "${YELLOW}[NOTE]${NC} Use run_kb_integration_tests.sh to execute the tests"
