# Enhanced Catalyst - AI-Powered Relationship Analysis Platform

## Overview

Enhanced Catalyst is a comprehensive AI-powered platform that combines advanced conversation analysis with therapeutic insights and real-time coaching. This enhanced version integrates the best features from both the original Catalyst project and the Relationship-Therapist system to create a unified, powerful tool for relationship analysis and improvement.

## 🚀 Key Features

### Core Analysis Capabilities

- **Comprehensive Conversation Analysis**: Multi-dimensional analysis of communication patterns
- **Sentiment Analysis**: Advanced emotion detection and tracking
- **Pattern Recognition**: Identification of communication trends and behaviors
- **Relationship Health Scoring**: Quantitative assessment of relationship dynamics
- **Conflict Detection**: Early warning system for potential issues

### AI-Powered Therapy & Coaching

- **Therapeutic Interventions**: AI-generated therapeutic recommendations
- **Real-time Coaching**: Live suggestions during conversations
- **Multiple Therapy Approaches**: Support for various therapeutic methodologies
- **Personalized Insights**: Tailored recommendations based on user profiles
- **Crisis Intervention**: Automated detection and response to urgent situations

### Advanced Features

- **Multi-Platform Support**: Import conversations from various messaging platforms
- **Goal Tracking**: Set and monitor relationship improvement goals
- **Progress Reports**: Comprehensive analytics and progress visualization
- **WebSocket Integration**: Real-time communication and updates
- **Secure Data Handling**: Privacy-first approach with encrypted storage

## 🏗️ Architecture

### Backend (FastAPI)

- **Enhanced AI Services**: Multi-provider AI integration (OpenAI, Anthropic, Local)
- **Unified Database Schema**: Comprehensive data models for all features
- **RESTful API**: Well-documented endpoints for all functionality
- **WebSocket Support**: Real-time coaching and notifications
- **Modular Design**: Easily extensible and maintainable codebase

### Frontend (React)

- **Modern UI**: Clean, intuitive interface built with Material-UI
- **Real-time Updates**: Live coaching and analysis results
- **Responsive Design**: Works seamlessly across devices
- **Interactive Dashboards**: Rich visualizations and analytics
- **Progressive Web App**: Offline capabilities and mobile optimization

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

### Optional

- PostgreSQL (for production)
- Redis (for caching and sessions)
- Docker (for containerized deployment)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Catalyst
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

#### Required Environment Variables

```env
# AI Provider API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Application Settings
CATALYST_SECRET_KEY=your_secret_key
CATALYST_ENVIRONMENT=development

# Database (SQLite by default)
CATALYST_DATABASE_URL=sqlite:///./catalyst_unified.db
```

#### Database Setup

```bash
# Run database migration
python database/migration_script.py

# Verify migration
python -c "from database.migration_script import DatabaseMigration; m = DatabaseMigration(); print(m.verify_migration())"
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install

# Create environment file
cp .env.example .env.local

# Edit with your backend URL
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
```

## 🚀 Running the Application

### Development Mode

#### Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend

```bash
cd frontend
npm start
```

The application will be available at:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API Documentation: <http://localhost:8000/docs>

### Production Deployment

#### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

#### Manual Deployment

```bash
# Backend
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
# Serve the build directory with your preferred web server
```

## 📚 API Documentation

### Core Endpoints

#### Projects

- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Analysis

- `POST /api/v1/analysis/upload` - Upload conversation data
- `GET /api/v1/analysis/{id}` - Get analysis results
- `POST /api/v1/analysis/batch` - Batch analysis

#### AI Therapy

- `POST /api/v1/ai-therapy/analyze-conversation` - Comprehensive analysis
- `POST /api/v1/ai-therapy/generate-intervention` - Generate therapeutic interventions
- `POST /api/v1/ai-therapy/real-time-coaching` - Get real-time coaching
- `GET /api/v1/ai-therapy/health` - Service health check

#### WebSocket

- `WS /api/v1/ai-therapy/ws/coaching/{user_id}/{project_id}` - Real-time coaching

### Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test

# Coverage report
npm run test:coverage
```

### Integration Tests

```bash
# Run full test suite
./scripts/run_tests.sh
```

## 🔧 Configuration

### AI Providers

The system supports multiple AI providers:

#### OpenAI

```env
OPENAI_API_KEY=your_key
CATALYST_OPENAI_MODEL=gpt-4
CATALYST_OPENAI_MAX_TOKENS=2000
```

#### Anthropic

```env
ANTHROPIC_API_KEY=your_key
CATALYST_ANTHROPIC_MODEL=claude-3-sonnet-20240229
CATALYST_ANTHROPIC_MAX_TOKENS=2000
```

#### Local AI (Ollama)

```env
CATALYST_LOCAL_AI_ENDPOINT=http://localhost:11434
CATALYST_LOCAL_AI_MODEL=llama2
```

### Database Options

#### SQLite (Default)

```env
CATALYST_DATABASE_TYPE=sqlite
CATALYST_DATABASE_URL=sqlite:///./catalyst_unified.db
```

#### PostgreSQL

```env
CATALYST_DATABASE_TYPE=postgresql
CATALYST_POSTGRES_HOST=localhost
CATALYST_POSTGRES_PORT=5432
CATALYST_POSTGRES_USER=catalyst
CATALYST_POSTGRES_PASSWORD=your_password
CATALYST_POSTGRES_DATABASE=catalyst_unified
```

### Feature Flags

Enable/disable features via environment variables:

```env
CATALYST_THERAPY_ENABLED=true
CATALYST_REAL_TIME_COACHING_ENABLED=true
CATALYST_INTERVENTION_AUTO_DELIVERY=false
```

## 📊 Usage Examples

### Basic Conversation Analysis

```python
import requests

