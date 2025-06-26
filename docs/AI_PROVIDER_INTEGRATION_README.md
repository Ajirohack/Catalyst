# AI Provider Integration System

A comprehensive, multi-provider AI/LLM integration system for the Catalyst platform supporting OpenAI, Mistral, Anthropic, OpenRouter, Ollama, Groq, and Huggingface with dynamic configuration, knowledge upload, and centralized management.

## 🚀 Features

### Multi-Provider Support

- **OpenAI**: GPT-4, GPT-3.5-turbo, embeddings
- **Mistral**: Mistral Large, Medium, Small models
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku
- **OpenRouter**: Access to 100+ models via single API
- **Ollama**: Local LLM deployment (Llama 2, Code Llama, etc.)
- **Groq**: Lightning-fast inference
- **Hugging Face**: Thousands of open-source models

### Dynamic Configuration

- **Admin UI**: Complete provider management interface
- **Real-time Model Sync**: Automatically fetch available models
- **Secure Key Storage**: Encrypted API key management
- **Health Monitoring**: Provider status and performance tracking
- **Cost Analytics**: Usage and cost tracking per provider

### Advanced Features

- **Intelligent Routing**: Automatic failover and load balancing
- **Knowledge Base Integration**: Upload and AI-process documents
- **Per-Request Model Selection**: Dynamic model choice in UI
- **Advanced Parameters**: Temperature, tokens, streaming support
- **Performance Monitoring**: Response times, success rates

## 📁 Architecture

```
backend/
├── database/
│   ├── models_ai_providers.py          # Database models
│   └── init_ai_providers.py            # DB initialization
├── services/
│   ├── ai_provider_service.py          # Provider CRUD & management
│   ├── enhanced_llm_router.py          # Multi-provider router
│   └── encryption_service.py           # Secure key storage
├── routers/
│   └── ai_providers_enhanced_admin.py  # Admin API endpoints
├── schemas/
│   └── ai_provider_enhanced_schema.py  # Pydantic schemas
├── startup.py                          # System initialization
├── demo_ai_integration.py              # Integration demo
└── test_ai_integration.py              # Test suite

frontend/
├── components/
│   ├── AIModelSelector.jsx             # Model selection component
│   └── KnowledgeBaseUpload.jsx         # Document upload
└── pages/admin/
    └── AIProviderManagement.jsx        # Admin interface
```

## 🛠️ Setup

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see below)
export OPENAI_API_KEY='your-openai-api-key'
export ANTHROPIC_API_KEY='your-anthropic-api-key'
# ... other API keys

# Initialize system and start
python startup.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=sqlite:///./catalyst.db

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_DEFAULT_MODEL=gpt-4-turbo

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_DEFAULT_MODEL=claude-3-sonnet-20240229

# Mistral
MISTRAL_API_KEY=your-mistral-api-key
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MISTRAL_DEFAULT_MODEL=mistral-large-latest

# OpenRouter
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3-opus

# Groq
GROQ_API_KEY=your-groq-api-key
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_DEFAULT_MODEL=llama2-70b-4096

# Hugging Face
HUGGINGFACE_API_KEY=your-huggingface-api-key
HUGGINGFACE_BASE_URL=https://api-inference.huggingface.co

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2

# Security
ENCRYPTION_KEY=your-32-character-encryption-key
```

## 📚 Usage

### Admin Interface

Navigate to `http://localhost:3000/admin/ai-providers` to:

- **Manage Providers**: Add, edit, enable/disable providers
- **Configure Models**: Sync and manage available models
- **Test Connections**: Verify provider connectivity
- **Monitor Usage**: Track costs, performance, and health
- **Secure Keys**: Encrypted API key storage

### Programmatic Usage

#### Using the Enhanced Router

```python
from services.enhanced_llm_router import enhanced_llm_router

# Simple chat completion
request = {
    "messages": [
        {"role": "user", "content": "Hello, world!"}
    ],
    "max_tokens": 100,
    "temperature": 0.7,
    "provider_preference": "openai"  # Optional
}

response = await enhanced_llm_router.generate_response(request)
print(f"Response: {response.content}")
print(f"Provider: {response.provider}")
print(f"Tokens: {response.usage['total_tokens']}")
```

#### Using the Provider Service

```python
from services.ai_provider_service import AIProviderService

# Create provider
provider_data = {
    "provider_type": "openai",
    "name": "My OpenAI Provider",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "enabled": True
}

provider = await provider_service.create_provider(provider_data)

# Test connection
result = await provider_service.test_provider_connection(provider["id"])
print(f"Connection status: {result['success']}")
```

### Frontend Components

#### AI Model Selector

```jsx
import AIModelSelector from '../components/AIModelSelector';

function MyComponent() {
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [modelParams, setModelParams] = useState({});

  return (
    <AIModelSelector
      selectedProvider={selectedProvider}
      onProviderChange={setSelectedProvider}
      selectedModel={selectedModel}
      onModelChange={setSelectedModel}
      showAdvancedSettings={true}
      onParametersChange={setModelParams}
    />
  );
}
```

