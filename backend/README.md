# Catalyst Backend API

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Enterprise-grade backend API for the Catalyst project management and analysis system, built with FastAPI and designed for scalability, security, and maintainability.

## 🚀 Features

- **RESTful API** with automatic OpenAPI documentation
- **Real-time WebSocket** support for live updates
- **AI-powered analysis** with OpenAI and Anthropic integration
- **Multi-format file processing** (PDF, DOCX, images with OCR)
- **Advanced reporting** and analytics
- **Therapeutic interventions** and recommendations
- **Knowledge base** with vector search capabilities
- **Enterprise security** with authentication and authorization
- **Production-ready** with Docker containerization
- **Comprehensive testing** and code quality tools

## 📋 Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

## 🛠️ Quick Start

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd catalyst/backend
   ```

2. **Run the setup script**
   ```bash
   ./scripts/setup-dev.sh
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Start the development server**
   ```bash
   python main.py
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Docker Development

1. **Start development environment**
   ```bash
   ./scripts/deploy.sh development
   ```

2. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## 🏗️ Project Structure

```
backend/
├── api/                    # API route handlers
│   ├── advanced_features.py
│   └── file_upload.py
├── config/                 # Configuration files
│   ├── ai_providers.py
│   ├── enhanced_config.py
│   ├── logging.py
│   └── nginx/             # Nginx configuration
├── database/              # Database models and migrations
│   ├── models.py
│   ├── unified_models.py
│   └── migrations/
├── routers/               # FastAPI routers
│   ├── analysis.py
│   ├── projects.py
│   ├── ai_therapy.py
│   └── ...
├── services/              # Business logic services
│   ├── ai_service.py
│   ├── analysis_service.py
│   ├── therapeutic_interventions.py
│   └── ...
├── schemas/               # Pydantic schemas
├── middleware/            # Custom middleware
├── validators/            # Input validators
├── tests/                 # Test suite
├── scripts/               # Deployment and utility scripts
├── docs/                  # Documentation
├── data/                  # Data storage
├── logs/                  # Application logs
└── reports/               # Generated reports
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/catalyst
# Or for SQLite: sqlite:///./catalyst.db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### AI Provider Setup

1. **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/)
2. **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com/)

## 🐳 Docker Deployment

### Development
```bash
# Start development environment with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Production
```bash
# Start production environment with all services
docker-compose --profile production up -d
```

### Services Included
- **catalyst-backend**: Main FastAPI application
- **postgres**: PostgreSQL database
- **redis**: Redis cache and session store
- **nginx**: Reverse proxy and load balancer (production)

## 🧪 Testing

### Run Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_analysis.py -v
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/projects` | GET, POST | Project management |
| `/api/analysis` | POST | Text analysis |
| `/api/v1/ai-therapy` | POST | AI therapy recommendations |
| `/api/v1/advanced` | POST | Advanced features |
| `/api/knowledge-base` | GET, POST | Knowledge base operations |

## 🔒 Security

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control
- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: API rate limiting with Redis
- **Input Validation**: Comprehensive input validation
- **Security Headers**: Standard security headers
- **Non-root Container**: Docker containers run as non-root user

## 📊 Monitoring

### Health Checks
- Application health: `/health`
- Database connectivity check
- AI service availability check

### Logging
- Structured logging with configurable levels
- Request/response logging
- Performance monitoring
- Error tracking

### Metrics (Optional)
- Prometheus metrics endpoint
- Custom business metrics
- Performance counters

## 🚀 Production Deployment

### Prerequisites
1. Docker and Docker Compose
2. SSL certificates (for HTTPS)
3. Environment variables configured
4. Database setup

### Deployment Steps
1. **Clone repository**
2. **Configure environment variables**
3. **Run deployment script**
   ```bash
   ./scripts/deploy.sh production
   ```
4. **Verify deployment**
   ```bash
   curl -f http://localhost:8000/health
   ```

### Scaling
```bash
# Scale backend service
docker-compose up -d --scale catalyst-backend=3

# Use nginx for load balancing
docker-compose --profile production up -d
```

## 🛠️ Development

### Adding New Features
1. Create feature branch
2. Add tests for new functionality
3. Implement feature
4. Update documentation
5. Run tests and quality checks
6. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Maintain test coverage above 80%

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python path and dependencies

2. **Database Connection**
   - Verify database URL in `.env`
   - Check database service status

3. **AI Service Errors**
   - Verify API keys are set
   - Check network connectivity

4. **Docker Issues**
   - Check Docker daemon status
   - Verify port availability
   - Review container logs

### Logs
```bash
# Application logs
tail -f logs/catalyst.log

# Docker logs
docker-compose logs -f catalyst-backend

# Database logs
docker-compose logs -f postgres
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review existing issues and discussions

---

**Built with ❤️ using FastAPI, Docker, and modern Python practices.**