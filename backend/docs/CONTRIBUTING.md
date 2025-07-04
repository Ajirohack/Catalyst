# Contributing to Catalyst Backend

Thank you for your interest in contributing to the Catalyst Backend API! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Security](#security)

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful**: Treat all contributors with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together to improve the project
- **Be constructive**: Provide helpful feedback and suggestions
- **Be professional**: Maintain a professional tone in all interactions

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Docker and Docker Compose (optional but recommended)
- Basic knowledge of FastAPI, Python, and REST APIs

### First-time Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/catalyst.git
   cd catalyst/backend
   ```

2. **Set up development environment**
   ```bash
   ./scripts/setup-dev.sh
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Run tests to ensure everything works**
   ```bash
   pytest tests/ -v
   ```

## 🛠️ Development Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Start development server
python main.py
```

### Docker Development

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f catalyst-backend
```

### Environment Configuration

Ensure you have the following in your `.env` file:

```env
DEBUG=true
LOG_LEVEL=DEBUG
OPENAI_API_KEY=your_key_here  # Optional for testing
ANTHROPIC_API_KEY=your_key_here  # Optional for testing
```

## 🔄 Contributing Process

### 1. Choose an Issue

- Look for issues labeled `good first issue` for beginners
- Check `help wanted` for areas needing assistance
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 3. Make Changes

- Follow the coding standards (see below)
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Commit Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new analysis endpoint"
# or
git commit -m "fix: resolve authentication issue"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use [mypy](https://mypy.readthedocs.io/) for type checking

### Code Formatting

```bash
# Format code
black .

# Sort imports
isort .

# Check linting
flake8 .

# Type checking
mypy .
```

### Code Quality Requirements

- **Type Hints**: All functions must have type hints
- **Docstrings**: All public functions and classes must have docstrings
- **Error Handling**: Proper exception handling with meaningful messages
- **Logging**: Use structured logging for important events
- **Security**: Follow security best practices

### Example Code Style

```python
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

class ProjectResponse(BaseModel):
    """Response model for project data."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

async def get_projects(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None
) -> List[ProjectResponse]:
    """Retrieve a list of projects with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Optional user ID for filtering
        
    Returns:
        List of project responses
        
    Raises:
        HTTPException: If database error occurs
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Failed to retrieve projects: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve projects"
        )
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── conftest.py              # Test configuration
├── test_main.py             # Main application tests
├── test_projects.py         # Project endpoint tests
├── test_analysis.py         # Analysis service tests
├── test_integration.py      # Integration tests
└── fixtures/                # Test data fixtures
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies
- Aim for >80% test coverage

### Test Examples

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_project_success():
    """Test successful project creation."""
    project_data = {
        "name": "Test Project",
        "description": "A test project"
    }
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"

def test_create_project_invalid_data():
    """Test project creation with invalid data."""
    project_data = {"name": ""}  # Empty name
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_analysis_service():
    """Test analysis service functionality."""
    from services.analysis_service import AnalysisService
    
    service = AnalysisService()
    result = await service.analyze_text("Sample text")
    assert result is not None
    assert "sentiment" in result
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_projects.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run integration tests only
pytest tests/test_integration.py -v
```

## 📚 Documentation

### Code Documentation

- Use clear, descriptive docstrings
- Document all parameters and return values
- Include usage examples for complex functions
- Keep documentation up-to-date with code changes

### API Documentation

- FastAPI automatically generates OpenAPI documentation
- Add detailed descriptions to endpoint functions
- Use Pydantic models for request/response documentation
- Include example requests and responses

### README Updates

- Update README.md for new features
- Add configuration instructions
- Include usage examples
- Update installation instructions if needed

## 🔍 Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
   ```bash
   pytest tests/ -v
   ```

2. **Check code quality**
   ```bash
   black . && isort . && flake8 . && mypy .
   ```

3. **Update documentation**
   - Update docstrings
   - Update README if needed
   - Add changelog entry

4. **Test manually**
   - Start the server
   - Test your changes manually
   - Check API documentation

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review code
3. **Feedback**: Address any requested changes
4. **Approval**: PR approved by maintainers
5. **Merge**: PR merged to main branch

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, include:

- **Environment**: OS, Python version, dependencies
- **Steps to reproduce**: Clear, step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error messages and stack traces
- **Additional context**: Screenshots, logs, etc.

### Feature Requests

When requesting features, include:

- **Problem description**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches considered
- **Additional context**: Use cases, examples, etc.

## 🔒 Security

### Reporting Security Issues

- **DO NOT** create public issues for security vulnerabilities
- Email security issues to: security@catalyst-platform.com
- Include detailed description and reproduction steps
- Allow time for investigation before public disclosure

### Security Guidelines

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Follow OWASP security guidelines
- Validate all user inputs
- Use secure authentication methods

## 🏷️ Commit Message Guidelines

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

### Examples
```
feat(api): add project search endpoint
fix(auth): resolve JWT token validation issue
docs(readme): update installation instructions
test(analysis): add unit tests for sentiment analysis
```

## 🎯 Development Tips

### Debugging

- Use the debugger in your IDE
- Add logging statements for complex logic
- Use FastAPI's automatic documentation for API testing
- Test with different data scenarios

### Performance

- Profile code for performance bottlenecks
- Use async/await for I/O operations
- Implement caching where appropriate
- Monitor database query performance

### Best Practices

- Keep functions small and focused
- Use dependency injection
- Implement proper error handling
- Write self-documenting code
- Follow SOLID principles

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and API docs
- **Code Review**: Ask for feedback in PRs

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation

Thank you for contributing to Catalyst Backend! 🚀