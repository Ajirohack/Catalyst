# Catalyst Backend API

A comprehensive FastAPI-based backend for project management with real-time communication analysis, sentiment tracking, and team collaboration insights.

## 🚀 Features

- **Project Management**: Create, update, and manage projects with detailed metadata
- **Real-time Analysis**: WebSocket-based communication analysis with sentiment tracking
- **Text Analysis**: Advanced NLP processing for meeting transcripts and messages
- **Team Insights**: Participant tracking and collaboration metrics
- **Performance Monitoring**: Built-in request tracking and performance metrics
- **Enhanced Validation**: Comprehensive input validation and security measures
- **Structured Logging**: Detailed logging with configurable levels and formats

## 📋 Requirements

- Python 3.8+
- FastAPI 0.104.1+
- See `requirements.txt` for complete dependency list

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ajirohack/Catalyst.git
cd Catalyst/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 5. Run the Application

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📖 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🏗️ Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── config/                # Configuration modules
│   ├── __init__.py
│   └── logging.py         # Logging configuration
├── database/              # Database models and future migrations
│   ├── __init__.py
│   └── models.py          # Database model definitions
├── docs/                  # API documentation enhancements
│   ├── __init__.py
│   └── api_documentation.py
├── middleware/            # Custom middleware
│   ├── __init__.py
│   └── performance.py     # Performance monitoring
├── models/                # Pydantic models
│   ├── __init__.py
│   └── project.py
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── analysis.py        # Text analysis endpoints
│   └── projects.py        # Project management endpoints
├── schemas/               # Request/response schemas
│   ├── __init__.py
│   └── project_schema.py
├── services/              # Business logic
│   ├── __init__.py
│   ├── analysis_service.py
│   ├── project_service.py
│   └── whisper_service.py
├── tests/                 # Test suite
│   ├── conftest.py
│   ├── test_analysis.py
│   ├── test_integration.py
│   ├── test_main.py
│   └── test_projects.py
└── validators/            # Input validation
    ├── __init__.py
    └── input_validators.py
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Security
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO

# Performance
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

### Logging Configuration

The application uses structured logging with multiple handlers:

- **Console**: Real-time log output
- **File**: Detailed logs in `logs/catalyst.log`
- **Error File**: Error-only logs in `logs/errors.log`

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests
pytest tests/test_*.py -v

# Integration tests
pytest tests/test_integration.py -v

# With coverage
pytest --cov=. --cov-report=html
```

### Test Coverage

Current test coverage: **58 tests passing** with comprehensive coverage of:

- Project management endpoints
- Text analysis functionality
- WebSocket communication
- Error handling and validation
- Integration workflows

## 🔌 API Endpoints

### Projects

- `POST /api/projects/` - Create new project
- `GET /api/projects/` - List all projects
- `GET /api/projects/{project_id}` - Get project details
- `PUT /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project

### Analysis

- `POST /api/analysis/text` - Analyze text content
- `GET /api/analysis/history/{project_id}` - Get analysis history
- `WebSocket /ws/{project_id}` - Real-time message processing

### Health & Monitoring

- `GET /health` - System health check
- `GET /api/analysis/health/check` - Analysis service health
- `GET /api/projects/health/check` - Project service health

## 🌐 WebSocket Communication

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/project-id');
```

### Message Types

```json
{
  "type": "whisper_message",
  "data": {
    "content": "Message content",
    "sender": "user@example.com",
    "platform": "slack",
    "project_id": "project-uuid"
  }
}
```

Supported types: `whisper_message`, `analysis_request`, `status_update`, `ping`, `pong`

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Configure PostgreSQL or preferred database
3. **Caching**: Set up Redis for improved performance
4. **Monitoring**: Enable Prometheus metrics collection
5. **Security**: Implement authentication and rate limiting
6. **SSL/TLS**: Configure HTTPS for production

## 🔒 Security

### Current Security Measures

- Input validation and sanitization
- CORS configuration
- Request size limits
- SQL injection prevention (prepared for database integration)

### Production Security Checklist

- [ ] Implement authentication (JWT/OAuth)
- [ ] Add rate limiting
- [ ] Configure HTTPS/SSL
- [ ] Set up API key management
- [ ] Enable request logging
- [ ] Implement role-based access control

## 📊 Performance Monitoring

The application includes built-in performance monitoring:

- **Request Timing**: Automatic response time tracking
- **Request Counting**: Endpoint usage statistics
- **Slow Request Detection**: Configurable threshold alerts
- **Error Rate Monitoring**: Automatic error tracking

### Performance Headers

Each response includes performance headers:

- `X-Process-Time`: Request processing time in seconds
- `X-Request-Count`: Total requests to this endpoint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Code Quality Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

For support and questions:

- **GitHub Issues**: [Create an issue](https://github.com/Ajirohack/Catalyst/issues)
- **Documentation**: Check the `/docs` endpoint when running
- **Email**: support@catalyst-platform.com

## 🗺️ Roadmap

### Upcoming Features

- [ ] Database integration (PostgreSQL)
- [ ] User authentication and authorization
- [ ] Advanced analytics dashboard
- [ ] Real-time collaboration features
- [ ] Mobile API optimizations
- [ ] Microservices architecture
- [ ] Advanced caching strategies
- [ ] Machine learning integration

### Version History

- **v1.0.0**: Initial release with core functionality
  - Project management
  - Text analysis
  - WebSocket communication
  - Comprehensive test suite