# Upload conversation data
response = requests.post(
    "http://localhost:8000/api/v1/ai-therapy/analyze-conversation",
    json={
        "project_id": "your_project_id",
        "conversation_data": [
            {
                "sender": "Alice",
                "content": "I feel like we never talk anymore",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "sender": "Bob",
                "content": "I'm sorry, I've been really busy with work",
                "timestamp": "2024-01-01T10:01:00Z"
            }
        ],
        "analysis_types": ["comprehensive", "sentiment"],
        "include_therapeutic": True
    }
)

analysis_result = response.json()
print(f"Overall Score: {analysis_result['analysis_results']['comprehensive']['overall_score']}")
```

### Real-time Coaching

```javascript
// WebSocket connection for real-time coaching
const ws = new WebSocket('ws://localhost:8000/api/v1/ai-therapy/ws/coaching/user123/project456');

ws.onmessage = (event) => {
    const coaching = JSON.parse(event.data);
    if (coaching.type === 'coaching') {
        console.log('Coaching suggestion:', coaching.data.coaching_suggestion);
    }
};

// Send message for analysis
ws.send(JSON.stringify({
    content: "I'm feeling frustrated with this conversation",
    platform: "generic",
    context: { urgency: "medium" }
}));
```

## 🔒 Security

### Data Protection

- All API communications use HTTPS in production
- Sensitive data is encrypted at rest
- User data is anonymized in analytics
- GDPR compliant data handling

### API Security

- JWT token authentication
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS protection

### Privacy Features

- Opt-in data sharing
- User data deletion capabilities
- Audit logging
- Consent management

## 🚨 Troubleshooting

### Common Issues

#### AI Provider Errors

```bash
# Test AI provider connectivity
curl -X POST "http://localhost:8000/api/v1/ai-therapy/test-ai-provider" \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "test_message": "Hello"}'
```

#### Database Issues

```bash
# Reset database
rm catalyst_unified.db
python database/migration_script.py
```

#### WebSocket Connection Issues

- Check firewall settings
- Verify WebSocket support in proxy/load balancer
- Ensure proper CORS configuration

### Logs

Check application logs:

```bash
# Backend logs
tail -f backend/catalyst.log

# Frontend logs (browser console)
# Check browser developer tools
```

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `./scripts/run_tests.sh`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Standards

- Python: Follow PEP 8, use type hints
- JavaScript: Use ESLint configuration
- Documentation: Update README and API docs
- Tests: Maintain >80% code coverage

### Adding New Features

1. **AI Services**: Extend `EnhancedAIService` class
2. **Analysis Types**: Add to `AnalysisType` enum and implement handler
3. **Therapy Approaches**: Add to `TherapyApproach` enum
4. **Database Models**: Update `unified_models.py` and create migration

## 📈 Roadmap

### Upcoming Features

- [ ] Mobile app (React Native)
- [ ] Voice conversation analysis
- [ ] Multi-language support
- [ ] Advanced visualization dashboards
- [ ] Integration with popular messaging platforms
- [ ] Therapist collaboration tools
- [ ] Group therapy support
- [ ] AI model fine-tuning capabilities

### Performance Improvements

- [ ] Caching layer optimization
- [ ] Database query optimization
- [ ] Async processing for large datasets
- [ ] CDN integration for static assets

## �️ Roadmap

### Phase 2.1: Knowledge Base Integration (Upcoming)

**Objective**: Implement advanced knowledge management and semantic search capabilities.

#### Vector Database Setup

- **Vector Search Service** (`backend/services/vector_search.py`)
  - Semantic document search with vector embeddings
  - Support for multiple vector databases (Pinecone, Weaviate, ChromaDB)
  - Real-time indexing and similarity search
  - Integration with existing conversation analysis

- **Knowledge Base Service** (`backend/services/knowledge_base.py`)
  - Document chunking and preprocessing pipeline
  - Automated metadata extraction and tagging
  - Document versioning and update management
  - RESTful API for knowledge operations

#### Document Management UI

- **Knowledge Base Interface** (`frontend/src/pages/KnowledgeBase.jsx`)
  - Drag-and-drop document upload with validation
  - Advanced search with filters and faceting
  - Document preview, annotation, and categorization
  - Real-time search suggestions and auto-complete

**Benefits**:

- Enhanced AI recommendations through contextual knowledge retrieval
- Improved therapeutic interventions with evidence-based resources
- Scalable document management for relationship coaching materials
- Semantic search across relationship therapy resources

**Timeline**: 22-26 hours | **Priority**: High | **Status**: Planned

### Phase 2.2: Enhanced Chrome Extension (Future)

- Advanced AI model integration in browser extension
- Context-aware therapeutic suggestions
- Personalized coaching patterns

### Phase 2.3: Testing Infrastructure Enhancement (Future)

- Comprehensive integration test suite
- End-to-end workflow automation
- Performance benchmarking tools

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Catalyst project contributors
- Relationship-Therapist project team
- OpenAI and Anthropic for AI capabilities
- FastAPI and React communities
- All beta testers and early adopters

## 📞 Support

- **Documentation**: [Full API Documentation](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: <support@catalyst.ai>

---

**Enhanced Catalyst** - Empowering relationships through AI-driven insights and therapeutic guidance.
