# Catalyst Backend Test Suite

Comprehensive test suite for the Catalyst relationship management system backend API.

## Overview

This test suite provides complete coverage for all backend endpoints and functionality, including:

- **Projects Router**: CRUD operations, filtering, pagination, goals management
- **Analysis Router**: Text analysis, file upload, WebSocket real-time features
- **Main Application**: Health checks, API status, documentation endpoints
- **Integration Tests**: End-to-end workflows and cross-service functionality
- **Performance Tests**: Load testing and response time validation
- **WebSocket Tests**: Real-time communication and connection handling

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_projects.py         # Projects router endpoint tests
├── test_analysis.py         # Analysis router endpoint tests
├── test_main.py            # Main application endpoint tests
├── test_integration.py     # Integration and workflow tests
├── requirements.txt        # Test dependencies
├── run_tests.sh           # Test runner script
├── reports/               # Generated test reports
└── README.md             # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Install test dependencies
./run_tests.sh --install-deps

# Or manually:
pip install -r requirements.txt
pip install -r ../requirements.txt  # Backend dependencies
```

### 2. Run Tests

```bash
# Run all tests with coverage
./run_tests.sh

# Quick test run (unit tests only)
./run_tests.sh --quick

# Run with verbose output
./run_tests.sh -v
```

### 3. View Reports

After running tests, reports are generated in the `reports/` directory:

- **HTML Report**: `reports/test_report.html` - Interactive test results
- **Coverage Report**: `reports/coverage/index.html` - Code coverage analysis
- **JSON Report**: `reports/test_report.json` - Machine-readable results
- **JUnit XML**: `reports/junit.xml` - CI/CD compatible format

## Test Runner Options

### Basic Usage

```bash
./run_tests.sh [OPTIONS]
```

### Available Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-u, --unit-only` | Run only unit tests |
| `-i, --integration-only` | Run only integration tests |
| `-p, --performance` | Include performance tests |
| `-w, --websocket-only` | Run only WebSocket tests |
| `-v, --verbose` | Verbose output |
| `-c, --no-coverage` | Skip coverage reporting |
| `-j, --parallel` | Run tests in parallel |
| `-f, --fail-fast` | Stop on first failure |
| `-k, --keep-reports` | Keep existing reports |
| `--install-deps` | Install test dependencies |
| `--check-deps` | Check if dependencies are installed |
| `--lint` | Run linting before tests |
| `--security` | Run security checks |
| `--quick` | Quick test run (unit tests only, no coverage) |

### Example Commands

```bash
# Run all tests with coverage (default)
./run_tests.sh

# Run only unit tests with verbose output
./run_tests.sh -u -v

# Run integration tests in parallel
./run_tests.sh -i -j

# Run performance tests (slow)
./run_tests.sh -p

# Run tests and stop on first failure
./run_tests.sh -f

# Quick development test
./run_tests.sh --quick

# Full test suite with all checks
./run_tests.sh -p -v --lint --security
```

## Manual Test Execution

You can also run tests manually using pytest:

```bash
# Change to backend directory
cd /path/to/backend

# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_projects.py

# Run specific test class
python -m pytest tests/test_projects.py::TestProjectsRouter

# Run specific test method
python -m pytest tests/test_projects.py::TestProjectsRouter::test_create_project_success

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run with markers
python -m pytest tests/ -m "unit"           # Unit tests only
python -m pytest tests/ -m "integration"    # Integration tests only
python -m pytest tests/ -m "not performance" # Exclude performance tests
python -m pytest tests/ -m "websocket"      # WebSocket tests only
```

## Test Categories

### Unit Tests

Test individual endpoints and functions in isolation:

```bash
./run_tests.sh -u
```

**Coverage:**
- Projects CRUD operations
- Analysis endpoints
- Health checks
- Error handling
- Input validation

### Integration Tests

Test complete workflows across multiple endpoints:

```bash
./run_tests.sh -i
```

**Coverage:**
- Project lifecycle (create → analyze → update → delete)
- Multi-project workflows
- Data consistency
- Error recovery
- Concurrent operations

### Performance Tests

Test system performance under load:

```bash
./run_tests.sh -p
```

**Coverage:**
- Response time validation
- Concurrent request handling
- Memory usage monitoring
- Load testing scenarios

### WebSocket Tests

Test real-time communication features:

```bash
./run_tests.sh -w
```

**Coverage:**
- Connection establishment
- Message handling
- Ping/pong mechanism
- Error handling
- Session management

## Test Data and Fixtures

The test suite uses pytest fixtures for consistent test data:

### Available Fixtures

