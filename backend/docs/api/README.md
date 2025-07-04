# Catalyst Backend API Documentation

Comprehensive API documentation for the Catalyst Backend system.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
- [WebSocket API](#websocket-api)
- [Examples](#examples)
- [SDKs and Libraries](#sdks-and-libraries)

## 🌟 Overview

The Catalyst Backend API is a RESTful API built with FastAPI that provides comprehensive project management, AI-powered analysis, and real-time communication capabilities.

### Key Features

- **Project Management**: Create, update, and manage projects
- **AI Analysis**: Text analysis with sentiment tracking
- **Therapeutic Interventions**: AI-powered therapy recommendations
- **File Processing**: Upload and process various file formats
- **Real-time Communication**: WebSocket support for live updates
- **Knowledge Base**: Vector search and knowledge management
- **Advanced Analytics**: Comprehensive reporting and insights

### API Characteristics

- **Protocol**: HTTPS (production), HTTP (development)
- **Format**: JSON
- **Authentication**: JWT Bearer tokens
- **Versioning**: URL path versioning (e.g., `/api/v1/`)
- **Documentation**: OpenAPI 3.0 specification

## 🔐 Authentication

### JWT Bearer Token

Most endpoints require authentication using JWT Bearer tokens.

```http
Authorization: Bearer <your_jwt_token>
```

### Obtaining a Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Token Refresh

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

## 🌐 Base URL

- **Production**: `https://api.catalyst.com`
- **Staging**: `https://staging-api.catalyst.com`
- **Development**: `http://localhost:8000`

## 📄 Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "name",
      "issue": "Field is required"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |
| `AI_SERVICE_ERROR` | AI service unavailable |
| `FILE_PROCESSING_ERROR` | File processing failed |

## 🚦 Rate Limiting

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per hour per user
- **Headers**: Rate limit information in response headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## 🛠️ Endpoints

### Health Check

#### GET /health

Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_services": "healthy"
  },
  "uptime": 86400
}
```

### Projects

#### GET /api/projects

Retrieve a list of projects.

**Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)
- `search` (string, optional): Search term for project names

**Response:**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "proj_123",
        "name": "Project Alpha",
        "description": "A sample project",
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "owner_id": "user_456"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 100
  }
}
```

#### POST /api/projects

Create a new project.

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description",
  "tags": ["tag1", "tag2"],
  "settings": {
    "privacy": "private",
    "collaboration": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proj_789",
    "name": "New Project",
    "description": "Project description",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_id": "user_456"
  }
}
```

#### GET /api/projects/{project_id}

Retrieve a specific project.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proj_123",
    "name": "Project Alpha",
    "description": "A sample project",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "owner_id": "user_456",
    "collaborators": [
      {
        "user_id": "user_789",
        "role": "editor",
        "joined_at": "2024-01-15T10:30:00Z"
      }
    ],
    "analytics": {
      "total_messages": 150,
      "sentiment_score": 0.75,
      "activity_level": "high"
    }
  }
}
```

#### PUT /api/projects/{project_id}

Update a project.

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "completed"
}
```

#### DELETE /api/projects/{project_id}

Delete a project.

**Response:**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

### Analysis

#### POST /api/analysis/text

Analyze text content for sentiment, topics, and insights.

**Request Body:**
```json
{
  "text": "This is a sample text to analyze",
  "project_id": "proj_123",
  "analysis_type": "comprehensive",
  "options": {
    "include_sentiment": true,
    "include_topics": true,
    "include_entities": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_456",
    "sentiment": {
      "score": 0.75,
      "label": "positive",
      "confidence": 0.92
    },
    "topics": [
      {
        "topic": "technology",
        "confidence": 0.85
      },
      {
        "topic": "innovation",
        "confidence": 0.78
      }
    ],
    "entities": [
      {
        "text": "FastAPI",
        "type": "TECHNOLOGY",
        "confidence": 0.95
      }
    ],
    "summary": "Positive sentiment analysis about technology and innovation",
    "processed_at": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /api/analysis/history/{project_id}

Retrieve analysis history for a project.

**Parameters:**
- `limit` (int, optional): Maximum records to return
- `start_date` (string, optional): Start date filter (ISO 8601)
- `end_date` (string, optional): End date filter (ISO 8601)

### AI Therapy

#### POST /api/v1/ai-therapy/recommendations

Get AI-powered therapy recommendations.

**Request Body:**
```json
{
  "user_input": "I've been feeling anxious lately",
  "context": {
    "previous_sessions": 3,
    "user_preferences": ["cognitive-behavioral", "mindfulness"]
  },
  "session_id": "session_789"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "type": "breathing_exercise",
        "title": "4-7-8 Breathing Technique",
        "description": "A calming breathing exercise",
        "duration": 300,
        "instructions": [
          "Inhale for 4 counts",
          "Hold for 7 counts",
          "Exhale for 8 counts"
        ]
      }
    ],
    "insights": {
      "detected_emotions": ["anxiety", "stress"],
      "confidence": 0.87,
      "suggested_approach": "cognitive-behavioral"
    },
    "follow_up": {
      "check_in_time": "2024-01-16T10:30:00Z",
      "suggested_topics": ["coping strategies", "stress management"]
    }
  }
}
```

### File Upload

#### POST /api/files/upload

Upload and process files (PDF, DOCX, images).

**Request:**
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: [binary file data]
project_id: proj_123
process_options: {"ocr": true, "extract_text": true}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "file_456",
    "filename": "document.pdf",
    "size": 1024000,
    "type": "application/pdf",
    "processed": true,
    "extracted_text": "Document content...",
    "metadata": {
      "pages": 5,
      "language": "en",
      "created_date": "2024-01-15T10:30:00Z"
    },
    "upload_url": "/api/files/file_456"
  }
}
```

### Knowledge Base

#### GET /api/knowledge-base/search

Search the knowledge base using vector similarity.

**Parameters:**
- `query` (string): Search query
- `limit` (int, optional): Maximum results (default: 10)
- `threshold` (float, optional): Similarity threshold (default: 0.7)

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "kb_123",
        "title": "FastAPI Best Practices",
        "content": "FastAPI is a modern web framework...",
        "similarity_score": 0.92,
        "source": "documentation",
        "tags": ["fastapi", "python", "web"]
      }
    ],
    "total_results": 1,
    "query_time": 0.045
  }
}
```

