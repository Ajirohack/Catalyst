#!/bin/bash
# setup_test_env.sh
# This script sets up the environment for running tests

# Get the absolute path to the backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Export PYTHONPATH
export PYTHONPATH=$BACKEND_DIR:$PYTHONPATH

echo "PYTHONPATH has been set to include: $BACKEND_DIR"
echo "You can now run tests with: pytest tests/"
