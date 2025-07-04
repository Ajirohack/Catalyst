#!/bin/bash

# Catalyst Backend Test Suite
# Comprehensive testing script for the backend API

set -e  # Exit on any error

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"
TEST_DIR="$BACKEND_DIR/tests"
REPORTS_DIR="$TEST_DIR/reports"
REQUIREMENTS_FILE="$TEST_DIR/requirements.txt"
BACKEND_REQUIREMENTS="$BACKEND_DIR/requirements.txt"
VENV_DIR="$BACKEND_DIR/venv"
COVERAGE_DIR="$REPORTS_DIR/coverage"
HTML_REPORT="$REPORTS_DIR/test_report.html"
JSON_REPORT="$REPORTS_DIR/test_report.json"
COVERAGE_REPORT="$COVERAGE_DIR/index.html"
JUNIT_REPORT="$REPORTS_DIR/junit.xml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
RUN_UNIT=true
RUN_INTEGRATION=true
FIX_IMPORTS=true

# Fix import paths
if [ "$FIX_IMPORTS" = true ]; then
    echo -e "${BLUE}[INFO]${NC} Setting up test environment with proper import paths..."
    # Ensure our backend directory is in PYTHONPATH
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    echo "PYTHONPATH set to: $PYTHONPATH"
fi
RUN_PERFORMANCE=false
RUN_WEBSOCKET=true
VERBOSE=false
COVERAGE=true
PARALLEL=false
FAIL_FAST=false
CLEAN_REPORTS=true

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -u, --unit-only         Run only unit tests
    -i, --integration-only  Run only integration tests
    -p, --performance       Include performance tests
    -w, --websocket-only    Run only WebSocket tests
    -v, --verbose           Verbose output
    -c, --no-coverage       Skip coverage reporting
    -j, --parallel          Run tests in parallel
    -f, --fail-fast         Stop on first failure
    -k, --keep-reports      Keep existing reports
    --install-deps          Install test dependencies
    --check-deps            Check if dependencies are installed
    --lint                  Run linting before tests
    --security              Run security checks
    --quick                 Quick test run (unit tests only, no coverage)

Examples:
    $0                      # Run all tests with coverage
    $0 -u -v               # Run unit tests with verbose output
    $0 -p -j                # Run all tests including performance, in parallel
    $0 --quick              # Quick test run
    $0 --install-deps       # Install test dependencies
EOF
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    if [ -f "$TEST_DIR/requirements.txt" ]; then
        pip install -r "$TEST_DIR/requirements.txt"
        print_success "Test dependencies installed"
    else
        print_error "Test requirements.txt not found"
        exit 1
    fi
    
    # Install main backend dependencies
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        pip install -r "$BACKEND_DIR/requirements.txt"
        print_success "Backend dependencies installed"
    else
        print_warning "Backend requirements.txt not found"
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Activate virtual environment if it exists
    if [ -d "$VENV_DIR" ]; then
        print_status "Using virtual environment: $VENV_DIR"
        source "$VENV_DIR/bin/activate"
    else
        print_warning "No virtual environment found at $VENV_DIR"
    fi
    
    local missing_deps=()
    
    # Check essential testing packages
    local required_packages=("pytest" "pytest_cov" "httpx" "fastapi")
    
    for package in "${required_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_deps+=("$package")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Run '$0 --install-deps' to install them"
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Function to run linting
run_linting() {
    print_status "Running code linting..."
    
    cd "$BACKEND_DIR"
    
    # Run flake8 if available
    if command -v flake8 &> /dev/null; then
        print_status "Running flake8..."
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
    fi
    
    # Run mypy if available
    if command -v mypy &> /dev/null; then
        print_status "Running mypy..."
        mypy . --ignore-missing-imports || true
    fi
    
    # Run bandit for security
    if command -v bandit &> /dev/null; then
        print_status "Running bandit security check..."
        bandit -r . -f json -o "$REPORTS_DIR/security_report.json" || true
    fi
}

# Function to run security checks
run_security_checks() {
    print_status "Running security checks..."
    
    cd "$BACKEND_DIR"
    
    # Check for known security vulnerabilities
    if command -v safety &> /dev/null; then
        print_status "Running safety check..."
        safety check --json --output "$REPORTS_DIR/safety_report.json" || true
    fi
    
    # Run bandit for code security issues
    if command -v bandit &> /dev/null; then
        print_status "Running bandit..."
        bandit -r . -f json -o "$REPORTS_DIR/bandit_report.json" || true
    fi
}

# Function to setup test environment
setup_test_environment() {
    print_status "Setting up test environment..."
    
    # Create reports directory
    if [ "$CLEAN_REPORTS" = true ] && [ -d "$REPORTS_DIR" ]; then
        print_status "Cleaning existing reports..."
        rm -rf "$REPORTS_DIR"
    fi
    
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$COVERAGE_DIR"
    
    # Set environment variables for testing
    export TESTING=true
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    
    # Change to backend directory
    cd "$BACKEND_DIR"
}