#### POST /api/knowledge-base/documents

Add a document to the knowledge base.

**Request Body:**
```json
{
  "title": "New Document",
  "content": "Document content...",
  "tags": ["tag1", "tag2"],
  "metadata": {
    "author": "John Doe",
    "category": "technical"
  }
}
```

## 🔌 WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/project_123');
```

### Message Types

#### Incoming Messages

**Analysis Update:**
```json
{
  "type": "analysis_update",
  "data": {
    "analysis_id": "analysis_456",
    "status": "completed",
    "results": {
      "sentiment": 0.75
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Real-time Message:**
```json
{
  "type": "message",
  "data": {
    "message_id": "msg_789",
    "content": "New message content",
    "sender": "user_456",
    "project_id": "proj_123"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Outgoing Messages

**Send Message:**
```json
{
  "type": "send_message",
  "data": {
    "content": "Hello, world!",
    "project_id": "proj_123"
  }
}
```

**Request Analysis:**
```json
{
  "type": "analyze_text",
  "data": {
    "text": "Text to analyze",
    "project_id": "proj_123"
  }
}
```

## 📚 Examples

### Python Example

```python
import requests
import json

# Authentication
auth_response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={
        'username': 'your_username',
        'password': 'your_password'
    }
)
token = auth_response.json()['access_token']

# Headers for authenticated requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Create a project
project_data = {
    'name': 'My New Project',
    'description': 'A project created via API'
}
response = requests.post(
    'http://localhost:8000/api/projects',
    json=project_data,
    headers=headers
)
project = response.json()['data']
print(f"Created project: {project['id']}")

# Analyze text
analysis_data = {
    'text': 'This is a great project!',
    'project_id': project['id']
}
response = requests.post(
    'http://localhost:8000/api/analysis/text',
    json=analysis_data,
    headers=headers
)
analysis = response.json()['data']
print(f"Sentiment score: {analysis['sentiment']['score']}")
```

### JavaScript Example

```javascript
// Authentication
const authResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'your_username',
    password: 'your_password'
  })
});
const { access_token } = await authResponse.json();

// Headers for authenticated requests
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};

// Create a project
const projectResponse = await fetch('http://localhost:8000/api/projects', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    name: 'My New Project',
    description: 'A project created via API'
  })
});
const { data: project } = await projectResponse.json();
console.log(`Created project: ${project.id}`);

// WebSocket connection
const ws = new WebSocket(`ws://localhost:8000/ws/${project.id}`);
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### cURL Examples

```bash
# Authentication
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Create project (replace TOKEN with actual token)
curl -X POST "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "API created project"}'

# Get projects
curl -X GET "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer TOKEN"

# Analyze text
curl -X POST "http://localhost:8000/api/analysis/text" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is amazing!", "project_id": "proj_123"}'
```

## 📦 SDKs and Libraries

### Official SDKs

- **Python SDK**: `pip install catalyst-python-sdk`
- **JavaScript SDK**: `npm install catalyst-js-sdk`
- **TypeScript SDK**: `npm install catalyst-ts-sdk`

### Community Libraries

- **Go Client**: `go get github.com/catalyst/go-client`
- **Ruby Gem**: `gem install catalyst-ruby`
- **PHP Package**: `composer require catalyst/php-client`

### OpenAPI Specification

Generate clients for any language using the OpenAPI specification:
- **Specification URL**: `http://localhost:8000/openapi.json`
- **Generator**: [OpenAPI Generator](https://openapi-generator.tech/)

## 🔗 Additional Resources

- **Interactive Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **GitHub Repository**: https://github.com/your-org/catalyst
- **Support**: support@catalyst-platform.com
- **Status Page**: https://status.catalyst.com

---

**Last Updated**: January 2024  
**API Version**: 1.0.0  
**Documentation Version**: 1.0.0