- `client`: FastAPI test client
- `clean_database`: Clean in-memory database
- `sample_project`: Sample project data
- `sample_analysis_data`: Sample analysis request data
- `sample_conversation_file`: Sample file content
- `mock_analysis_service`: Mocked analysis service
- `mock_whisper_service`: Mocked whisper service
- `websocket_session_id`: Unique WebSocket session ID
- `performance_timer`: Timer for performance tests
- `temp_file`: Temporary file for upload tests

### Using Fixtures

```python
def test_create_project(client, sample_project, clean_database):
    """Test project creation with clean database and sample data."""
    response = client.post("/api/projects/", json=sample_project)
    assert response.status_code == 201
```

## Continuous Integration

The test suite is designed for CI/CD integration:

### GitHub Actions Example

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend/tests
        ./run_tests.sh --install-deps
    
    - name: Run tests
      run: |
        cd backend/tests
        ./run_tests.sh -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/tests/reports/coverage.xml
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'cd backend/tests && ./run_tests.sh --install-deps'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'cd backend/tests && ./run_tests.sh -v'
            }
        }
        
        stage('Publish Results') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'backend/tests/reports',
                    reportFiles: 'test_report.html',
                    reportName: 'Test Report'
                ])
                
                junit 'backend/tests/reports/junit.xml'
            }
        }
    }
}
```

## Development Workflow

### Before Committing

```bash
# Run quick tests during development
./run_tests.sh --quick

# Run full test suite before committing
./run_tests.sh -v

# Run linting and security checks
./run_tests.sh --lint --security
```

### Adding New Tests

1. **For new endpoints**: Add tests to the appropriate test file
2. **For new features**: Create integration tests in `test_integration.py`
3. **For performance-critical code**: Add performance tests with `@pytest.mark.performance`
4. **For WebSocket features**: Add tests to the WebSocket test class

### Test Naming Conventions

```python
# Test classes
class TestProjectsRouter:
    pass

# Test methods
def test_create_project_success(self):
    """Test successful project creation."""
    pass

def test_create_project_invalid_data(self):
    """Test project creation with invalid data."""
    pass

# Integration tests
def test_complete_project_lifecycle(self):
    """Test complete project lifecycle from creation to deletion."""
    pass
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH includes backend directory
   export PYTHONPATH="/path/to/backend:$PYTHONPATH"
   ```

2. **Missing Dependencies**
   ```bash
   # Install all dependencies
   ./run_tests.sh --install-deps
   ```

3. **WebSocket Connection Issues**
   ```bash
   # Run WebSocket tests separately
   ./run_tests.sh -w -v
   ```

4. **Performance Test Timeouts**
   ```bash
   # Skip performance tests during development
   ./run_tests.sh -m "not performance"
   ```

### Debug Mode

```bash
# Run with maximum verbosity
./run_tests.sh -v -f

# Run specific failing test
python -m pytest tests/test_projects.py::test_failing_test -v -s

# Run with pdb debugger
python -m pytest tests/test_projects.py::test_failing_test --pdb
```

## Coverage Goals

The test suite aims for:

- **Overall Coverage**: > 90%
- **Critical Paths**: 100% (authentication, data validation, error handling)
- **API Endpoints**: 100%
- **Business Logic**: > 95%

### Viewing Coverage

```bash
# Generate coverage report
./run_tests.sh

# Open HTML coverage report
open reports/coverage/index.html

# View coverage in terminal
python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Performance Benchmarks

Expected performance benchmarks:

- **API Response Time**: < 200ms for simple endpoints
- **Database Operations**: < 100ms for CRUD operations
- **File Upload**: < 2s for files up to 10MB
- **WebSocket Connection**: < 50ms establishment time
- **Concurrent Requests**: Handle 100+ concurrent connections

## Security Testing

The test suite includes security validation:

```bash
# Run security checks
./run_tests.sh --security
```

**Security Tests Cover:**
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- File upload security
- Rate limiting
- Authentication and authorization

## Contributing

When contributing to the test suite:

1. **Write tests first** (TDD approach)
2. **Maintain high coverage** (aim for > 90%)
3. **Use descriptive test names** and docstrings
4. **Test both success and failure cases**
5. **Include integration tests** for new features
6. **Add performance tests** for critical paths
7. **Update documentation** when adding new test categories

## Support

For questions or issues with the test suite:

1. Check this README for common solutions
2. Review test output and error messages
3. Run tests with verbose output (`-v` flag)
4. Check the generated HTML reports for detailed information
5. Consult the main project documentation

---

**Happy Testing! 🧪**