#### Knowledge Base Upload

```jsx
import KnowledgeBaseUpload from '../components/KnowledgeBaseUpload';

function UploadPage() {
  const handleUploadComplete = (results) => {
    console.log('Upload results:', results);
  };

  return (
    <KnowledgeBaseUpload
      projectId="project-123"
      onUploadComplete={handleUploadComplete}
    />
  );
}
```

## 🔧 API Endpoints

### Provider Management

```bash
# List all providers
GET /api/v1/admin/ai-providers/

# Get supported provider types
GET /api/v1/admin/ai-providers/supported

# Create provider
POST /api/v1/admin/ai-providers/
{
  "provider_type": "openai",
  "name": "My OpenAI",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "enabled": true
}

# Update provider
PUT /api/v1/admin/ai-providers/{id}
{
  "name": "Updated Name",
  "enabled": false
}

# Test provider connection
POST /api/v1/admin/ai-providers/{id}/test

# Sync models from provider
POST /api/v1/admin/ai-providers/{id}/sync-models

# Get provider analytics
GET /api/v1/admin/ai-providers/{id}/analytics

# Delete provider
DELETE /api/v1/admin/ai-providers/{id}

# System health check
GET /api/v1/admin/ai-providers/health
```

### Model Management

```bash
# List models for provider
GET /api/v1/admin/ai-providers/{id}/models

# Add model to provider
POST /api/v1/admin/ai-providers/{id}/models
{
  "name": "gpt-4-turbo",
  "description": "GPT-4 Turbo model",
  "max_tokens": 128000,
  "cost_input_per_1k": 0.01,
  "cost_output_per_1k": 0.03
}

# Update model
PUT /api/v1/admin/ai-providers/{provider_id}/models/{model_id}

# Delete model
DELETE /api/v1/admin/ai-providers/{provider_id}/models/{model_id}
```

## 🧪 Testing

### Run Integration Tests

```bash
cd backend

# Test all endpoints and functionality
python test_ai_integration.py

# Run demo
python demo_ai_integration.py
```

### Test Coverage

- ✅ Provider CRUD operations
- ✅ Model synchronization
- ✅ Connection testing
- ✅ Authentication & security
- ✅ Error handling & failover
- ✅ Performance monitoring
- ✅ Cost tracking
- ✅ Frontend integration

## 🔒 Security

### API Key Protection

- **Encryption**: All API keys encrypted at rest
- **Secure Storage**: Keys never logged or exposed
- **Access Control**: Admin-only key management
- **Key Rotation**: Support for key updates

### Request Security

- **Rate Limiting**: Per-provider request limits
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error messages
- **Audit Logging**: Track all provider operations

## 📊 Monitoring

### Health Checks

- **Provider Status**: Real-time connectivity monitoring
- **Response Times**: Performance tracking
- **Error Rates**: Failure rate monitoring
- **Cost Tracking**: Usage and cost analytics

### Analytics Dashboard

- **Usage Metrics**: Requests, tokens, costs per provider
- **Performance Metrics**: Response times, success rates
- **Cost Analysis**: Detailed cost breakdown
- **Trending**: Historical usage patterns

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**

   ```bash
   export ENVIRONMENT=production
   export DATABASE_URL=postgresql://user:pass@host:5432/catalyst
   export REDIS_URL=redis://host:6379/0
   ```

2. **Security Hardening**

   ```bash
   # Generate secure encryption key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Set secure headers
   export SECURE_HEADERS=true
   export ALLOWED_HOSTS=your-domain.com
   ```

3. **Scaling Configuration**

   ```bash
   # Load balancing
   export WORKERS=4
   export MAX_CONNECTIONS=1000
   
   # Caching
   export ENABLE_CACHING=true
   export CACHE_TTL=3600
   ```

### Docker Deployment

```dockerfile
# Use provided Dockerfile
docker build -t catalyst-ai .
docker run -p 8000:8000 --env-file .env catalyst-ai
```

## 🛣️ Roadmap

### Phase 1 - Current ✅

- [x] Multi-provider support
- [x] Dynamic configuration
- [x] Admin UI
- [x] Basic analytics

### Phase 2 - In Progress 🚧

- [ ] Advanced knowledge base integration
- [ ] Vector search capabilities
- [ ] Real-time streaming
- [ ] Model fine-tuning support

### Phase 3 - Planned 📋

- [ ] Custom model deployment
- [ ] Advanced prompt engineering
- [ ] Multi-modal support (vision, audio)
- [ ] Automated model selection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [Mistral API Documentation](https://docs.mistral.ai)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Groq Documentation](https://console.groq.com/docs)
- [Hugging Face Documentation](https://huggingface.co/docs)

---

**Built with ❤️ for the Catalyst Platform**
