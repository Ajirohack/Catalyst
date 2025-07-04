#!/bin/bash

# Test script specifically for Knowledge Base tests
# This script uses a more direct approach to avoid import issues

set -e  # Exit on any error

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"
TEST_DIR="$BACKEND_DIR/tests"
REPORTS_DIR="$TEST_DIR/reports/kb"
mkdir -p "$REPORTS_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}[INFO]${NC} Running Knowledge Base tests directly"

# Set PYTHONPATH to include the backend directory
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# Run the custom test runner
echo -e "${BLUE}[INFO]${NC} Running custom test runner"
python "$TEST_DIR/test_kb_runner.py" | tee "$REPORTS_DIR/kb_test_results.log"

# Run pytest specifically for Knowledge Base tests
echo -e "${BLUE}[INFO]${NC} Running Knowledge Base tests with pytest"
python -m pytest "$TEST_DIR/test_knowledge_base.py" -v --no-header --tb=native | tee -a "$REPORTS_DIR/kb_test_results.log"

echo -e "${GREEN}[SUCCESS]${NC} Knowledge Base tests completed. Check $REPORTS_DIR for results."