# Function to build pytest command
build_pytest_command() {
    # Quote the PYTHONPATH to handle spaces in paths
    local cmd="PYTHONPATH=\"$BACKEND_DIR\" python -m pytest"
    
    # Add test directory
    cmd="$cmd tests/"
    
    # Add markers based on options
    local markers=()
    
    if [ "$RUN_UNIT" = true ] && [ "$RUN_INTEGRATION" = false ]; then
        markers+=("unit")
    elif [ "$RUN_INTEGRATION" = true ] && [ "$RUN_UNIT" = false ]; then
        markers+=("integration")
    fi
    
    if [ "$RUN_WEBSOCKET" = true ] && [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = false ]; then
        markers+=("websocket")
    fi
    
    if [ "$RUN_PERFORMANCE" = false ]; then
        markers+=("not performance")
    fi
    
    if [ ${#markers[@]} -gt 0 ]; then
        local marker_expr=$(IFS=" and "; echo "${markers[*]}")
        cmd="$cmd -m '$marker_expr'"
    fi
    
    # Add coverage options
    if [ "$COVERAGE" = true ]; then
        cmd="$cmd --cov=. --cov-report=html:$COVERAGE_DIR --cov-report=term --cov-report=xml:$REPORTS_DIR/coverage.xml"
    fi
    
    # Add reporting options
    cmd="$cmd --html=$HTML_REPORT --self-contained-html"
    cmd="$cmd --json-report --json-report-file=$JSON_REPORT"
    cmd="$cmd --junit-xml=$JUNIT_REPORT"
    
    # Add verbosity
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd -v"
    fi
    
    # Add parallel execution
    if [ "$PARALLEL" = true ]; then
        cmd="$cmd -n auto"
    fi
    
    # Add fail fast
    if [ "$FAIL_FAST" = true ]; then
        cmd="$cmd -x"
    fi
    
    echo "$cmd"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    local pytest_cmd=$(build_pytest_command)
    
    print_status "Executing: $pytest_cmd"
    
    if eval "$pytest_cmd"; then
        print_success "Tests completed successfully"
        return 0
    else
        print_error "Tests failed"
        return 1
    fi
}

# Function to generate summary report
generate_summary() {
    print_status "Generating test summary..."
    
    local summary_file="$REPORTS_DIR/summary.txt"
    
    cat > "$summary_file" << EOF
Catalyst Backend Test Summary
============================
Generated: $(date)
Test Directory: $TEST_DIR
Backend Directory: $BACKEND_DIR

Test Configuration:
- Unit Tests: $RUN_UNIT
- Integration Tests: $RUN_INTEGRATION
- Performance Tests: $RUN_PERFORMANCE
- WebSocket Tests: $RUN_WEBSOCKET
- Coverage Enabled: $COVERAGE
- Parallel Execution: $PARALLEL
- Verbose Output: $VERBOSE

Reports Generated:
- HTML Report: $HTML_REPORT
- JSON Report: $JSON_REPORT
- JUnit XML: $JUNIT_REPORT
- Coverage Report: $COVERAGE_REPORT

EOF
    
    if [ -f "$JSON_REPORT" ]; then
        # Extract summary from JSON report if available
        if command -v jq &> /dev/null; then
            echo "Test Results:" >> "$summary_file"
            jq -r '.summary | "- Total: \(.total)\n- Passed: \(.passed)\n- Failed: \(.failed)\n- Skipped: \(.skipped)"' "$JSON_REPORT" >> "$summary_file" 2>/dev/null || true
        fi
    fi
    
    print_success "Summary generated: $summary_file"
}

# Function to open reports
open_reports() {
    if [ -f "$HTML_REPORT" ]; then
        print_status "HTML report available: $HTML_REPORT"
        
        # Try to open in browser (macOS)
        if command -v open &> /dev/null; then
            read -p "Open HTML report in browser? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                open "$HTML_REPORT"
            fi
        fi
    fi
    
    if [ -f "$COVERAGE_REPORT" ] && [ "$COVERAGE" = true ]; then
        print_status "Coverage report available: $COVERAGE_REPORT"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -u|--unit-only)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            RUN_WEBSOCKET=false
            shift
            ;;
        -i|--integration-only)
            RUN_UNIT=false
            RUN_INTEGRATION=true
            RUN_WEBSOCKET=false
            shift
            ;;
        -p|--performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        -w|--websocket-only)
            RUN_UNIT=false
            RUN_INTEGRATION=false
            RUN_WEBSOCKET=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--no-coverage)
            COVERAGE=false
            shift
            ;;
        -j|--parallel)
            PARALLEL=true
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -k|--keep-reports)
            CLEAN_REPORTS=false
            shift
            ;;
        --install-deps)
            install_dependencies
            exit 0
            ;;
        --check-deps)
            check_dependencies
            exit 0
            ;;
        --lint)
            setup_test_environment
            run_linting
            exit 0
            ;;
        --security)
            setup_test_environment
            run_security_checks
            exit 0
            ;;
        --quick)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            RUN_PERFORMANCE=false
            RUN_WEBSOCKET=false
            COVERAGE=false
            VERBOSE=false
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting Catalyst Backend Test Suite"
    
    # Check dependencies
    check_dependencies
    
    # Setup test environment
    setup_test_environment
    
    # Run tests
    local test_result=0
    if ! run_tests; then
        test_result=1
    fi
    
    # Generate summary
    generate_summary
    
    # Open reports if tests passed
    if [ $test_result -eq 0 ]; then
        open_reports
        print_success "All tests completed successfully!"
    else
        print_error "Some tests failed. Check the reports for details."
    fi
    
    return $test_result
}

# Run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi